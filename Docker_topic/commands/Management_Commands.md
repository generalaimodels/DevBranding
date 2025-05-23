# Docker Management Commands: Complete Examples Guide

## Table of Contents
- [Docker AI Agent](#docker-ai-agent)
- [Builder](#builder)
- [Buildx](#buildx)
- [Cloud](#cloud)
- [Compose](#compose)
- [Container](#container)
- [Context](#context)
- [Debug](#debug)
- [Desktop](#desktop)
- [Dev](#dev)
- [Extension](#extension)
- [Image](#image)
- [Init](#init)
- [Manifest](#manifest)
- [Network](#network)
- [Plugin](#plugin)
- [SBOM](#sbom)
- [Scout](#scout)
- [System](#system)
- [Trust](#trust)
- [Volume](#volume)

## Docker AI Agent

### Basic Commands
```bash
docker ai ask "How do I optimize a multi-stage build?"
docker ai explain Dockerfile
docker ai suggest-improvements --dockerfile ./Dockerfile
```

### Advanced Usage
```bash
docker ai fix --error-log build-errors.log
docker ai optimize --target production --dockerfile ./Dockerfile
docker ai convert --from docker-compose.yml --to kubernetes
```

## Builder

### Managing Build Cache
```bash
docker builder prune
docker builder prune --all
docker builder prune --filter until=24h
```

### Build Info
```bash
docker builder ls
docker builder inspect
```

## Buildx

### Create and Use Builders
```bash
docker buildx create --name mybuilder
docker buildx use mybuilder
docker buildx ls
```

### Multi-platform Builds
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t username/demo:latest --push .
docker buildx build --platform linux/arm/v7 -t myapp:arm --load .
```

### Build with Cache Options
```bash
docker buildx build --cache-from type=registry,ref=username/image:cache .
docker buildx build --cache-to type=inline --tag myapp:latest .
```

## Cloud

### Authentication
```bash
docker cloud login
docker cloud logout
```

### Service Management
```bash
docker cloud service create --name webapp --image nginx
docker cloud service ps webapp
docker cloud service scale webapp=3
```

### Stack Operations
```bash
docker cloud stack up -n mystack -f docker-compose.yml
docker cloud stack rm mystack
docker cloud stack ls
```

## Compose

### Basic Operations
```bash
docker compose up
docker compose up -d
docker compose down
```

### Service Management
```bash
docker compose ps
docker compose logs -f service1
docker compose exec web bash
```

### Build and Scale
```bash
docker compose build
docker compose up --build
docker compose up --scale web=3 --scale worker=2
```

### Multiple Compose Files
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.override.yml config
```

## Container

### Lifecycle Management
```bash
docker container create --name web nginx:latest
docker container start web
docker container stop web
docker container restart web
docker container rm web
docker container rm -f $(docker container ls -aq)
```

### Inspection and Monitoring
```bash
docker container ls
docker container ls -a
docker container inspect web
docker container stats
docker container top web
```

### Execution and Logs
```bash
docker container exec -it web bash
docker container logs web
docker container logs -f --tail 100 web
```

### Port and Resource Management
```bash
docker container run -p 8080:80 nginx
docker container run --memory 512m --cpus 0.5 nginx
```

## Context

### Managing Contexts
```bash
docker context create mycontext --docker "host=ssh://user@remote-host"
docker context use mycontext
docker context ls
docker context rm mycontext
```

### Inspection
```bash
docker context inspect
docker context inspect mycontext
docker context export mycontext --output ./mycontext.tar
```

## Debug

### Debugging Containers
```bash
docker debug mycontainer
docker debug --target mycontainer
docker debug --image alpine mycontainer
```

### Debugging Images
```bash
docker debug nginx:latest
docker debug --type image ubuntu:20.04
```

## Desktop

### Management Commands
```bash
docker desktop version
docker desktop restart
docker desktop stop
```

### Settings
```bash
docker desktop settings
docker desktop settings --resources --cpus 4 --memory 8
docker desktop settings --kubernetes enable
```

## Dev

### Environment Management
```bash
docker dev create --name myproject
docker dev ls
docker dev open myproject
docker dev rm myproject
```

### Environment Configuration
```bash
docker dev up -f docker-compose.dev.yml
docker dev status
docker dev down
```

## Extension

### Extension Management
```bash
docker extension ls
docker extension install username/extension:latest
docker extension update username/extension:latest
docker extension uninstall username/extension:latest
```

### Development
```bash
docker extension init myextension
docker extension dev debug myextension
docker extension dev publish myextension
```

## Image

### Basic Operations
```bash
docker image pull nginx:latest
docker image build -t myapp:1.0 .
docker image push username/myapp:1.0
docker image rm nginx:latest
```

### Image Management
```bash
docker image ls
docker image ls --format "{{.Repository}}:{{.Tag}}"
docker image prune -a
docker image tag nginx:latest myregistry.com/nginx:v1
```

### Image Inspection
```bash
docker image inspect nginx:latest
docker image history nginx:latest
docker image inspect --format='{{.Config.Env}}' nginx:latest
```

## Init

### Project Initialization
```bash
docker init
docker init --platform java
docker init --file-name custom-dockerfile
```

### Customization
```bash
docker init --compose
docker init --description "My Python web application"
docker init --platform node --application-name my-node-app
```

## Manifest

### Create and Manage Manifests
```bash
docker manifest create myapp:latest myapp:amd64 myapp:arm64
docker manifest annotate myapp:latest myapp:arm64 --os linux --arch arm64
docker manifest push myapp:latest
```

### Inspection
```bash
docker manifest inspect nginx:latest
docker manifest inspect --verbose myapp:latest
```

## Network

### Network Creation and Management
```bash
docker network create mynetwork
docker network create --driver overlay --attachable myswarm
docker network rm mynetwork
docker network prune
```

### Network Inspection
```bash
docker network ls
docker network inspect mynetwork
docker network inspect bridge --format '{{json .Containers}}'
```

### Container Network Operations
```bash
docker network connect mynetwork container1
docker network disconnect mynetwork container1
docker run --network=mynetwork nginx
```

## Plugin

### Plugin Management
```bash
docker plugin install vieux/sshfs
docker plugin ls
docker plugin enable vieux/sshfs
docker plugin disable vieux/sshfs
docker plugin rm vieux/sshfs
```

### Plugin Settings
```bash
docker plugin inspect vieux/sshfs
docker plugin set vieux/sshfs DEBUG=1
```

## SBOM

### Generate and View SBOMs
```bash
docker sbom nginx:latest
docker sbom --format cyclonedx myapp:1.0
docker sbom --output sbom.json alpine:latest
```

### Filtering SBOM Results
```bash
docker sbom --filter-type package nginx:latest
docker sbom --filter-regex ".*openssl.*" ubuntu:20.04
```

## Scout

### Vulnerability Scanning
```bash
docker scout quickview nginx:latest
docker scout cves nginx:latest
docker scout recommendations nginx:latest
```

### Compare Images
```bash
docker scout compare nginx:1.21 nginx:1.22
docker scout compare --to nginx:latest myapp:1.0
```

### Generate Reports
```bash
docker scout generate-report nginx:latest --format pdf --output nginx-report.pdf
docker scout cves --format json --output cves.json nginx:latest
```

## System

### System Information
```bash
docker system info
docker system df
docker system events
```

### Resource Management
```bash
docker system prune
docker system prune --all --volumes
docker system prune --filter "until=24h"
```

## Trust

### Trust Management
```bash
docker trust key generate mykey
docker trust key load private.pem --name mykey
```

### Signing Images
```bash
docker trust sign username/image:tag
docker trust inspect --pretty username/image:tag
docker trust revoke username/image:tag
```

## Volume

### Volume Creation and Management
```bash
docker volume create myvolume
docker volume ls
docker volume inspect myvolume
docker volume rm myvolume
docker volume prune
```

### Volume Usage with Containers
```bash
docker run -v myvolume:/app/data nginx
docker run --mount source=myvolume,target=/app/data nginx
docker run --mount type=bind,source=/host/path,target=/container/path nginx
```

### Volume Driver Options
```bash
docker volume create --driver local --opt type=nfs --opt o=addr=192.168.1.1,rw --opt device=:/path/to/dir nfs-volume
```


----


**Docker Management Commands: A Comprehensive Guide**
=====================================================

Docker management commands are the backbone of containerization, allowing you to orchestrate, monitor, and control your Docker ecosystem. We'll explore each command, breaking down the syntax, options, and use cases. By the end of this odyssey, you'll wield Docker like a maestro.

**1. `ai*` - Docker AI Agent (Ask Gordon)**
------------------------------------------

**Overview**: The Docker AI Agent, codenamed "Gordon," is an experimental feature providing AI-driven assistance for Docker-related queries. It's like having a personal Docker butler!

**Syntax**: `docker ai [OPTIONS] COMMAND [ARG...]`

**Example Commands**:

* **Ask Gordon for help**: `docker ai --help` ( Lists all available AI commands )
* **Query Gordon about Docker Compose**: `docker ai "What is Docker Compose?"`
* **Get AI-generated Dockerfile for a Node.js app**: `docker ai "Generate Dockerfile for Node.js 14"`

**Real-time Example**:
```bash
$ docker ai "How do I optimize my Docker image size?"
Gordon: "Ah, excellent question! Use `docker image prune` to remove unused layers,
         and optimize your Dockerfile with multi-stage builds. Example:
         `docker build -t my-node-app --target production .`"
```
**2. `builder` - Manage Builds**
------------------------------

**Overview**: The `builder` command controls Docker's build process, allowing you to manage builders, inspect builds, and prune build cache.

**Syntax**: `docker builder [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `build`: Start a new build
* `inspect`: Inspect a build
* `ls`: List all builders
* `prune`: Remove unused build cache
* `rm`: Remove a builder

**Example Commands**:

* **List all builders**: `docker builder ls`
* **Inspect a build**: `docker builder inspect my-node-app:latest`
* **Prune build cache**: `docker builder prune -f` ( Force prune )
* **Create a new builder**: `docker builder create my-builder --driver docker-container`

**Real-time Example**:
```bash
$ docker builder ls
ID            NAME/nAMESPACE    DRIVER/ENDPOINT             STATUS
1234567890    default           docker-container          running

$ docker builder inspect my-node-app:latest
{
  "ID": "sha256:1234567890abcdef...",
  "Container": "my-node-app",
  "CreatedAt": "2023-02-20T14:30:00Z",
  "DockerVersion": "20.10.12",
  "Layers": [...]
}
```
**3. `buildx*` - Docker Buildx**
---------------------------

**Overview**: Docker Buildx is a next-generation build tool, offering advanced features like multi-arch builds, caching, and more.

**Syntax**: `docker buildx [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `bake`: Build a target from a HCL file
* `build`: Start a new build
* `create`: Create a new builder instance
* `du`: Disk usage
* `inspect`: Inspect a build
* `ls`: List all builder instances
* `prune`: Remove unused build cache
* `rm`: Remove a builder instance
* `stop`: Stop a build
* `use`: Set the current builder instance
* `version`: Show Buildx version information

**Example Commands**:

* **Build a multi-arch image**: `docker buildx build --platform linux/amd64,linux/arm64 -t my-node-app .`
* **Create a new Buildx instance**: `docker buildx create --name my-builder --driver docker-container`
* **List all Buildx instances**: `docker buildx ls`
* **Prune Buildx cache**: `docker buildx prune -f`

**Real-time Example**:
```bash
$ docker buildx build --platform linux/amd64,linux/arm64 -t my-node-app .
...
 => => naming to docker.io/my-node-app:latest                  0.0s
 => => naming to docker.io/my-node-app:linux-amd64            0.0s
 => => naming to docker.io/my-node-app:linux-arm64            0.0s

$ docker buildx ls
NAME/NAMESPACE    DRIVER/ENDPOINT             STATUS
default           docker-container          running
my-builder        docker-container          running
```
**4. `cloud*` - Docker Cloud**
---------------------------

**Overview**: Docker Cloud is a cloud-based platform for automating Docker deployments.

**Syntax**: `docker cloud [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `login`: Log in to Docker Cloud
* `logout`: Log out from Docker Cloud
* `namespace`: Manage namespaces
* `organization`: Manage organizations
* `registry`: Manage registries
* `repository`: Manage repositories
* `service`: Manage services
* `stack`: Manage stacks

**Example Commands**:

* **Log in to Docker Cloud**: `docker cloud login`
* **Create a new namespace**: `docker cloud namespace create my-namespace`
* **List repositories**: `docker cloud repository ls`
* **Deploy a service**: `docker cloud service create --name my-service --image my-node-app`

**Real-time Example**:
```bash
$ docker cloud login
Username: myuser
Password: ********
Login Succeeded!

$ docker cloud namespace create my-namespace
Namespace 'my-namespace' created

$ docker cloud repository ls
REPOSITORY          NAMESPACE       TAGS
my-node-app         my-namespace    latest, 1.0
```
**5. `compose*` - Docker Compose**
------------------------------

**Overview**: Docker Compose is a tool for defining and running multi-container Docker applications.

**Syntax**: `docker compose [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `build`: Build or rebuild services
* `config`: Validate and view the Compose file
* `create`: Create services
* `down`: Stop and remove containers, networks
* `events`: Receive real-time events from containers
* `exec`: Execute a command in a running container
* `images`: List images used by services
* `kill`: Kill containers
* `logs`: View output from containers
* `pause`: Pause services
* `port`: Print the public port for a port binding
* `ps`: List containers
* `pull`: Pull service images
* `push`: Push service images
* `restart`: Restart services
* `rm`: Remove stopped containers
* `run`: Run a one-time command
* `start`: Start services
* `stop`: Stop services
* `top`: Display the running processes
* `unpause`: Unpause services
* `up`: Create and start containers
* `version`: Show Docker Compose version

**Example Commands**:

* **Build and start services**: `docker compose up -d --build`
* **List services**: `docker compose ps`
* **View logs**: `docker compose logs -f`
* **Stop services**: `docker compose stop`

**Real-time Example**:
```bash
$ docker compose up -d --build
Building web...
...
Starting myapp_db_1 ... done
Starting myapp_web_1 ... done

$ docker compose ps
NAME                COMMAND                  SERVICE             STATUS              PORTS
myapp_db_1          "docker-entrypoint.s…"   db                  running             5432/tcp
myapp_web_1         "nginx -g 'daemon of…"   web                 running             0.0.0.0:80->80/tcp
```
**6. `container` - Manage Containers**
-----------------------------------

**Overview**: The `container` command manages the lifecycle of Docker containers.

**Syntax**: `docker container [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `attach`: Attach local standard input, output, and error streams to a running container
* `commit`: Create a new image from a container's changes
* `cp`: Copy files/folders between a container and the local filesystem
* `create`: Create a new container
* `diff`: Inspect changes to files or directories on a container's filesystem
* `exec`: Run a new command in a running container
* `export`: Export a container's filesystem as a tar archive
* `inspect`: Display detailed information on one or more containers
* `kill`: Kill one or more running containers
* `logs`: Fetch the logs of a container
* `ls`: List containers
* `pause`: Pause all processes within one or more containers
* `port`: List port mappings or a specific mapping for the container
* `prune`: Remove all stopped containers
* `rename`: Rename a container
* `restart`: Restart one or more containers
* `rm`: Remove one or more containers
* `run`: Run a command in a new container
* `start`: Start one or more stopped containers
* `stats`: Display a live stream of container(s) resource usage statistics
* `stop`: Stop one or more running containers
* `top`: Display the running processes of a container
* `unpause`: Unpause all processes within one or more containers
* `update`: Update configuration of one or more containers
* `wait`: Block until one or more containers stop, then print their exit codes

**Example Commands**:

* **List running containers**: `docker container ls`
* **Create and start a new container**: `docker container run -d --name my-web nginx`
* **Inspect a container**: `docker container inspect my-web`
* **Stop and remove a container**: `docker container rm -f my-web`

**Real-time Example**:
```bash
$ docker container run -d --name my-web nginx
646d81f7f66...

$ docker container ls
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                    PORTS     NAMES
646d81f7f66d   nginx         "/docker-entrypoint.…   3 seconds ago   Up 2 seconds   80/tcp   my-web

$ docker container inspect my-web
[
    {
        "Id": "646d81f7f66d...",
        "Created": "2023-02-20T14:45:00Z",
        "Path": "/docker-entrypoint.sh",
        "Args": [
            "nginx",
            "-g",
            "daemon off;"
        ],
...
```
**7. `context` - Manage Contexts**
-------------------------------

**Overview**: Docker contexts allow you to manage multiple Docker endpoints (e.g., local, remote, swarm).

**Syntax**: `docker context [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `create`: Create a new context
* `export`: Export a context to a tar file
* `import`: Import a context from a tar file
* `inspect`: Inspect a context
* `ls`: List contexts
* `rm`: Remove a context
* `update`: Update a context
* `use`: Set the current Docker context

**Example Commands**:

* **List contexts**: `docker context ls`
* **Create a new context**: `docker context create my-remote --docker "host=ssh://user@remote-host"`
* **Switch to a context**: `docker context use my-remote`
* **Inspect a context**: `docker context inspect my-remote`

**Real-time Example**:
```bash
$ docker context ls
NAME                DESCRIPTION                               DOCKER ENDPOINT               KUBERNETES ENDPOINT   ORCHESTRATOR
default *           Current DOCKER_HOST based configuration   unix:///var/run/docker.sock                         swarm

$ docker context create my-remote --docker "host=ssh://user@remote-host"
my-remote

$ docker context use my-remote
Current context is now "my-remote"

$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                    PORTS     NAMES
... ( remote host containers listed )
```
**8. `debug*` - Get a Shell into Any Image or Container**
---------------------------------------------------

**Overview**: `docker debug` allows you to spawn a shell in any image or container for troubleshooting.

**Syntax**: `docker debug [OPTIONS] CONTAINER|IMAGE [COMMAND]`

**Example Commands**:

* **Spawn a shell in a running container**: `docker debug my-web`
* **Spawn a shell in an image**: `docker debug nginx:latest`
* **Run a command in a container**: `docker debug my-web -- ls /app`

**Real-time Example**:
```bash
$ docker debug my-web
root@646d81f7f66d:/# ls /app
index.html  static

root@646d81f7f66d:/# exit
```
**9. `desktop*` - Docker Desktop Commands (Beta)**
---------------------------------------------

**Overview**: Docker Desktop commands manage Docker Desktop settings and features (Beta).

**Syntax**: `docker desktop [OPTIONS] COMMAND [ARG...]`

**Subcommands** (Beta):

* `cli-plugins`: Manage CLI plugins
* `disk`: Manage disk usage
* `settings`: Manage Docker Desktop settings

**Example Commands** (Beta):

* **List CLI plugins**: `docker desktop cli-plugins ls`
* **Show disk usage**: `docker desktop disk usage`
* **Open Docker Desktop settings**: `docker desktop settings`

**Real-time Example** (Beta):
```bash
$ docker desktop cli-plugins ls
PLUGIN NAME    VERSION    STATUS
compose        2.3.3      enabled

$ docker desktop disk usage
{
  "total": 123456789,
  "used": 98765432,
  "available": 24691357
}
```
**10. `dev*` - Docker Dev Environments**
--------------------------------------

**Overview**: Docker Dev Environments simplify development workflows with automated setup and tear-down.

**Syntax**: `docker dev [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `create`: Create a new dev environment
* `inspect`: Inspect a dev environment
* `ls`: List dev environments
* `rm`: Remove a dev environment
* `up`: Start a dev environment

**Example Commands**:

* **Create a new dev environment**: `docker dev create --name my-dev-env --image node:14`
* **List dev environments**: `docker dev ls`
* **Start a dev environment**: `docker dev up my-dev-env`

**Real-time Example**:
```bash
$ docker dev create --name my-dev-env --image node:14
my-dev-env

$ docker dev ls
NAME           IMAGE         STATUS
my-dev-env     node:14       created

$ docker dev up my-dev-env
Starting my-dev-env...
my-dev-env is running!
```
**11. `extension*` - Manage Docker Extensions**
--------------------------------------------

**Overview**: Docker Extensions enhance Docker functionality with third-party plugins.

**Syntax**: `docker extension [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `disable`: Disable an extension
* `enable`: Enable an extension
* `inspect`: Inspect an extension
* `install`: Install an extension
* `ls`: List extensions
* `rm`: Remove an extension
* `update`: Update an extension

**Example Commands**:

* **List extensions**: `docker extension ls`
* **Install an extension**: `docker extension install docker-compose`
* **Enable an extension**: `docker extension enable docker-compose`

**Real-time Example**:
```bash
$ docker extension ls
EXTENSION NAME    VERSION    STATUS
compose           2.3.3      enabled

$ docker extension install docker-scan
Installed docker-scan@1.2.3

$ docker extension ls
EXTENSION NAME    VERSION    STATUS
compose           2.3.3      enabled
docker-scan       1.2.3      enabled
```
**12. `image` - Manage Images**
---------------------------

**Overview**: The `image` command manages Docker images.

**Syntax**: `docker image [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `build`: Build an image from a Dockerfile
* `history`: Show the history of an image
* `import`: Import the contents from a tarball to create a filesystem image
* `inspect`: Display detailed information on one or more images
* `load`: Load an image from a tar archive or STDIN
* `ls`: List images
* `prune`: Remove unused images
* `pull`: Pull an image or a repository from a registry
* `push`: Push an image or a repository to a registry
* `rm`: Remove one or more images
* `save`: Save one or more images to a tar archive (streamed to STDOUT by default)
* `tag`: Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE

**Example Commands**:

* **List images**: `docker image ls`
* **Pull an image**: `docker image pull nginx:latest`
* **Inspect an image**: `docker image inspect nginx:latest`
* **Remove an image**: `docker image rm nginx:latest`

**Real-time Example**:
```bash
$ docker image ls
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         latest    1234567890ab   3 weeks ago    133MB

$ docker image inspect nginx:latest
[
    {
        "Id": "sha256:1234567890abcdef...",
        "RepoTags": [
            "nginx:latest"
        ],
        "Created": "2023-02-01T14:30:00Z",
...
```
**13. `init*` - Create Docker-Related Starter Files**
------------------------------------------------

**Overview**: `docker init` generates Docker-related starter files for your project.

**Syntax**: `docker init [OPTIONS] [PATH]`

**Example Commands**:

* **Create a new Dockerfile**: `docker init --dockerfile`
* **Create a docker-compose.yml**: `docker init --compose`

**Real-time Example**:
```bash
$ docker init --dockerfile
Wrote Dockerfile to ./Dockerfile

$ cat Dockerfile
FROM node:14
WORKDIR /app
COPY package*.json ./
...
```
**14. `manifest` - Manage Docker Image Manifests**
---------------------------------------------

**Overview**: The `manifest` command manages Docker image manifests and manifest lists.

**Syntax**: `docker manifest [OPTIONS] COMMAND [ARG...]`

**Subcommands**:

* `annotate`: Add additional information to a manifest list
* `create`: Create a manifest list
* `inspect`: Display a manifest
* `push`: Push a manifest list to a repository
* `rm`: Remove a manifest list

**Example Commands**:

* **Create a manifest list**: `docker manifest create my-node-app:latest my-node-app:amd64 my-node-app:arm64`
* **Annotate a manifest**: `docker manifest annotate my-node-app:latest --os linux --arch amd64`
* **Inspect a manifest**: `docker manifest inspect my-node-app:latest`

**Real-time Example**:
```bash
$ docker manifest create my-node-app:latest my-node-app:amd64 my-node-app:arm64
Created manifest list