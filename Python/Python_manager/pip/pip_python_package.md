# `pip` – End-to-End Technical Reference  

---

## 1. Foundations  
* Written in Python, bundled with CPython ≥ 3.4; maintained by PyPA.  
* Implements PEP 508, PEP 517/518, PEP 600, PEP 660, PEP 668 and the 2020 dependency resolver.  
* Installs **sdists**, **wheels**, **editable wheels** (PEP 660) and direct **VCS**/URL sources.  

---

## 2. Package Installation  

### 2.1 Core Syntax  
```bash
# Classic
python -m pip install <specifier> [options]

# Examples
python -m pip install requests==2.32.0
python -m pip install "uvicorn[standard]>=0.29,<0.30"
python -m pip install git+https://github.com/psf/requests.git@main
python -m pip install ./local_pkg/  # path
```

### 2.2 Source Types Accepted  
| Specifier                     | Parsed As                                   |
|-------------------------------|---------------------------------------------|
| `pkgname`                     | PyPI latest compatible release              |
| `pkgname==1.2.*`              | PEP 440 version specifier                   |
| `git+https://…@commit#egg=x`  | VCS (Git/SVN/Hg/Bzr)                        |
| `file:///abs/path/pkg.whl`    | Direct wheel                               |
| `https://example.com/pkg.tgz` | Remote sdist / wheel                        |
| `.` or `../src/pkg`           | Local directory (build → wheel → install)   |

### 2.3 Binary vs. Source  
```
--only-binary :all:         # prefer pre-built wheels
--no-binary :none:          # force sdist + build
```

### 2.4 Build Isolation & Backends  
PEP 517 mandates building in *isolated* envs. Options:  
* `--use-pep517` (default) / `--no-use-pep517`  
* `--no-build-isolation` – reuse invoking interpreter’s site-pkgs  
* Backends: setuptools, hatchling, poetry-core, mesonpep517, etc.  

---

## 3. Dependency Management  

### 3.1 Resolver  
* Backtracking algorithm introduced in pip 20.3.  
* Considers transitive requirements, extras, environment markers.  
* Strategies:  
  * `--upgrade-strategy eager|only-if-needed` (default: *only-if-needed*)  
  * `pip install -U` / `--upgrade`  

### 3.2 Constraint Files  
```
pip install -c constraints.txt <pkgs>
```
Freeze upper bounds without forcing install (`pkg==x.y` allowed).

### 3.3 Extras & Environment Markers  
`fastapi[all]==0.111.0 ; python_version >= "3.9" and sys_platform == "linux"`  

### 3.4 Skipping Deps  
`--no-deps` (build isolation still resolves backend deps).  

---

## 4. Semantic Versioning & PEP 440  

| Operator            | Meaning                                   |
|---------------------|-------------------------------------------|
| `==1.4.3`           | absolute pin                              |
| `==1.4.*`           | prefix match                              |
| `~=1.4`             | compatible release (`>=1.4,<2.0`)         |
| `>=,<=,!=`          | inclusive/exclusive bounds                |
| `===abc`            | arbitrary “exact” identifier              |
| `dev`, `rc`, `post` | pre-/post-releases                        |

`pip` validates tags on wheels; invalid versions -> install refused.

---

## 5. Lock File Handling  

### 5.1 Current State  
`pip` reads **requirements.txt** but does **not** yet output deterministic lock files. Community tools:  

| Tool         | Output File            | Notes                                     |
|--------------|------------------------|-------------------------------------------|
| pip-tools    | `requirements.txt/lock`| `pip-compile` generates fully hashed pins |
| Poetry       | `poetry.lock`          | Internally calls installer-engine         |
| PDM          | `pdm.lock`             | PEP 582 support                           |
| pipenv       | `Pipfile.lock`         | Uses pip-resolver                         |

### 5.2 Future: PEP 665  
Defines `requirements.lock` w/ hash-guaranteed index; implemented prototype in pip-664 fork.  

### 5.3 Hash-Checking Mode  
```
pip install --require-hashes -r req.txt
```
*All* requirements must include `--hash=sha256:...`; blocks supply-chain tampering.

---

## 6. Script Automation / CI  

### 6.1 Non-Interactive Flags  
```
python -m pip install -r req.txt --progress-bar off --no-input --disable-pip-version-check
```

### 6.2 Reproducibility  
* Pin interpreter (`pyenv`, Docker tag).  
* Add `--no-cache-dir` for hermetic builds.  
* Use `python -m pip wheel -r req.txt -w dist/` to pre-bake artifacts.  
* CI matrix example (GitHub Actions):  
```yaml
- name: Cache wheels
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/req.txt') }}
```

### 6.3 Tox / Nox / Hatch envs  
Leverage isolated venvs; pip invoked per environment.  

---

## 7. Package Publishing (Complementary)  

`pip` installs; distribution is handled by:  
```
python -m pip install build twine
python -m build             # sdist + wheel under ./dist
python -m twine upload dist/* --repository pypi
```
Recommended metadata in `pyproject.toml` (PEP 621). Signing: `twine upload --sign --identity <gpg-id>`.

---

## 8. Registry Interaction  

### 8.1 Index Selection  
```
--index-url https://pypi.org/simple
--extra-index-url https://internal/simple
--no-index                     # disable ALL index lookup
```

### 8.2 AuthN / AuthZ  
* Basic auth in URL or via keyring.  
* Environment variables: `PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL`, `PIP_TRUSTED_HOST`.  
* Token pattern (PyPI): `https://__token__:pypi-<hash>@pypi.org/simple`.

### 8.3 Caching  
* Wheels → `~/.cache/pip/wheels`  
* HTTP requests → `~/.cache/pip/http`  
* `--cache-dir <path>` / `--no-cache-dir`.  

### 8.4 Metadata Mirrors  
Implement PEP 503 simple API; ensure deterministic HTML.  

---

## 9. Configuration Management  

### 9.1 File Precedence (High → Low)  
1. CLI flags  
2. Env variables `PIP_*`  
3. `pip.ini` (Windows) / `pip.conf` (Unix)  
4. `~/.config/pip/pip.conf`  
5. `/etc/pip.conf`

Example `~/.config/pip/pip.conf`  
```ini
[global]
index-url = https://pypi.org/simple
require-virtualenv = true
[install]
use-feature = 2020-resolver
```

### 9.2 Tool-wide Features  
```
pip config get|set|unset
```

---

## 10. CLI Command Usage (Most-Used Sub-commands)  

| Command                        | Purpose                                          |
|--------------------------------|--------------------------------------------------|
| `install`                      | Fetch, build, install                            |
| `download`                     | Fetch only                                       |
| `wheel`                        | Build wheels from sdist                          |
| `uninstall`                    | Remove distributions                             |
| `list`, `show`, `search`*      | Query (*search deprecated on PyPI*)              |
| `check`                        | Verify installed dependency satisfaction         |
| `freeze`                       | Emit `pkg==ver` for current env                  |
| `hash`                         | Compute hashes for lock files                    |
| `inspect`                      | (new) introspect packages, metadata, files       |
| `cache`                        | Inspect / purge cache                            |
| `index versions <pkg>`         | List available versions                          |
| `completion`                   | Shell completion code                            |
| `audit` (≥ 23.2)               | Security advisories via OSV DB                   |

Common flags: `-U/--upgrade`, `--pre`, `--user`, `--root <dir>`, `--target <dir>`, `--prefix`.

---

## 11. Security Auditing  

### 11.1 `pip audit`  
* Resolves dependency graph → queries OSV and PyPI advisory DB.  
* Exit code 0 (no vulns), 1 (vulns), 2 (internal error).  
* `--require-hashes` synergizes to block post-download tampering.  

### 11.2 HTTPS Verification & Cert Pinning  
* Uses `certifi` bundle; override: `--cert <pem>`.  
* `--trusted-host <domain>` disables TLS verification (avoid!).  

### 11.3 Upcoming Work  
* PEP 458/480 (TUF signed metadata).  
* Sigstore-based wheel signature verification.  

---

## 12. Environment Management  

### 12.1 Virtual Environments  
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r req.txt
```
`PIP_REQUIRE_VIRTUALENV=1` to block accidental global installs.

### 12.2 Tooling Layer  
| Tool     | Purpose                               |
|----------|---------------------------------------|
| virtualenv | High-performance venv creator       |
| pipx      | Isolated install of CLI apps         |
| conda/mamba | Alt. solver + binary distro        |
| pyenv     | Multiplex CPython versions           |

### 12.3 PEP 582 (`__pypackages__`)  
Experimental, implemented by PDM; pip support not landed.

---

## 13. Advanced Flags Cheat-Sheet  

```
--proxy http://user:pass@host:port            # outbound proxy
--retries 5 --timeout 30                      # network tuning
--prefer-binary                               # pick wheel over sdist
--report report.json                          # JSON install report (PEP 655)
--break-system-packages                       # override Debian/Ubuntu PEP 668 guard
```

---

## 14. Reference Links  
* Source: https://github.com/pypa/pip  
* Docs:   https://pip.pypa.io  
* Packaging Guide: https://packaging.python.org  
* Advisory DB: https://github.com/pypa/advisory-database  
