# Creating Docker Images

## Introduction to Dockerfile
A Dockerfile is a text file containing instructions to build a Docker image. It uses a simple, declarative syntax to automate the image creation process in a reproducible way.

## Core Dockerfile Directives

### FROM
```
FROM <image>[:<tag>] [AS <name>]
```
- **Purpose**: Specifies base image to start from
- **Examples**: `FROM ubuntu:20.04`, `FROM node:14-alpine`
- **Key points**: 
  - Must be first non-comment instruction
  - Can use `scratch` for empty base image
  - Multiple FROM statements enable multi-stage builds

### RUN
```
RUN <command>
RUN ["executable", "param1", "param2"]
```
- **Purpose**: Executes commands in a new layer on top of current image
- **Shell form**: `RUN apt-get update && apt-get install -y nginx`
- **Exec form**: `RUN ["apt-get", "install", "-y", "nginx"]`
- **Best practices**:
  - Chain commands with `&&` to reduce layers
  - Clean up unnecessary files in same layer

### COPY
```
COPY <src> <dest>
COPY ["<src>", "<dest>"]
```
- **Purpose**: Copies files/directories from build context to image
- **Examples**: `COPY ./app /app`, `COPY package.json .`
- **Key points**:
  - Cannot copy files outside build context
  - More predictable than ADD (no auto-extraction)
  - Use `--chown=user:group` for file ownership

### CMD
```
CMD ["executable", "param1", "param2"]
CMD command param1 param2
CMD ["param1", "param2"]  # as default parameters to ENTRYPOINT
```
- **Purpose**: Provides default command for container execution
- **Key points**:
  - Only one CMD effective (last one wins)
  - Can be overridden at container runtime
  - Exec form preferred for consistent behavior

### ENTRYPOINT
```
ENTRYPOINT ["executable", "param1", "param2"]
ENTRYPOINT command param1 param2
```
- **Purpose**: Configures container to run as executable
- **Key points**:
  - Not easily overridden (requires --entrypoint flag)
  - CMD provides default arguments to ENTRYPOINT
  - Exec form recommended for signal handling

## Relationship Between CMD and ENTRYPOINT

| | No ENTRYPOINT | ENTRYPOINT exec_entry p1_entry | ENTRYPOINT ["exec_entry", "p1_entry"] |
|---|---|---|---|
| No CMD | Error, no command | /bin/sh -c exec_entry p1_entry | exec_entry p1_entry |
| CMD ["exec_cmd", "p1_cmd"] | exec_cmd p1_cmd | /bin/sh -c exec_entry p1_entry | exec_entry p1_entry exec_cmd p1_cmd |
| CMD ["p1_cmd", "p2_cmd"] | p1_cmd p2_cmd | /bin/sh -c exec_entry p1_entry | exec_entry p1_entry p1_cmd p2_cmd |
| CMD exec_cmd p1_cmd | /bin/sh -c exec_cmd p1_cmd | /bin/sh -c exec_entry p1_entry | exec_entry p1_entry /bin/sh -c exec_cmd p1_cmd |

## Image Building Process

### Basic Build Command
```
docker build -t name:tag .
```

### Build Context
- Directory containing Dockerfile
- All files referenced by COPY/ADD must be in context
- Use .dockerignore to exclude unnecessary files

### Layering Mechanics
- Each instruction creates a layer
- Layers are cached for faster rebuilds
- Only changed layers and subsequent ones are rebuilt

## Best Practices

### Layer Optimization
- Minimize layer count by combining related operations
- Order instructions by change frequency (least frequent first)
- Use multi-stage builds to reduce final image size

### Security Considerations
- Use specific tags instead of latest
- Remove development tools and build dependencies
- Run as non-root user with minimal privileges
- Scan images for vulnerabilities

### Dockerfile Example
```dockerfile
# Base image
FROM node:16-alpine AS build

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY src/ ./src/

# Build application
RUN npm run build

# Production image
FROM node:16-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy from build stage
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/dist ./dist

# Switch to non-root user
USER appuser

# Define container startup
ENTRYPOINT ["node"]
CMD ["dist/main.js"]

# Metadata
LABEL maintainer="developer@example.com"
LABEL version="1.0"
```

