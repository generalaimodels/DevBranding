# Docker Command Reference: Real-World Examples

## 1. docker run

### Basic Syntax
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

### Real-World Examples

**Run container in detached mode with port mapping:**
```bash
docker run -d -p 80:80 nginx
```

**Run with volume mounting:**
```bash
docker run -v $(pwd)/data:/app/data postgres:14
```

**Run with environment variables:**
```bash
docker run -e DB_HOST=localhost -e DB_PORT=5432 my-app:latest
```

**Run with resource constraints:**
```bash
docker run --memory="1g" --cpus="2" redis:alpine
```

**Run with network configuration:**
```bash
docker run --network="host" --name monitoring grafana/grafana
```

**Run with restart policy:**
```bash
docker run --restart=always -d mongodb:5
```

**Combination for production deployment:**
```bash
docker run -d --name api-service \
  -p 3000:3000 \
  -v /var/log/app:/app/logs \
  -e NODE_ENV=production \
  -e API_KEY=secret \
  --restart=unless-stopped \
  --memory="2g" \
  --cpus="1.5" \
  --network=app-network \
  my-api:1.0
```

## 2. docker exec

### Basic Syntax
```bash
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
```

### Real-World Examples

**Execute interactive bash shell:**
```bash
docker exec -it postgres_db bash
```

**Run database command:**
```bash
docker exec -it mysql mysql -uroot -psecret
```

**Check logs inside container:**
```bash
docker exec web-server cat /var/log/nginx/error.log
```

**Run application-specific command:**
```bash
docker exec app-container npm run migrate
```

**Execute with environment variable:**
```bash
docker exec -e DEBUG=true webserver python debug.py
```

**Run as specific user:**
```bash
docker exec -u postgres database-container psql
```

## 3. docker ps

### Basic Syntax
```bash
docker ps [OPTIONS]
```

### Real-World Examples

**List running containers:**
```bash
docker ps
```

**List all containers (including stopped):**
```bash
docker ps -a
```

**Show only container IDs:**
```bash
docker ps -q
```

**Filter containers by status:**
```bash
docker ps --filter "status=running"
```

**Filter by label:**
```bash
docker ps --filter "label=environment=production"
```

**Custom format output:**
```bash
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Show container sizes:**
```bash
docker ps -s
```

## 4. docker build

### Basic Syntax
```bash
docker build [OPTIONS] PATH | URL | -
```

### Real-World Examples

**Basic build:**
```bash
docker build -t myapp:1.0 .
```

**Build with specific Dockerfile:**
```bash
docker build -f Dockerfile.prod -t myapp:production .
```

**Build with build arguments:**
```bash
docker build --build-arg NODE_ENV=production -t myapp:1.0 .
```

**Build with no cache:**
```bash
docker build --no-cache -t fresh-build:latest .
```

**Build for multiple platforms:**
```bash
docker build --platform linux/amd64,linux/arm64 -t multi-arch-app:latest .
```

**Build with specific target stage:**
```bash
docker build --target development -t myapp:dev .
```

**Build and squash layers:**
```bash
docker build --squash -t optimized-image:1.0 .
```

## 5. docker pull

### Basic Syntax
```bash
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
```

### Real-World Examples

**Pull latest version:**
```bash
docker pull ubuntu
```

**Pull specific version:**
```bash
docker pull node:16-alpine
```

**Pull by digest (immutable):**
```bash
docker pull redis@sha256:a5a7e303b3211e67280393cb1c8554d114c3a8f8cd4fe2d96d1db7bc9f5e7cc5
```

**Pull all tags of an image:**
```bash
docker pull --all-tags nginx
```

**Pull from private registry:**
```bash
docker pull registry.example.com/myapp:latest
```

**Pull with platform specification:**
```bash
docker pull --platform linux/arm64 python:3.9
```

## 6. docker push

### Basic Syntax
```bash
docker push [OPTIONS] NAME[:TAG]
```

### Real-World Examples

**Push to Docker Hub:**
```bash
docker push username/myapp:1.0
```

**Push to private registry:**
```bash
docker push registry.company.com:5000/project/image:tag
```

**Push multiple tags:**
```bash
docker push myorg/app:1.0 && docker push myorg/app:latest
```

**Push to AWS ECR:**
```bash
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

**Push with configured registry:**
```bash
docker push ghcr.io/username/repo:tag
```

## 7. docker images

### Basic Syntax
```bash
docker images [OPTIONS] [REPOSITORY[:TAG]]
```

### Real-World Examples

**List all images:**
```bash
docker images
```

**Show only IDs:**
```bash
docker images -q
```

**Filter by reference:**
```bash
docker images nginx
```

**Filter by tag:**
```bash
docker images ubuntu:20.04
```

**Show dangling images:**
```bash
docker images --filter "dangling=true"
```

**Custom format output:**
```bash
docker images --format "{{.Repository}}:{{.Tag}} - {{.Size}}"
```

**Show image digests:**
```bash
docker images --digests
```

## 8. docker login

### Basic Syntax
```bash
docker login [OPTIONS] [SERVER]
```

### Real-World Examples

**Login to Docker Hub:**
```bash
docker login
```

**Login to private registry:**
```bash
docker login registry.example.com
```

**Login with username specified:**
```bash
docker login -u username registry.company.com
```

**Login to AWS ECR:**
```bash
docker login -u AWS -p $(aws ecr get-login-password) 123456789012.dkr.ecr.region.amazonaws.com
```

**Login with password from file:**
```bash
cat password.txt | docker login -u username --password-stdin
```

**Login to Google Container Registry:**
```bash
docker login -u _json_key --password-stdin https://gcr.io < keyfile.json
```

## 9. docker logout

### Basic Syntax
```bash
docker logout [SERVER]
```

### Real-World Examples

**Logout from Docker Hub:**
```bash
docker logout
```

**Logout from private registry:**
```bash
docker logout registry.example.com
```

**Logout from AWS ECR:**
```bash
docker logout 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

## 10. docker search

### Basic Syntax
```bash
docker search [OPTIONS] TERM
```

### Real-World Examples

**Basic search:**
```bash
docker search nginx
```

**Limit results:**
```bash
docker search --limit 5 database
```

**Filter by stars:**
```bash
docker search --filter=stars=100 python
```

**Show only official images:**
```bash
docker search --filter "is-official=true" ubuntu
```

**Search with automated build filter:**
```bash
docker search --filter "is-automated=true" jenkins
```

**Format search results:**
```bash
docker search --format "{{.Name}}: {{.StarCount}} stars" redis
```

## 11. docker version

### Basic Syntax
```bash
docker version [OPTIONS]
```

### Real-World Examples

**Show all version information:**
```bash
docker version
```

**Show only client version:**
```bash
docker version --format '{{.Client.Version}}'
```

**Output in JSON format:**
```bash
docker version --format '{{json .}}'
```

**Check API version:**
```bash
docker version --format '{{.Server.APIVersion}}'
```

## 12. docker info

### Basic Syntax
```bash
docker info [OPTIONS]
```

### Real-World Examples

**Display system information:**
```bash
docker info
```

**Format specific information:**
```bash
docker info --format '{{.ContainersRunning}} containers running'
```

**Get storage driver:**
```bash
docker info --format '{{.Driver}}'
```

**Output in JSON format:**
```bash
docker info --format '{{json .}}'
```

**Check if Swarm is active:**
```bash
docker info --format '{{.Swarm.LocalNodeState}}'
```

**Get total memory available:**
```bash
docker info --format '{{.MemTotal}}'
```

-----------------

**Docker Command Mastery: A Deep Dive**
=====================================

Docker has revolutionized the way we develop, ship, and run applications. Understanding Docker commands is pivotal for any developer aiming to containerize applications efficiently. Below, I'll dissect each common Docker command, providing you with a 360-degree view, complete with examples for every case and combination.

### 1. `run` - Create and Run a New Container from an Image
--------------------------------------------------------

**Purpose:** The `docker run` command is used to start a new container from a specified Docker image. It is the most frequently used Docker command.

**Syntax:**
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

**Common Options:**
- `-d`, `--detach`: Run container in background and print container ID.
- `-it`: `-i` for interactive, `-t` for tty (terminal). Used together for interactive shells.
- `--name`: Specify a name for the container.
- `-p`, `--publish`: Publish a container's port(s) to the host.
- `-v`, `--volume`: Bind mount a volume.

**Examples:**

1. **Simple Run**:
   ```bash
   docker run ubuntu
   ```
   This command runs `ubuntu` image, but since no command is specified, it starts, runs `/bin/bash` by default, and exits immediately because there's no interactive shell.

2. **Interactive Shell**:
   ```bash
   docker run -it ubuntu /bin/bash
   ```
   Now, you're inside the container's bash shell. You can run commands like `ls`, `apt-get`, etc.

3. **Detached Mode (Background)**:
   ```bash
   docker run -d nginx
   ```
   Starts an `nginx` server in the background. To verify, use `docker ps`.

4. **Naming Your Container**:
   ```bash
   docker run -d --name mynginx nginx
   ```
   Now, your `nginx` container is named `mynginx` for easier reference.

5. **Port Mapping**:
   ```bash
   docker run -d -p 8080:80 nginx
   ```
   Maps host's port `8080` to container's port `80`. Access `nginx` by visiting `http://localhost:8080` on your host machine.

6. **Volume Mounting** (Persistent Data):
   ```bash
   docker run -d -v /my/host/dir:/var/www/html nginx
   ```
   Maps a host directory `/my/host/dir` to the container's `/var/www/html`, useful for web development.

7. **Environment Variables**:
   ```bash
   docker run -d -e MYSQL_ROOT_PASSWORD=my-secret-pw mysql
   ```
   Sets an environment variable `MYSQL_ROOT_PASSWORD` inside the `mysql` container.

**Combination Example** (detached, named, port mapped, volume mounted):
```bash
docker run -d --name myapp \
  -p 8080:80 \
  -v /home/user/mywebapp:/var/www/html \
  nginx
```
Starts `nginx` named `myapp`, maps port `8080` to `80`, and mounts a local directory for web content.

### 2. `exec` - Execute a Command in a Running Container
--------------------------------------------------------

**Purpose:** To run a new command in a running container, useful for debugging or management.

**Syntax:**
```bash
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
```

**Common Options:**
- `-it`: For interactive processes (like shells).
- `-d`: Run in detached mode.

**Examples:**

1. **Interactive Bash**:
   ```bash
   docker exec -it mynginx /bin/bash
   ```
   Enters the `mynginx` container's shell.

2. **Detached Execution** (e.g., restarting a service):
   ```bash
   docker exec -d mynginx service nginx reload
   ```
   Reloads `nginx` configuration without entering the container.

3. **Viewing Logs**:
   ```bash
   docker exec -it mynginx tail -f /var/log/nginx/access.log
   ```
   Tails the `nginx` access logs in real-time.

**Combination Example** (useful for scripts or multiple actions):
```bash
docker exec -it mynginx sh -c "service nginx status && nginx -v"
```
Runs multiple commands inside `mynginx`: checks `nginx` service status and displays the `nginx` version.

### 3. `ps` - List Containers
---------------------------

**Purpose:** Lists all running containers by default. With options, can show all containers (running and stopped).

**Syntax:**
```bash
docker ps [OPTIONS]
```

**Common Options:**
- `-a`, `--all`: Show all containers (default shows just running).
- `-q`, `--quiet`: Only display numeric IDs.
- `--format`: Pretty-print containers using a Go template.

**Examples:**

1. **List Running Containers**:
   ```bash
   docker ps
   ```
   Shows containers that are currently running.

2. **List All Containers**:
   ```bash
   docker ps -a
   ```
   Includes stopped containers.

3. **List Latest Created Container**:
   ```bash
   docker ps -l
   ```
   Handy for checking the most recent container operations.

4. **List Container IDs Only**:
   ```bash
   docker ps -q
   ```
   Useful for scripting, e.g., stopping all running containers: `docker stop $(docker ps -q)`.

5. **Formatted Output** (e.g., show ID and Command):
   ```bash
   docker ps --format "table {{.ID}}\t{{.Command}}"
   ```
   Customizes the output for specific columns.

### 4. `build` - Build an Image from a Dockerfile
----------------------------------------------

**Purpose:** To create a Docker image from instructions written in a `Dockerfile`.

**Syntax:**
```bash
docker build [OPTIONS] PATH | URL | -
```

**Common Options:**
- `-t`, `--tag`: Name and optionally a tag (format: `name:tag`).
- `-f`, `--file`: Path to Dockerfile (if not named `Dockerfile`).

**Examples:**

1. **Basic Build**:
   ```bash
   docker build -t myimage .
   ```
   Builds an image tagged `myimage` using the `Dockerfile` in the current directory (`.`).

2. **Specify Dockerfile Location**:
   ```bash
   docker build -f /path/to/myDockerfile -t customimage .
   ```
   Uses a differently named/nlocated `Dockerfile`.

3. **Build from GitHub**:
   ```bash
   docker build -t mygithubimage github.com/user/repo
   ```
   Builds directly from a GitHub repository containing a `Dockerfile`.

4. **Build with Multiple Tags**:
   ```bash
   docker build -t myimage:latest -t myimage:v1.0 .
   ```
   Tags the built image with both `latest` and `v1.0`.

**Combination Example** (build, tag, and specify Dockerfile):
```bash
docker build -f ./dockerfiles/prodDockerfile \
  -t myapp:production \
  -t myregistry.com/myapp/production:latest .
```
Builds from a specific `Dockerfile`, tags it for production use, and also tags it for a remote registry.

### 5. `pull` - Download an Image from a Registry
----------------------------------------------

**Purpose:** Fetches an image or a repository from a registry (default is Docker Hub).

**Syntax:**
```bash
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
```

**Examples:**

1. **Pull Latest Image**:
   ```bash
   docker pull nginx
   ```
   Downloads the latest `nginx` image from Docker Hub.

2. **Pull Specific Tag**:
   ```bash
   docker pull nginx:alpine
   ```
   Fetches the `alpine` variant of `nginx`, which is smaller.

3. **Pull from Another Registry** (e.g., quay.io):
   ```bash
   docker pull quay.io/someorg/someimage
   ```
   Downloads from `quay.io` instead of Docker Hub.

### 6. `push` - Upload an Image to a Registry
--------------------------------------------

**Purpose:** Pushes an image or a repository to a registry (requires `docker login`).

**Syntax:**
```bash
docker push NAME[:TAG]
```

**Examples:**

1. **Push Image**:
   ```bash
   docker push myusername/myimage:latest
   ```
   Uploads `myimage:latest` to your Docker Hub account.

2. **Push to Specific Registry**:
   ```bash
   docker push registry.example.com:5000/myimage:latest
   ```
   Pushes to a private registry.

**Before Pushing:**
1. Tag your image correctly with your registry URL:
   ```bash
   docker tag myimage:latest myusername/myimage:latest
   ```
2. Login to the registry:
   ```bash
   docker login
   ```

### 7. `images` - List Images
---------------------------

**Purpose:** Lists all locally stored Docker images.

**Syntax:**
```bash
docker images [OPTIONS] [REPOSITORY[:TAG]]
```

**Common Options:**
- `-a`, `--all`: Show all images (including intermediates).
- `--digests`: Show digests (hashes).
- `-q`, `--quiet`: Only show numeric IDs.

**Examples:**

1. **List All Images**:
   ```bash
   docker images
   ```
   Shows repository, tag, created date, and size.

2. **Filter by Name**:
   ```bash
   docker images nginx
   ```
   Lists all `nginx` images with different tags.

3. **Show Intermediate Images**:
   ```bash
   docker images -a
   ```
   Intermediate images (those not tagged) are useful for debugging builds.

4. **Quiet Mode** (only IDs):
   ```bash
   docker images -q
   ```
   Useful for scripting, e.g., removing all images: `docker rmi $(docker images -q)`.

### 8. `login` / `logout` - Authenticate/Log Out from a Registry
----------------------------------------------------------

**Purpose:** Authenticates to a Docker registry (default Docker Hub).

**Syntax:**
```bash
docker login [OPTIONS] [SERVER]
docker logout [SERVER]
```

**Examples:**

1. **Login to Docker Hub**:
   ```bash
   docker login
   ```
   Prompts for username and password.

2. **Login to a Specific Registry**:
   ```bash
   docker login registry.example.com
   ```
   Useful for private enterprise registries.

3. **Logout** (default registry):
   ```bash
   docker logout
   ```

4. **Logout from Specific Registry**:
   ```bash
   docker logout registry.example.com
   ```

**Tip:** Store your Docker Hub credentials securely using:
```bash
docker login --username=myuser --password-stdin <<< "mypassword"
```

### 9. `search` - Search Docker Hub for Images
--------------------------------------------

**Purpose:** Searches Docker Hub for publicly available images.

**Syntax:**
```bash
docker search [OPTIONS] TERM
```

**Common Options:**
- `--limit`: Limit the number of results.

**Examples:**

1. **Simple Search**:
   ```bash
   docker search nginx
   ```
   Finds official and community `nginx` images.

2. **Limit Results**:
   ```bash
   docker search --limit 5 mysql
   ```
   Shows top 5 `mysql` images.

3. **Filter Official Builds**:
   ```bash
   docker search --filter=is-official=true nginx
   ```
   Only shows the official `nginx` image.

**Columns Explained:**
- `NAME`: Image name.
- `DESCRIPTION`: Short image description.
- `STARS`: Community likes (higher is better).
- `OFFICIAL`: `[OK]` means it's an official image.
- `AUTOMATED`: `[OK]` indicates automated builds.

### 10. `version` - Show the Docker Version Information
---------------------------------------------------

**Purpose:** Displays the Docker client and server versions.

**Syntax:**
```bash
docker version [OPTIONS]
```

**Common Options:**
- `--format`: Format the output using a Go template.

**Examples:**

1. **Default Version Info**:
   ```bash
   docker version
   ```
   Shows client and server details like version numbers, OS/architecture, etc.

2. **Formatted Output** (e.g., just client version):
   ```bash
   docker version --format '{{.Client.Version}}'
   ```

### 11. `info` - Display System-Wide Information
---------------------------------------------

**Purpose:** Provides detailed system-wide Docker information.

**Syntax:**
```bash
docker info [OPTIONS]
```

**Examples:**

1. **Show Docker System Info**:
   ```bash
   docker info
   ```
   Outputs:
   - Containers count (running, paused, stopped).
   - Images count.
   - Storage driver.
   - Execution driver.
   - Kernel version.
   - Total memory.
   - Docker root directory.

2. **Formatted Output**:
   ```bash
   docker info --format '{{json .}}'
   ```
   Dumps the info in JSON format for easy parsing.

**Key Highlights from `docker info`:**
- **Storage Driver**: `overlay2`, `devicemapper`, etc.
- **Logging Driver**: `json-file`, `journald`.
- **Cgroup Driver**: `cgroupfs` or `systemd`.
- **Registry**: Confirms default registry (Docker Hub).

---

**Practice Tip:**
Combine these commands in daily workflows:
1. `docker build` & `docker run` for development.
2. `docker exec -it` for debugging.
3. `docker ps -a` to monitor container states.
4. `docker images` to clean up unused images (`docker rmi`).
5. `docker login` & `docker push` for sharing images.

Now, you're not just familiar with Docker commands; you're a **Docker Command Maestro**! Keep experimenting, and remember: the best way to learn Docker is by Docker-ing! 

Happy Coding!