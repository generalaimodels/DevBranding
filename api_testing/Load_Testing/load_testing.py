#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Load Testing Framework in Python

This script provides a complete solution for load testing web applications,
APIs, and services with detailed metrics collection, analysis, and reporting.
"""

import argparse
import asyncio
import csv
import datetime
import json
import logging
import os
import platform
import random
import statistics
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
import psutil
import requests
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("load_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("load_tester")

# Constants
VERSION = "1.0.0"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_USER_AGENT = (
    "LoadTester/1.0.0 "
    f"(Python/{platform.python_version()}; "
    f"{platform.system()}/{platform.release()})"
)


class HttpMethod(Enum):
    """HTTP methods supported by the load tester."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RequestConfig:
    """Configuration for an individual HTTP request."""
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    timeout: int = DEFAULT_TIMEOUT
    verify_ssl: bool = True
    auth: Optional[Tuple[str, str]] = None


@dataclass
class RequestStats:
    """Statistics for a single request."""
    request_id: str
    url: str
    method: str
    status_code: int
    response_time: float  # in milliseconds
    response_size: int  # in bytes
    timestamp: float
    success: bool
    error: Optional[str] = None


@dataclass
class TestResult:
    """Overall results from a load test."""
    start_time: float
    end_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_bytes_received: int
    request_stats: List[RequestStats] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Total test duration in seconds."""
        return self.end_time - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful requests."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def requests_per_second(self) -> float:
        """Average number of requests per second."""
        if self.duration == 0:
            return 0.0
        return self.total_requests / self.duration
    
    @property
    def average_response_time(self) -> float:
        """Average response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        return statistics.mean(
            stat.response_time for stat in self.request_stats if stat.success
        )
    
    @property
    def median_response_time(self) -> float:
        """Median response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        return statistics.median(
            stat.response_time for stat in self.request_stats if stat.success
        )
    
    @property
    def min_response_time(self) -> float:
        """Minimum response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        return min(
            (stat.response_time for stat in self.request_stats if stat.success),
            default=0.0
        )
    
    @property
    def max_response_time(self) -> float:
        """Maximum response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        return max(
            (stat.response_time for stat in self.request_stats if stat.success),
            default=0.0
        )
    
    @property
    def p90_response_time(self) -> float:
        """90th percentile response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        response_times = sorted(
            stat.response_time for stat in self.request_stats if stat.success
        )
        if not response_times:
            return 0.0
        index = int(len(response_times) * 0.9)
        return response_times[index]
    
    @property
    def p95_response_time(self) -> float:
        """95th percentile response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        response_times = sorted(
            stat.response_time for stat in self.request_stats if stat.success
        )
        if not response_times:
            return 0.0
        index = int(len(response_times) * 0.95)
        return response_times[index]
    
    @property
    def p99_response_time(self) -> float:
        """99th percentile response time in milliseconds."""
        if not self.request_stats:
            return 0.0
        response_times = sorted(
            stat.response_time for stat in self.request_stats if stat.success
        )
        if not response_times:
            return 0.0
        index = int(len(response_times) * 0.99)
        return response_times[index]
    
    @property
    def throughput_bytes_per_second(self) -> float:
        """Throughput in bytes per second."""
        if self.duration == 0:
            return 0.0
        return self.total_bytes_received / self.duration


@dataclass
class LoadTestConfig:
    """Configuration for a load test."""
    name: str
    request_config: RequestConfig
    concurrent_users: int = 10
    ramp_up_time: int = 0  # seconds
    test_duration: int = 60  # seconds
    requests_per_user: Optional[int] = None  # None means unlimited
    think_time_min: float = 0.0  # seconds
    think_time_max: float = 0.0  # seconds
    request_timeout: int = DEFAULT_TIMEOUT
    use_async: bool = True
    max_retries: int = 0
    retry_delay: float = 1.0  # seconds
    output_dir: str = "results"
    save_responses: bool = False
    verbose: bool = False


class LoadTester:
    """Main load testing class that orchestrates the test execution."""

    def __init__(self, config: LoadTestConfig):
        """Initialize the load tester with the given configuration."""
        self.config = config
        self.console = Console()
        self.results = TestResult(
            start_time=0.0,
            end_time=0.0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            total_bytes_received=0,
        )
        self.system_metrics = []
        self.stop_event = asyncio.Event() if config.use_async else None
        self._create_output_dir()
        
    def _create_output_dir(self) -> None:
        """Create the output directory for test results if it doesn't exist."""
        output_dir = Path(self.config.output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        
        # Create a timestamped directory for this test run
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_dir = output_dir / f"{self.config.name}_{timestamp}"
        self.test_dir.mkdir()
        
    def _collect_system_metrics(self) -> None:
        """Collect system metrics during the test."""
        while time.time() < self.results.end_time:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            
            self.system_metrics.append({
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_available": memory.available,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
            })
            
            time.sleep(1)
    
    def _save_metrics(self) -> None:
        """Save collected metrics to disk."""
        # Save request stats as CSV
        requests_file = self.test_dir / "request_stats.csv"
        with open(requests_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "request_id", "url", "method", "status_code", 
                "response_time", "response_size", "timestamp", 
                "success", "error"
            ])
            for stat in self.results.request_stats:
                writer.writerow([
                    stat.request_id, stat.url, stat.method, stat.status_code,
                    stat.response_time, stat.response_size, stat.timestamp,
                    stat.success, stat.error or ""
                ])
        
        # Save system metrics as CSV
        if self.system_metrics:
            metrics_file = self.test_dir / "system_metrics.csv"
            with open(metrics_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "cpu_percent", "memory_percent", 
                    "memory_used", "memory_available", 
                    "network_bytes_sent", "network_bytes_recv"
                ])
                for metric in self.system_metrics:
                    writer.writerow([
                        metric["timestamp"],
                        metric["cpu_percent"],
                        metric["memory_percent"],
                        metric["memory_used"],
                        metric["memory_available"],
                        metric["network_bytes_sent"],
                        metric["network_bytes_recv"]
                    ])
        
        # Save summary as JSON
        summary_file = self.test_dir / "summary.json"
        summary = {
            "test_name": self.config.name,
            "start_time": self.results.start_time,
            "end_time": self.results.end_time,
            "duration": self.results.duration,
            "concurrent_users": self.config.concurrent_users,
            "total_requests": self.results.total_requests,
            "successful_requests": self.results.successful_requests,
            "failed_requests": self.results.failed_requests,
            "success_rate": self.results.success_rate,
            "requests_per_second": self.results.requests_per_second,
            "total_bytes_received": self.results.total_bytes_received,
            "throughput_bytes_per_second": self.results.throughput_bytes_per_second,
            "response_time": {
                "average": self.results.average_response_time,
                "median": self.results.median_response_time,
                "min": self.results.min_response_time,
                "max": self.results.max_response_time,
                "p90": self.results.p90_response_time,
                "p95": self.results.p95_response_time,
                "p99": self.results.p99_response_time,
            }
        }
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
    
    def _generate_report(self) -> None:
        """Generate visual reports of the test results."""
        if not self.results.request_stats:
            logger.warning("No request stats available for generating reports")
            return
        
        # Create plots directory
        plots_dir = self.test_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # 1. Response time distribution
        plt.figure(figsize=(10, 6))
        response_times = [
            stat.response_time for stat in self.results.request_stats if stat.success
        ]
        if response_times:
            plt.hist(response_times, bins=50, alpha=0.75)
            plt.axvline(
                x=self.results.average_response_time,
                color='r',
                linestyle='--',
                label=f'Mean: {self.results.average_response_time:.2f} ms'
            )
            plt.axvline(
                x=self.results.median_response_time,
                color='g',
                linestyle='--',
                label=f'Median: {self.results.median_response_time:.2f} ms'
            )
            plt.axvline(
                x=self.results.p95_response_time,
                color='b',
                linestyle='--',
                label=f'95th Percentile: {self.results.p95_response_time:.2f} ms'
            )
            plt.title('Response Time Distribution')
            plt.xlabel('Response Time (ms)')
            plt.ylabel('Frequency')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(plots_dir / "response_time_distribution.png")
            plt.close()
        
        # 2. Response time over time
        plt.figure(figsize=(10, 6))
        timestamps = [
            stat.timestamp - self.results.start_time 
            for stat in self.results.request_stats if stat.success
        ]
        response_times = [
            stat.response_time 
            for stat in self.results.request_stats if stat.success
        ]
        if timestamps and response_times:
            plt.scatter(timestamps, response_times, alpha=0.5, s=10)
            # Add trend line
            z = np.polyfit(timestamps, response_times, 1)
            p = np.poly1d(z)
            plt.plot(
                timestamps, p(timestamps), 
                "r--", linewidth=2,
                label=f'Trend: y={z[0]:.4f}x+{z[1]:.2f}'
            )
            plt.title('Response Time Over Test Duration')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Response Time (ms)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(plots_dir / "response_time_over_time.png")
            plt.close()
        
        # 3. Requests per second over time
        plt.figure(figsize=(10, 6))
        # Group requests into 1-second intervals
        start_time = self.results.start_time
        end_time = self.results.end_time
        duration = int(end_time - start_time) + 1
        requests_per_second = [0] * duration
        
        for stat in self.results.request_stats:
            second = min(
                int(stat.timestamp - start_time),
                duration - 1
            )
            if second >= 0:
                requests_per_second[second] += 1
        
        plt.bar(range(duration), requests_per_second, alpha=0.7)
        plt.axhline(
            y=self.results.requests_per_second,
            color='r',
            linestyle='--',
            label=f'Average: {self.results.requests_per_second:.2f} req/s'
        )
        plt.title('Requests Per Second')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Number of Requests')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(plots_dir / "requests_per_second.png")
        plt.close()
        
        # 4. System metrics over time (if available)
        if self.system_metrics:
            # CPU usage
            plt.figure(figsize=(10, 6))
            timestamps = [
                m["timestamp"] - self.results.start_time 
                for m in self.system_metrics
            ]
            cpu_percent = [m["cpu_percent"] for m in self.system_metrics]
            plt.plot(timestamps, cpu_percent, 'b-', linewidth=2)
            plt.title('CPU Usage During Test')
            plt.xlabel('Time (seconds)')
            plt.ylabel('CPU Usage (%)')
            plt.grid(True, alpha=0.3)
            plt.savefig(plots_dir / "cpu_usage.png")
            plt.close()
            
            # Memory usage
            plt.figure(figsize=(10, 6))
            memory_percent = [m["memory_percent"] for m in self.system_metrics]
            plt.plot(timestamps, memory_percent, 'g-', linewidth=2)
            plt.title('Memory Usage During Test')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Memory Usage (%)')
            plt.grid(True, alpha=0.3)
            plt.savefig(plots_dir / "memory_usage.png")
            plt.close()
            
            # Network throughput
            plt.figure(figsize=(10, 6))
            # Calculate bytes per second
            bytes_recv = [m["network_bytes_recv"] for m in self.system_metrics]
            bytes_recv_per_sec = [
                bytes_recv[i] - bytes_recv[i-1] if i > 0 else 0
                for i in range(len(bytes_recv))
            ]
            bytes_recv_per_sec[0] = bytes_recv_per_sec[1] if len(bytes_recv_per_sec) > 1 else 0
            
            plt.plot(timestamps, bytes_recv_per_sec, 'm-', linewidth=2)
            plt.title('Network Throughput During Test')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Bytes Received per Second')
            plt.grid(True, alpha=0.3)
            plt.savefig(plots_dir / "network_throughput.png")
            plt.close()
    
    def _print_summary(self) -> None:
        """Print a summary of the test results to the console."""
        self.console.print("\n[bold green]Load Test Complete[/bold green]\n")
        
        table = Table(title=f"Load Test Results: {self.config.name}")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Test Duration", f"{self.results.duration:.2f} seconds")
        table.add_row("Concurrent Users", str(self.config.concurrent_users))
        table.add_row("Total Requests", str(self.results.total_requests))
        table.add_row("Successful Requests", str(self.results.successful_requests))
        table.add_row("Failed Requests", str(self.results.failed_requests))
        table.add_row("Success Rate", f"{self.results.success_rate:.2f}%")
        table.add_row("Requests Per Second", f"{self.results.requests_per_second:.2f}")
        
        table.add_row("Response Time (Average)", f"{self.results.average_response_time:.2f} ms")
        table.add_row("Response Time (Median)", f"{self.results.median_response_time:.2f} ms")
        table.add_row("Response Time (Min)", f"{self.results.min_response_time:.2f} ms")
        table.add_row("Response Time (Max)", f"{self.results.max_response_time:.2f} ms")
        table.add_row("Response Time (90th Percentile)", f"{self.results.p90_response_time:.2f} ms")
        table.add_row("Response Time (95th Percentile)", f"{self.results.p95_response_time:.2f} ms")
        table.add_row("Response Time (99th Percentile)", f"{self.results.p99_response_time:.2f} ms")
        
        table.add_row(
            "Throughput", 
            f"{self.results.throughput_bytes_per_second / 1024:.2f} KB/s"
        )
        table.add_row("Results Directory", str(self.test_dir))
        
        self.console.print(table)
    
    async def _send_request_async(self, user_id: int, request_id: str) -> RequestStats:
        """Send a single HTTP request asynchronously."""
        req_config = self.config.request_config
        url = req_config.url
        method = req_config.method.value
        
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            **req_config.headers
        }
        
        start_time = time.time()
        success = False
        status_code = 0
        response_time_ms = 0
        response_size = 0
        error_msg = None
        
        try:
            timeout = aiohttp.ClientTimeout(total=req_config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                request_method = getattr(session, method.lower())
                
                async with request_method(
                    url,
                    headers=headers,
                    params=req_config.params,
                    json=req_config.json_data,
                    data=req_config.data,
                    ssl=req_config.verify_ssl,
                    auth=req_config.auth
                ) as response:
                    # Read the response body
                    body = await response.read()
                    response_size = len(body)
                    
                    # Calculate response time
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    
                    status_code = response.status
                    success = 200 <= status_code < 400
                    
                    # Optionally save response
                    if self.config.save_responses:
                        response_dir = self.test_dir / "responses"
                        response_dir.mkdir(exist_ok=True)
                        
                        with open(response_dir / f"{request_id}.txt", "wb") as f:
                            f.write(f"Status: {status_code}\n\n".encode())
                            f.write(body)
        
        except asyncio.TimeoutError:
            error_msg = "Request timed out"
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
        
        except Exception as e:
            error_msg = str(e)
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
        
        return RequestStats(
            request_id=request_id,
            url=url,
            method=method,
            status_code=status_code,
            response_time=response_time_ms,
            response_size=response_size,
            timestamp=start_time,
            success=success,
            error=error_msg
        )
    
    def _send_request(self, user_id: int, request_id: str) -> RequestStats:
        """Send a single HTTP request."""
        req_config = self.config.request_config
        url = req_config.url
        method = req_config.method.value
        
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            **req_config.headers
        }
        
        start_time = time.time()
        success = False
        status_code = 0
        response_time_ms = 0
        response_size = 0
        error_msg = None
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=req_config.params,
                json=req_config.json_data,
                data=req_config.data,
                timeout=req_config.timeout,
                verify=req_config.verify_ssl,
                auth=req_config.auth
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            status_code = response.status_code
            response_size = len(response.content)
            success = 200 <= status_code < 400
            
            # Optionally save response
            if self.config.save_responses:
                response_dir = self.test_dir / "responses"
                response_dir.mkdir(exist_ok=True)
                
                with open(response_dir / f"{request_id}.txt", "wb") as f:
                    f.write(f"Status: {status_code}\n\n".encode())
                    f.write(response.content)
        
        except requests.Timeout:
            error_msg = "Request timed out"
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
        
        except Exception as e:
            error_msg = str(e)
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
        
        return RequestStats(
            request_id=request_id,
            url=url,
            method=method,
            status_code=status_code,
            response_time=response_time_ms,
            response_size=response_size,
            timestamp=start_time,
            success=success,
            error=error_msg
        )
    
    async def _user_async(self, user_id: int, progress: Optional[Progress] = None,
                         task_id: Optional[int] = None) -> None:
        """Simulate a single user's behavior asynchronously."""
        # Calculate delay for ramp-up
        if self.config.ramp_up_time > 0:
            delay = (user_id / self.config.concurrent_users) * self.config.ramp_up_time
            await asyncio.sleep(delay)
        
        request_count = 0
        end_time = self.results.start_time + self.config.test_duration
        
        while time.time() < end_time and not self.stop_event.is_set():
            # Check if we've reached the request limit
            if (self.config.requests_per_user is not None and 
                request_count >= self.config.requests_per_user):
                break
            
            # Generate unique request ID
            request_id = f"user_{user_id}_req_{request_count}_{int(time.time())}"
            
            # Send request
            request_stats = await self._send_request_async(user_id, request_id)
            
            # Process results
            self.results.request_stats.append(request_stats)
            self.results.total_requests += 1
            
            if request_stats.success:
                self.results.successful_requests += 1
                self.results.total_bytes_received += request_stats.response_size
            else:
                self.results.failed_requests += 1
                
                # Retry failed requests if configured
                retries = 0
                while (not request_stats.success and 
                       retries < self.config.max_retries and 
                       time.time() < end_time and 
                       not self.stop_event.is_set()):
                    await asyncio.sleep(self.config.retry_delay)
                    
                    if self.config.verbose:
                        logger.info(
                            f"Retrying failed request: {request_id}, "
                            f"attempt {retries+1}/{self.config.max_retries}"
                        )
                    
                    request_stats = await self._send_request_async(
                        user_id, f"{request_id}_retry_{retries}"
                    )
                    
                    # Process retry results
                    self.results.request_stats.append(request_stats)
                    self.results.total_requests += 1
                    
                    if request_stats.success:
                        self.results.successful_requests += 1
                        self.results.total_bytes_received += request_stats.response_size
                    else:
                        self.results.failed_requests += 1
                    
                    retries += 1
            
            # Update progress
            if progress and task_id is not None:
                progress.update(task_id, advance=1)
            
            request_count += 1
            
            # Simulate think time
            if self.config.think_time_max > 0:
                think_time = random.uniform(
                    self.config.think_time_min, self.config.think_time_max
                )
                await asyncio.sleep(think_time)
    
    def _user(self, user_id: int) -> None:
        """Simulate a single user's behavior."""
        # Calculate delay for ramp-up
        if self.config.ramp_up_time > 0:
            delay = (user_id / self.config.concurrent_users) * self.config.ramp_up_time
            time.sleep(delay)
        
        request_count = 0
        end_time = self.results.start_time + self.config.test_duration
        
        while time.time() < end_time:
            # Check if we've reached the request limit
            if (self.config.requests_per_user is not None and 
                request_count >= self.config.requests_per_user):
                break
            
            # Generate unique request ID
            request_id = f"user_{user_id}_req_{request_count}_{int(time.time())}"
            
            # Send request
            request_stats = self._send_request(user_id, request_id)
            
            # Process results (thread-safe operation)
            with self._results_lock:
                self.results.request_stats.append(request_stats)
                self.results.total_requests += 1
                
                if request_stats.success:
                    self.results.successful_requests += 1
                    self.results.total_bytes_received += request_stats.response_size
                else:
                    self.results.failed_requests += 1
                    
                    # Retry failed requests if configured
                    retries = 0
                    while (not request_stats.success and 
                          retries < self.config.max_retries and 
                          time.time() < end_time):
                        time.sleep(self.config.retry_delay)
                        
                        if self.config.verbose:
                            logger.info(
                                f"Retrying failed request: {request_id}, "
                                f"attempt {retries+1}/{self.config.max_retries}"
                            )
                        
                        request_stats = self._send_request(
                            user_id, f"{request_id}_retry_{retries}"
                        )
                        
                        # Process retry results
                        self.results.request_stats.append(request_stats)
                        self.results.total_requests += 1
                        
                        if request_stats.success:
                            self.results.successful_requests += 1
                            self.results.total_bytes_received += request_stats.response_size
                        else:
                            self.results.failed_requests += 1
                        
                        retries += 1
            
            request_count += 1
            
            # Simulate think time
            if self.config.think_time_max > 0:
                think_time = random.uniform(
                    self.config.think_time_min, self.config.think_time_max
                )
                time.sleep(think_time)
    
    async def _run_async(self) -> None:
        """Run the load test using asyncio."""
        self.console.print(
            f"[bold]Starting load test: {self.config.name}[/bold]"
        )
        self.console.print(
            f"Target URL: {self.config.request_config.url}\n"
            f"Concurrent Users: {self.config.concurrent_users}\n"
            f"Test Duration: {self.config.test_duration} seconds"
        )
        
        self.results.start_time = time.time()
        self.results.end_time = self.results.start_time + self.config.test_duration
        self.stop_event = asyncio.Event()
        
        # Start system metrics collection in a separate thread
        import threading
        metrics_thread = threading.Thread(target=self._collect_system_metrics)
        metrics_thread.daemon = True
        metrics_thread.start()
        
        # Setup progress tracking
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TextColumn("[bold green]{task.completed} of {task.total}"),
            TextColumn("[bold yellow]{task.speed} req/s"),
        )
        
        with Live(progress, refresh_per_second=4):
            # Add tasks to progress
            task_id = progress.add_task(
                "Executing requests...",
                total=self.config.concurrent_users * (
                    self.config.requests_per_user or float('inf')
                )
            )
            
            # Create and run user tasks
            user_tasks = []
            for user_id in range(self.config.concurrent_users):
                user_task = asyncio.create_task(
                    self._user_async(user_id, progress, task_id)
                )
                user_tasks.append(user_task)
            
            # Wait for test duration or user tasks to complete
            try:
                await asyncio.sleep(self.config.test_duration)
                # Signal tasks to stop
                self.stop_event.set()
                # Wait for all tasks to complete with a timeout
                await asyncio.gather(*user_tasks, return_exceptions=True)
            except asyncio.CancelledError:
                # Handle external cancellation
                self.stop_event.set()
                for task in user_tasks:
                    task.cancel()
            finally:
                # Ensure end time is set
                self.results.end_time = time.time()
        
        # Wait for metrics thread to finish
        metrics_thread.join(timeout=2.0)
        
        self._save_metrics()
        self._generate_report()
        self._print_summary()
        
        self.console.print(
            f"[bold green]Test completed. Results saved to: {self.test_dir}[/bold green]"
        )
    
    def _run_threaded(self) -> None:
        """Run the load test using threads."""
        self.console.print(
            f"[bold]Starting load test: {self.config.name}[/bold]"
        )
        self.console.print(
            f"Target URL: {self.config.request_config.url}\n"
            f"Concurrent Users: {self.config.concurrent_users}\n"
            f"Test Duration: {self.config.test_duration} seconds"
        )
        
        self.results.start_time = time.time()
        self.results.end_time = self.results.start_time + self.config.test_duration
        self._results_lock = threading.Lock()
        
        # Start system metrics collection in a separate thread
        metrics_thread = threading.Thread(target=self._collect_system_metrics)
        metrics_thread.daemon = True
        metrics_thread.start()
        
        # Create user threads
        user_threads = []
        with ThreadPoolExecutor(max_workers=self.config.concurrent_users) as executor:
            for user_id in range(self.config.concurrent_users):
                future = executor.submit(self._user, user_id)
                user_threads.append(future)
            
            # Use a rich progress display
            with Progress() as progress:
                task = progress.add_task(
                    "[cyan]Running load test...", 
                    total=self.config.test_duration
                )
                
                # Wait for test duration
                elapsed = 0
                while elapsed < self.config.test_duration:
                    time.sleep(1)
                    elapsed += 1
                    progress.update(task, completed=elapsed)
        
        # Ensure end time is set
        self.results.end_time = time.time()
        
        # Wait for metrics thread to finish
        metrics_thread.join(timeout=2.0)
        
        self._save_metrics()
        self._generate_report()
        self._print_summary()
        
        self.console.print(
            f"[bold green]Test completed. Results saved to: {self.test_dir}[/bold green]"
        )
    
    def run(self) -> TestResult:
        """Run the load test and return the results."""
        if self.config.use_async:
            # Use asyncio.run to handle the event loop
            asyncio.run(self._run_async())
        else:
            self._run_threaded()
        
        return self.results


def main():
    """Command-line interface for the load tester."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Load Testing Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "url", 
        help="Target URL to test"
    )
    parser.add_argument(
        "-n", "--name",
        default="load_test",
        help="Name of the test run"
    )
    parser.add_argument(
        "-c", "--concurrent-users",
        type=int,
        default=10,
        help="Number of concurrent users"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=60,
        help="Test duration in seconds"
    )
    parser.add_argument(
        "-r", "--ramp-up",
        type=int,
        default=0,
        help="Ramp-up time in seconds"
    )
    parser.add_argument(
        "-m", "--method",
        choices=[m.value for m in HttpMethod],
        default="GET",
        help="HTTP method to use"
    )
    parser.add_argument(
        "--requests-per-user",
        type=int,
        help="Maximum number of requests per user (unlimited if not specified)"
    )
    parser.add_argument(
        "--think-time-min",
        type=float,
        default=0.0,
        help="Minimum think time between requests in seconds"
    )
    parser.add_argument(
        "--think-time-max",
        type=float,
        default=0.0,
        help="Maximum think time between requests in seconds"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--headers",
        action="append",
        help="Request headers in format 'Key: Value'"
    )
    parser.add_argument(
        "--data",
        help="Request body data as a JSON string"
    )
    parser.add_argument(
        "--params",
        action="append",
        help="URL parameters in format 'key=value'"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory to save test results"
    )
    parser.add_argument(
        "--save-responses",
        action="store_true",
        help="Save all HTTP responses"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="Maximum number of retries for failed requests"
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        help="Delay between retries in seconds"
    )
    parser.add_argument(
        "--threaded",
        action="store_true",
        help="Use threading instead of asyncio"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Process headers
    headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()
    
    # Process URL parameters
    params = {}
    if args.params:
        for param in args.params:
            key, value = param.split("=", 1)
            params[key.strip()] = value.strip()
    
    # Process request data
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print("Error: Request data must be valid JSON")
            sys.exit(1)
    
    # Create request configuration
    request_config = RequestConfig(
        url=args.url,
        method=HttpMethod(args.method),
        headers=headers,
        params=params,
        json_data=data,
        timeout=args.timeout,
        verify_ssl=not args.no_verify_ssl
    )
    
    # Create load test configuration
    test_config = LoadTestConfig(
        name=args.name,
        request_config=request_config,
        concurrent_users=args.concurrent_users,
        ramp_up_time=args.ramp_up,
        test_duration=args.duration,
        requests_per_user=args.requests_per_user,
        think_time_min=args.think_time_min,
        think_time_max=args.think_time_max,
        request_timeout=args.timeout,
        use_async=not args.threaded,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        output_dir=args.output_dir,
        save_responses=args.save_responses,
        verbose=args.verbose
    )
    
    # Run the load test
    load_tester = LoadTester(test_config)
    results = load_tester.run()


if __name__ == "__main__":
    main()