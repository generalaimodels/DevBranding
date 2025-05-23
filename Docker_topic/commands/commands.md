```markdown
Usage:  docker [OPTIONS] COMMAND

A self-sufficient runtime for containers

Common Commands:
  run         Create and run a new container from an image
  exec        Execute a command in a running container
  ps          List containers
  build       Build an image from a Dockerfile
  pull        Download an image from a registry
  push        Upload an image to a registry
  images      List images
  login       Authenticate to a registry
  logout      Log out from a registry
  search      Search Docker Hub for images
  version     Show the Docker version information
  info        Display system-wide information

Management Commands:
  ai*         Docker AI Agent - Ask Gordon
  builder     Manage builds
  buildx*     Docker Buildx
  cloud*      Docker Cloud
  compose*    Docker Compose
  container   Manage containers
  context     Manage contexts
  debug*      Get a shell into any image or container
  desktop*    Docker Desktop commands (Beta)
  dev*        Docker Dev Environments
  extension*  Manages Docker extensions
  image       Manage images
  init*       Creates Docker-related starter files for your project
  manifest    Manage Docker image manifests and manifest lists
  network     Manage networks
  plugin      Manage plugins
  sbom*       View the packaged-based Software Bill Of Materials (SBOM) for an image
  scout*      Docker Scout
  system      Manage Docker
  trust       Manage trust on Docker images
  volume      Manage volumes

Swarm Commands:
  swarm       Manage Swarm

Commands:
  attach      Attach local standard input, output, and error streams to a running container
  commit      Create a new image from a container's changes
  cp          Copy files/folders between a container and the local filesystem
  create      Create a new container
  diff        Inspect changes to files or directories on a container's filesystem
  events      Get real time events from the server
  export      Export a container's filesystem as a tar archive
  history     Show the history of an image
  import      Import the contents from a tarball to create a filesystem image
  inspect     Return low-level information on Docker objects
  kill        Kill one or more running containers
  load        Load an image from a tar archive or STDIN
  logs        Fetch the logs of a container
  pause       Pause all processes within one or more containers
  port        List port mappings or a specific mapping for the container
  rename      Rename a container
  restart     Restart one or more containers
  rm          Remove one or more containers
  rmi         Remove one or more images
  save        Save one or more images to a tar archive (streamed to STDOUT by default)
  start       Start one or more stopped containers
  stats       Display a live stream of container(s) resource usage statistics
  stop        Stop one or more running containers
  tag         Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
  top         Display the running processes of a container
  unpause     Unpause all processes within one or more containers
  update      Update configuration of one or more containers
  wait        Block until one or more containers stop, then print their exit codes

Global Options:
      --config string      Location of client config files (default
                           "C:\\Users\\heman\\.docker")
  -c, --context string     Name of the context to use to connect to the
                           daemon (overrides DOCKER_HOST env var and
                           default context set with "docker context use")
  -D, --debug              Enable debug mode
  -H, --host list          Daemon socket to connect to
  -l, --log-level string   Set the logging level ("debug", "info",
                           "warn", "error", "fatal") (default "info")
      --tls                Use TLS; implied by --tlsverify
      --tlscacert string   Trust certs signed only by this CA (default
                           "C:\\Users\\heman\\.docker\\ca.pem")
      --tlscert string     Path to TLS certificate file (default
                           "C:\\Users\\heman\\.docker\\cert.pem")
      --tlskey string      Path to TLS key file (default
                           "C:\\Users\\heman\\.docker\\key.pem")
      --tlsverify          Use TLS and verify the remote
  -v, --version            Print version information and quit

Run 'docker COMMAND --help' for more information on a command.

For more help on how to use Docker, head to https://docs.docker.com/go/guides/
```
---------
# RUN
```markdown
Usage:  docker run [OPTIONS] IMAGE [COMMAND] [ARG...]

Create and run a new container from an image

Aliases:
  docker container run, docker run

Options:
      --add-host list                    Add a custom host-to-IP mapping
                                         (host:ip)
      --annotation map                   Add an annotation to the
                                         container (passed through to the
                                         OCI runtime) (default map[])
  -a, --attach list                      Attach to STDIN, STDOUT or STDERR
      --blkio-weight uint16              Block IO (relative weight),
                                         between 10 and 1000, or 0 to
                                         disable (default 0)
      --blkio-weight-device list         Block IO weight (relative device
                                         weight) (default [])
      --cap-add list                     Add Linux capabilities
      --cap-drop list                    Drop Linux capabilities
      --cgroup-parent string             Optional parent cgroup for the
                                         container
      --cgroupns string                  Cgroup namespace to use
                                         (host|private)
                                         'host':    Run the container in
                                         the Docker host's cgroup
                                         namespace
                                         'private': Run the container in
                                         its own private cgroup namespace
                                         '':        Use the cgroup
                                         namespace as configured by the
                                                    default-cgroupns-mode
                                         option on the daemon (default)
      --cidfile string                   Write the container ID to the file
      --cpu-period int                   Limit CPU CFS (Completely Fair
                                         Scheduler) period
      --cpu-quota int                    Limit CPU CFS (Completely Fair
                                         Scheduler) quota
      --cpu-rt-period int                Limit CPU real-time period in
                                         microseconds
      --cpu-rt-runtime int               Limit CPU real-time runtime in
                                         microseconds
  -c, --cpu-shares int                   CPU shares (relative weight)
      --cpus decimal                     Number of CPUs
      --cpuset-cpus string               CPUs in which to allow execution
                                         (0-3, 0,1)
      --cpuset-mems string               MEMs in which to allow execution
                                         (0-3, 0,1)
  -d, --detach                           Run container in background and
                                         print container ID
      --detach-keys string               Override the key sequence for
                                         detaching a container
      --device list                      Add a host device to the container
      --device-cgroup-rule list          Add a rule to the cgroup allowed
                                         devices list
      --device-read-bps list             Limit read rate (bytes per
                                         second) from a device (default [])
      --device-read-iops list            Limit read rate (IO per second)
                                         from a device (default [])
      --device-write-bps list            Limit write rate (bytes per
                                         second) to a device (default [])
      --device-write-iops list           Limit write rate (IO per second)
                                         to a device (default [])
      --disable-content-trust            Skip image verification (default
                                         true)
      --dns list                         Set custom DNS servers
      --dns-option list                  Set DNS options
      --dns-search list                  Set custom DNS search domains
      --domainname string                Container NIS domain name
      --entrypoint string                Overwrite the default ENTRYPOINT
                                         of the image
  -e, --env list                         Set environment variables
      --env-file list                    Read in a file of environment
                                         variables
      --expose list                      Expose a port or a range of ports
      --gpus gpu-request                 GPU devices to add to the
                                         container ('all' to pass all GPUs)
      --group-add list                   Add additional groups to join
      --health-cmd string                Command to run to check health
      --health-interval duration         Time between running the check
                                         (ms|s|m|h) (default 0s)
      --health-retries int               Consecutive failures needed to
                                         report unhealthy
      --health-start-interval duration   Time between running the check
                                         during the start period
                                         (ms|s|m|h) (default 0s)
      --health-start-period duration     Start period for the container
                                         to initialize before starting
                                         health-retries countdown
                                         (ms|s|m|h) (default 0s)
      --health-timeout duration          Maximum time to allow one check
                                         to run (ms|s|m|h) (default 0s)
      --help                             Print usage
  -h, --hostname string                  Container host name
      --init                             Run an init inside the container
                                         that forwards signals and reaps
                                         processes
  -i, --interactive                      Keep STDIN open even if not attached
      --ip string                        IPv4 address (e.g., 172.30.100.104)
      --ip6 string                       IPv6 address (e.g., 2001:db8::33)
      --ipc string                       IPC mode to use
      --isolation string                 Container isolation technology
      --kernel-memory bytes              Kernel memory limit
  -l, --label list                       Set meta data on a container
      --label-file list                  Read in a line delimited file of
                                         labels
      --link list                        Add link to another container
      --link-local-ip list               Container IPv4/IPv6 link-local
                                         addresses
      --log-driver string                Logging driver for the container
      --log-opt list                     Log driver options
      --mac-address string               Container MAC address (e.g.,
                                         92:d0:c6:0a:29:33)
  -m, --memory bytes                     Memory limit
      --memory-reservation bytes         Memory soft limit
      --memory-swap bytes                Swap limit equal to memory plus
                                         swap: '-1' to enable unlimited swap
      --memory-swappiness int            Tune container memory swappiness
                                         (0 to 100) (default -1)
      --mount mount                      Attach a filesystem mount to the
                                         container
      --name string                      Assign a name to the container
      --network network                  Connect a container to a network
      --network-alias list               Add network-scoped alias for the
                                         container
      --no-healthcheck                   Disable any container-specified
                                         HEALTHCHECK
      --oom-kill-disable                 Disable OOM Killer
      --oom-score-adj int                Tune host's OOM preferences
                                         (-1000 to 1000)
      --pid string                       PID namespace to use
      --pids-limit int                   Tune container pids limit (set
                                         -1 for unlimited)
      --platform string                  Set platform if server is
                                         multi-platform capable
      --privileged                       Give extended privileges to this
                                         container
  -p, --publish list                     Publish a container's port(s) to
                                         the host
  -P, --publish-all                      Publish all exposed ports to
                                         random ports
      --pull string                      Pull image before running
                                         ("always", "missing", "never")
                                         (default "missing")
  -q, --quiet                            Suppress the pull output
      --read-only                        Mount the container's root
                                         filesystem as read only
      --restart string                   Restart policy to apply when a
                                         container exits (default "no")
      --rm                               Automatically remove the
                                         container and its associated
                                         anonymous volumes when it exits
      --runtime string                   Runtime to use for this container
      --security-opt list                Security Options
      --shm-size bytes                   Size of /dev/shm
      --sig-proxy                        Proxy received signals to the
                                         process (default true)
      --stop-signal string               Signal to stop the container
      --stop-timeout int                 Timeout (in seconds) to stop a
                                         container
      --storage-opt list                 Storage driver options for the
                                         container
      --sysctl map                       Sysctl options (default map[])
      --tmpfs list                       Mount a tmpfs directory
  -t, --tty                              Allocate a pseudo-TTY
      --ulimit ulimit                    Ulimit options (default [])
  -u, --user string                      Username or UID (format:
                                         <name|uid>[:<group|gid>])
      --userns string                    User namespace to use
      --uts string                       UTS namespace to use
  -v, --volume list                      Bind mount a volume
      --volume-driver string             Optional volume driver for the
                                         container
      --volumes-from list                Mount volumes from the specified
                                         container(s)
  -w, --workdir string                   Working directory inside the
                                         container
```
# EXEC
```markdown
Usage:  docker exec [OPTIONS] CONTAINER COMMAND [ARG...]

Execute a command in a running container

Aliases:
  docker container exec, docker exec

Options:
  -d, --detach               Detached mode: run command in the background
      --detach-keys string   Override the key sequence for detaching a
                             container
  -e, --env list             Set environment variables
      --env-file list        Read in a file of environment variables
  -i, --interactive          Keep STDIN open even if not attached
      --privileged           Give extended privileges to the command
  -t, --tty                  Allocate a pseudo-TTY
  -u, --user string          Username or UID (format:
                             "<name|uid>[:<group|gid>]")
  -w, --workdir string       Working directory inside the container
```
# PS
```markdown
Usage:  docker ps [OPTIONS]

List containers

Aliases:
  docker container ls, docker container list, docker container ps, docker ps

Options:
  -a, --all             Show all containers (default shows just running)
  -f, --filter filter   Filter output based on conditions provided
      --format string   Format output using a custom template:
                        'table':            Print output in table format
                        with column headers (default)
                        'table TEMPLATE':   Print output in table format
                        using the given Go template
                        'json':             Print in JSON format
                        'TEMPLATE':         Print output using the given
                        Go template.
                        Refer to https://docs.docker.com/go/formatting/
                        for more information about formatting output with
                        templates
  -n, --last int        Show n last created containers (includes all
                        states) (default -1)
  -l, --latest          Show the latest created container (includes all
                        states)
      --no-trunc        Don't truncate output
  -q, --quiet           Only display container IDs
  -s, --size            Display total file sizes
```
# Build
```markdown
Start a build

Usage:  docker buildx build [OPTIONS] PATH | URL | -

Start a build

Aliases:
  docker build, docker builder build, docker image build, docker buildx b

Options:
      --add-host strings              Add a custom host-to-IP mapping
                                      (format: "host:ip")
      --allow stringArray             Allow extra privileged entitlement
                                      (e.g., "network.host",
                                      "security.insecure")
      --annotation stringArray        Add annotation to the image
      --attest stringArray            Attestation parameters (format:
                                      "type=sbom,generator=image")
      --build-arg stringArray         Set build-time variables
      --build-context stringArray     Additional build contexts (e.g.,
                                      name=path)
      --builder string                Override the configured builder
                                      instance (default "desktop-linux")
      --cache-from stringArray        External cache sources (e.g.,
                                      "user/app:cache",
                                      "type=local,src=path/to/dir")
      --cache-to stringArray          Cache export destinations (e.g.,
                                      "user/app:cache",
                                      "type=local,dest=path/to/dir")
      --call string                   Set method for evaluating build
                                      ("check", "outline", "targets")
                                      (default "build")
      --cgroup-parent string          Set the parent cgroup for the "RUN"
                                      instructions during build
      --check                         Shorthand for "--call=check" (default )
  -D, --debug                         Enable debug logging
  -f, --file string                   Name of the Dockerfile (default:
                                      "PATH/Dockerfile")
      --iidfile string                Write the image ID to a file
      --label stringArray             Set metadata for an image
      --load                          Shorthand for "--output=type=docker"
      --metadata-file string          Write build result metadata to a file
      --network string                Set the networking mode for the
                                      "RUN" instructions during build
                                      (default "default")
      --no-cache                      Do not use cache when building the image
      --no-cache-filter stringArray   Do not cache specified stages
  -o, --output stringArray            Output destination (format:
                                      "type=local,dest=path")
      --platform stringArray          Set target platform for build
      --progress string               Set type of progress output
                                      ("auto", "quiet", "plain", "tty",
                                      "rawjson"). Use plain to show
                                      container output (default "auto")
      --provenance string             Shorthand for "--attest=type=provenance"
      --pull                          Always attempt to pull all
                                      referenced images
      --push                          Shorthand for "--output=type=registry"
  -q, --quiet                         Suppress the build output and print
                                      image ID on success
      --sbom string                   Shorthand for "--attest=type=sbom"
      --secret stringArray            Secret to expose to the build
                                      (format:
                                      "id=mysecret[,src=/local/secret]")
      --shm-size bytes                Shared memory size for build containers
      --ssh stringArray               SSH agent socket or keys to expose
                                      to the build (format:
                                      "default|<id>[=<socket>|<key>[,<key>]]")
  -t, --tag stringArray               Name and optionally a tag (format:
                                      "name:tag")
      --target string                 Set the target build stage to build
      --ulimit ulimit                 Ulimit options (default [])

Experimental commands and flags are hidden. Set BUILDX_EXPERIMENTAL=1 to show them.
```
# PULL
```markdown
Usage:  docker pull [OPTIONS] NAME[:TAG|@DIGEST]

Download an image from a registry

Aliases:
  docker image pull, docker pull

Options:
  -a, --all-tags                Download all tagged images in the repository
      --disable-content-trust   Skip image verification (default true)
      --platform string         Set platform if server is multi-platform
                                capable
  -q, --quiet                   Suppress verbose output
```
# PUSH
```markdown

Usage:  docker push [OPTIONS] NAME[:TAG]

Upload an image to a registry

Aliases:
  docker image push, docker push

Options:
  -a, --all-tags                Push all tags of an image to the repository
      --disable-content-trust   Skip image signing (default true)
      --platform string         Push a platform-specific manifest as a
                                single-platform image to the registry.
                                Image index won't be pushed, meaning that
                                other manifests, including attestations
                                won't be preserved.
                                'os[/arch[/variant]]': Explicit platform
                                (eg. linux/amd64)
  -q, --quiet                   Suppress verbose output
```
# IMAGES
```markdown
Usage:  docker images [OPTIONS] [REPOSITORY[:TAG]]

List images

Aliases:
  docker image ls, docker image list, docker images

Options:
  -a, --all             Show all images (default hides intermediate images)
      --digests         Show digests
  -f, --filter filter   Filter output based on conditions provided
      --format string   Format output using a custom template:
                        'table':            Print output in table format
                        with column headers (default)
                        'table TEMPLATE':   Print output in table format
                        using the given Go template
                        'json':             Print in JSON format
                        'TEMPLATE':         Print output using the given
                        Go template.
                        Refer to https://docs.docker.com/go/formatting/
                        for more information about formatting output with
                        templates
      --no-trunc        Don't truncate output
  -q, --quiet           Only show image IDs
      --tree            List multi-platform images as a tree (EXPERIMENTAL)
```

# LOGIN
```markdown
Usage:  docker login [OPTIONS] [SERVER]

Authenticate to a registry.
Defaults to Docker Hub if no server is specified.

Options:
  -p, --password string   Password or Personal Access Token (PAT)
      --password-stdin    Take the Password or Personal Access Token
                          (PAT) from stdin
  -u, --username string   Username
```
# Search
```markdown
Usage:  docker search [OPTIONS] TERM

Search Docker Hub for images

Options:
  -f, --filter filter   Filter output based on conditions provided
      --format string   Pretty-print search using a Go template
      --limit int       Max number of search results
      --no-trunc        Don't truncate output
```
# INFO

```markdown
Client:
 Version:    28.0.4
 Context:    desktop-linux
 Debug Mode: false
 Plugins:
  ai: Docker AI Agent - Ask Gordon (Docker Inc.)
    Version:  v1.1.3
    Path:     C:\Program Files\Docker\cli-plugins\docker-ai.exe
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.22.0-desktop.1
    Path:     C:\Program Files\Docker\cli-plugins\docker-buildx.exe
  cloud: Docker Cloud (Docker Inc.)
    Version:  0.2.20
    Path:     C:\Program Files\Docker\cli-plugins\docker-cloud.exe
  compose: Docker Compose (Docker Inc.)
    Version:  v2.34.0-desktop.1
    Path:     C:\Program Files\Docker\cli-plugins\docker-compose.exe
  debug: Get a shell into any image or container (Docker Inc.)
    Version:  0.0.38
    Path:     C:\Program Files\Docker\cli-plugins\docker-debug.exe
  desktop: Docker Desktop commands (Beta) (Docker Inc.)
    Version:  v0.1.6
    Path:     C:\Program Files\Docker\cli-plugins\docker-desktop.exe
  dev: Docker Dev Environments (Docker Inc.)
    Version:  v0.1.2
    Path:     C:\Program Files\Docker\cli-plugins\docker-dev.exe
  extension: Manages Docker extensions (Docker Inc.)
    Version:  v0.2.27
    Path:     C:\Program Files\Docker\cli-plugins\docker-extension.exe
  init: Creates Docker-related starter files for your project (Docker Inc.)
    Version:  v1.4.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-init.exe
  sbom: View the packaged-based Software Bill Of Materials (SBOM) for an image (Anchore Inc.)
    Version:  0.6.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-sbom.exe
  scout: Docker Scout (Docker Inc.)
    Version:  v1.17.0
    Path:     C:\Program Files\Docker\cli-plugins\docker-scout.exe

Server:
 Containers: 0
  Running: 0
  Paused: 0
  Stopped: 0
 Images: 9
 Server Version: 28.0.4
 Storage Driver: overlayfs
  driver-type: io.containerd.snapshotter.v1
 Logging Driver: json-file
 Cgroup Driver: cgroupfs
 Cgroup Version: 1
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local splunk syslog
 CDI spec directories:
  /etc/cdi
  /var/run/cdi
 Swarm: inactive
 Runtimes: io.containerd.runc.v2 nvidia runc
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: xxxxx
 runc version: v1.2.5-0-g59923ef
 init version: de40ad0
 Security Options:
  seccomp
   Profile: unconfined
 Kernel Version: 5.15.133.1-microsoft-standard-WSL2
 Operating System: Docker Desktop
 OSType: linux
 Architecture: x86_64
 CPUs: 8
 Total Memory: 7.645GiB
 Name: docker-desktop
 ID: xxxxxxxxxx
 Docker Root Dir: /var/lib/docker
 Debug Mode: false
 HTTP Proxy: http.docker.internal:3128
 HTTPS Proxy: http.docker.internal:3128
 No Proxy: hubproxy.docker.internal
 Labels:
  com.docker.desktop.address=npipe://\\.\pipe\docker_cli
 Experimental: false
 Insecure Registries:
  hubproxy.docker.internal:4444
  ::1/128
  127.0.0.0/5
 Live Restore Enabled: false

WARNING: No blkio throttle.read_bps_device support
WARNING: No blkio throttle.write_bps_device support
WARNING: No blkio throttle.read_iops_device support
WARNING: No blkio throttle.write_iops_device support
WARNING: DOCKER_INSECURE_NO_IPTABLES_RAW is set
WARNING: daemon is not using the default seccomp profile
```