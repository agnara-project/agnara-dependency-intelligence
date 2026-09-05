# Agent Instructions & Repository Guide

Welcome, Agent. This repository is **Agnara Historical Reference Application #002: Dependency Intelligence**.

---

## Mandatory Historical Invariant

> **This repository intentionally preserves the `agnara==0.1.0a2` historical baseline. Ordinary maintenance must not upgrade Agnara or migrate the application to newer Agnara APIs.**

- Do **not** upgrade `agnara` in `pyproject.toml`, `requirements.txt`, or GitHub workflows.
- Do **not** import or simulate APIs that exist only in newer Agnara releases or unreleased `main`.
- The installed `agnara==0.1.0a2` wheel from PyPI is the ultimate source of truth for all API signatures and behaviors.

---

## What This Repository Teaches

This repository teaches how Agnara cleanly isolates caller-owned business inputs from runtime-owned dependencies:

1. **Caller-owned parameters:** The business payload supplied by the caller in `Invocation.payload` (e.g. `task: str`).
2. **Runtime-owned dependencies:** Services and repositories resolved by Agnara's DI engine from registered providers (e.g. `TaskRepository`, `RiskAnalyzer`).
3. **Provider declaration:** Using `@provider(scope=Scope.SINGLETON)` or `@provider(scope=Scope.INVOCATION)`.
4. **Registry binding:** Registering providers into `DIRegistry`.
5. **Static graph compilation:** Using `ExecutionPlan.compile()` which calls `compile_dag()` to detect cycles and unbound dependencies before any capability runs.
6. **Container resolution:** Executing capabilities with `DIContainer` managing singleton and invocation scopes with context-exit cleanup.
7. **Protected parameter enforcement:** Automatically rejecting any caller invocation that attempts to supply runtime-owned parameters in its payload (`InvocationError`).

---

## What NOT to Expand Into

To preserve the focus and historical clarity of this reference application, do **not**:

- Add HTTP, REST, or GraphQL endpoints.
- Add Model Context Protocol (MCP) servers or tools.
- Add Agent-to-Agent (A2A) protocols or handshakes.
- Add Event streaming, message buses, or async queues.
- Add external database engines (SQLite, PostgreSQL, MySQL) or ORMs (SQLAlchemy).
- Add caching services (Redis, Memcached).
- Add LLM SDKs (OpenAI, Anthropic, Google GenAI).
- Pass runtime dependencies manually inside `Invocation.payload`.
- Implement security/policy governance features intended for Reference Application #003.

---

## File Synchronization Map

When making maintenance edits, keep the following artifacts synchronized:

| File | Purpose | Synchronization Rule |
| :--- | :--- | :--- |
| `domain.py` | Domain models, repository, rules, analyzer | Must remain pure Python without Agnara imports. |
| `app.py` | Application root, capability, providers, CLI | Must use public `agnara==0.1.0a2` APIs only. |
| `tests/` | Test suite | Must assert behavior on Python 3.14 without warnings. |
| `README.md` | Primary documentation | Must reflect current scenario outputs and architecture. |
| `ARCHITECTURE.md` | Architectural specification | Must reflect the real `0.1.0a2` compilation and execution flow. |
| `docs/*.md` | Deep dive educational docs | Must match actual code and test assertions. |

---

## Quality Gates for Agents

Before completing any task, execute and verify:

```bash
# Verify Python version (must be >= 3.14)
python --version

# Verify Agnara release (must be 0.1.0a2)
python -c "import agnara; print(agnara.__version__)"

# Check formatting
ruff format --check .

# Lint codebase
ruff check .

# Run test suite
python -m pytest tests/ -v

# Run demonstration scenarios
python app.py
```
