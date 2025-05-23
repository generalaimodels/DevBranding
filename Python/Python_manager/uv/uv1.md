# uv – Ultra-fast Python Package & Project Manager (written in Rust)

---

## 1. Installation

### 1.1 One-line installer (Linux/macOS)
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

### 1.2 Homebrew (macOS/Linux)
```bash
brew install uv
```

### 1.3 Cargo (if Rust tool-chain is present)
```bash
cargo install uv
```

### 1.4 Windows (Powershell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 1.5 PyPI (virtual-env or pipx)
```bash
pipx install uv     # recommended
# or
pip install uv
```

Binary is dropped into `$HOME/.cargo/bin`, `$HOME/.local/bin`, or the equivalent platform path; add it to `$PATH` if necessary.

---

## 2. Package Installation

```bash
uv pip install <package> [--extras ...] [--dry-run] [--upgrade]
```
Key flags  
- `--upgrade`, `-U` Update existing requirements.  
- `--index-url/-i <url>` Alternative index.  
- `--pre` Allow pre-release versions.  
- `--target <dir>` Install into custom directory (zip-safe for Lambda, Layer, etc.).  

Caching: uv keeps a local wheel cache (`~/.cache/uv/wheels`) enabling multi-second cold installs and sub-second warm installs.

---

## 3. Dependency Management

### 3.1 Generate/Update `requirements.txt`
```bash
uv pip compile pyproject.toml -o requirements.txt
```

### 3.2 Install from lock/requirements
```bash
uv pip sync requirements.txt
```

### 3.3 Optional extras
```bash
uv pip install 'fastapi[all]' --lock
```

Resolver algorithms are implemented in Rust (same as Cargo’s PubGrub) → O(N log N) resolution complexity.

---

## 4. Semantic Versioning Support

uv understands standard PEP 440 & SemVer ranges:

| Constraint | Example | Meaning                              |
|------------|---------|--------------------------------------|
| Exact      | `uv pip install numpy==1.26.4` | Pin to given build |
| Compatible | `^1.26` | `>=1.26,<2.0`                       |
| Wildcard   | `1.*`   | `>=1,<2`                             |
| Range      | `>=1.2,<1.5` | Closed interval                |
| Pre-releases | `--pre` flag | Include rc, beta, alpha |

---

## 5. Lock File Handling

| Lock format       | File          | Command                                    |
|-------------------|--------------|--------------------------------------------|
| uv native (deterministic) | `uv.lock`   | `uv lock`                                 |
| pip-tools style   | `requirements.txt` | `uv pip compile` → pinned hashes          |
| Poetry            | `poetry.lock`      | `uv pip install --sync` (partial support) |
| PEP 665           | future ready        | `uv lock --format pep665`                 |

Lock generation is hash-based (`sha256`) and includes source URL for reproducibility.

---

## 6. Script Automation

Add scripts in `pyproject.toml`:

```toml
[tool.uv.scripts]
test = "pytest -q"
format = "black src tests"
```

Run:
```bash
uv run test
uv run format
```

Shebang helper:
```python
#!/usr/bin/env uv
# uv will create venv + install requires listed in comment block if absent
```

---

## 7. Package Publishing

```bash
uv publish \
  --username $PYPI_USER \
  --password-stdin $PYPI_PASS \
  --repository pypi  # or custom
```
Steps:  
1. Builds sdist + manylinux/macos/windows wheels in isolated build env (PEP 517).  
2. Signs artifacts (`--sign` uses GPG).  
3. Uploads via twine-compatible Rust client with TUF fallback.

---

## 8. Registry Interaction

- Mirrors supported via `.uv/config.toml` or `--index-url`, `--extra-index-url`.
- Token storage encrypted in OS keyring (`SecretService`, `Keychain`, DPAPI).
- TUF metadata validated (PEP 458 draft) when connecting to PyPI.

---

## 9. Configuration Management

System-wide:  
`$XDG_CONFIG_HOME/uv/config.toml` (Linux/macOS)  
`%APPDATA%\uv\config.toml` (Windows)

Sample:
```toml
[defaults]
index-url = "https://pypi.org/simple"
cache-dir = "~/.cache/uv"

[resolver]
max-parallel = 16
pre = true

[virtualenvs]
path = ".venv"
in-project = true
```

Environment variables override config:

| Variable             | Purpose                     |
|----------------------|-----------------------------|
| `UV_INDEX_URL`       | Primary index              |
| `UV_CACHE_DIR`       | Cache root                 |
| `UV_NO_COLOR`        | Disable ANSI output        |
| `UV_MAX_PARALLEL`    | Thread pool size           |

---

## 10. CLI Command Usage (cheat-sheet)

| Category | Command | Description |
|----------|---------|-------------|
| Install  | `uv pip install fastapi` | Install package(s) |
| Upgrade  | `uv pip install -U fastapi` | Update to latest allowed |
| Remove   | `uv pip uninstall fastapi` | Remove package |
| Compile  | `uv pip compile` | Resolve & freeze deps |
| Sync     | `uv pip sync` | Reconcile env with lock |
| Lock     | `uv lock` | Produce `uv.lock` |
| Run      | `uv run <script>` | Execute project script |
| Shell    | `uv venv shell` | Spawn subshell in venv |
| Publish  | `uv publish` | Upload distribution |
| Audit    | `uv audit` | Vulnerability scan |
| Doctor   | `uv doctor` | Diagnose env issues |

All commands support `-q/--quiet`, `-v/--verbose`, and `--json` log modes.

---

## 11. Security Auditing

```bash
uv audit [--output json] [--fix]
```
Pipeline:  
1. Parse installed wheel metadata (or lock file).  
2. Cross-reference against OSV & PyPI CVE feeds.  
3. Prints severity (CVSS), patched versions.  
4. Optional `--fix` reruns resolver constrained by patched versions only.

Reproducible SBOM (`--sbom cyclonedx`) generation available.

---

## 12. Environment Management

### 12.1 Create / Activate Virtual Envs
```bash
uv venv create 3.11    # ~/.virtualenvs/<project>-3.11
uv venv shell          # drops into env
```
Automatic: running any `uv` command inside a project root containing `pyproject.toml` will bootstrap `.venv` if absent (`in-project = true`).

### 12.2 List / Prune
```bash
uv venv list     # shows Python version, path, size
uv venv prune    # remove orphaned envs
```

### 12.3 Global toolchain
```bash
uv python install 3.12.0b1  # portable build, unpacked under ~/.uv/pythons
uv python use 3.12          # set project local interpreter
```

Downloads CPython builds using PEP 711 strategy with signature validation.

---

(End of reference)