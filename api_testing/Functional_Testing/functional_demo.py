#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Functional Testing Implementation in Python

This module demonstrates end-to-end functional testing for a calculator application,
covering test organization, execution, reporting, mocking, parameterization, 
fixtures, and test coverage analysis.
"""

import unittest
import pytest
import sys
import logging
import json
import os
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import coverage


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# ----- APPLICATION CODE (TARGET OF TESTING) -----

class CalculationError(Exception):
    """Custom exception for calculator errors."""
    pass


class Calculator:
    """Simple calculator class with basic arithmetic operations."""
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b."""
        if b == 0:
            raise CalculationError("Division by zero is not allowed")
        return a / b
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """Raise base to the power of exponent."""
        try:
            return base ** exponent
        except OverflowError:
            raise CalculationError("Result too large to compute")


class CalculatorAPI:
    """API interface for the Calculator."""
    
    def __init__(self, data_source: str = None):
        """Initialize with a calculator and optional data source."""
        self.calculator = Calculator()
        self.data_source = data_source
        
    def process_calculation(self, operation: str, a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
        """Process calculation request and return result with metadata."""
        result = None
        try:
            if operation == 'add':
                result = self.calculator.add(a, b)
            elif operation == 'subtract':
                result = self.calculator.subtract(a, b)
            elif operation == 'multiply':
                result = self.calculator.multiply(a, b)
            elif operation == 'divide':
                result = self.calculator.divide(a, b)
            elif operation == 'power':
                result = self.calculator.power(a, b)
            else:
                raise CalculationError(f"Unknown operation: {operation}")
                
            return {
                'status': 'success',
                'operation': operation,
                'operands': {'a': a, 'b': b},
                'result': result
            }
        except CalculationError as e:
            return {
                'status': 'error',
                'operation': operation,
                'operands': {'a': a, 'b': b},
                'message': str(e)
            }
    
    def load_calculations(self) -> List[Dict[str, Any]]:
        """Load calculations from data source."""
        if not self.data_source or not os.path.exists(self.data_source):
            return []
        
        try:
            with open(self.data_source, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load calculations: {e}")
            return []
    
    def save_calculation(self, calculation: Dict[str, Any]) -> bool:
        """Save calculation to data source."""
        if not self.data_source:
            return False
        
        calculations = self.load_calculations()
        calculations.append(calculation)
        
        try:
            with open(self.data_source, 'w') as f:
                json.dump(calculations, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Failed to save calculation: {e}")
            return False


# ----- FUNCTIONAL TESTING WITH UNITTEST -----

class CalculatorTestCase(unittest.TestCase):
    """Test case for Calculator class using unittest framework."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calculator = Calculator()
        logger.info("Setting up calculator test case")
    
    def tearDown(self):
        """Clean up after each test method."""
        logger.info("Tearing down calculator test case")
    
    def test_add(self):
        """Test addition functionality."""
        self.assertEqual(self.calculator.add(3, 5), 8)
        self.assertEqual(self.calculator.add(-1, 1), 0)
        self.assertEqual(self.calculator.add(0, 0), 0)
        
    def test_subtract(self):
        """Test subtraction functionality."""
        self.assertEqual(self.calculator.subtract(10, 5), 5)
        self.assertEqual(self.calculator.subtract(-1, -1), 0)
        self.assertEqual(self.calculator.subtract(0, 10), -10)
    
    def test_multiply(self):
        """Test multiplication functionality."""
        self.assertEqual(self.calculator.multiply(3, 4), 12)
        self.assertEqual(self.calculator.multiply(-2, 3), -6)
        self.assertEqual(self.calculator.multiply(0, 5), 0)
    
    def test_divide(self):
        """Test division functionality."""
        self.assertEqual(self.calculator.divide(10, 2), 5)
        self.assertEqual(self.calculator.divide(7, 2), 3.5)
        self.assertEqual(self.calculator.divide(0, 5), 0)
    
    def test_divide_by_zero(self):
        """Test division by zero raises appropriate exception."""
        with self.assertRaises(CalculationError):
            self.calculator.divide(5, 0)
    
    def test_power(self):
        """Test power functionality."""
        self.assertEqual(self.calculator.power(2, 3), 8)
        self.assertEqual(self.calculator.power(2, 0), 1)
        self.assertEqual(self.calculator.power(0, 5), 0)
    
    def test_power_large_numbers(self):
        """Test power with large numbers that might cause overflow."""
        with self.assertRaises(CalculationError):
            self.calculator.power(10**100, 10**100)


class CalculatorAPITestCase(unittest.TestCase):
    """Test case for CalculatorAPI class using unittest framework."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test case."""
        cls.test_data_file = "test_calculations.json"
        # Ensure the test file doesn't exist initially
        if os.path.exists(cls.test_data_file):
            os.remove(cls.test_data_file)
        logger.info("Setting up class fixtures")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class have run."""
        if os.path.exists(cls.test_data_file):
            os.remove(cls.test_data_file)
        logger.info("Tearing down class fixtures")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api = CalculatorAPI(data_source=self.test_data_file)
    
    def test_process_calculation_add(self):
        """Test processing an addition calculation."""
        result = self.api.process_calculation('add', 5, 3)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['result'], 8)
    
    def test_process_calculation_error(self):
        """Test processing a calculation with an error."""
        result = self.api.process_calculation('divide', 5, 0)
        self.assertEqual(result['status'], 'error')
        self.assertIn('Division by zero', result['message'])
    
    def test_unknown_operation(self):
        """Test processing an unknown operation."""
        result = self.api.process_calculation('invalid_op', 5, 3)
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unknown operation', result['message'])
    
    @patch('builtins.open', side_effect=IOError("Mocked IO error"))
    def test_load_calculations_io_error(self, mock_open):
        """Test loading calculations with IO error."""
        api = CalculatorAPI("nonexistent_file.json")
        result = api.load_calculations()
        self.assertEqual(result, [])
        
    def test_save_and_load_calculation(self):
        """Test saving and loading a calculation."""
        calculation = {
            'status': 'success',
            'operation': 'add',
            'operands': {'a': 5, 'b': 3},
            'result': 8
        }
        
        # Save the calculation
        success = self.api.save_calculation(calculation)
        self.assertTrue(success)
        
        # Load calculations and check
        calculations = self.api.load_calculations()
        self.assertEqual(len(calculations), 1)
        self.assertEqual(calculations[0]['result'], 8)
    
    @patch('json.dump', side_effect=IOError("Mocked IO error during save"))
    def test_save_calculation_io_error(self, mock_dump):
        """Test saving a calculation with IO error."""
        calculation = {'operation': 'add', 'result': 8}
        success = self.api.save_calculation(calculation)
        self.assertFalse(success)


# ----- FUNCTIONAL TESTING WITH PYTEST -----

@pytest.fixture
def calculator():
    """Pytest fixture that provides a Calculator instance."""
    return Calculator()

@pytest.fixture
def calculator_api():
    """Pytest fixture that provides a CalculatorAPI instance."""
    # Use a temporary file for testing
    temp_file = "pytest_calculations.json"
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    api = CalculatorAPI(data_source=temp_file)
    yield api
    
    # Cleanup after test
    if os.path.exists(temp_file):
        os.remove(temp_file)

@pytest.mark.parametrize("a,b,expected", [
    (5, 3, 8),
    (-1, 1, 0),
    (0, 0, 0),
    (1.5, 2.5, 4.0)
])
def test_calculator_add(calculator, a, b, expected):
    """Parameterized test for addition with various inputs."""
    assert calculator.add(a, b) == expected

def test_calculator_divide_by_zero(calculator):
    """Test division by zero raises appropriate exception."""
    with pytest.raises(CalculationError) as excinfo:
        calculator.divide(5, 0)
    assert "Division by zero" in str(excinfo.value)

def test_calculator_api_process(calculator_api, monkeypatch):
    """Test API with mocked calculator."""
    # Create a mock calculator
    mock_calc = MagicMock()
    mock_calc.add.return_value = 10
    
    # Replace real calculator with mock
    monkeypatch.setattr(calculator_api, "calculator", mock_calc)
    
    # Process calculation
    result = calculator_api.process_calculation('add', 5, 5)
    
    # Check mock was called correctly
    mock_calc.add.assert_called_once_with(5, 5)
    
    # Check result
    assert result['status'] == 'success'
    assert result['result'] == 10


# ----- TEST RUNNER -----

class TestRunner:
    """Custom test runner to execute and report test results."""
    
    def __init__(self, verbosity: int = 2):
        """Initialize with verbosity level."""
        self.verbosity = verbosity
    
    def run_unittest_tests(self):
        """Run unittest tests."""
        logger.info("Running unittest tests...")
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test cases to the suite
        suite.addTests(loader.loadTestsFromTestCase(CalculatorTestCase))
        suite.addTests(loader.loadTestsFromTestCase(CalculatorAPITestCase))
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = runner.run(suite)
        
        # Report results
        logger.info(f"Tests run: {result.testsRun}")
        logger.info(f"Failures: {len(result.failures)}")
        logger.info(f"Errors: {len(result.errors)}")
        
        return result
    
    def run_pytest_tests(self):
        """Run pytest tests."""
        logger.info("Running pytest tests...")
        # This would normally use pytest.main(), but for demonstration
        # we'll just print what would happen
        logger.info("Would run: pytest -xvs")
        logger.info("Pytest would discover and run all test_* functions")
    
    def measure_coverage(self):
        """Measure test coverage."""
        logger.info("Measuring test coverage...")
        cov = coverage.Coverage(source=["__main__"])
        cov.start()
        
        # Run tests under coverage measurement
        self.run_unittest_tests()
        
        cov.stop()
        cov.save()
        
        # Report coverage
        total_percentage = cov.report()
        logger.info(f"Total coverage: {total_percentage:.2f}%")


# ----- MAIN ENTRY POINT -----

if __name__ == "__main__":
    runner = TestRunner()
    
    print("\n=== FUNCTIONAL TESTING DEMONSTRATION ===\n")
    
    # Run unittest tests
    print("\n=== Running unittest tests ===\n")
    result = runner.run_unittest_tests()
    
    # Mention pytest (without actual execution)
    print("\n=== Pytest alternative (demonstration only) ===\n")
    runner.run_pytest_tests()
    
    # Measure coverage
    print("\n=== Measuring test coverage ===\n")
    runner.measure_coverage()
    
    print("\n=== Testing complete ===\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)