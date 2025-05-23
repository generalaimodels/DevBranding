#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Testing in Python: Comprehensive End-to-End Implementation
This file demonstrates various approaches to integration testing in Python,
covering different strategies, frameworks, and best practices.
"""

import unittest
import pytest
import json
import os
import sys
import logging
import requests
from unittest import mock
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Callable, Generator, Tuple
import sqlite3
import tempfile
from dataclasses import dataclass
from abc import ABC, abstractmethod


# Configure logging for test execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('integration_tests.log')
    ]
)
logger = logging.getLogger('integration_tests')


# ============================================================================
# SECTION 1: Application Components to Test
# ============================================================================

class DatabaseManager:
    """Handles database operations."""
    
    def __init__(self, db_path: str):
        """Initialize the database connection."""
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
            
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            
    def initialize_db(self) -> None:
        """Create initial database schema."""
        if not self.connection:
            self.connect()
            
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        self.connection.commit()
        logger.info("Database schema initialized")


class UserService:
    """Handles user-related operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with a database manager instance."""
        self.db_manager = db_manager
        
    def create_user(self, username: str, email: str) -> int:
        """Create a new user and return the user ID."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email)
            )
            self.db_manager.connection.commit()
            user_id = cursor.lastrowid
            logger.info(f"Created user: {username} with ID: {user_id}")
            return user_id
        except sqlite3.IntegrityError:
            logger.error(f"User already exists: {username}")
            raise ValueError(f"User already exists: {username}")
            
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Retrieve user by ID."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError(f"User not found: {user_id}")
            
        return dict(user)
        
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieve all users."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return [dict(user) for user in users]


class ProductService:
    """Handles product-related operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with a database manager instance."""
        self.db_manager = db_manager
        
    def create_product(self, name: str, price: float, stock: int = 0) -> int:
        """Create a new product and return the product ID."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock)
        )
        self.db_manager.connection.commit()
        product_id = cursor.lastrowid
        logger.info(f"Created product: {name} with ID: {product_id}")
        return product_id
        
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Retrieve product by ID."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            logger.warning(f"Product not found: {product_id}")
            raise ValueError(f"Product not found: {product_id}")
            
        return dict(product)
        
    def update_stock(self, product_id: int, quantity: int) -> None:
        """Update product stock."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (quantity, product_id)
        )
        self.db_manager.connection.commit()
        
        if cursor.rowcount == 0:
            logger.warning(f"Product not found: {product_id}")
            raise ValueError(f"Product not found: {product_id}")
            
        logger.info(f"Updated stock for product {product_id}: {quantity}")


class ExternalPaymentService:
    """External payment service client."""
    
    def __init__(self, api_url: str, api_key: str):
        """Initialize with API endpoint and credentials."""
        self.api_url = api_url
        self.api_key = api_key
        
    def process_payment(self, amount: float, card_details: Dict[str, str]) -> Dict[str, Any]:
        """Process a payment using the external payment service."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": amount,
            "currency": "USD",
            "card": card_details
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/payments",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Payment processed: {result['id']}")
            return result
        except requests.RequestException as e:
            logger.error(f"Payment processing error: {e}")
            raise RuntimeError(f"Payment processing failed: {e}")


class OrderService:
    """Handles order-related operations."""
    
    def __init__(
        self, 
        db_manager: DatabaseManager,
        product_service: ProductService,
        payment_service: ExternalPaymentService
    ):
        """Initialize with required service dependencies."""
        self.db_manager = db_manager
        self.product_service = product_service
        self.payment_service = payment_service
        
    def create_order(
        self, 
        user_id: int, 
        items: List[Dict[str, Any]],
        payment_details: Optional[Dict[str, str]] = None
    ) -> int:
        """
        Create a new order with the specified items.
        Each item should have product_id and quantity.
        """
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        # Validate items and calculate total
        total_amount = 0
        order_items = []
        
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            try:
                product = self.product_service.get_product(product_id)
                
                if product['stock'] < quantity:
                    raise ValueError(f"Insufficient stock for product {product_id}")
                    
                price = product['price']
                total_amount += price * quantity
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': price
                })
            except ValueError as e:
                logger.error(f"Order creation failed: {e}")
                raise
                
        # Begin transaction
        self.db_manager.connection.execute("BEGIN TRANSACTION")
        try:
            # Process payment if provided
            if payment_details:
                payment_result = self.payment_service.process_payment(
                    total_amount, payment_details
                )
                if payment_result.get('status') != 'success':
                    raise RuntimeError("Payment failed")
                    
            # Create order
            cursor = self.db_manager.connection.cursor()
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
                (user_id, total_amount, "paid" if payment_details else "pending")
            )
            order_id = cursor.lastrowid
            
            # Add order items
            for item in order_items:
                cursor.execute(
                    """
                    INSERT INTO order_items 
                    (order_id, product_id, quantity, price) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (order_id, item['product_id'], item['quantity'], item['price'])
                )
                
                # Update product stock
                self.product_service.update_stock(item['product_id'], -item['quantity'])
                
            # Commit transaction
            self.db_manager.connection.commit()
            logger.info(f"Created order {order_id} for user {user_id}")
            return order_id
            
        except Exception as e:
            # Rollback transaction on any error
            self.db_manager.connection.rollback()
            logger.error(f"Order creation failed with rollback: {e}")
            raise
            
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Retrieve order details including items."""
        if not self.db_manager.connection:
            self.db_manager.connect()
            
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            logger.warning(f"Order not found: {order_id}")
            raise ValueError(f"Order not found: {order_id}")
            
        result = dict(order)
        
        # Get order items
        cursor.execute(
            "SELECT * FROM order_items WHERE order_id = ?", 
            (order_id,)
        )
        result['items'] = [dict(item) for item in cursor.fetchall()]
        
        return result


# ============================================================================
# SECTION 2: Integration Test Framework Setup
# ============================================================================

@contextmanager
def temp_database() -> Generator[str, None, None]:
    """Context manager to create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_db.sqlite")
    
    try:
        yield db_path
    finally:
        # Clean up
        try:
            os.unlink(db_path)
            os.rmdir(temp_dir)
        except (OSError, IOError) as e:
            logger.warning(f"Failed to clean up temp database: {e}")


@contextmanager
def mock_payment_service() -> Generator[mock.MagicMock, None, None]:
    """Context manager to create a mock payment service for testing."""
    mock_service = mock.MagicMock(spec=ExternalPaymentService)
    mock_service.process_payment.return_value = {
        "id": "mock-payment-123",
        "status": "success",
        "amount": 100.0
    }
    
    try:
        yield mock_service
    finally:
        pass  # No cleanup needed for mock object


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests providing common utilities."""
    
    def setUp(self) -> None:
        """Set up test environment before each test."""
        self.db_path_ctx = temp_database()
        self.db_path = self.db_path_ctx.__enter__()
        
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.connect()
        self.db_manager.initialize_db()
        
        self.mock_payment_service_ctx = mock_payment_service()
        self.mock_payment_service = self.mock_payment_service_ctx.__enter__()
        
        self.user_service = UserService(self.db_manager)
        self.product_service = ProductService(self.db_manager)
        self.order_service = OrderService(
            self.db_manager,
            self.product_service,
            self.mock_payment_service
        )
        
        logger.info(f"Test environment set up with database: {self.db_path}")
        
    def tearDown(self) -> None:
        """Clean up test environment after each test."""
        self.db_manager.disconnect()
        self.db_path_ctx.__exit__(None, None, None)
        self.mock_payment_service_ctx.__exit__(None, None, None)
        logger.info("Test environment cleaned up")
        
    def create_test_user(self) -> int:
        """Helper to create a test user."""
        user_id = self.user_service.create_user(
            f"testuser_{os.urandom(4).hex()}", 
            f"test_{os.urandom(4).hex()}@example.com"
        )
        return user_id
        
    def create_test_product(self, stock: int = 10) -> int:
        """Helper to create a test product with stock."""
        product_id = self.product_service.create_product(
            f"Test Product {os.urandom(4).hex()}",
            price=9.99,
            stock=stock
        )
        return product_id


# ============================================================================
# SECTION 3: Integration Tests - Bottom-Up Approach
# ============================================================================

class TestDatabaseIntegration(IntegrationTestCase):
    """Tests for database component integration."""
    
    def test_database_initialization(self) -> None:
        """Test that database is properly initialized with all tables."""
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'products', 'orders', 'order_items']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table '{table}' should exist in database")
            
    def test_database_connection_error_handling(self) -> None:
        """Test database connection error handling."""
        invalid_db_manager = DatabaseManager("/invalid/path/to/db.sqlite")
        with self.assertRaises(sqlite3.Error):
            invalid_db_manager.connect()


class TestUserServiceIntegration(IntegrationTestCase):
    """Tests for UserService integration with the database."""
    
    def test_create_and_retrieve_user(self) -> None:
        """Test creating a user and retrieving it."""
        username = "testuser_create"
        email = "testuser_create@example.com"
        
        # Create user
        user_id = self.user_service.create_user(username, email)
        self.assertIsNotNone(user_id)
        
        # Retrieve user
        user = self.user_service.get_user(user_id)
        self.assertEqual(user['username'], username)
        self.assertEqual(user['email'], email)
        
    def test_create_duplicate_user(self) -> None:
        """Test handling of duplicate user creation."""
        username = "testuser_duplicate"
        email = "testuser_duplicate@example.com"
        
        # Create user once
        self.user_service.create_user(username, email)
        
        # Try to create duplicate user
        with self.assertRaises(ValueError):
            self.user_service.create_user(username, email)
            
    def test_get_nonexistent_user(self) -> None:
        """Test retrieving a non-existent user."""
        with self.assertRaises(ValueError):
            self.user_service.get_user(999999)
            
    def test_get_all_users(self) -> None:
        """Test retrieving all users."""
        # Create a few users
        usernames = ["user1", "user2", "user3"]
        for i, name in enumerate(usernames):
            self.user_service.create_user(name, f"{name}@example.com")
            
        # Get all users
        users = self.user_service.get_all_users()
        self.assertGreaterEqual(len(users), len(usernames))
        
        # Check usernames exist in the result
        db_usernames = [user['username'] for user in users]
        for name in usernames:
            self.assertIn(name, db_usernames)


class TestProductServiceIntegration(IntegrationTestCase):
    """Tests for ProductService integration with the database."""
    
    def test_create_and_retrieve_product(self) -> None:
        """Test creating a product and retrieving it."""
        name = "Test Product"
        price = 29.99
        stock = 100
        
        # Create product
        product_id = self.product_service.create_product(name, price, stock)
        self.assertIsNotNone(product_id)
        
        # Retrieve product
        product = self.product_service.get_product(product_id)
        self.assertEqual(product['name'], name)
        self.assertEqual(product['price'], price)
        self.assertEqual(product['stock'], stock)
        
    def test_update_product_stock(self) -> None:
        """Test updating product stock."""
        # Create product
        product_id = self.product_service.create_product("Stock Test", 19.99, 50)
        
        # Update stock
        self.product_service.update_stock(product_id, 10)
        
        # Check stock was updated
        product = self.product_service.get_product(product_id)
        self.assertEqual(product['stock'], 60)
        
        # Decrease stock
        self.product_service.update_stock(product_id, -20)
        
        # Check stock was decreased
        product = self.product_service.get_product(product_id)
        self.assertEqual(product['stock'], 40)
        
    def test_update_nonexistent_product(self) -> None:
        """Test updating stock of a non-existent product."""
        with self.assertRaises(ValueError):
            self.product_service.update_stock(999999, 10)


# ============================================================================
# SECTION 4: Integration Tests - Top-Down Approach with Mocks
# ============================================================================

class TestOrderServiceIntegration(IntegrationTestCase):
    """Tests for OrderService integration with other services."""
    
    def test_create_and_retrieve_order(self) -> None:
        """Test creating an order and retrieving it."""
        # Create a user and products
        user_id = self.create_test_user()
        product1_id = self.create_test_product(stock=20)
        product2_id = self.create_test_product(stock=30)
        
        # Create order items
        items = [
            {"product_id": product1_id, "quantity": 2},
            {"product_id": product2_id, "quantity": 3}
        ]
        
        # Create order
        order_id = self.order_service.create_order(user_id, items)
        self.assertIsNotNone(order_id)
        
        # Retrieve order
        order = self.order_service.get_order(order_id)
        self.assertEqual(order['user_id'], user_id)
        self.assertEqual(order['status'], "pending")
        self.assertEqual(len(order['items']), 2)
        
        # Check stock was updated
        product1 = self.product_service.get_product(product1_id)
        self.assertEqual(product1['stock'], 18)
        
        product2 = self.product_service.get_product(product2_id)
        self.assertEqual(product2['stock'], 27)
        
    def test_create_order_with_payment(self) -> None:
        """Test creating an order with payment processing."""
        # Create a user and product
        user_id = self.create_test_user()
        product_id = self.create_test_product(stock=10)
        
        # Create order items
        items = [{"product_id": product_id, "quantity": 2}]
        
        # Mock payment details
        payment_details = {
            "card_number": "4111111111111111",
            "expiry_month": "12",
            "expiry_year": "2025",
            "cvv": "123"
        }
        
        # Create order with payment
        order_id = self.order_service.create_order(
            user_id, items, payment_details
        )
        self.assertIsNotNone(order_id)
        
        # Verify payment service was called
        self.mock_payment_service.process_payment.assert_called_once()
        
        # Retrieve order and check status
        order = self.order_service.get_order(order_id)
        self.assertEqual(order['status'], "paid")
        
    def test_create_order_with_insufficient_stock(self) -> None:
        """Test creating an order with insufficient product stock."""
        # Create a user and product with low stock
        user_id = self.create_test_user()
        product_id = self.create_test_product(stock=3)
        
        # Try to create order with quantity exceeding stock
        items = [{"product_id": product_id, "quantity": 5}]
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.order_service.create_order(user_id, items)
            
        # Verify stock wasn't changed
        product = self.product_service.get_product(product_id)
        self.assertEqual(product['stock'], 3)
        
    def test_create_order_with_nonexistent_product(self) -> None:
        """Test creating an order with a non-existent product."""
        # Create a user
        user_id = self.create_test_user()
        
        # Try to create order with non-existent product
        items = [{"product_id": 999999, "quantity": 1}]
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.order_service.create_order(user_id, items)
            
    def test_create_order_with_payment_failure(self) -> None:
        """Test creating an order with failed payment."""
        # Create a user and product
        user_id = self.create_test_user()
        product_id = self.create_test_product(stock=10)
        
        # Create order items
        items = [{"product_id": product_id, "quantity": 2}]
        
        # Mock payment details
        payment_details = {
            "card_number": "4111111111111111",
            "expiry_month": "12",
            "expiry_year": "2025",
            "cvv": "123"
        }
        
        # Mock payment failure
        self.mock_payment_service.process_payment.return_value = {
            "id": "mock-payment-failure",
            "status": "failed",
            "error": "Card declined"
        }
        
        # Should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.order_service.create_order(user_id, items, payment_details)
            
        # Verify stock wasn't changed
        product = self.product_service.get_product(product_id)
        self.assertEqual(product['stock'], 10)


# ============================================================================
# SECTION 5: End-to-End Integration Test
# ============================================================================

class TestEcommerceSystemE2E(IntegrationTestCase):
    """End-to-end tests for the complete ecommerce system."""
    
    def test_complete_order_workflow(self) -> None:
        """
        Test the complete workflow from user creation to order completion.
        This is a comprehensive end-to-end test.
        """
        # Step 1: Create a user
        username = "e2e_user"
        email = "e2e_user@example.com"
        user_id = self.user_service.create_user(username, email)
        
        # Step 2: Create multiple products
        product_ids = []
        for i in range(3):
            product_id = self.product_service.create_product(
                f"E2E Product {i+1}",
                price=(10.0 + i * 5.0),
                stock=50
            )
            product_ids.append(product_id)
            
        # Step 3: Check inventory before order
        pre_order_stock = {}
        for pid in product_ids:
            product = self.product_service.get_product(pid)
            pre_order_stock[pid] = product['stock']
            
        # Step 4: Create an order
        items = [
            {"product_id": product_ids[0], "quantity": 2},
            {"product_id": product_ids[1], "quantity": 1},
            {"product_id": product_ids[2], "quantity": 3}
        ]
        
        payment_details = {
            "card_number": "4242424242424242",
            "expiry_month": "12",
            "expiry_year": "2028",
            "cvv": "123"
        }
        
        order_id = self.order_service.create_order(
            user_id, items, payment_details
        )
        
        # Step 5: Verify order details
        order = self.order_service.get_order(order_id)
        self.assertEqual(order['user_id'], user_id)
        self.assertEqual(order['status'], "paid")
        self.assertEqual(len(order['items']), 3)
        
        # Calculate expected total manually
        expected_total = (
            (10.0 * 2) +      # First product
            (15.0 * 1) +      # Second product
            (20.0 * 3)        # Third product
        )
        self.assertAlmostEqual(order['total_amount'], expected_total)
        
        # Step 6: Verify stock levels were updated correctly
        for pid in product_ids:
            product = self.product_service.get_product(pid)
            item_quantity = 0
            for item in items:
                if item['product_id'] == pid:
                    item_quantity = item['quantity']
                    break
                    
            expected_stock = pre_order_stock[pid] - item_quantity
            self.assertEqual(
                product['stock'], 
                expected_stock,
                f"Stock for product {pid} should be {expected_stock}"
            )
            
        # Step 7: Verify payment service was called correctly
        self.mock_payment_service.process_payment.assert_called_once_with(
            expected_total, payment_details
        )


# ============================================================================
# SECTION 6: Integration Tests with Pytest
# ============================================================================

@pytest.fixture
def test_db():
    """Pytest fixture for creating a test database."""
    with temp_database() as db_path:
        db_manager = DatabaseManager(db_path)
        db_manager.connect()
        db_manager.initialize_db()
        yield db_manager
        db_manager.disconnect()


@pytest.fixture
def test_payment_service():
    """Pytest fixture for creating a mock payment service."""
    with mock_payment_service() as mock_service:
        yield mock_service


@pytest.fixture
def test_services(test_db, test_payment_service):
    """Pytest fixture for creating test service instances."""
    user_service = UserService(test_db)
    product_service = ProductService(test_db)
    order_service = OrderService(
        test_db,
        product_service,
        test_payment_service
    )
    
    return {
        "db_manager": test_db,
        "user_service": user_service,
        "product_service": product_service,
        "order_service": order_service,
        "payment_service": test_payment_service
    }


def test_create_order_with_pytest(test_services):
    """Test order creation using pytest."""
    # Create a user
    user_service = test_services["user_service"]
    product_service = test_services["product_service"]
    order_service = test_services["order_service"]
    
    # Create a test user
    username = f"pytest_user_{os.urandom(4).hex()}"
    email = f"{username}@example.com"
    user_id = user_service.create_user(username, email)
    
    # Create a test product
    product_name = f"pytest_product_{os.urandom(4).hex()}"
    product_id = product_service.create_product(product_name, 25.99, 15)
    
    # Create an order
    items = [{"product_id": product_id, "quantity": 3}]
    order_id = order_service.create_order(user_id, items)
    
    # Verify order was created
    order = order_service.get_order(order_id)
    assert order["user_id"] == user_id
    assert len(order["items"]) == 1
    assert order["items"][0]["product_id"] == product_id
    assert order["items"][0]["quantity"] == 3
    
    # Verify stock was updated
    product = product_service.get_product(product_id)
    assert product["stock"] == 12


@pytest.mark.parametrize("stock,quantity,should_succeed", [
    (10, 5, True),    # Enough stock
    (5, 5, True),     # Just enough stock
    (3, 5, False),    # Not enough stock
])
def test_order_with_different_stock_levels(test_services, stock, quantity, should_succeed):
    """Parameterized test for different stock levels."""
    user_service = test_services["user_service"]
    product_service = test_services["product_service"]
    order_service = test_services["order_service"]
    
    # Create a test user
    user_id = user_service.create_user(
        f"stock_test_user_{os.urandom(4).hex()}", 
        f"stock_test_{os.urandom(4).hex()}@example.com"
    )
    
    # Create a test product with specified stock
    product_id = product_service.create_product("Stock Test Product", 15.99, stock)
    
    # Try to create an order
    items = [{"product_id": product_id, "quantity": quantity}]
    
    if should_succeed:
        order_id = order_service.create_order(user_id, items)
        assert order_id is not None
        
        # Verify stock was updated
        product = product_service.get_product(product_id)
        assert product["stock"] == stock - quantity
    else:
        with pytest.raises(ValueError):
            order_service.create_order(user_id, items)
            
        # Verify stock wasn't changed
        product = product_service.get_product(product_id)
        assert product["stock"] == stock


# ============================================================================
# SECTION 7: Main Test Runner
# ============================================================================

if __name__ == "__main__":
    # Run unittest tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Run pytest tests
    pytest.main(['-v', __file__])