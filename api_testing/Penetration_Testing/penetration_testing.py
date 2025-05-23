#!/usr/bin/env python3
"""
Comprehensive Penetration Testing Framework

This script provides a modular penetration testing framework implementing
various security testing techniques including network scanning, vulnerability
assessment, web application testing, and password security evaluation.

For educational and authorized security testing purposes only.
"""

import argparse
import socket
import ipaddress
import threading
import queue
import time
import requests
import ssl
import sys
import os
import json
import hashlib
import re
import random
import logging
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Set, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pentest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PenTest")


class PenetrationTest:
    """Main class for orchestrating penetration testing operations"""
    
    def __init__(self, target: str, output_dir: str = "results", verbosity: int = 1):
        """
        Initialize the penetration testing framework.
        
        Args:
            target: Target IP address, hostname, or URL
            output_dir: Directory to save results
            verbosity: Level of detail in output (1-3)
        """
        self.target = target
        self.output_dir = output_dir
        self.verbosity = verbosity
        self.results = {
            "metadata": {
                "target": target,
                "start_time": datetime.now().isoformat(),
                "finish_time": None
            },
            "network": {},
            "vulnerabilities": [],
            "web": {},
            "password": {},
            "summary": {}
        }
        
        # Initialize components
        self.network_scanner = NetworkScanner(self)
        self.vuln_scanner = VulnerabilityScanner(self)
        self.web_scanner = WebApplicationScanner(self)
        self.password_tester = PasswordSecurityTester(self)
        self.report_generator = ReportGenerator(self)
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        logger.info(f"Initialized penetration test against {target}")
    
    def run_full_scan(self) -> Dict:
        """Execute a complete penetration test"""
        try:
            logger.info("Starting full penetration test")
            
            # Phase 1: Network Scanning
            logger.info("Phase 1: Network Scanning")
            self.network_scanner.scan()
            
            # Phase 2: Vulnerability Assessment 
            logger.info("Phase 2: Vulnerability Assessment")
            self.vuln_scanner.scan()
            
            # Phase 3: Web Application Testing
            logger.info("Phase 3: Web Application Testing")
            self.web_scanner.scan()
            
            # Phase 4: Password Security Testing
            logger.info("Phase 4: Password Security Testing")
            self.password_tester.test()
            
            # Generate Summary
            self.summarize_findings()
            
            # Finalize results
            self.results["metadata"]["finish_time"] = datetime.now().isoformat()
            
            # Generate report
            self.report_generator.generate()
            
            return self.results
            
        except Exception as e:
            logger.error(f"Error during penetration test: {str(e)}")
            self.results["metadata"]["error"] = str(e)
            return self.results
    
    def summarize_findings(self) -> None:
        """Create a summary of all findings"""
        summary = {
            "open_ports": len(self.results.get("network", {}).get("open_ports", [])),
            "vulnerabilities": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "web_issues": len(self.results.get("web", {}).get("issues", [])),
            "password_issues": len(self.results.get("password", {}).get("issues", []))
        }
        
        # Count vulnerabilities by severity
        for vuln in self.results.get("vulnerabilities", []):
            severity = vuln.get("severity", "info").lower()
            if severity in summary["vulnerabilities"]:
                summary["vulnerabilities"][severity] += 1
        
        self.results["summary"] = summary
        logger.info(f"Summary: {json.dumps(summary, indent=2)}")


class NetworkScanner:
    """Component for network reconnaissance and port scanning"""
    
    def __init__(self, parent: PenetrationTest):
        """
        Initialize the network scanner.
        
        Args:
            parent: Parent PenetrationTest instance
        """
        self.parent = parent
        self.target = parent.target
        self.open_ports = []
        self.host_info = {}
        self.port_queue = queue.Queue()
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 
            993, 995, 1723, 3306, 3389, 5900, 8080, 8443
        ]
    
    def scan(self) -> Dict:
        """Perform comprehensive network scanning"""
        results = {}
        
        # Resolve target if it's a hostname
        try:
            ip_address = socket.gethostbyname(self.target)
            results["ip_address"] = ip_address
            results["hostname"] = self.target if ip_address != self.target else self._reverse_dns(ip_address)
        except socket.gaierror:
            logger.error(f"Could not resolve hostname: {self.target}")
            results["error"] = f"Could not resolve hostname: {self.target}"
            self.parent.results["network"] = results
            return results
        
        # OS detection (simplified)
        results["os_detection"] = self._detect_os(ip_address)
        
        # Port scanning
        logger.info(f"Starting port scan on {ip_address}")
        open_ports = self._scan_ports(ip_address)
        results["open_ports"] = open_ports
        
        # Service detection
        services = {}
        for port in open_ports:
            service = self._detect_service(ip_address, port)
            services[port] = service
        
        results["services"] = services
        
        # Network topology (simplified)
        results["traceroute"] = self._traceroute(ip_address)
        
        # Save results
        self.parent.results["network"] = results
        return results
    
    def _scan_ports(self, ip_address: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan for open ports on the target.
        
        Args:
            ip_address: Target IP address
            ports: List of ports to scan (default: common ports)
            
        Returns:
            List of dictionaries with port information
        """
        open_ports = []
        ports_to_scan = ports if ports else self.common_ports
        
        # Queue up ports to scan
        for port in ports_to_scan:
            self.port_queue.put(port)
        
        # Create worker threads
        threads = []
        for _ in range(min(100, len(ports_to_scan))):
            t = threading.Thread(target=self._port_scan_worker, 
                                args=(ip_address, open_ports))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Wait for all threads to complete
        self.port_queue.join()
        for t in threads:
            t.join(1)
        
        logger.info(f"Found {len(open_ports)} open ports")
        return open_ports
    
    def _port_scan_worker(self, ip_address: str, results: List[Dict]) -> None:
        """Worker thread for port scanning"""
        while not self.port_queue.empty():
            try:
                port = self.port_queue.get(timeout=1)
                
                # TCP Connect scan
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_address, port))
                
                if result == 0:
                    # Port is open
                    service_name = self._get_service_name(port)
                    port_info = {
                        "port": port,
                        "protocol": "tcp",
                        "state": "open",
                        "service": service_name
                    }
                    results.append(port_info)
                    logger.info(f"Port {port}/tcp is open: {service_name}")
                
                sock.close()
                self.port_queue.task_done()
                
            except Exception as e:
                logger.debug(f"Error scanning port: {str(e)}")
                self.port_queue.task_done()
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for a standard port number"""
        common_services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 111: "rpcbind",
            135: "msrpc", 139: "netbios-ssn", 143: "imap",
            443: "https", 445: "microsoft-ds", 993: "imaps",
            995: "pop3s", 1723: "pptp", 3306: "mysql",
            3389: "ms-wbt-server", 5900: "vnc", 8080: "http-proxy",
            8443: "https-alt"
        }
        return common_services.get(port, "unknown")
    
    def _detect_service(self, ip_address: str, port_info: Dict) -> Dict:
        """
        Detect service details for an open port.
        
        Args:
            ip_address: Target IP address
            port_info: Port information dictionary
            
        Returns:
            Dictionary with service details
        """
        port = port_info["port"]
        service = port_info["service"]
        service_details = {
            "name": service,
            "product": "unknown",
            "version": "unknown",
            "extra_info": ""
        }
        
        try:
            # Try to gather banner information
            if service in ["http", "https"]:
                protocol = "https" if service == "https" else "http"
                response = requests.get(
                    f"{protocol}://{ip_address}:{port}/",
                    timeout=3,
                    verify=False
                )
                server = response.headers.get("Server", "")
                service_details["product"] = server
                service_details["extra_info"] = f"Status: {response.status_code}"
            
            elif service in ["ssh"]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip_address, port))
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                sock.close()
                service_details["product"] = banner
            
            # More service detection methods could be added here
            
        except Exception as e:
            logger.debug(f"Error detecting service on port {port}: {str(e)}")
        
        return service_details
    
    def _detect_os(self, ip_address: str) -> Dict:
        """
        Perform OS detection (simplified implementation).
        
        Args:
            ip_address: Target IP address
            
        Returns:
            Dictionary with OS detection results
        """
        os_info = {
            "type": "unknown",
            "vendor": "unknown",
            "confidence": 0
        }
        
        # This is a simplified OS detection based on TTL values
        try:
            # Use a simple ping to get TTL
            if os.name == "nt":  # Windows
                ping_cmd = f"ping -n 1 {ip_address}"
            else:  # Unix/Linux
                ping_cmd = f"ping -c 1 {ip_address}"
            
            result = subprocess.run(
                ping_cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Extract TTL from ping output
            output = result.stdout.decode()
            ttl_match = re.search(r"TTL=(\d+)", output, re.IGNORECASE)
            
            if ttl_match:
                ttl = int(ttl_match.group(1))
                
                # Very simplified OS fingerprinting based on initial TTL values
                if ttl <= 64:
                    os_info = {"type": "Linux/Unix", "vendor": "Various", "confidence": 60}
                elif ttl <= 128:
                    os_info = {"type": "Windows", "vendor": "Microsoft", "confidence": 60}
                elif ttl <= 255:
                    os_info = {"type": "Cisco/Network", "vendor": "Various", "confidence": 50}
        
        except Exception as e:
            logger.debug(f"Error detecting OS: {str(e)}")
        
        return os_info
    
    def _reverse_dns(self, ip_address: str) -> str:
        """Perform a reverse DNS lookup"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return hostname
        except (socket.herror, socket.gaierror):
            return ip_address
    
    def _traceroute(self, ip_address: str, max_hops: int = 10) -> List[Dict]:
        """
        Perform a simple traceroute.
        
        Args:
            ip_address: Target IP address
            max_hops: Maximum number of hops
            
        Returns:
            List of dictionaries with hop information
        """
        hops = []
        
        for ttl in range(1, max_hops + 1):
            hop_info = {"hop": ttl, "ip": None, "hostname": None, "rtt": None}
            
            try:
                # Create a UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                sock.settimeout(2)
                
                # Send a packet to an invalid port
                start_time = time.time()
                sock.sendto(b"", (ip_address, 33434))
                
                # Wait for a response
                try:
                    data, addr = sock.recvfrom(1024)
                    hop_info["ip"] = addr[0]
                    hop_info["rtt"] = round((time.time() - start_time) * 1000, 2)
                    
                    # Reverse DNS lookup
                    try:
                        hostname, _, _ = socket.gethostbyaddr(addr[0])
                        hop_info["hostname"] = hostname
                    except (socket.herror, socket.gaierror):
                        hop_info["hostname"] = addr[0]
                    
                except socket.timeout:
                    hop_info["ip"] = "*"
                    hop_info["hostname"] = "*"
                    hop_info["rtt"] = None
                
                sock.close()
                hops.append(hop_info)
                
                # Stop if we reached the destination
                if hop_info["ip"] == ip_address:
                    break
                
            except Exception as e:
                logger.debug(f"Error in traceroute at hop {ttl}: {str(e)}")
                hop_info["ip"] = "Error"
                hop_info["hostname"] = str(e)
                hops.append(hop_info)
        
        return hops


class VulnerabilityScanner:
    """Component for vulnerability scanning and assessment"""
    
    def __init__(self, parent: PenetrationTest):
        """
        Initialize the vulnerability scanner.
        
        Args:
            parent: Parent PenetrationTest instance
        """
        self.parent = parent
        self.target = parent.target
        self.vulnerabilities = []
        self.severity_levels = ["critical", "high", "medium", "low", "info"]
    
    def scan(self) -> List[Dict]:
        """Perform vulnerability scanning"""
        vulnerabilities = []
        
        # Check if we have network scan results
        network_results = self.parent.results.get("network", {})
        open_ports = network_results.get("open_ports", [])
        
        if not open_ports:
            logger.warning("No open ports found for vulnerability scanning")
            self.parent.results["vulnerabilities"] = vulnerabilities
            return vulnerabilities
        
        # Scan each open port for vulnerabilities
        for port_info in open_ports:
            port = port_info["port"]
            service = port_info["service"]
            
            logger.info(f"Scanning for vulnerabilities on port {port} ({service})")
            
            # Service-specific vulnerability checks
            if service == "http" or service == "https":
                web_vulns = self._check_web_vulnerabilities(port, service)
                vulnerabilities.extend(web_vulns)
            
            elif service == "ssh":
                ssh_vulns = self._check_ssh_vulnerabilities(port)
                vulnerabilities.extend(ssh_vulns)
            
            elif service == "ftp":
                ftp_vulns = self._check_ftp_vulnerabilities(port)
                vulnerabilities.extend(ftp_vulns)
            
            # Generic service checks
            generic_vulns = self._check_generic_vulnerabilities(port, service)
            vulnerabilities.extend(generic_vulns)
        
        # System vulnerability checks
        system_vulns = self._check_system_vulnerabilities()
        vulnerabilities.extend(system_vulns)
        
        # Save results
        self.parent.results["vulnerabilities"] = vulnerabilities
        return vulnerabilities
    
    def _check_web_vulnerabilities(self, port: int, service: str) -> List[Dict]:
        """Check for web-specific vulnerabilities"""
        vulnerabilities = []
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        protocol = "https" if service == "https" else "http"
        base_url = f"{protocol}://{ip_address}:{port}"
        
        try:
            # Check for server information disclosure
            response = requests.get(base_url, timeout=5, verify=False)
            server_header = response.headers.get("Server", "")
            
            if server_header and len(server_header) > 0:
                vulnerabilities.append({
                    "name": "Server Information Disclosure",
                    "description": f"The server is revealing its software and version: {server_header}",
                    "severity": "low",
                    "evidence": f"Server header: {server_header}",
                    "remediation": "Configure the web server to suppress version information in HTTP headers"
                })
            
            # Check for missing security headers
            security_headers = {
                "Strict-Transport-Security": "Missing HSTS header",
                "X-Frame-Options": "Missing X-Frame-Options header",
                "X-Content-Type-Options": "Missing X-Content-Type-Options header",
                "Content-Security-Policy": "Missing Content-Security-Policy header"
            }
            
            for header, issue in security_headers.items():
                if header not in response.headers:
                    vulnerabilities.append({
                        "name": issue,
                        "description": f"The {header} security header is not set",
                        "severity": "medium",
                        "evidence": f"Header not present in response",
                        "remediation": f"Configure the web server to include the {header} header"
                    })
            
            # Check for directory listing
            test_dirs = ["/images/", "/css/", "/js/", "/backup/", "/admin/"]
            for directory in test_dirs:
                try:
                    dir_url = f"{base_url}{directory}"
                    dir_response = requests.get(dir_url, timeout=3, verify=False)
                    
                    # Simple check for directory listing patterns
                    content = dir_response.text.lower()
                    if (dir_response.status_code == 200 and 
                        ("index of" in content or 
                         "<title>directory listing for" in content or
                         "parent directory" in content)):
                        
                        vulnerabilities.append({
                            "name": "Directory Listing Enabled",
                            "description": f"Directory listing is enabled at {directory}",
                            "severity": "medium",
                            "evidence": f"Directory listing detected at {dir_url}",
                            "remediation": "Disable directory listing in the web server configuration"
                        })
                
                except requests.RequestException:
                    pass
            
            # Simple check for common files
            test_files = [
                "/robots.txt", 
                "/.git/HEAD", 
                "/.env", 
                "/wp-config.php", 
                "/config.php",
                "/.htaccess",
                "/phpinfo.php"
            ]
            
            for file in test_files:
                try:
                    file_url = f"{base_url}{file}"
                    file_response = requests.get(file_url, timeout=3, verify=False)
                    
                    if file_response.status_code == 200:
                        vulnerabilities.append({
                            "name": "Sensitive File Exposure",
                            "description": f"Sensitive file {file} is accessible",
                            "severity": "medium",
                            "evidence": f"File accessible at {file_url}",
                            "remediation": f"Remove or restrict access to {file}"
                        })
                
                except requests.RequestException:
                    pass
            
        except Exception as e:
            logger.debug(f"Error checking web vulnerabilities: {str(e)}")
        
        return vulnerabilities
    
    def _check_ssh_vulnerabilities(self, port: int) -> List[Dict]:
        """Check for SSH-specific vulnerabilities"""
        vulnerabilities = []
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        
        try:
            # Connect to SSH to get banner
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip_address, port))
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            sock.close()
            
            # Check for outdated SSH versions
            ssh_version_match = re.search(r"SSH-(\d+\.\d+)-([^\s]+)", banner)
            if ssh_version_match:
                protocol_version = ssh_version_match.group(1)
                software_version = ssh_version_match.group(2)
                
                if protocol_version == "1.0" or protocol_version == "1":
                    vulnerabilities.append({
                        "name": "Outdated SSH Protocol",
                        "description": "SSH server is using the deprecated SSH v1 protocol",
                        "severity": "high",
                        "evidence": f"SSH banner: {banner}",
                        "remediation": "Configure SSH to use protocol version 2 only"
                    })
                
                # Check for known vulnerable SSH versions (simplified)
                vulnerable_versions = {
                    "OpenSSH": ["1.", "2.0", "2.1", "2.2", "2.3", "2.9", "3.0", "3.1", "4.0", "4.1", "4.2", "4.3"]
                }
                
                for vendor, versions in vulnerable_versions.items():
                    if vendor.lower() in software_version.lower():
                        for ver in versions:
                            if software_version.lower().startswith(ver.lower()):
                                vulnerabilities.append({
                                    "name": "Vulnerable SSH Version",
                                    "description": f"SSH server is running a potentially vulnerable version: {software_version}",
                                    "severity": "high",
                                    "evidence": f"SSH banner: {banner}",
                                    "remediation": "Upgrade to the latest SSH server version"
                                })
                                break
            
        except Exception as e:
            logger.debug(f"Error checking SSH vulnerabilities: {str(e)}")
        
        return vulnerabilities
    
    def _check_ftp_vulnerabilities(self, port: int) -> List[Dict]:
        """Check for FTP-specific vulnerabilities"""
        vulnerabilities = []
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        
        try:
            # Connect to FTP to get banner
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip_address, port))
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            sock.close()
            
            # Check for anonymous FTP access
            try:
                import ftplib
                ftp = ftplib.FTP()
                ftp.connect(ip_address, port, timeout=5)
                
                # Try anonymous login
                try:
                    ftp.login("anonymous", "anonymous@example.com")
                    vulnerabilities.append({
                        "name": "Anonymous FTP Access",
                        "description": "FTP server allows anonymous access",
                        "severity": "high",
                        "evidence": "Successfully logged in as anonymous user",
                        "remediation": "Disable anonymous FTP access or restrict it appropriately"
                    })
                    
                    # Check if we can write to the FTP server
                    try:
                        test_file = f"pentest-check-{random.randint(1000, 9999)}.txt"
                        ftp.storbinary(f"STOR {test_file}", 
                                      open(io.BytesIO(b"Penetration test check"), "rb"))
                        
                        vulnerabilities.append({
                            "name": "Anonymous FTP Write Access",
                            "description": "FTP server allows anonymous users to upload files",
                            "severity": "critical",
                            "evidence": f"Successfully uploaded test file {test_file}",
                            "remediation": "Disable anonymous FTP access or make it read-only"
                        })
                        
                        # Try to delete the test file
                        try:
                            ftp.delete(test_file)
                        except:
                            pass
                        
                    except:
                        # Read-only anonymous access
                        pass
                    
                    ftp.quit()
                    
                except ftplib.error_perm:
                    # Anonymous login failed
                    pass
                
            except Exception as e:
                logger.debug(f"Error checking anonymous FTP: {str(e)}")
            
            # Check for plain text FTP (not using FTPS)
            if not self._check_ftps_support(ip_address, port):
                vulnerabilities.append({
                    "name": "Plain Text FTP",
                    "description": "FTP server does not support encrypted connections (FTPS)",
                    "severity": "high",
                    "evidence": "FTP server does not support AUTH TLS/SSL",
                    "remediation": "Configure FTP server to support FTPS or replace with SFTP"
                })
            
        except Exception as e:
            logger.debug(f"Error checking FTP vulnerabilities: {str(e)}")
        
        return vulnerabilities
    
    def _check_ftps_support(self, ip_address: str, port: int) -> bool:
        """Check if FTP server supports FTPS (TLS/SSL)"""
        try:
            import ftplib
            ftp = ftplib.FTP()
            ftp.connect(ip_address, port, timeout=5)
            
            # Try to establish a secure connection
            try:
                ftp.sendcmd("AUTH TLS")
                ftp.quit()
                return True
            except ftplib.error_perm:
                try:
                    ftp.sendcmd("AUTH SSL")
                    ftp.quit()
                    return True
                except ftplib.error_perm:
                    ftp.quit()
                    return False
            
        except Exception:
            return False
    
    def _check_generic_vulnerabilities(self, port: int, service: str) -> List[Dict]:
        """Check for generic service vulnerabilities"""
        vulnerabilities = []
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        
        # Check for telnet service
        if service == "telnet":
            vulnerabilities.append({
                "name": "Telnet Service Enabled",
                "description": "Telnet service is running which transmits data in cleartext",
                "severity": "high",
                "evidence": f"Telnet service detected on port {port}",
                "remediation": "Replace Telnet with SSH or other encrypted alternatives"
            })
        
        # Check for unencrypted services
        unencrypted_services = {
            "http": "Use HTTPS instead of HTTP",
            "pop3": "Use POP3S (POP3 over SSL/TLS) instead",
            "imap": "Use IMAPS (IMAP over SSL/TLS) instead",
            "smtp": "Use SMTPS (SMTP over SSL/TLS) instead",
            "ftp": "Use SFTP or FTPS instead of plain FTP"
        }
        
        if service in unencrypted_services:
            vulnerabilities.append({
                "name": "Unencrypted Service",
                "description": f"Service {service} on port {port} transmits data without encryption",
                "severity": "medium",
                "evidence": f"Unencrypted {service} service detected on port {port}",
                "remediation": unencrypted_services[service]
            })
        
        return vulnerabilities
    
    def _check_system_vulnerabilities(self) -> List[Dict]:
        """Check for system-level vulnerabilities"""
        vulnerabilities = []
        os_info = self.parent.results.get("network", {}).get("os_detection", {})
        
        # Generic OS-based vulnerabilities
        os_type = os_info.get("type", "unknown")
        
        if "windows" in os_type.lower():
            vulnerabilities.append({
                "name": "Windows Operating System",
                "description": "The target appears to be running Windows",
                "severity": "info",
                "evidence": f"OS detection: {os_type}",
                "remediation": "Ensure Windows is fully patched and configured securely"
            })
            
            # Check for Windows SMB (port 445)
            smb_port = 445
            open_ports = self.parent.results.get("network", {}).get("open_ports", [])
            for port_info in open_ports:
                if port_info["port"] == smb_port:
                    vulnerabilities.append({
                        "name": "SMB Service Exposed",
                        "description": "Windows SMB service is exposed to the network",
                        "severity": "medium",
                        "evidence": f"SMB service detected on port {smb_port}",
                        "remediation": "Restrict SMB access with firewall rules if not needed externally"
                    })
        
        elif "linux" in os_type.lower() or "unix" in os_type.lower():
            vulnerabilities.append({
                "name": "Linux/Unix Operating System",
                "description": "The target appears to be running Linux or Unix",
                "severity": "info",
                "evidence": f"OS detection: {os_type}",
                "remediation": "Ensure the system is fully patched and configured securely"
            })
        
        return vulnerabilities


class WebApplicationScanner:
    """Component for web application security testing"""
    
    def __init__(self, parent: PenetrationTest):
        """
        Initialize the web application scanner.
        
        Args:
            parent: Parent PenetrationTest instance
        """
        self.parent = parent
        self.target = parent.target
        self.results = {
            "target_url": "",
            "issues": []
        }
    
    def scan(self) -> Dict:
        """Perform web application security scanning"""
        # Check if we have an HTTP service
        network_results = self.parent.results.get("network", {})
        ip_address = network_results.get("ip_address", self.target)
        
        # Find HTTP or HTTPS services
        web_services = []
        for port_info in network_results.get("open_ports", []):
            if port_info["service"] in ["http", "https"]:
                web_services.append({
                    "port": port_info["port"],
                    "service": port_info["service"]
                })
        
        if not web_services:
            logger.info("No web services found for scanning")
            self.parent.results["web"] = self.results
            return self.results
        
        # Set target URL to first web service
        service = web_services[0]["service"]
        port = web_services[0]["port"]
        target_url = f"{service}://{ip_address}:{port}"
        self.results["target_url"] = target_url
        
        logger.info(f"Starting web application scan on {target_url}")
        
        # Perform various web security checks
        self._check_ssl_security(target_url)
        self._crawl_website(target_url)
        self._check_common_vulnerabilities(target_url)
        
        # Save results
        self.parent.results["web"] = self.results
        return self.results
    
    def _check_ssl_security(self, url: str) -> None:
        """Check SSL/TLS security configuration"""
        if not url.startswith("https"):
            return
        
        hostname = url.split("://")[1].split(":")[0]
        
        try:
            # Get SSL certificate information
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    not_after = cert.get("notAfter", "")
                    if not_after:
                        expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        now = datetime.now()
                        days_until_expiry = (expiry_date - now).days
                        
                        if days_until_expiry < 0:
                            self.results["issues"].append({
                                "name": "Expired SSL Certificate",
                                "description": "The SSL certificate has expired",
                                "severity": "critical",
                                "evidence": f"Certificate expired on {not_after}",
                                "remediation": "Renew the SSL certificate immediately"
                            })
                        elif days_until_expiry < 30:
                            self.results["issues"].append({
                                "name": "SSL Certificate Expiring Soon",
                                "description": f"The SSL certificate will expire in {days_until_expiry} days",
                                "severity": "high",
                                "evidence": f"Certificate expires on {not_after}",
                                "remediation": "Renew the SSL certificate before it expires"
                            })
                    
                    # Check certificate subject
                    subject = dict(x[0] for x in cert.get("subject", []))
                    common_name = subject.get("commonName", "")
                    
                    if common_name != hostname and not (
                        common_name.startswith("*.") and 
                        hostname.endswith(common_name[1:])
                    ):
                        self.results["issues"].append({
                            "name": "SSL Certificate Hostname Mismatch",
                            "description": f"The SSL certificate is issued for {common_name}, not {hostname}",
                            "severity": "high",
                            "evidence": f"Certificate CN: {common_name}, Hostname: {hostname}",
                            "remediation": "Obtain a certificate valid for this hostname"
                        })
                    
                    # Check protocol version
                    version = ssock.version()
                    if version == "TLSv1" or version == "TLSv1.1":
                        self.results["issues"].append({
                            "name": "Outdated TLS Protocol",
                            "description": f"Server is using outdated {version} protocol",
                            "severity": "medium",
                            "evidence": f"TLS Version: {version}",
                            "remediation": "Configure server to use TLS 1.2 or 1.3 only"
                        })
        
        except Exception as e:
            logger.debug(f"Error checking SSL security: {str(e)}")
    
    def _crawl_website(self, url: str) -> List[str]:
        """
        Perform basic website crawling to discover pages.
        
        Args:
            url: Base URL to crawl
            
        Returns:
            List of discovered URLs
        """
        discovered_urls = set([url])
        urls_to_visit = [url]
        visited_urls = set()
        max_urls = 20  # Limit for the demonstration
        
        try:
            while urls_to_visit and len(visited_urls) < max_urls:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                
                logger.info(f"Crawling: {current_url}")
                
                try:
                    response = requests.get(current_url, timeout=5, verify=False)
                    visited_urls.add(current_url)
                    
                    # Parse HTML and extract links
                    if "text/html" in response.headers.get("Content-Type", ""):
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        for link in soup.find_all("a", href=True):
                            href = link["href"]
                            
                            # Normalize URL
                            if href.startswith("/"):
                                # Convert relative URL to absolute
                                parsed_url = urlparse(current_url)
                                absolute_url = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                            elif href.startswith("http"):
                                # Already absolute URL
                                absolute_url = href
                            else:
                                # Relative URL (not starting with /)
                                parsed_url = urlparse(current_url)
                                path = os.path.dirname(parsed_url.path)
                                absolute_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}/{href}"
                            
                            # Only add URLs from the same domain
                            if urlparse(absolute_url).netloc == urlparse(url).netloc:
                                discovered_urls.add(absolute_url)
                                if absolute_url not in visited_urls:
                                    urls_to_visit.append(absolute_url)
                
                except requests.RequestException as e:
                    logger.debug(f"Error crawling {current_url}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error during website crawling: {str(e)}")
        
        # Save discovered URLs to results
        self.results["crawled_urls"] = list(discovered_urls)
        return list(discovered_urls)
    
    def _check_common_vulnerabilities(self, url: str) -> None:
        """Check for common web vulnerabilities"""
        # Check for SQL injection
        self._check_sql_injection(url)
        
        # Check for Cross-Site Scripting (XSS)
        self._check_xss(url)
        
        # Check for CSRF
        self._check_csrf(url)
        
        # Check for sensitive information exposure
        self._check_information_exposure(url)
    
    def _check_sql_injection(self, base_url: str) -> None:
        """
        Check for potential SQL injection vulnerabilities.
        
        Args:
            base_url: Base URL of the web application
        """
        # Simple SQL injection check on discovered pages with parameters
        discovered_urls = self.results.get("crawled_urls", [base_url])
        
        # SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "\" OR \"1\"=\"1",
            "1' OR '1'='1' --",
            "1\" OR \"1\"=\"1\" --",
            "' OR 1=1 --",
            "\" OR 1=1 --",
            "' OR '1'='1' /*",
            "\" OR \"1\"=\"1\" /*"
        ]
        
        # Error patterns indicating SQL injection vulnerabilities
        error_patterns = [
            "SQL syntax",
            "mysql_fetch",
            "ORA-",
            "PostgreSQL",
            "SQLite",
            "Incorrect syntax",
            "Unclosed quotation mark",
            "mysql_query",
            "pg_query"
        ]
        
        for url in discovered_urls:
            # Check if URL has parameters
            parsed_url = urlparse(url)
            if parsed_url.query:
                # Extract parameters
                params = parse_qs(parsed_url.query)
                
                for param_name, param_values in params.items():
                    original_value = param_values[0]
                    
                    for payload in payloads:
                        # Create modified URL with SQL injection payload
                        modified_params = params.copy()
                        modified_params[param_name] = [payload]
                        
                        modified_query = urlencode(modified_params, doseq=True)
                        modified_url = urlunparse((
                            parsed_url.scheme,
                            parsed_url.netloc,
                            parsed_url.path,
                            parsed_url.params,
                            modified_query,
                            parsed_url.fragment
                        ))
                        
                        try:
                            response = requests.get(modified_url, timeout=5, verify=False)
                            
                            # Check for error messages indicating SQL injection
                            for pattern in error_patterns:
                                if pattern.lower() in response.text.lower():
                                    self.results["issues"].append({
                                        "name": "Potential SQL Injection",
                                        "description": f"Parameter {param_name} may be vulnerable to SQL injection",
                                        "severity": "critical",
                                        "evidence": f"SQL error pattern '{pattern}' found in response",
                                        "url": url,
                                        "parameter": param_name,
                                        "payload": payload,
                                        "remediation": "Use parameterized queries or prepared statements"
                                    })
                                    break
                        
                        except requests.RequestException as e:
                            logger.debug(f"Error testing SQL injection: {str(e)}")
    
    def _check_xss(self, base_url: str) -> None:
        """
        Check for potential Cross-Site Scripting (XSS) vulnerabilities.
        
        Args:
            base_url: Base URL of the web application
        """
        # Simple XSS check on discovered pages with parameters
        discovered_urls = self.results.get("crawled_urls", [base_url])
        
        # XSS test payloads
        payloads = [
            "<script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "'><script>alert(1)</script>",
            "><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "\"><img src=x onerror=alert(1)>",
            "'><img src=x onerror=alert(1)>"
        ]
        
        for url in discovered_urls:
            # Check if URL has parameters
            parsed_url = urlparse(url)
            if parsed_url.query:
                # Extract parameters
                params = parse_qs(parsed_url.query)
                
                for param_name, param_values in params.items():
                    original_value = param_values[0]
                    
                    for payload in payloads:
                        # Create modified URL with XSS payload
                        modified_params = params.copy()
                        modified_params[param_name] = [payload]
                        
                        modified_query = urlencode(modified_params, doseq=True)
                        modified_url = urlunparse((
                            parsed_url.scheme,
                            parsed_url.netloc,
                            parsed_url.path,
                            parsed_url.params,
                            modified_query,
                            parsed_url.fragment
                        ))
                        
                        try:
                            response = requests.get(modified_url, timeout=5, verify=False)
                            
                            # Check if the payload is reflected in the response
                            if payload in response.text:
                                self.results["issues"].append({
                                    "name": "Potential Cross-Site Scripting (XSS)",
                                    "description": f"Parameter {param_name} may be vulnerable to XSS",
                                    "severity": "high",
                                    "evidence": f"XSS payload was reflected in the response",
                                    "url": url,
                                    "parameter": param_name,
                                    "payload": payload,
                                    "remediation": "Implement proper input validation and output encoding"
                                })
                                break
                        
                        except requests.RequestException as e:
                            logger.debug(f"Error testing XSS: {str(e)}")
    
    def _check_csrf(self, base_url: str) -> None:
        """
        Check for Cross-Site Request Forgery (CSRF) protection.
        
        Args:
            base_url: Base URL of the web application
        """
        # Find forms on the website
        discovered_urls = self.results.get("crawled_urls", [base_url])
        
        for url in discovered_urls:
            try:
                response = requests.get(url, timeout=5, verify=False)
                
                if "text/html" in response.headers.get("Content-Type", ""):
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Find forms
                    forms = soup.find_all("form")
                    for form in forms:
                        # Check for CSRF token
                        csrf_found = False
                        
                        # Common CSRF token field names
                        csrf_fields = [
                            "csrf", "csrf_token", "_csrf", "token", "authenticity_token",
                            "xsrf", "xsrf_token", "_xsrf", "csrfmiddlewaretoken"
                        ]
                        
                        for field in form.find_all("input"):
                            field_name = field.get("name", "").lower()
                            
                            if any(token_name in field_name for token_name in csrf_fields):
                                csrf_found = True
                                break
                        
                        if not csrf_found and form.get("method", "").lower() == "post":
                            self.results["issues"].append({
                                "name": "Missing CSRF Protection",
                                "description": "A form was found without CSRF protection",
                                "severity": "medium",
                                "evidence": f"Form action: {form.get('action', 'unknown')}",
                                "url": url,
                                "remediation": "Implement CSRF tokens for all POST forms"
                            })
            
            except requests.RequestException as e:
                logger.debug(f"Error checking CSRF: {str(e)}")
    
    def _check_information_exposure(self, base_url: str) -> None:
        """
        Check for sensitive information exposure.
        
        Args:
            base_url: Base URL of the web application
        """
        # Check for common sensitive files
        sensitive_files = [
            "/.git/config",
            "/.env",
            "/config.php",
            "/wp-config.php",
            "/config.js",
            "/config.yml",
            "/config.xml",
            "/credentials.txt",
            "/database.yml",
            "/settings.py",
            "/.htpasswd",
            "/.bash_history",
            "/server-status",
            "/phpinfo.php"
        ]
        
        parsed_url = urlparse(base_url)
        base = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for file_path in sensitive_files:
            url = f"{base}{file_path}"
            
            try:
                response = requests.get(url, timeout=3, verify=False)
                
                if response.status_code == 200:
                    # Check response size to filter out error pages
                    if len(response.text) > 0:
                        self.results["issues"].append({
                            "name": "Sensitive Information Exposure",
                            "description": f"Sensitive file {file_path} is accessible",
                            "severity": "high",
                            "evidence": f"File accessible at {url}",
                            "url": url,
                            "remediation": "Restrict access to sensitive files or remove them"
                        })
            
            except requests.RequestException:
                pass
        
        # Check for information disclosure in HTTP headers
        try:
            response = requests.get(base_url, timeout=5, verify=False)
            
            sensitive_headers = {
                "X-Powered-By": "Technology disclosure",
                "Server": "Server software disclosure",
                "X-AspNet-Version": ".NET version disclosure",
                "X-AspNetMvc-Version": "ASP.NET MVC version disclosure"
            }
            
            for header, description in sensitive_headers.items():
                if header in response.headers:
                    self.results["issues"].append({
                        "name": "Information Disclosure in HTTP Headers",
                        "description": f"{description}: {header}: {response.headers[header]}",
                        "severity": "low",
                        "evidence": f"{header}: {response.headers[header]}",
                        "url": base_url,
                        "remediation": "Configure web server to remove version information from HTTP headers"
                    })
        
        except requests.RequestException:
            pass


class PasswordSecurityTester:
    """Component for testing password security"""
    
    def __init__(self, parent: PenetrationTest):
        """
        Initialize the password security tester.
        
        Args:
            parent: Parent PenetrationTest instance
        """
        self.parent = parent
        self.target = parent.target
        self.results = {
            "issues": []
        }
        
        # Commonly used default credentials
        self.default_credentials = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "administrator", "password": "administrator"},
            {"username": "root", "password": "root"},
            {"username": "root", "password": "toor"},
            {"username": "user", "password": "user"},
            {"username": "guest", "password": "guest"}
        ]
    
    def test(self) -> Dict:
        """Perform password security testing"""
        # Check for default credentials on various services
        network_results = self.parent.results.get("network", {})
        open_ports = network_results.get("open_ports", [])
        
        for port_info in open_ports:
            port = port_info["port"]
            service = port_info["service"]
            
            if service == "ssh":
                self._test_ssh_passwords(port)
            elif service == "ftp":
                self._test_ftp_passwords(port)
            elif service in ["http", "https"]:
                self._test_web_passwords(port, service)
        
        # Save results
        self.parent.results["password"] = self.results
        return self.results
    
    def _test_ssh_passwords(self, port: int) -> None:
        """
        Test for weak SSH passwords.
        
        Args:
            port: SSH port number
        """
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        
        logger.info(f"Testing SSH passwords on {ip_address}:{port}")
        
        # In a real implementation, this would test SSH credentials
        # For demonstration purposes, we'll simulate the check
        
        # Warning about brute force instead of actually attempting it
        self.results["issues"].append({
            "name": "SSH Password Brute Force Check",
            "description": "SSH services should be tested for weak or default credentials",
            "severity": "info",
            "evidence": "SSH service identified on port " + str(port),
            "remediation": "Implement strong password policies and consider key-based authentication"
        })
    
    def _test_ftp_passwords(self, port: int) -> None:
        """
        Test for weak FTP passwords.
        
        Args:
            port: FTP port number
        """
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        
        logger.info(f"Testing FTP passwords on {ip_address}:{port}")
        
        # Try anonymous login
        try:
            import ftplib
            ftp = ftplib.FTP()
            ftp.connect(ip_address, port, timeout=5)
            
            try:
                ftp.login("anonymous", "anonymous@example.com")
                self.results["issues"].append({
                    "name": "Anonymous FTP Access",
                    "description": "FTP server allows anonymous access",
                    "severity": "high",
                    "evidence": "Successfully logged in as anonymous user",
                    "remediation": "Disable anonymous FTP access or restrict it appropriately"
                })
                ftp.quit()
            except ftplib.error_perm:
                # Anonymous login failed, which is good
                ftp.quit()
                
                # In a real implementation, this would test common FTP credentials
                # For demonstration purposes, we'll simulate the check
                self.results["issues"].append({
                    "name": "FTP Password Brute Force Check",
                    "description": "FTP services should be tested for weak or default credentials",
                    "severity": "info",
                    "evidence": "FTP service identified on port " + str(port),
                    "remediation": "Implement strong password policies for FTP accounts"
                })
            
        except Exception as e:
            logger.debug(f"Error testing FTP passwords: {str(e)}")
    
    def _test_web_passwords(self, port: int, service: str) -> None:
        """
        Test for weak web application passwords.
        
        Args:
            port: Web server port number
            service: Service type (http or https)
        """
        ip_address = self.parent.results.get("network", {}).get("ip_address", self.target)
        url = f"{service}://{ip_address}:{port}"
        
        logger.info(f"Testing web passwords on {url}")
        
        # Find login forms
        login_urls = self._find_login_forms(url)
        
        if login_urls:
            # In a real implementation, this would test web credentials
            # For demonstration purposes, we'll simulate the check
            for login_url in login_urls:
                self.results["issues"].append({
                    "name": "Web Application Login Found",
                    "description": "Web login form should be tested for weak or default credentials",
                    "severity": "info",
                    "evidence": f"Login form found at {login_url}",
                    "remediation": "Implement strong password policies, account lockout, and multi-factor authentication"
                })
    
    def _find_login_forms(self, base_url: str) -> List[str]:
        """
        Find login forms on the website.
        
        Args:
            base_url: Base URL of the web application
            
        Returns:
            List of URLs with login forms
        """
        login_urls = []
        crawl_paths = [
            "/", "/login", "/admin", "/administrator", "/wp-login.php",
            "/user/login", "/sign-in", "/signin", "/account/login",
            "/auth/login", "/admin/login", "/wp-admin", "/control-panel",
            "/cp", "/portal", "/dashboard", "/backend"
        ]
        
        for path in crawl_paths:
            url = f"{base_url.rstrip('/')}{path}"
            
            try:
                response = requests.get(url, timeout=5, verify=False)
                
                if response.status_code == 200 and "text/html" in response.headers.get("Content-Type", ""):
                    content = response.text.lower()
                    
                    # Check if this looks like a login page
                    login_indicators = [
                        "login", "log in", "sign in", "signin", "username", "password",
                        "user name", "email", "authentication", "auth", "credentials"
                    ]
                    
                    if any(indicator in content for indicator in login_indicators):
                        # Check for form elements
                        soup = BeautifulSoup(response.text, "html.parser")
                        forms = soup.find_all("form")
                        
                        for form in forms:
                            # Check if form has password field
                            has_password = any(
                                input_tag.get("type") == "password" 
                                for input_tag in form.find_all("input")
                            )
                            
                            if has_password:
                                login_urls.append(url)
                                break
            
            except requests.RequestException:
                pass
        
        return login_urls


class ReportGenerator:
    """Component for generating penetration test reports"""
    
    def __init__(self, parent: PenetrationTest):
        """
        Initialize the report generator.
        
        Args:
            parent: Parent PenetrationTest instance
        """
        self.parent = parent
        self.results = parent.results
    
    def generate(self) -> None:
        """Generate penetration test report"""
        output_dir = self.parent.output_dir
        target = self.parent.target
        
        # Generate JSON report
        json_file = os.path.join(output_dir, f"pentest_{target}_{int(time.time())}.json")
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"JSON report saved to {json_file}")
        
        # Generate HTML report
        html_file = os.path.join(output_dir, f"pentest_{target}_{int(time.time())}.html")
        self._generate_html_report(html_file)
        
        logger.info(f"HTML report saved to {html_file}")
    
    def _generate_html_report(self, filename: str) -> None:
        """
        Generate an HTML report.
        
        Args:
            filename: Output filename
        """
        # Create a basic HTML report
        target = self.results["metadata"]["target"]
        start_time = self.results["metadata"]["start_time"]
        finish_time = self.results["metadata"].get("finish_time", "N/A")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Penetration Test Report: {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3, h4 {{ color: #2c3e50; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background-color: #34495e; color: white; padding: 20px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
        .footer {{ margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .severity-critical {{ color: #fff; background-color: #e74c3c; padding: 5px 10px; border-radius: 3px; }}
        .severity-high {{ color: #fff; background-color: #e67e22; padding: 5px 10px; border-radius: 3px; }}
        .severity-medium {{ color: #fff; background-color: #f39c12; padding: 5px 10px; border-radius: 3px; }}
        .severity-low {{ color: #fff; background-color: #3498db; padding: 5px 10px; border-radius: 3px; }}
        .severity-info {{ color: #fff; background-color: #2ecc71; padding: 5px 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Penetration Test Report</h1>
            <p>Target: {target}</p>
            <p>Start Time: {start_time}</p>
            <p>Finish Time: {finish_time}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This report presents the findings of a penetration test conducted against {target}.</p>
            
            <h3>Key Findings</h3>
            <ul>
"""
        
        # Summary counts
        summary = self.results.get("summary", {})
        vuln_counts = summary.get("vulnerabilities", {})
        
        if vuln_counts.get("critical", 0) > 0:
            html += f"<li><strong>{vuln_counts['critical']}</strong> critical vulnerabilities</li>\n"
        if vuln_counts.get("high", 0) > 0:
            html += f"<li><strong>{vuln_counts['high']}</strong> high severity vulnerabilities</li>\n"
        if vuln_counts.get("medium", 0) > 0:
            html += f"<li><strong>{vuln_counts['medium']}</strong> medium severity vulnerabilities</li>\n"
        if vuln_counts.get("low", 0) > 0:
            html += f"<li><strong>{vuln_counts['low']}</strong> low severity vulnerabilities</li>\n"
        if vuln_counts.get("info", 0) > 0:
            html += f"<li><strong>{vuln_counts['info']}</strong> informational findings</li>\n"
        
        html += f"""            </ul>
        </div>
        
        <div class="section">
            <h2>Network Scan Results</h2>
"""
        
        # Network results
        network = self.results.get("network", {})
        ip_address = network.get("ip_address", "N/A")
        hostname = network.get("hostname", "N/A")
        
        html += f"""            <p><strong>IP Address:</strong> {ip_address}</p>
            <p><strong>Hostname:</strong> {hostname}</p>
            
            <h3>Open Ports</h3>
            <table>
                <tr>
                    <th>Port</th>
                    <th>Protocol</th>
                    <th>Service</th>
                    <th>State</th>
                </tr>
"""
        
        for port in network.get("open_ports", []):
            html += f"""                <tr>
                    <td>{port.get('port', 'N/A')}</td>
                    <td>{port.get('protocol', 'N/A')}</td>
                    <td>{port.get('service', 'N/A')}</td>
                    <td>{port.get('state', 'N/A')}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
        
        <div class="section">
            <h2>Vulnerabilities</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Severity</th>
                    <th>Description</th>
                    <th>Remediation</th>
                </tr>
"""
        
        # Vulnerabilities
        vulnerabilities = self.results.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info").lower()
            html += f"""                <tr>
                    <td>{vuln.get('name', 'N/A')}</td>
                    <td><span class="severity-{severity}">{severity.upper()}</span></td>
                    <td>{vuln.get('description', 'N/A')}</td>
                    <td>{vuln.get('remediation', 'N/A')}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
        
        <div class="section">
            <h2>Web Application Issues</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Severity</th>
                    <th>Description</th>
                    <th>Remediation</th>
                </tr>
"""
        
        # Web issues
        web = self.results.get("web", {})
        for issue in web.get("issues", []):
            severity = issue.get("severity", "info").lower()
            html += f"""                <tr>
                    <td>{issue.get('name', 'N/A')}</td>
                    <td><span class="severity-{severity}">{severity.upper()}</span></td>
                    <td>{issue.get('description', 'N/A')}</td>
                    <td>{issue.get('remediation', 'N/A')}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
        
        <div class="section">
            <h2>Password Security Issues</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Severity</th>
                    <th>Description</th>
                    <th>Remediation</th>
                </tr>
"""
        
        # Password issues
        password = self.results.get("password", {})
        for issue in password.get("issues", []):
            severity = issue.get("severity", "info").lower()
            html += f"""                <tr>
                    <td>{issue.get('name', 'N/A')}</td>
                    <td><span class="severity-{severity}">{severity.upper()}</span></td>
                    <td>{issue.get('description', 'N/A')}</td>
                    <td>{issue.get('remediation', 'N/A')}</td>
                </tr>
"""
        
        html += """            </table>
        </div>
        
        <div class="footer">
            <p>This report was generated by the Python Penetration Testing Framework</p>
            <p>For educational and authorized security testing purposes only</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write HTML to file
        with open(filename, "w") as f:
            f.write(html)


def main():
    """Main function to run the penetration testing framework"""
    parser = argparse.ArgumentParser(description="Python Penetration Testing Framework")
    parser.add_argument("target", help="Target IP address, hostname, or URL")
    parser.add_argument("-o", "--output", default="results", help="Output directory for reports")
    parser.add_argument("-v", "--verbosity", type=int, choices=[1, 2, 3], default=1, 
                       help="Verbosity level (1-3)")
    
    args = parser.parse_args()
    
    # Suppress InsecureRequestWarning for HTTPS connections
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Create and run the penetration test
    pentest = PenetrationTest(args.target, args.output, args.verbosity)
    results = pentest.run_full_scan()
    
    logger.info(f"Penetration test completed. Results saved to {args.output} directory.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())