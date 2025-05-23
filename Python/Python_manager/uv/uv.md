# uv: An Extremely Fast Python Package and Project Manager

**uv** is a high-performance Python package and project manager, written in Rust, designed to be a drop-in replacement for pip, pip-tools, and virtualenv. It offers significant speed improvements and modern features for Python development workflows.

---

## Installation

### Prerequisites

- Python 3.7+
- Rust (for building from source, optional)
- Supported OS: Linux, macOS, Windows

### Installation Methods

#### Using pipx (Recommended)
```bash
pipx install uv
```

#### Using pip
```bash
pip install uv
```

#### Pre-built Binaries
Download from [uv releases](https://github.com/astral-sh/uv/releases) and add to your PATH.

#### From Source
```bash
cargo install --locked uv
```

---

## Package Installation

- Install packages into the current environment:
  ```bash
  uv pip install <package>
  ```
- Install from a requirements file:
  ```bash
  uv pip install -r requirements.txt
  ```
- Install specific versions:
  ```bash
  uv pip install "requests==2.31.0"
  ```

---

## Dependency Management

- Add dependencies to your project:
  ```bash
  uv pip add <package>
  ```
- Remove dependencies:
  ```bash
  uv pip remove <package>
  ```
- Update dependencies:
  ```bash
  uv pip update
  ```

---

## Semantic Versioning

- Supports standard Python version specifiers:
  - Exact: `package==1.2.3`
  - Range: `package>=1.0,<2.0`
  - Compatible: `package~=1.4.2`
- Handles pre-releases and post-releases per PEP 440.

---

## Lock File Handling

- Generates and maintains a `uv.lock` file for reproducible environments.
- Lock file ensures deterministic installs across machines.
- Update lock file:
  ```bash
  uv pip update
  ```
- Install from lock file:
  ```bash
  uv pip sync
  ```

---

## Script Automation

- Define scripts in `pyproject.toml` under `[tool.uv.scripts]`:
  ```toml
  [tool.uv.scripts]
  test = "pytest tests/"
  lint = "flake8 src/"
  ```
- Run scripts:
  ```bash
  uv run test
  uv run lint
  ```

---

## Package Publishing

- Build and publish packages to PyPI or custom registries:
  ```bash
  uv publish
  ```
- Supports PEP 621 metadata in `pyproject.toml`.

---

## Registry Interaction

- Configure custom package indexes:
  ```bash
  uv config set index-url https://custom.pypi.org/simple
  ```
- Authenticate with private registries:
  ```bash
  uv config set pypi-token <token>
  ```

---

## Configuration Management

- Global and project-level configuration via `uv config`:
  - Set config:
    ```bash
    uv config set <key> <value>
    ```
  - View config:
    ```bash
    uv config list
    ```
  - Unset config:
    ```bash
    uv config unset <key>
    ```

---

## CLI Command Usage

- List installed packages:
  ```bash
  uv pip list
  ```
- Show package info:
  ```bash
  uv pip show <package>
  ```
- Uninstall packages:
  ```bash
  uv pip uninstall <package>
  ```
- Freeze environment:
  ```bash
  uv pip freeze
  ```

---

## Security Auditing

- Audit dependencies for known vulnerabilities:
  ```bash
  uv audit
  ```
- Integrates with public vulnerability databases.

---

## Environment Management

- Create isolated Python environments:
  ```bash
  uv venv
  ```
- Activate environment:
  - Unix:
    ```bash
    source .venv/bin/activate
    ```
  - Windows:
    ```bash
    .venv\Scripts\activate
    ```
- Remove environment:
  ```bash
  uv venv remove
  ```

---

**uv** provides a modern, high-performance, and feature-rich alternative to traditional Python package management tools, streamlining workflows for developers and teams.