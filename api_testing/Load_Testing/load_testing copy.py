"""
Topic: Load Testing in Python
Description: This script provides a comprehensive guide to performing load testing in Python. 
It covers the concept of load testing, tools, methodologies, implementation, monitoring, 
result analysis, best practices, and exception handling. The code adheres to PEP-8 standards 
and is structured for clarity and maintainability.

Load Testing: A type of performance testing to evaluate system behavior under expected or peak load conditions.
"""

import asyncio
import time
import threading
import logging
import concurrent.futures
from typing import List, Dict, Any
from dataclasses import dataclass
import requests
from urllib.parse import urljoin
import statistics
import sys
from http.client import HTTPException
import json
from queue import Queue

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Constants for configuration
BASE_URL = "http://example.com"  # Replace with your target URL
ENDPOINTS = ["/api/endpoint1", "/api/endpoint2"]  # List of endpoints to test
NUM_USERS = 100  # Number of concurrent users
REQUESTS_PER_USER = 10  # Number of requests per user
TIMEOUT = 5  # Request timeout in seconds

@dataclass
class TestResult:
    """Class to store results of individual requests."""
    endpoint: str
    status_code: int
    response_time: float
    error: str = None

class LoadTester:
    """
    LoadTester: A class to perform load testing on a web application.
    It simulates multiple users, tracks performance metrics, and handles exceptions.
    """
    
    def __init__(self, base_url: str, endpoints: List[str], num_users: int, 
                 requests_per_user: int, timeout: int):
        self.base_url = base_url
        self.endpoints = endpoints
        self.num_users = num_users
        self.requests_per_user = requests_per_user
        self.timeout = timeout
        self.results: List[TestResult] = []
        self.result_queue = Queue()

    def make_request(self, endpoint: str) -> TestResult:
        """
        Simulate a single HTTP request to the given endpoint and record the result.
        
        Args:
            endpoint (str): The endpoint to test.
        
        Returns:
            TestResult: The result of the request.
        """
        url = urljoin(self.base_url, endpoint)
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time
            )
            logging.info(f"Request to {url} completed with status {response.status_code}")
            return result
        except requests.exceptions.Timeout:
            logging.error(f"Timeout error for {url}")
            return TestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=self.timeout,
                error="Timeout"
            )
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error for {url}")
            return TestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=0,
                error="ConnectionError"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {str(e)}")
            return TestResult(
                endpoint=endpoint,
                status_code=0,
                response_time=0,
                error=str(e)
            )

    def simulate_user(self, user_id: int):
        """
        Simulate the behavior of a single user making multiple requests.
        
        Args:
            user_id (int): The ID of the user for logging purposes.
        """
        for _ in range(self.requests_per_user):
            for endpoint in self.endpoints:
                result = self.make_request(endpoint)
                self.result_queue.put(result)

    def run_sync_test(self):
        """
        Run a synchronous load test using threading to simulate concurrent users.
        """
        logging.info(f"Starting synchronous load test with {self.num_users} users...")
        start_time = time.time()
        
        threads = []
        for user_id in range(self.num_users):
            thread = threading.Thread(target=self.simulate_user, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Collect results from the queue
        while not self.result_queue.empty():
            self.results.append(self.result_queue.get())
        
        total_time = time.time() - start_time
        logging.info(f"Synchronous load test completed in {total_time:.2f} seconds.")

    async def async_make_request(self, session: requests.Session, endpoint: str) -> TestResult:
        """
        Asynchronous version of make_request for improved performance.
        
        Args:
            session (requests.Session): The session for making requests.
            endpoint (str): The endpoint to test.
        
        Returns:
            TestResult: The result of the request.
        """
        return self.make_request(endpoint)

    async def simulate_async_user(self, user_id: int):
        """
        Asynchronous version of simulate_user to handle concurrency more efficiently.
        
        Args:
            user_id (int): The ID of the user for logging purposes.
        """
        async with requests.Session() as session:
            tasks = []
            for _ in range(self.requests_per_user):
                for endpoint in self.endpoints:
                    task = asyncio.create_task(self.async_make_request(session, endpoint))
                    tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if not isinstance(result, Exception):
                    self.result_queue.put(result)

    async def run_async_test(self):
        """
        Run an asynchronous load test using asyncio for high concurrency.
        """
        logging.info(f"Starting asynchronous load test with {self.num_users} users...")
        start_time = time.time()
        
        tasks = []
        for user_id in range(self.num_users):
            task = asyncio.create_task(self.simulate_async_user(user_id))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Collect results from the queue
        while not self.result_queue.empty():
            self.results.append(self.result_queue.get())
        
        total_time = time.time() - start_time
        logging.info(f"Asynchronous load test completed in {total_time:.2f} seconds.")

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the results of the load test and generate performance metrics.
        
        Returns:
            Dict[str, Any]: A dictionary containing detailed metrics.
        """
        if not self.results:
            logging.warning("No results to analyze.")
            return {}

        metrics: Dict[str, Any] = {}
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.status_code == 200)
        failed_requests = total_requests - successful_requests
        
        response_times = [r.response_time for r in self.results if r.status_code == 200]
        error_summary = {}
        for r in self.results:
            if r.error:
                error_summary[r.error] = error_summary.get(r.error, 0) + 1

        metrics["total_requests"] = total_requests
        metrics["successful_requests"] = successful_requests
        metrics["failed_requests"] = failed_requests
        metrics["success_rate"] = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        metrics["error_summary"] = error_summary
        
        if response_times:
            metrics["avg_response_time"] = statistics.mean(response_times)
            metrics["min_response_time"] = min(response_times)
            metrics["max_response_time"] = max(response_times)
            metrics["median_response_time"] = statistics.median(response_times)
            metrics["stddev_response_time"] = statistics.stdev(response_times) if len(response_times) > 1 else 0
        else:
            metrics.update({
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "median_response_time": 0,
                "stddev_response_time": 0
            })

        logging.info("Load test analysis completed.")
        return metrics

    def save_results(self, filename: str = "load_test_results.json"):
        """
        Save the load test results and metrics to a JSON file.
        
        Args:
            filename (str): The name of the file to save results to.
        """
        metrics = self.analyze_results()
        results_data = {
            "metrics": metrics,
            "results": [r.__dict__ for r in self.results]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=4)
            logging.info(f"Results saved to {filename}")
        except IOError as e:
            logging.error(f"Failed to save results to {filename}: {str(e)}")

def main():
    """
    Main function to execute the load test.
    """
    tester = LoadTester(BASE_URL, ENDPOINTS, NUM_USERS, REQUESTS_PER_USER, TIMEOUT)
    
    # Run synchronous test
    tester.run_sync_test()
    tester.save_results("sync_load_test_results.json")
    
    # Reset results for async test
    tester.results = []
    tester.result_queue = Queue()
    
    # Run asynchronous test
    asyncio.run(tester.run_async_test())
    tester.save_results("async_load_test_results.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Load test interrupted by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

"""
Detailed Explanation of Load Testing and Implementation:

### What is Load Testing?
Load testing is a type of performance testing that evaluates how a system behaves under expected or peak load conditions. 
It helps determine:
- System capacity (how many users/requests it can handle)
- Response times under load
- Bottlenecks or points of failure
- Scalability and reliability

### Key Components of Load Testing:
1. **Workload Simulation**: Mimic real-world usage by simulating multiple users or requests.
2. **Concurrency**: Test how the system handles simultaneous requests (using threads or asyncio).
3. **Metrics Collection**: Measure response times, error rates, throughput, etc.
4. **Result Analysis**: Analyze metrics to identify performance issues.
5. **Monitoring**: Track system resources (CPU, memory, etc.) during the test.
6. **Reporting**: Generate detailed reports for stakeholders.

### Tools for Load Testing:
- **Locust**: A popular Python-based load testing tool for defining user behavior.
- **JMeter**: A GUI-based tool for load and performance testing.
- **Gatling**: A Scala-based tool for high-performance testing.
- **Custom Scripts (like this one)**: For tailored and lightweight testing.

### Implementation in This Script:
1. **Configuration**:
   - Constants like `BASE_URL`, `ENDPOINTS`, `NUM_USERS`, etc., allow easy customization.
   - Logging is configured to capture detailed information for debugging and monitoring.

2. **TestResult Class**:
   - A dataclass to store request results, including endpoint, status code, response time, and errors.

3. **LoadTester Class**:
   - **Initialization**: Sets up the test environment with user-defined parameters.
   - **make_request**: Handles individual HTTP requests with comprehensive exception handling (timeout, connection errors, etc.).
   - **simulate_user**: Simulates a single user's behavior by making multiple requests.
   - **run_sync_test**: Uses threading for synchronous concurrency.
   - **run_async_test**: Uses asyncio for asynchronous concurrency, offering better performance for high concurrency.
   - **analyze_results**: Calculates detailed metrics like success rate, response time statistics, and error summaries.
   - **save_results**: Saves results to a JSON file for later analysis.

4. **Exception Handling**:
   - Handles various exceptions like `Timeout`, `ConnectionError`, `RequestException`, etc.
   - Uses logging to track errors and successes.
   - Includes a global try-except in `main()` to handle unexpected interruptions (e.g., KeyboardInterrupt).

5. **Concurrency Models**:
   - **Synchronous (Threading)**: Suitable for moderate concurrency. Each user is simulated in a separate thread.
   - **Asynchronous (asyncio)**: More efficient for high concurrency, as it avoids the overhead of threads.

6. **Result Analysis**:
   - Metrics include total requests, success/failure rates, response time statistics (mean, median, etc.), and error summaries.
   - Results are saved to JSON for further analysis or visualization.

### Best Practices for Load Testing:
1. **Define Clear Objectives**: Understand what you want to test (e.g., max users, response time thresholds).
2. **Start Small**: Begin with a small load and gradually increase to identify breaking points.
3. **Use Realistic Scenarios**: Simulate real-world user behavior, including think time, random delays, etc.
4. **Monitor Resources**: Track server CPU, memory, and network usage during the test.
5. **Test in Isolation**: Avoid running tests on production systems without proper isolation.
6. **Analyze Bottlenecks**: Use profiling tools to identify slow components (e.g., database queries, API calls).
7. **Repeat Tests**: Run tests multiple times to ensure consistent results.
8. **Document Results**: Maintain detailed logs and reports for future reference.

### Limitations of This Script:
1. **HTTP Only**: Currently supports only GET requests. Extend it for POST, PUT, etc., as needed.
2. **Basic Metrics**: Does not include advanced metrics like throughput or latency percentiles (e.g., 95th percentile).
3. **No Resource Monitoring**: Does not track server-side metrics (CPU, memory). Use external tools like Prometheus or New Relic for this.
4. **Single Machine**: Runs on a single machine, which may limit the load generation capacity. For large-scale testing, consider distributed testing.

### How to Extend This Script:
1. **Add POST/PUT Requests**: Modify `make_request` to support different HTTP methods and payloads.
2. **Implement Think Time**: Add random delays between requests to simulate realistic user behavior.
3. **Distributed Testing**: Use tools like Locust or a custom setup with multiple machines.
4. **Advanced Metrics**: Include metrics like percentile response times or throughput.
5. **Visualization**: Integrate with libraries like Matplotlib or Plotly to visualize results.
6. **Authentication**: Add support for authenticated requests (e.g., OAuth, API tokens).

### Exception Handling in Load Testing:
- **Timeouts**: Handle with a reasonable timeout value to avoid hanging requests.
- **Connection Errors**: Retry mechanisms can be added for transient failures.
- **Rate Limits**: Detect and handle HTTP 429 (Too Many Requests) errors.
- **Server Errors**: Log and analyze HTTP 5xx errors to identify server-side issues.
- **Client Errors**: Handle HTTP 4xx errors to debug client-side issues (e.g., malformed requests).

### Running the Script:
1. Replace `BASE_URL` and `ENDPOINTS` with your target application's details.
2. Adjust `NUM_USERS`, `REQUESTS_PER_USER`, and `TIMEOUT` based on your testing needs.
3. Run the script: `python load_test.py`
4. Analyze the results in `sync_load_test_results.json` and `async_load_test_results.json`.

### Conclusion:
This script provides a solid foundation for load testing in Python, covering synchronous and asynchronous approaches, detailed metrics, and robust exception handling. It can be extended based on specific requirements, making it a versatile tool for performance testing.
"""