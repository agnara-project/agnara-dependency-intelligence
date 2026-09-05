# Development Guide

This guide describes how to configure your local development environment, run the reference application, execute the test suite, and run quality checks.

---

## 1. Prerequisites

- **Python:** CPython 3.14 or newer.
- **Git:** Standard Git client.

---

## 2. Environment Setup

### On Linux / macOS

```bash
# Clone the repository
git clone https://github.com/agnara-project/agnara-dependency-intelligence.git
cd agnara-dependency-intelligence

# Create virtual environment with Python 3.14
python3.14 -m venv .venv
source .venv/bin/activate

# Install runtime and development dependencies
pip install -r requirements.txt
pip install pytest>=9.0.0 ruff>=0.16.0
```

### On Windows

```bat
# Clone the repository
git clone https://github.com/agnara-project/agnara-dependency-intelligence.git
cd agnara-dependency-intelligence

# Create virtual environment with Python 3.14
py -3.14 -m venv .venv
.venv\Scripts\activate

# Install runtime and development dependencies
pip install -r requirements.txt
pip install pytest>=9.0.0 ruff>=0.16.0
```

---

## 3. Running the Application

Execute the educational demonstration scenarios directly:

```bash
python app.py
```

This runs:
1. Compile-time inspection of direct dependencies, protected parameters, and input schemas.
2. **Scenario A:** Standard authentication task ("Add OAuth login to the admin portal").
3. **Scenario B:** High-risk credential migration ("Replace production authentication and migrate customer credentials").
4. **Negative Demonstration 1:** Attempting to inject runtime-owned dependencies into `Invocation.payload` (rejected by runtime with `InvocationError`).
5. **Negative Demonstration 2:** Passing wrong caller input types (rejected by schema engine with canonical `FailureCode.INVALID_INPUT`).

---

## 4. Running the Test Suite

Run the full pytest suite:

```bash
python -m pytest tests/ -v
```

---

## 5. Code Quality & Formatting

The repository enforces formatting and linting via Ruff:

```bash
# Check formatting
ruff format --check .

# Run linter
ruff check .

# Apply safe auto-fixes
ruff check --fix .
ruff format .
```
