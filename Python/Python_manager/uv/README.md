# UV: An Exceptionally Fast Python Package Manager

`uv` is a modern, high-performance CLI tool for Python project and environment management. It combines dependency resolution, virtual environments, Python version management, packaging, and publishing into a single, unified interface—while optimizing for speed and reliability.

---

## Table of Contents  
1. [Key Concepts & Architecture](#key-concepts--architecture)  
2. [Installation & Quickstart](#installation--quickstart)  
3. [Project Initialization (`uv init`)](#project-initialization-uv-init)  
4. [Dependency Management](#dependency-management)  
   - `uv add`  
   - `uv remove`  
   - `uv lock`  
   - `uv sync`  
   - `uv export`  
   - `uv tree`  
5. [Environment & Python Management](#environment--python-management)  
   - `uv python`  
   - `uv pip`  
   - `uv venv`  
6. [Running Code & Tools](#running-code--tools)  
   - `uv run`  
   - `uv tool`  
7. [Building & Publishing](#building--publishing)  
   - `uv build`  
   - `uv publish`  
8. [Cache & Self Management](#cache--self-management)  
   - `uv cache`  
   - `uv self`  
9. [Versioning & Shell Completion](#versioning--shell-completion)  
   - `uv version`  
   - `uv generate-shell-completion`  
10. [Global Options & Env Vars](#global-options--env-vars)  
11. [Configuration: `uv.toml` & `pyproject.toml`](#configuration-uvtoml--pyprojecttoml)  
12. [Under the Hood](#under-the-hood)  
13. [Best Practices & Troubleshooting](#best-practices--troubleshooting)  

---

## 1. Key Concepts & Architecture

- **Unified CLI**  
  One tool for creating projects, managing dependencies, Python versions, virtual environments, building, and publishing.

- **Speed**  
  - Parallel resolution of dependencies  
  - Local cache & optimized downloads  
  - Native Rust backend for performance (if applicable)

- **Isolation**  
  - Automatic creation of per-project venvs  
  - Custom Python interpreter management  
  - Lockfile-based reproducibility

- **Lockfile-Driven**  
  Ensures deterministic installs across machines.

---

## 2. Installation & Quickstart

```bash
# Linux/macOS (via shell script)
curl -sSL https://get.uv.dev | bash

# Windows (PowerShell)
irm https://get.uv.dev | iex
```

Verify:
```bash
uv --version
```

---

## 3. Project Initialization (`uv init`)

```bash
uv init [--name <project-name>] [--python <specifier>] [--template <template>]
```

- Creates:
  - `pyproject.toml` (PEP 621-compliant)
  - `uv.toml` (uv-specific config; optional)
  - Virtual environment
- Options:
  - `--name`: project package name
  - `--python`: interpreter spec (e.g., `^3.8`)
  - `--template`: custom scaffolding template

Example:
```bash
uv init --name myapp --python "^3.9"
```

---

## 4. Dependency Management

### `uv add`
Add one or more dependencies to the project.

```bash
uv add <package>[@<version>] [--dev] [--extras <features>]
```

- `--dev`: save under `[project.dev-dependencies]`
- Supports version specifiers (`>=`, `<`, `^`, etc.)

Example:
```bash
uv add requests^2.25.0
uv add pytest --dev
```

### `uv remove`
Remove dependencies.

```bash
uv remove <package> [--dev]
```

### `uv lock`
Generate or update the lockfile (`uv.lock`).

```bash
uv lock [--check] [--no-update]
```

- `--check`: exit non-zero if lockfile is out of date
- `--no-update`: only read existing lockfile

### `uv sync`
Synchronize the virtual environment to match `pyproject.toml` + `uv.lock`.

```bash
uv sync [--no-install]
```

- Installs/removes packages to reflect declared dependencies.

### `uv export`
Export lockfile to alternate formats (e.g., `requirements.txt`).

```bash
uv export --format requirements.txt > requirements.txt
```

### `uv tree`
Visualize dependency graph.

```bash
uv tree [--depth <n>] [--graphviz]
```

---

## 5. Environment & Python Management

### `uv python`
Manage interpreters.

- `uv python list`: list installed Pythons  
- `uv python install <version>`: download & install  
- `uv python remove <version>`  

### `uv pip`
Direct pip-compatible interface inside managed venv.

```bash
uv pip install black
```

### `uv venv`
Create or manage separate venvs.

```bash
uv venv create <name> [--python <specifier>]
uv venv remove <name>
uv venv list
```

---

## 6. Running Code & Tools

### `uv run`
Run commands or scripts within project venv.

```bash
uv run python main.py
uv run pytest -- -q
```

### `uv tool`
Install & run package-provided CLI tools without polluting your venv.

```bash
uv tool run mypy@0.910 -- src/
```

---

## 7. Building & Publishing

### `uv build`
Produce source distributions (`sdist`) and wheels.

```bash
uv build [--sdist] [--wheel] [--out-dir <dir>]
```

### `uv publish`
Upload distributions to a package index.

```bash
uv publish [--repository <name>] [--user <user>] [--password <pwd>]
```

---

## 8. Cache & Self Management

### `uv cache`
Inspect or clear uv’s cache.

```bash
uv cache list
uv cache clear [<package>]
```

### `uv self`
Manage uv installation.

```bash
uv self update
uv self uninstall
```

---

## 9. Versioning & Shell Completion

### `uv version`
Read or bump project version (PEP 621).

```bash
uv version           # current version
uv version patch     # bump patch
uv version minor
uv version major
```

### `uv generate-shell-completion`
Generate shell completions.

```bash
uv generate-shell-completion bash > /etc/bash_completion.d/uv
```

---

## 10. Global Options & Env Vars

- `-q, --quiet`
- `-v, --verbose` (repeat for more verbosity)
- `--color [auto|always|never]`
- `--offline` (disable network)
- `--no-progress`
- `--directory <dir>` (chdir before running)
- `--project <path>`
- `--config-file <file>`
- `--no-config`
- Cache control:
  - `--no-cache`
  - `--cache-dir <dir>`
- Python downloads:
  - `--managed-python` / `--no-managed-python`
  - `--no-python-downloads`

Environment variables mirror flags (e.g., `UV_OFFLINE=1`).

---

## 11. Configuration: `uv.toml` & `pyproject.toml`

Typical `pyproject.toml` snippet:
```toml
[project]
name = "myapp"
version = "0.1.0"
dependencies = [
  "requests>=2.25,<3.0"
]

[project.optional-dependencies]
dev = ["pytest", "flake8"]

[tool.uv]
cache-dir = ".uv_cache"
```

`uv.toml` may override uv-specific settings (cache paths, indexes, plugin configs).

---

## 12. Under the Hood

1. **Dependency Resolution**  
   - SAT solver (parallelized)  
   - Respects PEP 508, extras, markers  
2. **Lockfile (`uv.lock`)**  
   - Captures exact versions, hashes  
   - Ensures reproducible installs  
3. **Virtual Envs**  
   - One venv per project by default  
   - Can manage multiple via `uv venv`  
4. **Cache**  
   - Speeds up downloads & builds  
   - Prunes stale artifacts  
5. **Python Management**  
   - Downloads interpreters from official sources  
   - Isolated from system Python  

---

## 13. Best Practices & Troubleshooting

- Always run `uv lock` after dependency changes.  
- Use `uv sync --check` in CI to catch drift.  
- Pin dependency versions for production.  
- Leverage `uv export` for Docker’s `requirements.txt`.  
- In offline or air-gapped environments, pre-populate cache.  
- If facing SSL issues, try `--native-tls` or `--allow-insecure-host`.

---

With this comprehensive guide, you now have an end-to-end understanding of `uv`—from initialization through publishing. Explore each command with `uv help <command>` and integrate `uv` into your Python workflow to maximize speed, reproducibility, and convenience. 🚀