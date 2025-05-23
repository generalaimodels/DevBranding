# Docker Installation and Setup Guide

## Introduction

Docker is a platform that enables developers to build, share, and run applications in containers. This guide covers Docker installation and setup on Windows, Linux, and Mac systems.

## Windows Installation

### System Requirements

- Windows 10 64-bit: Pro, Enterprise, or Education (Build 16299 or later)
- Windows 11 64-bit
- 4GB RAM minimum
- BIOS-level hardware virtualization support enabled

### Installation Steps

1. **Download Docker Desktop**
   ```
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   ```

2. **Install Docker Desktop**
   - Run the installer with administrative privileges
   - Enable Hyper-V Windows features when prompted
   - Click "OK" to start installation

3. **Start Docker Desktop**
   ```
   Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
   ```

4. **Verify Installation**
   ```powershell
   docker --version
   docker run hello-world
   ```

## Linux Installation

### Ubuntu/Debian

1. **Update package index**
   ```bash
   sudo apt-get update
   ```

2. **Install prerequisites**
   ```bash
   sudo apt-get install ca-certificates curl gnupg lsb-release
   ```

3. **Add Docker's official GPG key**
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```

4. **Setup repository**
   ```bash
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. **Install Docker Engine**
   ```bash
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

6. **Verify installation**
   ```bash
   sudo docker run hello-world
   ```

### CentOS/RHEL

1. **Install prerequisites**
   ```bash
   sudo yum install -y yum-utils
   ```

2. **Add Docker repository**
   ```bash
   sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   ```

3. **Install Docker Engine**
   ```bash
   sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

4. **Start and enable Docker service**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

5. **Verify installation**
   ```bash
   sudo docker run hello-world
   ```

## macOS Installation

### System Requirements

- macOS 11 (Big Sur) or newer
- At least 4GB RAM
- Intel or Apple Silicon processor

### Installation Steps

1. **Download Docker Desktop for Mac**
   ```
   https://desktop.docker.com/mac/main/amd64/Docker.dmg
   ```
   For Apple Silicon:
   ```
   https://desktop.docker.com/mac/main/arm64/Docker.dmg
   ```

2. **Install Docker Desktop**
   - Open the downloaded .dmg file
   - Drag Docker.app to the Applications folder
   - Open Docker from Applications

3. **Verify installation**
   ```bash
   docker --version
   docker run hello-world
   ```

## Post-Installation Setup

### Configure Non-Root User Access (Linux)

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

### Configure Docker to Start on Boot

**Windows:**
- Docker Desktop starts automatically by default
- To disable: Docker Desktop > Settings > General > Uncheck "Start Docker Desktop when you log in"

**Linux:**
```bash
sudo systemctl enable docker
```

**macOS:**
- Docker Desktop starts automatically by default
- To disable: Docker Desktop > Preferences > General > Uncheck "Start Docker when you log in"

### Basic Configuration

1. **Adjust Resource Allocation (Docker Desktop)**
   - Open Docker Desktop > Settings/Preferences > Resources
   - Adjust CPU, memory, and disk limits according to your system capabilities

2. **Configure Docker Daemon (Linux)**
   ```bash
   sudo nano /etc/docker/daemon.json
   ```
   Example configuration:
   ```json
   {
     "default-address-pools": [
       {"base":"172.17.0.0/16","size":24}
     ],
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "10m",
       "max-file": "3"
     }
   }
   ```
   Apply configuration:
   ```bash
   sudo systemctl restart docker
   ```

## Verification Commands

Test your Docker installation with these commands:

```bash
# Check Docker version
docker --version

# View detailed Docker info
docker info

# Run test container
docker run hello-world

# List running containers
docker ps

# List all containers
docker ps -a

# List downloaded images
docker images
```
