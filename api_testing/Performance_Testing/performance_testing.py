#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Testing in Python - Comprehensive Implementation

This module provides end-to-end implementations of different performance testing
techniques including benchmarking, profiling, load testing, and monitoring.
"""

import time
import timeit
import cProfile
import pstats
import io
import gc
import statistics
import os
import psutil
import multiprocessing
import threading
import concurrent.futures
import requests
import random
import logging
import json
from functools import wraps
from typing import Callable, List, Dict, Any, Union, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===== DECORATORS FOR TIMING AND BENCHMARKING =====

def timer_decorator(func):
    """Decorator that measures and logs execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.6f} seconds")
        return result
    return wrapper


def benchmark_decorator(repeat=5):
    """Decorator that benchmarks a function by running it multiple times."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            times = []
            for _ in range(repeat):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            logger.info(f"Benchmark results for {func.__name__}:")
            logger.info(f"  Avg: {avg_time:.6f}s, Min: {min_time:.6f}s, Max: {max_time:.6f}s, StdDev: {std_dev:.6f}s")
            
            return result
        return wrapper
    return decorator


# ===== MEMORY USAGE MONITORING =====

@dataclass
class MemoryStats:
    """Dataclass to store memory usage statistics."""
    peak_memory_mb: float
    initial_memory_mb: float
    final_memory_mb: float
    diff_memory_mb: float


def get_process_memory() -> float:
    """Get the current memory usage of the process in MB."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert to MB


def memory_usage_decorator(func):
    """Decorator that monitors memory usage of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Clear garbage collector to get accurate memory reading
        gc.collect()
        initial_memory = get_process_memory()
        
        # Track peak memory during execution
        peak_memory = initial_memory
        
        def memory_monitor():
            nonlocal peak_memory
            monitoring = True
            while monitoring:
                current = get_process_memory()
                peak_memory = max(peak_memory, current)
                time.sleep(0.001)  # Small sleep to reduce CPU usage
                if not monitoring:
                    break
        
        # Start memory monitoring in a separate thread
        monitor_thread = threading.Thread(target=memory_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            result = func(*args, **kwargs)
        finally:
            # Stop monitoring thread
            monitor_thread.monitoring = False
            monitor_thread.join(timeout=1.0)
            
            # Collect garbage before final measurement
            gc.collect()
            final_memory = get_process_memory()
        
        memory_stats = MemoryStats(
            peak_memory_mb=peak_memory,
            initial_memory_mb=initial_memory,
            final_memory_mb=final_memory,
            diff_memory_mb=final_memory - initial_memory
        )
        
        logger.info(f"Memory usage for {func.__name__}:")
        logger.info(f"  Initial: {memory_stats.initial_memory_mb:.2f} MB")
        logger.info(f"  Peak: {memory_stats.peak_memory_mb:.2f} MB")
        logger.info(f"  Final: {memory_stats.final_memory_mb:.2f} MB")
        logger.info(f"  Diff: {memory_stats.diff_memory_mb:.2f} MB")
        
        return result
    
    return wrapper


# ===== ADVANCED PROFILING FUNCTIONS =====

def profile_function(func, *args, **kwargs) -> pstats.Stats:
    """
    Profile a function using cProfile and return profiling statistics.
    
    Args:
        func: The function to profile
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        pstats.Stats: Profiling statistics
    """
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args, **kwargs)
    profiler.disable()
    
    # Process the stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    
    return stats


def detailed_profile(func, *args, **kwargs) -> Dict[str, Any]:
    """
    Perform detailed profiling of a function and return structured results.
    
    Args:
        func: Function to profile
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Dict containing profile results
    """
    # Clear any cached data and collect garbage
    gc.collect()
    
    # Time measurement
    start_time = time.time()
    
    # Use cProfile for detailed analysis
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    execution_time = time.time() - start_time
    
    # Extract profiling data
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 time-consuming functions
    
    # Process memory
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / (1024 * 1024)
    
    # CPU usage
    cpu_percent = process.cpu_percent(interval=0.1)
    
    # Create structured results
    profile_results = {
        "function_name": func.__name__,
        "execution_time": execution_time,
        "memory_usage_mb": memory_mb,
        "cpu_percent": cpu_percent,
        "profile_details": s.getvalue(),
        "timestamp": datetime.now().isoformat()
    }
    
    return profile_results


def save_profile_results(profile_data: Dict[str, Any], filename: str = None) -> str:
    """
    Save profile results to a file and return the filename.
    
    Args:
        profile_data: Profile data dictionary
        filename: Optional filename to save to
        
    Returns:
        Filename where results were saved
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"profile_{profile_data['function_name']}_{timestamp}.json"
    
    # Create a version of the profile data that's JSON serializable
    serializable_data = profile_data.copy()
    serializable_data['timestamp'] = str(serializable_data['timestamp'])
    
    with open(filename, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    logger.info(f"Profile results saved to {filename}")
    return filename


# ===== BENCHMARKING UTILITIES =====

def benchmark_comparison(funcs: List[Callable], args_list: List[tuple] = None, 
                          kwargs_list: List[dict] = None, iterations: int = 5) -> Dict[str, Dict]:
    """
    Compare performance of multiple functions.
    
    Args:
        funcs: List of functions to benchmark
        args_list: List of args tuples for each function (or None for empty args)
        kwargs_list: List of kwargs dicts for each function (or None for empty kwargs)
        iterations: Number of iterations for each function
        
    Returns:
        Dictionary with benchmark results
    """
    if args_list is None:
        args_list = [()] * len(funcs)
    if kwargs_list is None:
        kwargs_list = [{}] * len(funcs)
    
    results = {}
    
    for idx, (func, args, kwargs) in enumerate(zip(funcs, args_list, kwargs_list)):
        times = []
        for _ in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        results[func.__name__] = {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'all_times': times
        }
    
    return results


def timeit_benchmark(code_snippet: str, setup: str = "pass", 
                     number: int = 1000, repeat: int = 5) -> Dict[str, float]:
    """
    Benchmark a code snippet using timeit.
    
    Args:
        code_snippet: The code to benchmark
        setup: Setup code to run before benchmarking
        number: Number of times to execute the snippet per test
        repeat: Number of times to repeat the test
        
    Returns:
        Dictionary with benchmark results
    """
    times = timeit.repeat(code_snippet, setup=setup, number=number, repeat=repeat)
    
    # Calculate statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    std_dev = statistics.stdev(times) if repeat > 1 else 0
    
    results = {
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'std_dev': std_dev,
        'all_times': times,
        'per_iteration': min_time / number
    }
    
    return results


def visualize_benchmark_results(results: Dict[str, Dict], title: str = "Performance Comparison") -> None:
    """
    Visualize benchmark results using matplotlib.
    
    Args:
        results: Dictionary with benchmark results
        title: Title for the plot
    """
    function_names = list(results.keys())
    avg_times = [results[func]['avg_time'] for func in function_names]
    
    # Create figure
    plt.figure(figsize=(10, 6))
    bars = plt.bar(function_names, avg_times)
    
    # Add error bars for standard deviation
    std_devs = [results[func]['std_dev'] for func in function_names]
    plt.errorbar(function_names, avg_times, yerr=std_devs, fmt='none', ecolor='black', capsize=5)
    
    # Add labels and formatting
    plt.title(title)
    plt.xlabel('Function')
    plt.ylabel('Average Execution Time (s)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Add values on top of bars
    for bar, time_val in zip(bars, avg_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002, 
                 f'{time_val:.6f}s', ha='center', va='bottom', fontsize=8)
    
    # Save and show
    plt.savefig(f"{title.replace(' ', '_')}.png")
    plt.show()


# ===== LOAD AND STRESS TESTING =====

class LoadTester:
    """Class for performing HTTP-based load testing."""
    
    def __init__(self, base_url: str, max_workers: int = 10, timeout: int = 30):
        """
        Initialize the load tester.
        
        Args:
            base_url: Base URL to test
            max_workers: Maximum number of concurrent workers
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.max_workers = max_workers
        self.timeout = timeout
        self.results = []
        self.session = requests.Session()
    
    def single_request(self, endpoint: str = "", method: str = "GET", 
                       data: Dict = None, headers: Dict = None) -> Dict:
        """
        Make a single request and measure performance.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send with the request
            headers: Headers to include
            
        Returns:
            Dictionary with request results
        """
        url = f"{self.base_url}/{endpoint}".rstrip('/')
        headers = headers or {}
        data = data or {}
        
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": 200 <= response.status_code < 400,
                "content_size": len(response.content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "url": url,
                "method": method,
                "error": str(e),
                "response_time": response_time,
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
        
        return result
    
    def load_test(self, endpoint: str = "", num_requests: int = 100, 
                  method: str = "GET", data: Dict = None, 
                  headers: Dict = None, ramp_up: bool = False) -> Dict:
        """
        Perform load testing by sending multiple concurrent requests.
        
        Args:
            endpoint: API endpoint to call
            num_requests: Number of requests to make
            method: HTTP method to use
            data: Data to send with the request
            headers: Headers to include
            ramp_up: Whether to gradually increase load
            
        Returns:
            Dictionary with test results
        """
        self.results = []
        headers = headers or {}
        data = data or {}
        
        # Determine the number of workers based on ramp_up setting
        if ramp_up:
            # Start with 1 worker and gradually increase
            worker_groups = min(5, num_requests // 20 + 1)
            requests_per_group = num_requests // worker_groups
            remaining = num_requests
        else:
            # Use fixed number of workers
            workers = min(self.max_workers, num_requests)
        
        start_time = time.time()
        
        if ramp_up:
            # Execute with gradually increasing concurrency
            for i in range(worker_groups):
                current_workers = max(1, (i + 1) * self.max_workers // worker_groups)
                current_requests = min(remaining, requests_per_group)
                
                logger.info(f"Ramp-up phase {i+1}/{worker_groups}: {current_workers} workers, {current_requests} requests")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=current_workers) as executor:
                    future_to_url = {
                        executor.submit(self.single_request, endpoint, method, data, headers): i 
                        for i in range(current_requests)
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_url):
                        result = future.result()
                        self.results.append(result)
                
                remaining -= current_requests
                
                # Small pause between phases to see patterns clearly
                if i < worker_groups - 1:
                    time.sleep(1.0)
        else:
            # Execute all requests with fixed concurrency
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_url = {
                    executor.submit(self.single_request, endpoint, method, data, headers): i 
                    for i in range(num_requests)
                }
                
                for future in concurrent.futures.as_completed(future_to_url):
                    result = future.result()
                    self.results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_requests = sum(1 for r in self.results if r.get('success', False))
        failed_requests = num_requests - successful_requests
        
        if successful_requests > 0:
            response_times = [r['response_time'] for r in self.results if r.get('success', False)]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            if len(response_times) > 1:
                std_dev_response_time = statistics.stdev(response_times)
                percentile_90 = np.percentile(response_times, 90)
                percentile_95 = np.percentile(response_times, 95)
                percentile_99 = np.percentile(response_times, 99)
            else:
                std_dev_response_time = 0
                percentile_90 = percentile_95 = percentile_99 = response_times[0]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            std_dev_response_time = percentile_90 = percentile_95 = percentile_99 = 0
        
        # Prepare summary results
        test_results = {
            "url": f"{self.base_url}/{endpoint}".rstrip('/'),
            "method": method,
            "num_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / num_requests if num_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time if total_time > 0 else 0,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "std_dev_response_time": std_dev_response_time,
            "percentile_90": percentile_90,
            "percentile_95": percentile_95,
            "percentile_99": percentile_99,
            "timestamp": datetime.now().isoformat(),
            "detailed_results": self.results
        }
        
        return test_results
    
    def stress_test(self, endpoint: str = "", start_concurrency: int = 5, 
                    max_concurrency: int = 50, step_size: int = 5, 
                    requests_per_step: int = 100, method: str = "GET", 
                    data: Dict = None, headers: Dict = None) -> Dict:
        """
        Perform stress testing by gradually increasing load until failure.
        
        Args:
            endpoint: API endpoint to call
            start_concurrency: Initial number of concurrent users
            max_concurrency: Maximum number of concurrent users
            step_size: How much to increase concurrency in each step
            requests_per_step: Number of requests per concurrency level
            method: HTTP method to use
            data: Data to send with the request
            headers: Headers to include
            
        Returns:
            Dictionary with test results
        """
        headers = headers or {}
        data = data or {}
        
        overall_start_time = time.time()
        step_results = []
        breaking_point = None
        
        for concurrency in range(start_concurrency, max_concurrency + 1, step_size):
            logger.info(f"Stress testing with concurrency level: {concurrency}")
            
            # Save original max_workers and temporarily set it to current concurrency
            original_max_workers = self.max_workers
            self.max_workers = concurrency
            
            # Run the test for this concurrency level
            step_result = self.load_test(
                endpoint=endpoint,
                num_requests=requests_per_step,
                method=method,
                data=data,
                headers=headers
            )
            
            # Add concurrency level to results
            step_result['concurrency'] = concurrency
            step_results.append(step_result)
            
            # Restore original max_workers
            self.max_workers = original_max_workers
            
            # Check if this is the breaking point (success rate < 90% or avg response time > 1s)
            if (step_result['success_rate'] < 0.9 or 
                step_result['avg_response_time'] > 1.0 or 
                step_result['requests_per_second'] < (requests_per_step / 10)):
                
                if breaking_point is None:
                    breaking_point = concurrency
                    logger.info(f"Breaking point detected at concurrency level: {concurrency}")
                    
                    # Continue for one more step to confirm the breaking point
                    if concurrency + step_size <= max_concurrency:
                        continue
                    else:
                        break
                else:
                    # We've confirmed the breaking point with another test
                    logger.info(f"Breaking point confirmed at concurrency level: {breaking_point}")
                    break
            
            # Small pause between steps to let the system recover
            time.sleep(2.0)
        
        overall_end_time = time.time()
        total_test_time = overall_end_time - overall_start_time
        
        # Calculate overall statistics
        all_success_rates = [r['success_rate'] for r in step_results]
        all_response_times = [r['avg_response_time'] for r in step_results]
        all_requests_per_second = [r['requests_per_second'] for r in step_results]
        
        # Find the optimal concurrency (best requests/second with good success rate)
        optimal_idx = 0
        max_throughput = 0
        
        for idx, result in enumerate(step_results):
            if (result['success_rate'] >= 0.95 and 
                result['requests_per_second'] > max_throughput):
                max_throughput = result['requests_per_second']
                optimal_idx = idx
        
        optimal_concurrency = step_results[optimal_idx]['concurrency']
        
        # Prepare summary results
        stress_test_results = {
            "url": f"{self.base_url}/{endpoint}".rstrip('/'),
            "method": method,
            "start_concurrency": start_concurrency,
            "max_tested_concurrency": step_results[-1]['concurrency'],
            "breaking_point": breaking_point,
            "optimal_concurrency": optimal_concurrency,
            "optimal_requests_per_second": max_throughput,
            "total_test_time": total_test_time,
            "success_rates": all_success_rates,
            "avg_response_times": all_response_times,
            "requests_per_second": all_requests_per_second,
            "timestamp": datetime.now().isoformat(),
            "detailed_step_results": step_results
        }
        
        return stress_test_results
    
    def visualize_stress_test(self, results: Dict) -> None:
        """
        Visualize stress test results.
        
        Args:
            results: Dictionary with stress test results
        """
        concurrency_levels = [r['concurrency'] for r in results['detailed_step_results']]
        success_rates = [r['success_rate'] * 100 for r in results['detailed_step_results']]  # Convert to percentage
        response_times = [r['avg_response_time'] * 1000 for r in results['detailed_step_results']]  # Convert to ms
        throughputs = [r['requests_per_second'] for r in results['detailed_step_results']]
        
        # Create figure with multiple subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
        
        # Plot success rate
        ax1.plot(concurrency_levels, success_rates, 'o-', color='green', label='Success Rate (%)')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_title('Stress Test Results')
        ax1.grid(True)
        ax1.legend()
        
        # Plot response time
        ax2.plot(concurrency_levels, response_times, 's-', color='blue', label='Response Time (ms)')
        ax2.set_ylabel('Avg Response Time (ms)')
        ax2.grid(True)
        ax2.legend()
        
        # Plot throughput
        ax3.plot(concurrency_levels, throughputs, '^-', color='red', label='Requests/Second')
        ax3.set_xlabel('Concurrency Level')
        ax3.set_ylabel('Requests/Second')
        ax3.grid(True)
        ax3.legend()
        
        # Mark breaking point if detected
        if results.get('breaking_point'):
            breaking_point = results['breaking_point']
            for ax in [ax1, ax2, ax3]:
                ax.axvline(x=breaking_point, color='red', linestyle='--', alpha=0.7, label='Breaking Point')
        
        # Mark optimal concurrency
        if results.get('optimal_concurrency'):
            optimal = results['optimal_concurrency']
            for ax in [ax1, ax2, ax3]:
                ax.axvline(x=optimal, color='green', linestyle='--', alpha=0.7, label='Optimal Concurrency')
        
        plt.tight_layout()
        plt.savefig("stress_test_results.png")
        plt.show()


# ===== SYSTEM RESOURCE MONITORING =====

class ResourceMonitor:
    """Class for monitoring system resources during performance tests."""
    
    def __init__(self, interval: float = 0.1):
        """
        Initialize the resource monitor.
        
        Args:
            interval: Sampling interval in seconds
        """
        self.interval = interval
        self.running = False
        self.monitor_thread = None
        self.start_time = None
        self.data = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_percent': [],
            'memory_used': [],
            'disk_io_read': [],
            'disk_io_write': [],
            'network_sent': [],
            'network_recv': []
        }
    
    def _monitor_resources(self):
        """Background thread that collects resource usage data."""
        # Get initial disk and network counters
        initial_disk_io = psutil.disk_io_counters()
        initial_net_io = psutil.net_io_counters()
        last_disk_read = initial_disk_io.read_bytes if initial_disk_io else 0
        last_disk_write = initial_disk_io.write_bytes if initial_disk_io else 0
        last_net_sent = initial_net_io.bytes_sent if initial_net_io else 0
        last_net_recv = initial_net_io.bytes_recv if initial_net_io else 0
        
        while self.running:
            current_time = time.time() - self.start_time
            
            # CPU and memory
            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_read = disk_io.read_bytes
                disk_write = disk_io.write_bytes
                read_rate = (disk_read - last_disk_read) / self.interval
                write_rate = (disk_write - last_disk_write) / self.interval
                last_disk_read = disk_read
                last_disk_write = disk_write
            else:
                read_rate = write_rate = 0
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                net_sent = net_io.bytes_sent
                net_recv = net_io.bytes_recv
                sent_rate = (net_sent - last_net_sent) / self.interval
                recv_rate = (net_recv - last_net_recv) / self.interval
                last_net_sent = net_sent
                last_net_recv = net_recv
            else:
                sent_rate = recv_rate = 0
            
            # Record data
            self.data['timestamps'].append(current_time)
            self.data['cpu_percent'].append(cpu)
            self.data['memory_percent'].append(memory.percent)
            self.data['memory_used'].append(memory.used / (1024 * 1024))  # Convert to MB
            self.data['disk_io_read'].append(read_rate / (1024 * 1024))  # Convert to MB/s
            self.data['disk_io_write'].append(write_rate / (1024 * 1024))  # Convert to MB/s
            self.data['network_sent'].append(sent_rate / (1024 * 1024))  # Convert to MB/s
            self.data['network_recv'].append(recv_rate / (1024 * 1024))  # Convert to MB/s
            
            # Sleep for the specified interval
            time.sleep(self.interval)
    
    def start(self):
        """Start monitoring resources."""
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.monitor_thread = threading.Thread(target=self._monitor_resources)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Resource monitoring started")
        else:
            logger.warning("Resource monitor is already running")
    
    def stop(self):
        """Stop monitoring resources."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2 * self.interval)
            logger.info("Resource monitoring stopped")
        else:
            logger.warning("Resource monitor is not running")
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics from the collected data.
        
        Returns:
            Dictionary with resource usage statistics
        """
        stats = {}
        
        for key in ['cpu_percent', 'memory_percent', 'memory_used', 
                    'disk_io_read', 'disk_io_write', 
                    'network_sent', 'network_recv']:
            if self.data[key]:
                stats[key] = {
                    'min': min(self.data[key]),
                    'max': max(self.data[key]),
                    'avg': statistics.mean(self.data[key]),
                    'std_dev': statistics.stdev(self.data[key]) if len(self.data[key]) > 1 else 0
                }
            else:
                stats[key] = {
                    'min': 0,
                    'max': 0,
                    'avg': 0,
                    'std_dev': 0
                }
        
        return stats
    
    def visualize(self, title: str = "Resource Utilization"):
        """
        Visualize the resource monitoring data.
        
        Args:
            title: Title for the plot
        """
        if not self.data['timestamps']:
            logger.warning("No monitoring data available to visualize")
            return
        
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
        
        # CPU and Memory
        ax1.plot(self.data['timestamps'], self.data['cpu_percent'], label='CPU %', color='red')
        ax1.plot(self.data['timestamps'], self.data['memory_percent'], label='Memory %', color='blue')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_title(title)
        ax1.grid(True)
        ax1.legend()
        
        # Memory Used
        ax2.plot(self.data['timestamps'], self.data['memory_used'], label='Memory Used (MB)', color='green')
        ax2.set_ylabel('Memory (MB)')
        ax2.grid(True)
        ax2.legend()
        
        # Disk I/O
        ax3.plot(self.data['timestamps'], self.data['disk_io_read'], label='Disk Read (MB/s)', color='purple')
        ax3.plot(self.data['timestamps'], self.data['disk_io_write'], label='Disk Write (MB/s)', color='orange')
        ax3.set_ylabel('Disk I/O (MB/s)')
        ax3.grid(True)
        ax3.legend()
        
        # Network I/O
        ax4.plot(self.data['timestamps'], self.data['network_sent'], label='Network Sent (MB/s)', color='teal')
        ax4.plot(self.data['timestamps'], self.data['network_recv'], label='Network Recv (MB/s)', color='brown')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Network I/O (MB/s)')
        ax4.grid(True)
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig(f"{title.replace(' ', '_')}.png")
        plt.show()
    
    def reset(self):
        """Reset the collected data."""
        self.data = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_percent': [],
            'memory_used': [],
            'disk_io_read': [],
            'disk_io_write': [],
            'network_sent': [],
            'network_recv': []
        }
        logger.info("Resource monitoring data reset")


# ===== EXAMPLE USAGE FUNCTIONS =====

@timer_decorator
def example_cpu_bound_task(n: int = 5000000):
    """
    Example CPU-bound task for testing.
    
    Args:
        n: Size of computation
    """
    result = 0
    for i in range(n):
        result += i ** 2
    return result


@memory_usage_decorator
def example_memory_intensive_task(size_mb: int = 100):
    """
    Example memory-intensive task for testing.
    
    Args:
        size_mb: Size of memory to allocate in MB
    """
    # Allocate a large list (each element is 8 bytes in 64-bit Python)
    elements = size_mb * 1024 * 1024 // 8
    large_list = [i for i in range(elements)]
    # Do some operations to prevent optimization
    for _ in range(10):
        random_idx = random.randint(0, elements - 1)
        large_list[random_idx] = random.randint(0, 1000000)
    return sum(large_list[:1000])


@benchmark_decorator(repeat=3)
def example_io_bound_task(url: str = "https://httpbin.org/get"):
    """
    Example I/O-bound task for testing.
    
    Args:
        url: URL to request
    """
    response = requests.get(url, timeout=10)
    return response.status_code


def demonstrate_performance_testing():
    """Run examples of all performance testing techniques."""
    logger.info("Starting performance testing demonstration")
    
    # Basic timing and benchmarking
    logger.info("\n1. Basic timing and benchmarking:")
    example_cpu_bound_task(1000000)
    example_memory_intensive_task(50)
    example_io_bound_task()
    
    # Function comparison
    logger.info("\n2. Function comparison:")
    
    def fibonacci_recursive(n):
        if n <= 1:
            return n
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
    
    def fibonacci_iterative(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    
    results = benchmark_comparison(
        [fibonacci_recursive, fibonacci_iterative],
        args_list=[(20,), (20,)],
        iterations=3
    )
    visualize_benchmark_results(results, "Fibonacci Implementation Comparison")
    
    # Detailed profiling
    logger.info("\n3. Detailed profiling:")
    profile_results = detailed_profile(example_cpu_bound_task, 1000000)
    save_profile_results(profile_results)
    
    # Memory profiling
    logger.info("\n4. Memory profiling:")
    memory_results = []
    for size in [10, 20, 50]:
        logger.info(f"Testing with {size}MB")
        example_memory_intensive_task(size)
    
    # Resource monitoring
    logger.info("\n5. Resource monitoring:")
    monitor = ResourceMonitor(interval=0.2)
    monitor.start()
    
    # Perform some operations
    example_cpu_bound_task(2000000)
    example_memory_intensive_task(100)
    example_io_bound_task()
    
    # Stop monitoring and visualize
    monitor.stop()
    stats = monitor.get_statistics()
    logger.info(f"Resource statistics: {json.dumps(stats, indent=2)}")
    monitor.visualize("Demo Resource Utilization")
    
    # Load testing (only if network is available)
    logger.info("\n6. Load testing example (not actually executing):")
    logger.info("To perform load testing, you would use code like:")
    logger.info("    load_tester = LoadTester('https://api.example.com')")
    logger.info("    results = load_tester.load_test(endpoint='users', num_requests=100)")
    
    logger.info("\nPerformance testing demonstration completed")


if __name__ == "__main__":
    demonstrate_performance_testing()