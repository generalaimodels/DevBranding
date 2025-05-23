"""
Topic: Penetration Testing in Python
Description: This script provides a comprehensive implementation of penetration testing concepts, covering 
network scanning, vulnerability assessment, password cracking, exploitation, and reporting. It adheres to 
PEP-8 standards, with detailed explanations, error handling, and modular design. Note: This is for educational 
purposes only. Unauthorized penetration testing is illegal.

Author: World No. 1 Coder
"""

# Import required libraries
import socket
import threading
import queue
import time
import ssl
import re
import subprocess
import os
import sys
import logging
import nmap
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Optional
import paramiko
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging for penetration testing activities
logging.basicConfig(
    filename='pentest_report.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
TIMEOUT = 1.0
WORDLIST_PATH = "/usr/share/wordlists/rockyou.txt"  # Path to wordlist for password cracking
SSH_TIMEOUT = 10

# Custom Exceptions
class PenetrationTestError(Exception):
    """Base exception for penetration testing errors."""
    pass

class NetworkError(PenetrationTestError):
    """Exception for network-related errors."""
    pass

class ExploitationError(PenetrationTestError):
    """Exception for exploitation-related errors."""
    pass

# 1. Network Scanning
class NetworkScanner:
    """Class to handle network scanning operations."""
    
    def __init__(self, target: str, ports: List[int] = COMMON_PORTS):
        self.target = target
        self.ports = ports
        self.open_ports = []
        self.queue = queue.Queue()
        self.nm = nmap.PortScanner()
        
    def port_scan(self, port: int) -> Tuple[int, bool]:
        """Scan a specific port on the target host."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            result = sock.connect_ex((self.target, port))
            sock.close()
            return port, result == 0
        except socket.gaierror:
            raise NetworkError(f"Hostname {self.target} could not be resolved.")
        except socket.error as e:
            raise NetworkError(f"Socket error occurred: {e}")

    def threader(self) -> None:
        """Worker thread for port scanning."""
        while True:
            port = self.queue.get()
            try:
                port, is_open = self.port_scan(port)
                if is_open:
                    self.open_ports.append(port)
                    logging.info(f"Port {port} is open on {self.target}")
            except NetworkError as e:
                logging.error(f"Network error on port {port}: {e}")
            finally:
                self.queue.task_done()

    def scan_ports(self, num_threads: int = 50) -> List[int]:
        """Scan all specified ports using multiple threads."""
        logging.info(f"Starting port scan on {self.target}")
        
        # Fill the queue with ports
        for port in self.ports:
            self.queue.put(port)
        
        # Start threads
        for _ in range(num_threads):
            t = threading.Thread(target=self.threader, daemon=True)
            t.start()
        
        # Wait for all tasks to complete
        self.queue.join()
        
        logging.info(f"Port scan completed. Open ports: {self.open_ports}")
        return sorted(self.open_ports)

    def service_detection(self) -> Dict:
        """Detect services running on open ports using nmap."""
        try:
            logging.info(f"Starting service detection on {self.target}")
            self.nm.scan(self.target, arguments='-sV -p ' + ','.join(map(str, self.open_ports)))
            return self.nm[self.target]
        except nmap.PortScannerError as e:
            logging.error(f"Nmap service detection failed: {e}")
            raise NetworkError(f"Service detection failed: {e}")

# 2. Vulnerability Assessment
class VulnerabilityScanner:
    """Class to handle vulnerability scanning using external tools and APIs."""
    
    def __init__(self, target: str, open_ports: List[int]):
        self.target = target
        self.open_ports = open_ports
    
    def check_vulnerabilities(self) -> Dict[str, List[str]]:
        """Check for known vulnerabilities using NVD or other sources."""
        vulnerabilities = {}
        try:
            logging.info(f"Starting vulnerability scan on {self.target}")
            for port in self.open_ports:
                # Simulate vulnerability check (replace with actual NVD API or other DB)
                vuln_info = self._simulate_vuln_check(port)
                if vuln_info:
                    vulnerabilities[port] = vuln_info
            return vulnerabilities
        except Exception as e:
            logging.error(f"Vulnerability scan failed: {e}")
            raise PenetrationTestError(f"Vulnerability scan error: {e}")

    def _simulate_vuln_check(self, port: int) -> List[str]:
        """Simulate vulnerability check for a port."""
        # Placeholder for actual vulnerability database lookup
        if port == 80:
            return ["CVE-2023-1234: Apache HTTP Server Vulnerability"]
        elif port == 22:
            return ["CVE-2022-5678: OpenSSH Weak Key Exchange"]
        return []

# 3. Password Cracking
class PasswordCracker:
    """Class to handle password cracking for services like SSH."""
    
    def __init__(self, target: str, username: str, port: int = 22):
        self.target = target
        self.username = username
        self.port = port
        self.wordlist = self._load_wordlist()
    
    def _load_wordlist(self) -> List[str]:
        """Load wordlist for password cracking."""
        try:
            if not os.path.exists(WORDLIST_PATH):
                raise FileNotFoundError(f"Wordlist not found at {WORDLIST_PATH}")
            with open(WORDLIST_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError as e:
            logging.error(f"Wordlist loading failed: {e}")
            raise PenetrationTestError(f"Wordlist error: {e}")

    def try_ssh_login(self, password: str) -> Optional[str]:
        """Attempt SSH login with a given password."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                self.target,
                port=self.port,
                username=self.username,
                password=password,
                timeout=SSH_TIMEOUT
            )
            client.close()
            logging.info(f"SSH login successful with password: {password}")
            return password
        except paramiko.AuthenticationException:
            return None
        except paramiko.SSHException as e:
            logging.error(f"SSH error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected SSH error: {e}")
            return None

    def crack_password(self, max_attempts: int = 1000) -> Optional[str]:
        """Attempt to crack SSH password using wordlist."""
        logging.info(f"Starting password cracking on {self.target}:{self.port}")
        with ThreadPoolExecutor(max_workers=5) as executor:
            attempts = 0
            for password in self.wordlist:
                if attempts >= max_attempts:
                    break
                future = executor.submit(self.try_ssh_login, password)
                result = future.result()
                if result:
                    return result
                attempts += 1
        logging.info("Password cracking completed. No password found.")
        return None

# 4. Exploitation
class Exploiter:
    """Class to handle exploitation of identified vulnerabilities."""
    
    def __init__(self, target: str, open_ports: List[int]):
        self.target = target
        self.open_ports = open_ports
    
    def exploit_service(self, port: int) -> bool:
        """Simulate exploitation of a service (replace with actual exploits)."""
        try:
            logging.info(f"Attempting exploitation on {self.target}:{port}")
            if port == 80:
                # Simulate HTTP exploitation (e.g., SQL injection, XSS)
                return self._exploit_http()
            elif port == 22:
                # Simulate SSH exploitation (e.g., weak credentials)
                return self._exploit_ssh()
            return False
        except Exception as e:
            logging.error(f"Exploitation failed on port {port}: {e}")
            raise ExploitationError(f"Exploitation error: {e}")

    def _exploit_http(self) -> bool:
        """Simulate HTTP exploitation."""
        # Placeholder for actual HTTP exploitation
        try:
            response = requests.get(f"http://{self.target}", timeout=5)
            if response.status_code == 200:
                logging.info("HTTP service potentially vulnerable to exploitation.")
                return True
        except requests.RequestException:
            return False
        return False

    def _exploit_ssh(self) -> bool:
        """Simulate SSH exploitation."""
        # Placeholder for actual SSH exploitation
        return False

# 5. Reporting
class ReportGenerator:
    """Class to generate penetration test reports."""
    
    def __init__(self, target: str):
        self.target = target
        self.report_data = {
            "open_ports": [],
            "services": {},
            "vulnerabilities": {},
            "exploits": {},
            "password_cracking": {}
        }
    
    def add_scan_results(self, open_ports: List[int]) -> None:
        """Add port scan results to the report."""
        self.report_data["open_ports"] = open_ports

    def add_service_results(self, services: Dict) -> None:
        """Add service detection results to the report."""
        self.report_data["services"] = services

    def add_vulnerability_results(self, vulnerabilities: Dict) -> None:
        """Add vulnerability scan results to the report."""
        self.report_data["vulnerabilities"] = vulnerabilities

    def add_exploit_results(self, port: int, success: bool) -> None:
        """Add exploitation results to the report."""
        self.report_data["exploits"][port] = success

    def add_password_cracking_results(self, username: str, password: Optional[str]) -> None:
        """Add password cracking results to the report."""
        self.report_data["password_cracking"][username] = password if password else "Not cracked"

    def generate_report(self) -> str:
        """Generate a detailed penetration test report."""
        report = f"""
Penetration Test Report for {self.target}
======================================

1. Port Scanning Results
------------------------
Open Ports: {', '.join(map(str, self.report_data['open_ports'])) if self.report_data['open_ports'] else 'None'}

2. Service Detection Results
---------------------------
{self._format_services()}

3. Vulnerability Scan Results
----------------------------
{self._format_vulnerabilities()}

4. Exploitation Results
----------------------
{self._format_exploits()}

5. Password Cracking Results
---------------------------
{self._format_password_cracking()}
"""
        logging.info("Generated penetration test report.")
        return report

    def _format_services(self) -> str:
        """Format service detection results for the report."""
        if not self.report_data["services"]:
            return "No services detected."
        result = ""
        for port, info in self.report_data["services"].items():
            result += f"Port {port}: {info.get('name', 'Unknown')} ({info.get('version', 'Unknown')})\n"
        return result

    def _format_vulnerabilities(self) -> str:
        """Format vulnerability scan results for the report."""
        if not self.report_data["vulnerabilities"]:
            return "No vulnerabilities found."
        result = ""
        for port, vulns in self.report_data["vulnerabilities"].items():
            result += f"Port {port}:\n"
            for vuln in vulns:
                result += f"  - {vuln}\n"
        return result

    def _format_exploits(self) -> str:
        """Format exploitation results for the report."""
        if not self.report_data["exploits"]:
            return "No exploitation attempted."
        result = ""
        for port, success in self.report_data["exploits"].items():
            result += f"Port {port}: {'Success' if success else 'Failed'}\n"
        return result

    def _format_password_cracking(self) -> str:
        """Format password cracking results for the report."""
        if not self.report_data["password_cracking"]:
            return "No password cracking attempted."
        result = ""
        for username, password in self.report_data["password_cracking"].items():
            result += f"Username {username}: {password}\n"
        return result

    def email_report(self, recipient: str, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str) -> None:
        """Send the report via email."""
        try:
            report = self.generate_report()
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = f"Penetration Test Report for {self.target}"
            msg.attach(MIMEText(report, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"Report emailed to {recipient}")
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")
            raise PenetrationTestError(f"Email error: {e}")

# Main Penetration Testing Workflow
def run_penetration_test(target: str, username: str = "admin") -> None:
    """Run a complete penetration test on the target."""
    try:
        # Initialize report generator
        report = ReportGenerator(target)
        
        # Step 1: Network Scanning
        scanner = NetworkScanner(target)
        open_ports = scanner.scan_ports()
        report.add_scan_results(open_ports)
        
        if not open_ports:
            logging.info("No open ports found. Penetration test aborted.")
            print(report.generate_report())
            return
        
        # Step 2: Service Detection
        services = scanner.service_detection()
        report.add_service_results(services['tcp'])
        
        # Step 3: Vulnerability Assessment
        vuln_scanner = VulnerabilityScanner(target, open_ports)
        vulnerabilities = vuln_scanner.check_vulnerabilities()
        report.add_vulnerability_results(vulnerabilities)
        
        # Step 4: Password Cracking (for SSH if open)
        if 22 in open_ports:
            cracker = PasswordCracker(target, username)
            password = cracker.crack_password()
            report.add_password_cracking_results(username, password)
        
        # Step 5: Exploitation
        exploiter = Exploiter(target, open_ports)
        for port in open_ports:
            success = exploiter.exploit_service(port)
            report.add_exploit_results(port, success)
        
        # Step 6: Generate and Email Report
        print(report.generate_report())
        # Uncomment and configure the following for email reporting
        # report.email_report(
        #     recipient="security@example.com",
        #     smtp_server="smtp.example.com",
        #     smtp_port=587,
        #     sender_email="sender@example.com",
        #     sender_password="yourpassword"
        # )
    
    except PenetrationTestError as e:
        logging.error(f"Penetration test failed: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")

# Entry Point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pentest.py <target_ip> [username]")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "admin"
    
    print(f"Starting penetration test on {target_ip}")
    run_penetration_test(target_ip, username)