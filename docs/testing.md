# Testing Strategy & Verification

The test suite of **Agnara Historical Reference Application #002** serves as an executable specification of Agnara's dependency injection model.

---

## 1. Test Architecture

The tests are organized into four focused modules under `tests/`:

```text
tests/
├── __init__.py
├── test_domain.py            # Unit tests for domain models, repository, rules, and analyzer
├── test_di_registration.py   # Tests for @provider decorator, Scope, and DIRegistry
├── test_plan_compilation.py  # Tests for ExecutionPlan compilation, DAG construction, cycles, errors
└── test_execution.py         # End-to-end tests for runtime execution, isolation, and scope caching
```

---

## 2. Key Invariants Tested

### Invariant 1: Caller Supplies Only Business Data
Verified in `test_caller_payload_contains_only_business_data`:
```python
payload = {"task": "Add OAuth login to the admin portal"}
assert "repository" not in payload
assert "analyzer" not in payload
```
The caller provides only `task`. Agnara supplies `repository` and `analyzer` via DI.

### Invariant 2: Runtime Rejects Protected Parameter Injection
Verified in `test_runtime_rejects_payload_supplying_protected_parameters`:
If a caller attempts to supply `repository` or `analyzer` in `Invocation.payload`, `invoke()` raises `InvocationError`:
```text
invocation payload supplies runtime-owned parameter(s): repository
```

### Invariant 3: Compile-Time Discovery of Unbound Dependencies
Verified in:
- `test_missing_provider_causes_schema_compilation_failure`: If a capability parameter is unbound, `StandardSchemaAdapter` rejects it during plan compilation.
- `test_unbound_subdependency_in_provider_raises_dependency_resolution_error`: If a provider requires an unbound parameter, `compile_dag` raises `DependencyResolutionError`.

### Invariant 4: Compile-Time Cycle Detection
Verified in `test_cyclic_dependencies_raise_dependency_cycle_error`:
If providers form a circular dependency (`A -> B -> A`), `compile_dag` detects the cycle and raises `DependencyCycleError`.

### Invariant 5: Scope Lifetime Caching
Verified in `test_scope_caching_behavior`:
- `Scope.SINGLETON`: The injected `TaskRepository` instance is identical across multiple invocations (`repo1 is repo2`).
- `Scope.INVOCATION`: The injected `RiskAnalyzer` is instantiated afresh per invocation (`analyzer1 is not analyzer2`).

### Invariant 6: Input Validation via Canonical Failures
Verified in `test_caller_payload_validation_failure`:
Passing invalid types (e.g. `{"task": 12345}`) results in a canonical `Failure` with `FailureCode.INVALID_INPUT` and error path `('task',)`.

---

## 3. Running the Tests

Execute pytest with verbose output:

```bash
python -m pytest tests/ -v
```
