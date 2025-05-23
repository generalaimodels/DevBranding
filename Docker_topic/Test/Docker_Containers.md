# Docker Containers Basics

## What are Containers?

Containers are lightweight, standalone, executable software packages that include everything needed to run an application: code, runtime, system tools, libraries, and settings. They provide isolation from the environment and from other containers.

Key characteristics:
- **Isolation**: Uses kernel namespaces and cgroups to isolate processes
- **Lightweight**: Share the host OS kernel rather than running a complete OS
- **Portable**: Run consistently across different environments
- **Efficient**: Consume fewer resources than virtual machines

Architecture components:
- **Container runtime**: Implementation of container technology (containerd, CRI-O)
- **Images**: Read-only templates with application code and dependencies
- **Containerization layer**: Handles isolation via Linux namespaces and cgroups

## Container Lifecycle

1. **Create**: Container is created from an image
2. **Start**: Container processes begin execution
3. **Running**: Container is actively executing
4. **Paused**: Container processes are temporarily suspended
5. **Stopped**: Container processes are terminated but configuration/files remain
6. **Removed**: Container is deleted permanently

## Basic Container Commands

### `docker ps`: List Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Show only container IDs
docker ps -q

# Show container sizes
docker ps -s

# Custom format output
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
```

### `docker run`: Create and Run Containers

```bash
# Basic syntax
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]

# Run container in detached mode
docker run -d nginx

# Run with port mapping
docker run -p 8080:80 nginx

# Run with volume mount
docker run -v /host/path:/container/path nginx

# Run with environment variables
docker run -e VAR=value nginx

# Run with resource constraints
docker run --memory=512m --cpus=0.5 nginx

# Run with container name
docker run --name my-container nginx
```

## Advanced Container Commands

### Container Management

```bash
# Start stopped container
docker start CONTAINER

# Stop running container
docker stop CONTAINER

# Restart container
docker restart CONTAINER

# Pause container processes
docker pause CONTAINER

# Unpause container processes
docker unpause CONTAINER

# Kill container (SIGKILL)
docker kill CONTAINER

# Rename container
docker rename OLD_NAME NEW_NAME

# Update container configuration
docker update --cpus 0.8 --memory 1G CONTAINER
```

### Container Inspection

```bash
# View container logs
docker logs CONTAINER

# Follow log output
docker logs -f CONTAINER

# Show container details
docker inspect CONTAINER

# Show container resource usage stats
docker stats CONTAINER

# List processes running in container
docker top CONTAINER

# Run command inside running container
docker exec -it CONTAINER COMMAND

# Get container IP address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' CONTAINER
```

### Container Networking

```bash
# Connect container to network
docker network connect NETWORK CONTAINER

# Disconnect container from network
docker network disconnect NETWORK CONTAINER

# Create container with specific network
docker run --network=NETWORK IMAGE

# Publish all exposed ports to random ports
docker run -P IMAGE

# Link containers (legacy)
docker run --link OTHER_CONTAINER:ALIAS IMAGE
```

### Container Cleanup

```bash
# Remove container
docker rm CONTAINER

# Force remove running container
docker rm -f CONTAINER

# Remove all stopped containers
docker container prune

# Remove container when it exits
docker run --rm IMAGE

# Remove all containers (caution!)
docker rm -f $(docker ps -aq)
```

### Resource Controls

```bash
# Set memory limits
docker run --memory=1g --memory-swap=2g IMAGE

# Set CPU limits
docker run --cpus=0.5 --cpu-shares=512 IMAGE

# Set ulimits
docker run --ulimit nofile=1024:1024 IMAGE

# Set restart policy
docker run --restart=always IMAGE

# Set storage options
docker run --storage-opt size=10G IMAGE
```
