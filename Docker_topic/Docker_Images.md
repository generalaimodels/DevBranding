# Docker Images Basics

## What are Docker Images?

Docker images are read-only templates containing application code, libraries, dependencies, tools, and other files needed to run an application. They serve as the blueprint for creating containers. Key attributes:

- **Immutable**: Once created, cannot be modified (create new image instead)
- **Layered**: Composed of multiple filesystem layers stacked together
- **Portable**: Same image runs consistently across any Docker environment
- **Self-contained**: Includes everything needed to run the application

## Image Layers

Docker images utilize a layered architecture leveraging a union filesystem:

- **Base Layer**: Usually a minimal OS like Alpine, Debian, or Ubuntu
- **Additional Layers**: Each instruction in Dockerfile creates a new layer
- **Layer Caching**: Unchanged layers are reused between builds for efficiency
- **Copy-on-Write**: Container runtime adds a writable layer on top of read-only image layers
- **Sharing**: Multiple containers can share the same underlying image layers

## Docker Images Command

The `docker images` command displays locally available images:

```bash
docker images [OPTIONS] [REPOSITORY[:TAG]]
```

Common options:
- `--all, -a`: Show all images including intermediates
- `--digests`: Show digests
- `--filter, -f`: Filter output based on conditions
- `--format`: Format output using Go template
- `--no-trunc`: Don't truncate output
- `--quiet, -q`: Only show image IDs

Example output:
```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
nginx               latest              a6eb2c7da49a        2 weeks ago         133MB
ubuntu              20.04               1318b700e415        3 weeks ago         72.8MB
```

## Advanced Image Commands

### Inspecting Images
```bash
# Detailed image metadata
docker inspect [IMAGE]

# View image layer history
docker history [IMAGE]
```

### Image Management
```bash
# Build image from Dockerfile
docker build -t name:tag .

# Tag an existing image
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]

# Remove image(s)
docker rmi [OPTIONS] IMAGE [IMAGE...]

# Remove unused images
docker image prune [OPTIONS]
```

### Registry Operations
```bash
# Pull image from registry
docker pull [OPTIONS] NAME[:TAG|@DIGEST]

# Push image to registry
docker push [OPTIONS] NAME[:TAG]

# Save image to tar archive
docker save -o filename.tar IMAGE[:TAG]

# Load image from tar archive
docker load -i filename.tar
```

### Filtering and Formatting
```bash
# Filter images by label
docker images --filter "label=maintainer=user@example.com"

# Filter by reference
docker images --filter=reference='ubuntu:*'

# Custom format output
docker images --format "{{.ID}}: {{.Repository}}"
```
