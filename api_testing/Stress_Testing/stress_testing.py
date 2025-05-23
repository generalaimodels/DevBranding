#!/usr/bin/env python3
"""
Comprehensive Stress Testing Framework in Python
Author: Claude
Purpose: Provide end-to-end stress testing capabilities for algorithms and systems
PEP-8 compliant code with detailed implementation
"""
import traceback
import random
import time
import sys
import os
import threading
import multiprocessing
import concurrent.futures
import tracemalloc
import statistics
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Callable, List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from contextlib import contextmanager
from collections import deque


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stress_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StressTester")


class TestType(Enum):
    """Enumeration of different stress test types."""
    CORRECTNESS = auto()
    PERFORMANCE = auto()
    MEMORY = auto()
    CONCURRENCY = auto()
    EDGE_CASE = auto()
    COMPARISON = auto()


class InputGenerator:
    """Generate various types of test inputs for stress testing."""
    
    @staticmethod
    def random_array(size: int, min_val: int = -10**9, max_val: int = 10**9) -> List[int]:
        """Generate a random array of integers."""
        return [random.randint(min_val, max_val) for _ in range(size)]
    
    @staticmethod
    def sorted_array(size: int, min_val: int = 0, max_val: int = 10**9) -> List[int]:
        """Generate a sorted array of integers."""
        return sorted(InputGenerator.random_array(size, min_val, max_val))
    
    @staticmethod
    def reverse_sorted_array(size: int, min_val: int = 0, max_val: int = 10**9) -> List[int]:
        """Generate a reverse sorted array of integers."""
        return sorted(InputGenerator.random_array(size, min_val, max_val), reverse=True)
    
    @staticmethod
    def random_string(length: int, charset: str = "abcdefghijklmnopqrstuvwxyz") -> str:
        """Generate a random string with specified character set."""
        return ''.join(random.choice(charset) for _ in range(length))
    
    @staticmethod
    def random_graph(nodes: int, edges: int, weighted: bool = False, 
                    min_weight: int = 1, max_weight: int = 100) -> List[Tuple]:
        """Generate a random graph as a list of edges."""
        if edges > nodes * (nodes - 1) // 2:
            raise ValueError("Too many edges for given number of nodes")
        
        edge_set = set()
        result = []
        
        while len(edge_set) < edges:
            u = random.randint(0, nodes - 1)
            v = random.randint(0, nodes - 1)
            if u != v and (u, v) not in edge_set and (v, u) not in edge_set:
                edge_set.add((u, v))
                if weighted:
                    weight = random.randint(min_weight, max_weight)
                    result.append((u, v, weight))
                else:
                    result.append((u, v))
        
        return result
    
    @staticmethod
    def edge_cases() -> Dict[str, Any]:
        """Generate common edge cases for testing."""
        return {
            "empty_array": [],
            "single_element": [42],
            "duplicate_elements": [1, 1, 2, 2, 3, 3],
            "extreme_values": [sys.maxsize, -sys.maxsize - 1],
            "zero_values": [0, 0, 0],
            "alternating": [1, -1, 1, -1, 1, -1],
            "empty_string": "",
            "single_char": "a",
            "large_number": 10**18,
            "negative_zero": -0.0,
        }


@contextmanager
def time_measurement():
    """Context manager to measure execution time."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        elapsed = end_time - start_time
        logger.debug(f"Execution time: {elapsed:.6f} seconds")


@contextmanager
def memory_measurement():
    """Context manager to measure memory usage."""
    tracemalloc.start()
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        logger.debug(f"Current memory usage: {current / 10**6:.6f} MB")
        logger.debug(f"Peak memory usage: {peak / 10**6:.6f} MB")
        tracemalloc.stop()


@dataclass
class TestCase:
    """Data class to represent a test case."""
    input_data: Any
    expected_output: Any = None
    description: str = ""
    
    def __str__(self) -> str:
        """String representation of the test case."""
        input_str = str(self.input_data)
        if len(input_str) > 100:
            input_str = input_str[:97] + "..."
        
        expected_str = str(self.expected_output) if self.expected_output is not None else "None"
        if len(expected_str) > 100:
            expected_str = expected_str[:97] + "..."
            
        return f"TestCase({self.description}): Input={input_str}, Expected={expected_str}"


@dataclass
class TestResult:
    """Data class to store test result information."""
    success: bool
    execution_time: float
    memory_usage: float
    input_data: Any
    actual_output: Any
    expected_output: Any = None
    error: Exception = None
    description: str = ""
    
    def __str__(self) -> str:
        """String representation of the test result."""
        status = "PASSED" if self.success else "FAILED"
        return (f"TestResult({status}): {self.description}\n"
                f"  Time: {self.execution_time:.6f}s, Memory: {self.memory_usage:.6f}MB\n" 
                f"  {'Error: ' + str(self.error) if self.error else ''}")


class StressTester:
    """Main class for stress testing algorithms and systems."""
    
    def __init__(self, name: str = "StressTest"):
        """Initialize a new stress tester instance."""
        self.name = name
        self.results = []
        self.logger = logging.getLogger(f"StressTester.{name}")
    
    def correctness_test(self, func: Callable, test_cases: List[TestCase], 
                         timeout: float = None) -> List[TestResult]:
        """
        Test the correctness of a function with given test cases.
        
        Args:
            func: The function to test
            test_cases: List of test cases to run
            timeout: Maximum execution time allowed per test
            
        Returns:
            List of test results
        """
        results = []
        
        for i, test_case in enumerate(test_cases):
            self.logger.info(f"Running test case {i+1}/{len(test_cases)}: {test_case.description}")
            
            tracemalloc.start()
            start_time = time.time()
            error = None
            success = False
            actual_output = None
            
            try:
                if timeout:
                    # Using concurrent.futures for timeout support
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(func, *test_case.input_data 
                                               if isinstance(test_case.input_data, tuple) 
                                               else (test_case.input_data,))
                        actual_output = future.result(timeout=timeout)
                else:
                    actual_output = func(*test_case.input_data 
                                      if isinstance(test_case.input_data, tuple) 
                                      else (test_case.input_data,))
                
                if test_case.expected_output is not None:
                    success = actual_output == test_case.expected_output
                else:
                    success = True  # No expected output means we're just testing for errors
                    
            except concurrent.futures.TimeoutError:
                error = TimeoutError(f"Function execution exceeded timeout of {timeout} seconds")
                self.logger.error(f"Test case {i+1} timed out after {timeout} seconds")
            except Exception as e:
                error = e
                self.logger.error(f"Test case {i+1} raised exception: {e}")
                self.logger.debug(traceback.format_exc())
            
            end_time = time.time()
            execution_time = end_time - start_time
            current, peak = tracemalloc.get_traced_memory()
            memory_usage = peak / 10**6  # Convert to MB
            tracemalloc.stop()
            
            result = TestResult(
                success=success,
                execution_time=execution_time,
                memory_usage=memory_usage,
                input_data=test_case.input_data,
                actual_output=actual_output,
                expected_output=test_case.expected_output,
                error=error,
                description=test_case.description
            )
            
            self.logger.info(str(result))
            results.append(result)
        
        self.results.extend(results)
        return results
    
    def performance_test(self, func: Callable, input_generator: Callable, 
                         sizes: List[int], runs_per_size: int = 5) -> Dict[int, Dict[str, float]]:
        """
        Test the performance of a function with increasing input sizes.
        
        Args:
            func: The function to test
            input_generator: Function to generate inputs of various sizes
            sizes: List of input sizes to test
            runs_per_size: Number of runs per size for statistical significance
            
        Returns:
            Dictionary with performance metrics for each size
        """
        performance_data = {}
        
        for size in sizes:
            self.logger.info(f"Testing performance with input size {size}")
            times = []
            memory_usages = []
            
            for run in range(runs_per_size):
                self.logger.debug(f"Run {run+1}/{runs_per_size} for size {size}")
                test_input = input_generator(size)
                
                # Measure time and memory
                tracemalloc.start()
                start_time = time.time()
                
                try:
                    func(test_input)
                except Exception as e:
                    self.logger.error(f"Exception during performance test: {e}")
                    self.logger.debug(traceback.format_exc())
                    continue
                
                end_time = time.time()
                execution_time = end_time - start_time
                current, peak = tracemalloc.get_traced_memory()
                memory_usage = peak / 10**6  # Convert to MB
                tracemalloc.stop()
                
                times.append(execution_time)
                memory_usages.append(memory_usage)
            
            # Calculate statistics
            if times:
                performance_data[size] = {
                    "min_time": min(times),
                    "max_time": max(times),
                    "avg_time": statistics.mean(times),
                    "median_time": statistics.median(times),
                    "stdev_time": statistics.stdev(times) if len(times) > 1 else 0,
                    "min_memory": min(memory_usages),
                    "max_memory": max(memory_usages),
                    "avg_memory": statistics.mean(memory_usages),
                    "median_memory": statistics.median(memory_usages),
                    "stdev_memory": statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
                }
                
                self.logger.info(f"Size {size}: Avg time {performance_data[size]['avg_time']:.6f}s, "
                               f"Avg memory {performance_data[size]['avg_memory']:.6f}MB")
        
        return performance_data
    
    def plot_performance(self, performance_data: Dict[int, Dict[str, float]], 
                         title: str = "Performance Analysis", 
                         save_path: str = None) -> None:
        """
        Plot performance data from performance tests.
        
        Args:
            performance_data: Performance data from performance_test
            title: Title for the plot
            save_path: Path to save the plot, if None it will be displayed
        """
        sizes = sorted(performance_data.keys())
        avg_times = [performance_data[size]["avg_time"] for size in sizes]
        avg_memories = [performance_data[size]["avg_memory"] for size in sizes]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Time plot
        ax1.plot(sizes, avg_times, 'o-', color='blue')
        ax1.set_title("Execution Time vs Input Size")
        ax1.set_xlabel("Input Size")
        ax1.set_ylabel("Time (seconds)")
        ax1.grid(True)
        
        # Memory plot
        ax2.plot(sizes, avg_memories, 'o-', color='green')
        ax2.set_title("Memory Usage vs Input Size")
        ax2.set_xlabel("Input Size")
        ax2.set_ylabel("Memory (MB)")
        ax2.grid(True)
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Performance plot saved to {save_path}")
        else:
            plt.show()
    
    def compare_algorithms(self, funcs: List[Callable], func_names: List[str], 
                           input_generator: Callable, sizes: List[int], 
                           runs_per_size: int = 3) -> Dict[str, Dict[int, Dict[str, float]]]:
        """
        Compare multiple algorithms on the same input sizes.
        
        Args:
            funcs: List of functions to compare
            func_names: Names of the functions for display
            input_generator: Function to generate inputs
            sizes: List of input sizes to test
            runs_per_size: Number of runs per size
            
        Returns:
            Dictionary with performance data for each algorithm
        """
        if len(funcs) != len(func_names):
            raise ValueError("Number of functions must match number of function names")
        
        comparison_data = {name: {} for name in func_names}
        
        for size in sizes:
            self.logger.info(f"Comparing algorithms with input size {size}")
            
            # Generate inputs once for this size to ensure fair comparison
            inputs = [input_generator(size) for _ in range(runs_per_size)]
            
            for func, name in zip(funcs, func_names):
                self.logger.info(f"Testing {name} with size {size}")
                times = []
                memory_usages = []
                
                for run, test_input in enumerate(inputs):
                    input_copy = test_input.copy() if hasattr(test_input, 'copy') else test_input
                    
                    self.logger.debug(f"Run {run+1}/{runs_per_size} for {name} with size {size}")
                    
                    # Measure time and memory
                    tracemalloc.start()
                    start_time = time.time()
                    
                    try:
                        func(input_copy)
                    except Exception as e:
                        self.logger.error(f"Exception during comparison test for {name}: {e}")
                        self.logger.debug(traceback.format_exc())
                        continue
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    current, peak = tracemalloc.get_traced_memory()
                    memory_usage = peak / 10**6  # Convert to MB
                    tracemalloc.stop()
                    
                    times.append(execution_time)
                    memory_usages.append(memory_usage)
                
                # Calculate statistics
                if times:
                    comparison_data[name][size] = {
                        "min_time": min(times),
                        "max_time": max(times),
                        "avg_time": statistics.mean(times),
                        "median_time": statistics.median(times),
                        "stdev_time": statistics.stdev(times) if len(times) > 1 else 0,
                        "min_memory": min(memory_usages),
                        "max_memory": max(memory_usages),
                        "avg_memory": statistics.mean(memory_usages),
                        "median_memory": statistics.median(memory_usages),
                        "stdev_memory": statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
                    }
                    
                    self.logger.info(f"{name} with size {size}: "
                                    f"Avg time {comparison_data[name][size]['avg_time']:.6f}s, "
                                    f"Avg memory {comparison_data[name][size]['avg_memory']:.6f}MB")
        
        return comparison_data
    
    def plot_comparison(self, comparison_data: Dict[str, Dict[int, Dict[str, float]]],
                        title: str = "Algorithm Comparison",
                        metric: str = "avg_time",
                        save_path: str = None) -> None:
        """
        Plot comparison data from algorithm comparisons.
        
        Args:
            comparison_data: Data from compare_algorithms
            title: Title for the plot
            metric: Which metric to plot ('avg_time', 'avg_memory', etc.)
            save_path: Path to save the plot, if None it will be displayed
        """
        plt.figure(figsize=(10, 6))
        
        metric_name = metric.split('_')[1].capitalize()
        y_label = f"{metric_name} ({'seconds' if 'time' in metric else 'MB'})"
        
        for name, data in comparison_data.items():
            sizes = sorted(data.keys())
            values = [data[size][metric] for size in sizes]
            plt.plot(sizes, values, 'o-', label=name)
        
        plt.title(title)
        plt.xlabel("Input Size")
        plt.ylabel(y_label)
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Comparison plot saved to {save_path}")
        else:
            plt.show()
    
    def edge_case_test(self, func: Callable) -> List[TestResult]:
        """
        Test a function with common edge cases.
        
        Args:
            func: Function to test
            
        Returns:
            List of test results
        """
        edge_cases = InputGenerator.edge_cases()
        test_cases = []
        
        for case_name, case_input in edge_cases.items():
            test_cases.append(TestCase(
                input_data=case_input,
                description=f"Edge case: {case_name}"
            ))
        
        return self.correctness_test(func, test_cases)
    
    def concurrency_test(self, func: Callable, input_generator: Callable, 
                        size: int, num_threads: List[int]) -> Dict[int, float]:
        """
        Test how a function performs under concurrent execution.
        
        Args:
            func: Function to test
            input_generator: Function to generate inputs
            size: Size of each input
            num_threads: List of thread counts to test
            
        Returns:
            Dictionary mapping thread count to execution time
        """
        results = {}
        
        for n_threads in num_threads:
            self.logger.info(f"Testing with {n_threads} concurrent threads")
            
            # Generate inputs
            inputs = [input_generator(size) for _ in range(n_threads)]
            
            # Measure execution time with multiple threads
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures = [executor.submit(func, input_data) for input_data in inputs]
                
                # Wait for all threads to complete
                concurrent.futures.wait(futures)
                
                # Check for exceptions
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"Exception in thread: {e}")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            results[n_threads] = execution_time
            self.logger.info(f"{n_threads} threads: {execution_time:.6f} seconds")
        
        return results
    
    def multiprocess_test(self, func: Callable, input_generator: Callable, 
                         size: int, num_processes: List[int]) -> Dict[int, float]:
        """
        Test how a function performs under multiprocessing.
        
        Args:
            func: Function to test (must be picklable)
            input_generator: Function to generate inputs (must be picklable)
            size: Size of each input
            num_processes: List of process counts to test
            
        Returns:
            Dictionary mapping process count to execution time
        """
        results = {}
        
        for n_processes in num_processes:
            self.logger.info(f"Testing with {n_processes} concurrent processes")
            
            # Generate inputs
            inputs = [input_generator(size) for _ in range(n_processes)]
            
            # Measure execution time with multiple processes
            start_time = time.time()
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=n_processes) as executor:
                futures = [executor.submit(func, input_data) for input_data in inputs]
                
                # Wait for all processes to complete
                concurrent.futures.wait(futures)
                
                # Check for exceptions
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"Exception in process: {e}")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            results[n_processes] = execution_time
            self.logger.info(f"{n_processes} processes: {execution_time:.6f} seconds")
        
        return results
    
    def generate_report(self, output_file: str = "stress_test_report.txt") -> None:
        """
        Generate a report of all test results.
        
        Args:
            output_file: File to write the report to
        """
        with open(output_file, 'w') as f:
            f.write(f"Stress Test Report: {self.name}\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total tests run: {len(self.results)}\n")
            passed = sum(1 for r in self.results if r.success)
            failed = len(self.results) - passed
            f.write(f"Tests passed: {passed}\n")
            f.write(f"Tests failed: {failed}\n\n")
            
            if failed > 0:
                f.write("Failed tests:\n")
                f.write("-" * 80 + "\n")
                for i, result in enumerate(self.results):
                    if not result.success:
                        f.write(f"Test #{i+1}: {result.description}\n")
                        f.write(f"  Error: {result.error}\n")
                        f.write(f"  Input: {result.input_data}\n")
                        f.write(f"  Expected: {result.expected_output}\n")
                        f.write(f"  Actual: {result.actual_output}\n")
                        f.write(f"  Time: {result.execution_time:.6f}s\n")
                        f.write(f"  Memory: {result.memory_usage:.6f}MB\n")
                        f.write("-" * 80 + "\n")
                f.write("\n")
            
            f.write("Performance Summary:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Average execution time: {statistics.mean([r.execution_time for r in self.results]):.6f}s\n")
            f.write(f"Average memory usage: {statistics.mean([r.memory_usage for r in self.results]):.6f}MB\n")
            f.write(f"Max execution time: {max([r.execution_time for r in self.results]):.6f}s\n")
            f.write(f"Max memory usage: {max([r.memory_usage for r in self.results]):.6f}MB\n")
            
        self.logger.info(f"Report generated: {output_file}")


# Example usage: Stress testing sorting algorithms
def example_stress_test():
    """Example of how to use the stress testing framework."""
    
    # Algorithms to test
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def merge_sort(arr):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        
        return merge(left, right)
    
    def merge(left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    # Python's built-in sort
    def python_sort(arr):
        return sorted(arr)
    
    # Create test cases
    def create_test_cases():
        test_cases = []
        
        # Basic test cases
        test_cases.append(TestCase(
            input_data=[5, 2, 8, 1, 9, 3],
            expected_output=[1, 2, 3, 5, 8, 9],
            description="Basic sorting test"
        ))
        
        # Already sorted
        test_cases.append(TestCase(
            input_data=[1, 2, 3, 4, 5],
            expected_output=[1, 2, 3, 4, 5],
            description="Already sorted array"
        ))
        
        # Reverse sorted
        test_cases.append(TestCase(
            input_data=[5, 4, 3, 2, 1],
            expected_output=[1, 2, 3, 4, 5],
            description="Reverse sorted array"
        ))
        
        # Random larger arrays
        for i in range(3):
            arr = InputGenerator.random_array(100)
            test_cases.append(TestCase(
                input_data=arr.copy(),
                expected_output=sorted(arr),
                description=f"Random array test {i+1}"
            ))
        
        return test_cases
    
    # Initialize the stress tester
    tester = StressTester("Sorting Algorithm Tests")
    
    # Correctness tests
    test_cases = create_test_cases()
    tester.correctness_test(bubble_sort, test_cases)
    tester.correctness_test(merge_sort, test_cases)
    tester.correctness_test(python_sort, test_cases)
    
    # Edge case tests
    tester.edge_case_test(bubble_sort)
    tester.edge_case_test(merge_sort)
    tester.edge_case_test(python_sort)
    
    # Performance tests
    sizes = [10, 100, 1000, 5000]
    bubble_perf = tester.performance_test(bubble_sort, InputGenerator.random_array, sizes)
    merge_perf = tester.performance_test(merge_sort, InputGenerator.random_array, sizes)
    python_perf = tester.performance_test(python_sort, InputGenerator.random_array, sizes)
    
    # Compare algorithms
    comparison = tester.compare_algorithms(
        [bubble_sort, merge_sort, python_sort],
        ["Bubble Sort", "Merge Sort", "Python Sort"],
        InputGenerator.random_array,
        [10, 100, 1000]
    )
    
    # Concurrency test (only for thread-safe functions)
    thread_counts = [1, 2, 4, 8]
    thread_results = tester.concurrency_test(
        python_sort,
        InputGenerator.random_array,
        1000,
        thread_counts
    )
    
    # Generate report
    tester.generate_report()
    
    # Plot results
    tester.plot_comparison(comparison, title="Sorting Algorithm Comparison", metric="avg_time")
    
    return tester


if __name__ == "__main__":
    # Run the example stress test
    example_stress_test()