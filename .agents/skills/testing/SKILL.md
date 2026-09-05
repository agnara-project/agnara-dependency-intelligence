---
name: testing
description: Guide for running and extending tests for Agnara Dependency Intelligence.
---

# Testing Skill

Use this skill to run and extend the test suite for **Agnara Historical Reference Application #002**.

## 1. Test Invariant Guidelines

- Keep tests isolated, deterministic, and fast.
- Do not introduce asynchronous test plugins when `asyncio.run()` in standard test functions works cleanly.
- Assert public behavior rather than internal private variables.

## 2. Testing DI Proofs

When testing dependency injection:
1. Test that the caller invokes the capability using **only business data**:
   ```python
   payload = {"task": "Add OAuth login to the admin portal"}
   assert "repository" not in payload
   ```
2. Test that attempting to supply runtime-owned parameters in `payload` raises `InvocationError`.
3. Test compile-time graph validation:
   - Missing provider: raises `SchemaError` (capability argument) or `DependencyResolutionError` (provider argument).
   - Cycles: raises `DependencyCycleError`.
4. Test scope caching:
   - Singletons must maintain object identity across invocations (`a is b`).
   - Invocation-scoped dependencies must yield fresh instances (`a is not b`).

## 3. Running Quality Gates

```bash
ruff format --check .
ruff check .
python -m pytest tests/ -v
python app.py
```
