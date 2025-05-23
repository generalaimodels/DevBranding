# Comprehensive Guide to `pyproject.toml` & Modern Python Packaging

This document covers everything you need to know about Python’s core packaging specification (`pyproject.toml`), the associated PEPs, build back-ends, tooling configurations, editable installs, dynamic metadata and dependency specification.  

---

## 1. Key PEPs & Their Roles

1. **PEP 518** – Introduces `pyproject.toml` and the `[build-system]` table.  
2. **PEP 517** – Defines the front-end / back-end API for building distributions.  
3. **PEP 660** – Adds “editable installs” support to back-ends via `pyproject.toml`.  

---

## 2. `pyproject.toml` Overview

The single central file for:

- Declaring your build requirements  
- Specifying project metadata  
- Configuring tools (formatters, type‐checkers, linters, etc.)  

It has three primary tables:

1. **`[build-system]`** – Required by PEP 518.  
2. **`[project]`** – Required by PEP 621 (metadata spec).  
3. **`[tool.<toolname>]`** – Any tool‐specific configuration.  

---

## 3. `[build-system]` Table (PEP 518)

Specifies how to build your project into a source or wheel distribution:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
```

- **`requires`**: A list of packages (and optional versions) your build needs installed in an isolated environment.  
- **`build-backend`**: The import path of a build‐backend that implements PEP 517 hooks.  

### Common Back-Ends

| Backend                                | Implements                          |
|----------------------------------------|-------------------------------------|
| `setuptools.build_meta`                | Legacy `setup.py`, PEP 517 hooks    |
| `poetry.core.masonry.api`              | Poetry’s own build routines         |
| `flit_core.buildapi`                   | Flit’s simple build                |
| `hatchling.build`                      | Hatch’s minimal backend             |
| `pdm.pep517.api`                       | PDM’s PEP 517 API                   |

---

## 4. The `[project]` Table (PEP 621)

Standardizes project metadata:

```toml
[project]
name = "my_package"
version = "0.1.0"
description = "A sample package"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name="Alice", email="alice@example.com" }]
dependencies = [
  "requests>=2.25,<3.0",
  "numpy>=1.21"
]
optional-dependencies = { dev = ["pytest", "mypy"] }
classifiers = [
  "Programming Language :: Python :: 3.10",
  "License :: OSI Approved :: MIT License"
]
dynamic = ["version", "dependencies"]
```

- **Static fields**: `name`, `version`, `description`, `authors`, `dependencies`, etc.  
- **`dynamic`**: Lists metadata to be provided at build time (e.g., via SCM tags or code introspection).  

### Dependencies Specification

- **Simple**: `"package>=1.0,<2.0"`  
- **Extras**: `"requests[socks]>=2.25"`  
- **Environment markers**: `"dataclasses; python_version<'3.7'"`  

---

## 5. Tool Configuration: `[tool.*]`

Any TOML table under `[tool.<toolname>]` is reserved for plugin or tooling configuration. Common examples:

```toml
[tool.black]
line-length = 88
target-version = ["py38"]

[tool.isort]
profile = "black"

[tool.mypy]
python_version = 3.10
check_untyped_defs = true

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203"]
```

| Tool    | Config Key Examples                     |
|---------|------------------------------------------|
| Black   | `line-length`, `target-version`          |
| isort   | `profile`, `lines_after_imports`         |
| Mypy    | `python_version`, `plugins`              |
| Flake8  | `max-line-length`, `ignore`, `per-file-ignores` |

---

## 6. Build Back-Ends

### 6.1 setuptools
- Traditional, feature-rich.
- Supports both static metadata in `setup.cfg` and dynamic code in `setup.py`.
- PEP 660 support via `setuptools.build_meta:__legacy__`.

### 6.2 Poetry
- All-in-one: dependency resolver + publishing.
- Stores metadata in `pyproject.toml` under `[tool.poetry]`.
- PEP 517 back-end: `poetry.core.masonry.api`.

### 6.3 Flit
- Minimal: just builds pure-Python wheels.
- Metadata under `[tool.flit.metadata]`.

### 6.4 Hatchling
- Core build back-end for the Hatch ecosystem.
- Config under `[tool.hatch.build]`.

### 6.5 PDM
- PEP 582-based, interactive CLI.
- Metadata under `[tool.pdm]`.
- Implements PEP 517 API.

---

## 7. Editable Installs (PEP 660)

- Traditional `pip install -e .` relied on `setup.py develop`.
- PEP 660 defines a `get_editable()` hook in back-end.
- To enable: your back-end must implement `build_wheel`, `prepare_metadata_for_build_wheel`, **and** `get_editable`.
- Example with setuptools:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

Now `pip install -e .` will symlink or `.pth` your project in.

---

## 8. Dynamic Metadata

Use when values aren’t known at authoring time:

```toml
[project]
dynamic = ["version", "dependencies"]
```

- **Version from SCM**: back-ends can read `git` tags.  
- **Dependencies generated**: custom logic in `build.py`.  

---

## 9. Dependency Specification Deep-Dive

- **Exact**: `foo==1.2.3`
- **Range**: `foo>=1.2,<2.0`
- **Caret**: `foo^1.2.3` (semver, Poetry-only)
- **Tilde**: `foo~=1.2` → `>=1.2,==1.*`
- **Extras**: `foo[extra1,extra2]>=1.0`
- **Markers**: `bar; sys_platform=='win32'`

---

## 10. Putting It All Together: Sample `pyproject.toml`

```toml
[build-system]
requires = [
  "setuptools>=61.0",
  "wheel"
]
build-backend = "setuptools.build_meta"

[project]
name = "awesome_pkg"
version = "0.0.1"
description = "An awesome package"
readme = "README.md"
license = { file = "LICENSE" }
authors = [{ name="Dev", email="dev@example.com" }]
dependencies = [
  "requests>=2.25,<3.0",
  "numpy>=1.20"
]
optional-dependencies = {
  dev = ["pytest>=6.0", "mypy", "flake8"]
}
classifiers = [
  "Programming Language :: Python :: 3.10",
  "License :: OSI Approved :: MIT License"
]
dynamic = ["version"]

[tool.black]
line-length = 88
target-version = ["py310"]

[tool.isort]
profile = "black"

[tool.mypy]
python_version = 3.10
disallow_untyped_defs = true

[tool.flake8]
max-line-length = 88
ignore = ["E203"]
```

---

## 11. Summary

- **PEP 518**: Declare build back-end & its requirements in `[build-system]`.  
- **PEP 517**: Talk to that back-end via standardized hooks.  
- **PEP 660**: Get editable installs without `setup.py`.  
- **PEP 621**: Standardize project metadata in `[project]`.  
- **Tool Tables**: Configure Black, isort, Mypy, Flake8 under `[tool.*]`.  
- **Back-ends**: Choose from setuptools, Poetry, Flit, Hatchling, PDM.  
- **Dynamic metadata** & **dependency spec** give flexibility and precision.  

With this fully in place, any modern Python project is:
- **Fully standardized**: one file to rule them all.  
- **Reusable**: compatible with `pip`, CI, IDEs.  
- **Extensible**: easy to add new tools or custom build steps.  
