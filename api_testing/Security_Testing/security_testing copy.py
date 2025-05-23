"""
Topic: Security Testing in Python
Description: This file demonstrates various security testing techniques, best practices, 
and tools for securing Python applications. It covers input validation, secure coding, 
cryptography, XSS prevention, SQL injection prevention, secure file handling, 
exception handling, and security testing tools integration.

Follows PEP-8 standards and includes detailed explanations of each security aspect.
"""

import re
import hashlib
import hmac
import secrets
import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote, unquote
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import sqlite3
from html import escape
import jwt  # Requires: pip install pyjwt
import requests  # Requires: pip install requests
import bandit  # Requires: pip install bandit (for static analysis)

# Configure logging for security events
logging.basicConfig(
    filename='security_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants for security
MIN_PASSWORD_LENGTH = 8
ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9@#$%^&+=]*$')
SECRET_KEY = secrets.token_hex(32)  # Generate a secure secret key

class SecurityTesting:
    """
    A class to demonstrate various security testing techniques in Python.
    Covers input validation, secure coding, cryptography, and more.
    """

    def __init__(self):
        """Initialize the security testing class with encryption key."""
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        logging.info("SecurityTesting class initialized with secure key.")

    # 1. Input Validation
    def validate_input(self, user_input: str) -> Optional[str]:
        """
        Validate user input to prevent injection attacks and ensure data integrity.
        Args:
            user_input: The input string to validate.
        Returns:
            Validated input or None if invalid.
        """
        try:
            if not isinstance(user_input, str):
                logging.error("Input validation failed: Input is not a string.")
                raise ValueError("Input must be a string.")

            # Sanitize input: remove leading/trailing whitespace
            user_input = user_input.strip()

            # Check for allowed characters (prevent injection attacks)
            if not ALLOWED_CHARS.match(user_input):
                logging.error(f"Input validation failed: Invalid characters in input: {user_input}")
                raise ValueError("Input contains invalid characters.")

            # Escape HTML to prevent XSS
            sanitized_input = escape(user_input)
            logging.info("Input validated and sanitized successfully.")
            return sanitized_input

        except ValueError as e:
            logging.error(f"Validation error: {str(e)}")
            return None

    # 2. Secure Password Hashing
    def hash_password(self, password: str) -> Dict[str, str]:
        """
        Securely hash a password using PBKDF2 with salt.
        Args:
            password: The password to hash.
        Returns:
            Dictionary containing salt and hashed password.
        """
        try:
            if len(password) < MIN_PASSWORD_LENGTH:
                raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

            # Generate a random salt
            salt = os.urandom(16)

            # Use PBKDF2 for secure password hashing
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            logging.info("Password hashed successfully.")
            return {"salt": base64.b64encode(salt).decode('utf-8'), "hashed": key.decode('utf-8')}

        except Exception as e:
            logging.error(f"Password hashing error: {str(e)}")
            raise

    # 3. Secure Token Generation (JWT)
    def generate_jwt_token(self, user_id: int) -> str:
        """
        Generate a secure JWT token for user authentication.
        Args:
            user_id: The user ID to encode in the token.
        Returns:
            JWT token string.
        """
        try:
            payload = {
                "user_id": user_id,
                "exp": 3600  # Token expires in 1 hour
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            logging.info(f"JWT token generated for user_id: {user_id}")
            return token

        except Exception as e:
            logging.error(f"JWT token generation error: {str(e)}")
            raise

    # 4. SQL Injection Prevention
    def secure_database_query(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Execute a secure database query using parameterized statements to prevent SQL injection.
        Args:
            user_id: The user ID to query.
        Returns:
            User data or None if not found.
        """
        try:
            conn = sqlite3.connect("secure_database.db")
            cursor = conn.cursor()

            # Create a sample table (for demonstration)
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")

            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))  # Parameterized query
            result = cursor.fetchone()

            logging.info(f"Secure database query executed for user_id: {user_id}")
            conn.close()
            return result

        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            return None

    # 5. Secure File Handling
    def secure_file_upload(self, file_path: str, content: bytes) -> bool:
        """
        Securely handle file uploads by validating file paths and content.
        Args:
            file_path: The path to save the file.
            content: The file content in bytes.
        Returns:
            Boolean indicating success or failure.
        """
        try:
            # Prevent path traversal attacks
            safe_path = os.path.abspath(file_path)
            if not safe_path.startswith(os.path.abspath("uploads/")):
                logging.error(f"Path traversal attempt detected: {file_path}")
                raise ValueError("Invalid file path.")

            # Ensure directory exists
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)

            # Write file securely
            with open(safe_path, "wb") as f:
                f.write(content)

            logging.info(f"File uploaded securely: {safe_path}")
            return True

        except Exception as e:
            logging.error(f"File upload error: {str(e)}")
            return False

    # 6. Cryptography (Encryption/Decryption)
    def encrypt_data(self, data: str) -> bytes:
        """
        Encrypt sensitive data using Fernet (symmetric encryption).
        Args:
            data: The data to encrypt.
        Returns:
            Encrypted data in bytes.
        """
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            logging.info("Data encrypted successfully.")
            return encrypted_data

        except Exception as e:
            logging.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypt data encrypted with Fernet.
        Args:
            encrypted_data: The encrypted data in bytes.
        Returns:
            Decrypted data as string.
        """
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
            logging.info("Data decrypted successfully.")
            return decrypted_data

        except Exception as e:
            logging.error(f"Decryption error: {str(e)}")
            raise

    # 7. XSS Prevention
    def prevent_xss(self, user_input: str) -> str:
        """
        Prevent XSS by escaping HTML characters in user input.
        Args:
            user_input: The input string to sanitize.
        Returns:
            Sanitized string safe for HTML rendering.
        """
        try:
            safe_input = escape(user_input)
            logging.info("XSS prevention applied successfully.")
            return safe_input

        except Exception as e:
            logging.error(f"XSS prevention error: {str(e)}")
            raise

    # 8. Secure API Calls
    def secure_api_call(self, url: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a secure API call with proper headers and error handling.
        Args:
            url: The API endpoint URL.
            data: The data to send in the request.
        Returns:
            API response or None if failed.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.generate_jwt_token(1)}"
            }
            response = requests.post(url, json=data, headers=headers, timeout=10)

            # Validate response
            response.raise_for_status()
            logging.info(f"Secure API call successful to: {url}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"API call error: {str(e)}")
            return None

    # 9. Static Security Analysis (Using Bandit)
    def run_security_scan(self, file_path: str) -> None:
        """
        Run a static security analysis on the given Python file using Bandit.
        Args:
            file_path: The path to the Python file to analyze.
        """
        try:
            # This is a programmatic way to run Bandit (for demonstration)
            # In practice, run `bandit -r <file_path>` in the terminal
            from bandit.core import manager
            bandit_manager = manager.BanditManager(config=None, agg_type='file', quiet=True)
            bandit_manager.discover_files([file_path], False)
            bandit_manager.run_tests()
            logging.info(f"Security scan completed on: {file_path}")

            # Log results
            if bandit_manager.results_count():
                logging.warning(f"Security issues found in {file_path}: {bandit_manager.get_issue_list()}")
            else:
                logging.info("No security issues found.")

        except Exception as e:
            logging.error(f"Security scan error: {str(e)}")
            raise

# Example Usage
if __name__ == "__main__":
    security = SecurityTesting()

    # Test Input Validation
    user_input = "<script>alert('XSS')</script>"
    validated_input = security.validate_input(user_input)
    print(f"Validated Input: {validated_input}")

    # Test Password Hashing
    password = "SecurePass123"
    hashed_data = security.hash_password(password)
    print(f"Hashed Password: {hashed_data}")

    # Test JWT Token Generation
    token = security.generate_jwt_token(user_id=1)
    print(f"JWT Token: {token}")

    # Test Secure Database Query
    user_data = security.secure_database_query(user_id=1)
    print(f"Database Query Result: {user_data}")

    # Test Secure File Upload
    file_content = b"Secure file content"
    upload_success = security.secure_file_upload("uploads/secure_file.txt", file_content)
    print(f"File Upload Success: {upload_success}")

    # Test Encryption/Decryption
    sensitive_data = "Sensitive Information"
    encrypted = security.encrypt_data(sensitive_data)
    decrypted = security.decrypt_data(encrypted)
    print(f"Encrypted Data: {encrypted}")
    print(f"Decrypted Data: {decrypted}")

    # Test XSS Prevention
    xss_input = "<script>alert('XSS')</script>"
    safe_input = security.prevent_xss(xss_input)
    print(f"XSS Safe Input: {safe_input}")

    # Test Secure API Call
    api_url = "https://api.example.com/data"
    api_data = {"key": "value"}
    api_response = security.secure_api_call(api_url, api_data)
    print(f"API Response: {api_response}")

    # Test Security Scan (Static Analysis)
    security.run_security_scan(__file__)