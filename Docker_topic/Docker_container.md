**Mastering Docker CLI: A Comprehensive Guide**
=====================================================

This tutorial covers **all** Docker CLI commands, from basic to advanced, ensuring you grasp the concepts end-to-end. Buckle up, developers!

**Table of Contents**
-----------------

1. **Introduction to Docker CLI**
2. **Basic Commands**
   - 2.1 `docker --help`
   - 2.2 `docker info`
   - 2.3 `docker version`
3. **Docker CLI Syntax and Structure**
4. **Management Commands**
   - 4.1 `docker container`
   - 4.2 `docker image`
   - 4.3 `docker volume`
   - 4.4 `docker network`
   - 4.5 `docker system`
5. **Container Commands**
   - 5.1 `docker run`
   - 5.2 `docker ps`
   - 5.3 `docker inspect`
   - 5.4 `docker logs`
   - 5.5 `docker attach`
   - 5.6 `docker exec`
   - 5.7 `docker stop`
   - 5.8 `docker start`
   - 5.9 `docker restart`
   - 5.10 `docker rm`
   - 5.11 `docker pause` / `docker unpause`
6. **Image Commands**
   - 6.1 `docker build`
   - 6.2 `docker pull`
   - 6.3 `docker push`
   - 6.4 `docker images`
   - 6.5 `docker rmi`
   - 6.6 `docker tag`
   - 6.7 `docker history`
   - 6.8 `docker save` / `docker load`
7. **Volume Commands**
   - 7.1 `docker volume create`
   - 7.2 `docker volume ls`
   - 7.3 `docker volume inspect`
   - 7.4 `docker volume rm`
   - 7.5 `docker volume prune`
8. **Network Commands**
   - 8.1 `docker network create`
   - 8.2 `docker network ls`
   - 8.3 `docker network inspect`
   - 8.4 `docker network rm`
   - 8.5 `docker network connect` / `docker network disconnect`
9. **System Commands**
   - 9.1 `docker system df`
   - 9.2 `docker system prune`
   - 9.3 `docker system events`
10. **Miscellaneous Commands**
   - 10.1 `docker login`
   - 10.2 `docker logout`
   - 10.3 `docker search`
   - 10.4 `docker stats`
   - 10.5 `docker top`
11. **Conclusion**

**1. Introduction to Docker CLI**
--------------------------------

Docker CLI (Command-Line Interface) is a powerful tool for interacting with Docker, a containerization platform. It allows you to manage containers, images, volumes, networks, and more. Familiarity with Docker CLI is essential for efficient development, testing, and deployment of containerized applications.

**2. Basic Commands**
--------------------

Let's start with the fundamental commands that every Docker user should know.

### 2.1 `docker --help`

**Purpose:** Display Docker CLI usage and available commands.

**Syntax:** `docker --help` or `docker -h`

**Output:**
```markdown
Usage: docker [OPTIONS] COMMAND

A self-sufficient runtime for containers

Options:
      --config string      Location of client config files (default "/Users/<username>/.docker")
  -c, --context string     Name of the context to use to connect to the daemon (overrides DOCKER_HOST env var and default context set with "docker context use")
  -D, --debug              Enable debug mode
  -H, --host list          Daemon socket(s) to connect to
  -l, --log-level string   Set the logging level ("debug"|"info"|"warn"|"error"|"fatal") (default "info")
      --tls                Use TLS; implied by --tlsverify
      --tlscacert string   Trust certs signed only by this CA (default "/Users/<username>/.docker/ca.pem")
      --tlscert string     Path to TLS certificate file (default "/Users/<username>/.docker/cert.pem")
      --tlskey string      Path to TLS key file (default "/Users/<username>/.docker/key.pem")
      --tlsverify          Use TLS and verify the remote
  -v, --version            Print version information and quit

Management Commands:
  builder     Manage builds
  config      Manage Docker configs
  container   Manage containers
  image       Manage images
  network     Manage networks
  node        Manage Swarm nodes
  plugin      Manage plugins
  secret      Manage Docker secrets
  service     Manage services
  stack       Manage Docker stacks
  swarm       Manage Swarm
  system      Manage Docker
  trust       Manage trust on Docker images
  volume      Manage volumes

Commands:
  attach      Attach local standard input, output, and error streams to a running container
  build       Build an image from a Dockerfile
  commit      Create a new image from a container's changes
  cp          Copy files/folders between a container and the local filesystem
  create      Create a new container
  diff        Inspect changes to files or directories on a container's filesystem
  events      Get real time events from the server
  exec        Run a command in a running container
  export      Export a container's filesystem as a tar archive
  history     Show the history of an image
  images      List images
  import      Import the contents from a tarball to create a filesystem image
  info        Display system-wide information
  inspect     Return low-level information on Docker objects
  kill        Kill one or more running containers
  load        Load an image from a tar archive or STDIN
  login       Log in to a Docker registry
  logout      Log out from a Docker registry
  logs        Fetch the logs of a container
  pause       Pause all processes within one or more containers
  port        List port mappings or a specific mapping for the container
  ps          List containers
  pull        Pull an image or a repository from a registry
  push        Push an image or a repository to a registry
  rename      Rename a container
  restart     Restart one or more containers
  rm          Remove one or more containers
  rmi         Remove one or more images
  run         Run a command in a new container
  save        Save one or more images to a tar archive (streamed to STDOUT by default)
  search      Search the Docker Hub for images
  start       Start one or more stopped containers
  stats       Display a live stream of container(s) resource usage statistics
  stop        Stop one or more running containers
  tag         Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
  top         Display the running processes of a container
  unpause     Unpause all processes within one or more containers
  update      Update configuration of one or more containers
  version     Show the Docker version information
  wait        Block until one or more containers stop, then print their exit codes
```
The `--help` command lists all available Docker CLI commands and options.

### 2.2 `docker info`

**Purpose:** Display system-wide information about Docker.

**Syntax:** `docker info`

**Output:**
```markdown
Client:
 Context:    default
 Debug Mode: false
 Plugins:
  app: Docker App (Docker Inc., v0.9.1-beta3)
  buildx: Build with BuildKit (Docker Inc., v0.6.3-docker)

Server:
 Containers: 5
  Running: 2
  Paused: 0
  Stopped: 3
 Images: 23
 Server Version: 20.10.7
 Storage Driver: overlay2
  Backing Filesystem: extfs
  Supports d_type: true
  Native Overlay Diff: true
  userxattr: false
 Logging Driver: json-file
 Cgroup Driver: cgroupfs
 Cgroup Version: 1
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local logentries splunk syslog
 Swarm: inactive
 Runtimes: io.containerd.runtime.v1.linux runc io.containerd.runc.v2
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: d71fcd7d5767f2969d8f1158611f4d4ea3c62e39
 runc version: 12644e614e25b05da6fd08a38ffa0cfe1903fdec
 init version: de40ad0
 Security Options:
  seccomp
   Profile: default
 Kernel Version: 5.10.25-linuxkit
 Operating System: Docker Desktop
 OSType: linux
 Architecture: x86_64
 CPUs: 4
 Total Memory: 7.776GiB
 Name: docker-desktop
 ID: I54V:5U3T:G7BJ:43UF:Z65W:UEBS:U3VD:357T:UHLR:KV2N:W6GA:QMXN
 Docker Root Dir: /var/lib/docker
 Debug Mode: false
 Registry: https://index.docker.io/v1/
 Labels:
 Experimental: false
 Insecure Registries:
  127.0.0.0/8
 Live Restore Enabled: false
```
The `docker info` command provides an overview of your Docker setup, including:

* Client and server versions
* Number of containers and images
* Storage driver and filesystem details
* Logging and cgroup drivers
* Available plugins
* Swarm status (if enabled)
* Runtime and init binary versions
* Security options
* Kernel and OS information
* Hardware resources (CPUs, memory)

### 2.3 `docker version`

**Purpose:** Show the Docker version information.

**Syntax:** `docker version`

**Output:**
```markdown
Client: Docker Engine - Community
 Version:           20.10.7
 API version:       1.41
 Go version:        go1.16.4
 Git commit:        f0df350
 Built:             Wed Jun  2 11:56:22 2021
 OS/Arch:           darwin/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.7
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.16.4
  Git commit:       b0f2284
  Built:            Wed Jun  2 11:54:48 2021
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.4.6
  GitCommit:        d71fcd7d5767f2969d8f1158611f4d4ea3c62e39
 runc:
  Version:          1.0.0-rc95
  GitCommit:        12644e614e25b05da6fd08a38ffa0cfe1903fdec
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```
The `docker version` command displays:

* Client and server versions
* API versions
* Go version used for building Docker
* Git commit hashes
* Build timestamps
* OS and architecture information
* Experimental feature flags

**3. Docker CLI Syntax and Structure**
---------------------------------------

Docker CLI commands follow a consistent structure:
```bash
docker [OPTIONS] COMMAND [ARG...]
```
* `docker`: The command-line executable.
* `[OPTIONS]`: Optional flags that modify the command's behavior (e.g., `-d`, `--help`).
* `COMMAND`: The specific Docker command (e.g., `run`, `ps`, `build`).
* `[ARG...]`: Arguments passed to the command (e.g., container names, image tags).

**4. Management Commands**
-------------------------

Management commands are used to manage Docker objects (containers, images, volumes, networks, etc.). They are structured as `docker <object> <action>`.

### 4.1 `docker container`

**Purpose:** Manage containers.

**Subcommands:**

* `docker container ls` (alias: `docker ps`): List containers.
* `docker container inspect`: Inspect a container.
* `docker container rm`: Remove a container.
* `docker container run`: Run a command in a new container (alias: `docker run`).
* ...

Example: `docker container ls -a` (list all containers, including stopped ones)

### 4.2 `docker image`

**Purpose:** Manage images.

**Subcommands:**

* `docker image ls` (alias: `docker images`): List images.
* `docker image inspect`: Inspect an image.
* `docker image rm` (alias: `docker rmi`): Remove an image.
* `docker image build`: Build an image from a Dockerfile (alias: `docker build`).
* ...

Example: `docker image ls -a` (list all images, including intermediate ones)

### 4.3 `docker volume`

**Purpose:** Manage volumes.

**Subcommands:**

* `docker volume create`: Create a volume.
* `docker volume ls`: List volumes.
* `docker volume inspect`: Inspect a volume.
* `docker volume rm`: Remove a volume.
* ...

Example: `docker volume create myvol` (create a new volume named "myvol")

### 4.4 `docker network`

**Purpose:** Manage networks.

**Subcommands:**

* `docker network create`: Create a network.
* `docker network ls`: List networks.
* `docker network inspect`: Inspect a network.
* `docker network rm`: Remove a network.
* ...

Example: `docker network create mynet` (create a new network named "mynet")

### 4.5 `docker system`

**Purpose:** Manage Docker system-wide settings.

**Subcommands:**

* `docker system df`: Show Docker disk usage.
* `docker system prune`: Remove unused data (containers, images, volumes, networks).
* `docker system events`: Monitor system events (e.g., container creation, image pulls).

Example: `docker system df -v` (show detailed disk usage information)

**5. Container Commands**
-------------------------

These commands operate on containers.

### 5.1 `docker run`

**Purpose:** Run a command in a new container.

**Syntax:** `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`

**Options:**

* `-d`, `--detach`: Run in detached mode (background).
* `-it`, `--interactive --tty`: Allocate a pseudo-TTY and keep STDIN open.
* `--name`: Assign a name to the container.
* `-p`, `--publish`: Publish container ports to the host.
* `-v`, `--volume`: Mount a volume.
* ...

**Example:** `docker run -it --name mycnt ubuntu /bin/bash` (start a new Ubuntu container and open a bash shell)

### 5.2 `docker ps`

**Purpose:** List containers.

**Syntax:** `docker ps [OPTIONS]`

**Options:**

* `-a`, `--all`: Show all containers (default shows just running).
* `-l`, `--latest`: Show the latest created container (including all states).
* `-n`, `--last`: Show n last created containers (includes all states).
* `-q`, `--quiet`: Only display numeric IDs.

**Example:** `docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"` (list all containers with custom format)

### 5.3 `docker inspect`

**Purpose:** Inspect a container (or image, volume, network).

**Syntax:** `docker inspect [OPTIONS] NAME|ID [NAME|ID...]`

**Options:**

* `-f`, `--format`: Format the output using a Go template.
* `-s`, `--size`: Display total file sizes (containers only).

**Example:** `docker inspect -f '{{.NetworkSettings.IPAddress}}' mycnt` (get the IP address of container "mycnt")

### 5.4 `docker logs`

**Purpose:** Fetch the logs of a container.

**Syntax:** `docker logs [OPTIONS] CONTAINER`

**Options:**

* `-f`, `--follow`: Follow log output (stream new logs).
* `--since`: Show logs since a timestamp (e.g., `2022-01-01T00:00:00Z`).
* `--until`: Show logs until a timestamp.
* `-t`, `--timestamps`: Show timestamps.

**Example:** `docker logs -f mycnt` (follow the logs of container "mycnt")

### 5.5 `docker attach`

**Purpose:** Attach local standard input, output, and error streams to a running container.

**Syntax:** `docker attach [OPTIONS] CONTAINER`

**Options:**

* `--detach-keys`: Override the key sequence for detaching a container.
* `--no-stdin`: Do not attach STDIN.
* `--sig-proxy`: Proxy all received signals to the process (non-TTY mode only).

**Example:** `docker attach mycnt` (attach to container "mycnt" interactively)

### 5.6 `docker exec`

**Purpose:** Run a new command in a running container.

**Syntax:** `docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`

**Options:**

* `-d`, `--detach`: Run in detached mode.
* `-e`, `--env`: Set environment variables.
* `-it`, `--interactive --tty`: Allocate a pseudo-TTY and keep STDIN open.
* `-u`, `--user`: Username or UID (format: `<name|uid>[:<group|gid>]`).

**Example:** `docker exec -it mycnt /bin/bash` (open a new bash shell in container "mycnt")

### 5.7 `docker stop`

**Purpose:** Stop one or more running containers.

**Syntax:** `docker stop [OPTIONS] CONTAINER [CONTAINER...]`

**Options:**

* `-t`, `--time`: Seconds to wait for stop before killing it (default 10).

**Example:** `docker stop -t 30 mycnt` (stop container "mycnt" with a 30-second timeout)

### 5.8 `docker start`

**Purpose:** Start one or more stopped containers.

**Syntax:** `docker start [OPTIONS] CONTAINER [CONTAINER...]`

**Options:**

* `-a`, `--attach`: Attach STDOUT/STDERR and forward signals.
* `-i`, `--interactive`: Attach container's STDIN.

**Example:** `docker start -a mycnt` (start container