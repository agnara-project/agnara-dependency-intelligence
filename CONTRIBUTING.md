# Contributing to Agnara Dependency Intelligence

Thank you for your interest in contributing to **Agnara Historical Reference Application #002**!

## Historical Invariant

This repository is intentionally frozen against the public release:

```text
agnara==0.1.0a2
```

The fundamental purpose of this repository is to serve as an immutable reference showing how Dependency Injection and runtime-owned parameters work in that specific release.

### Rules for Contributions

1. **Do not upgrade `agnara`:** The framework dependency must remain `agnara==0.1.0a2`.
2. **Do not introduce APIs from newer releases or unreleased `main`:** If a feature does not exist in `0.1.0a2`, it must not be added here.
3. **Preserve parameter separation:** The caller must supply only business input. Runtime-owned dependencies must never be passed in `Invocation.payload`.
4. **No heavy runtime dependencies:** The application runtime must remain stdlib-only plus `agnara`. Do not introduce web frameworks (FastAPI, Flask), databases, ORMs, Redis, cloud SDKs, or LLM libraries.
5. **Quality gates:** All contributions must pass formatting, linting, tests, and smoke scenarios on Python 3.14:
   ```bash
   ruff format --check .
   ruff check .
   pytest tests/ -v
   python app.py
   ```

## Development Setup

See [docs/development.md](docs/development.md) for step-by-step installation and environment instructions.
