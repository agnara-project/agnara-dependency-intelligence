# Dependency Injection in Agnara 0.1.0a2

In Agnara, dependency injection separates caller-owned business input from runtime-owned dependencies. The compiled execution plan identifies dependency-backed parameters as protected runtime parameters, so callers provide business payload data while the runtime resolves registered dependencies.

This document is the core educational guide for **Agnara Historical Reference Application #002**, detailing how Agnara separates caller-owned capability inputs from runtime-owned dependencies.

---

## 1. The Core Paradigm: Caller-Owned vs Runtime-Owned

In traditional web frameworks, endpoints often receive request data, database sessions, and configuration mixed into the same argument list or request context.

Agnara explicitly divides a capability's signature into two distinct classes:

```text
def prepare_task_plan(
    task: str,                    <-- Caller-Owned Parameter
    repository: TaskRepository,   <-- Runtime-Owned Dependency
    analyzer: RiskAnalyzer,       <-- Runtime-Owned Dependency
) -> TaskPlan:
```

### Caller-Owned Parameters

- **What they are:** Business inputs required from the caller to perform the requested operation (e.g. `task: str`).
- **Where they originate:** The caller supplies them in `Invocation.payload`.
- **Validation:** Agnara compiles an input schema (via `StandardSchemaAdapter`) and strictly validates each value before handler execution.
- **Access control:** If a caller omits a required input or supplies unexpected fields, Agnara returns a `ValidationError`.

### Runtime-Owned Dependencies

- **What they are:** Infrastructure services, repositories, analyzers, or database clients needed by the capability handler to carry out its task.
- **Where they originate:** The execution runtime resolves them from the `DIRegistry` using registered `@provider` functions.
- **Caller prohibition:** The caller **cannot** supply them. If a caller places `repository` or `analyzer` inside `Invocation.payload`, the runtime detects a protected parameter violation and raises `InvocationError`.

---

## 2. Defining Providers with `@provider`

A provider is a factory function decorated with `@provider` from `agnara.core.di`:

```python
from agnara.core.di import Scope, provider
from domain import InMemoryTaskRepository, TaskRepository


@provider(scope=Scope.SINGLETON)
def provide_task_repository() -> TaskRepository:
    """Instantiate and return the task repository."""
    return InMemoryTaskRepository()
```

### Provider Characteristics

1. **Mandatory Type Annotation:** The provider function must declare an explicit return type hint. The returned type is what `DIRegistry` binds.
2. **Provider Scopes:**
   - `Scope.SINGLETON`: Instantiated once per `DIContainer` and cached globally. Useful for stateless rule engines, connection pools, and immutable repositories.
   - `Scope.INVOCATION`: Instantiated afresh for each capability execution and cached locally within that invocation.
3. **Supported Callables:**
   - Synchronous functions: `def factory() -> T`
   - Asynchronous coroutines: `async def factory() -> T`
   - Synchronous generator contexts: `def factory() -> Iterator[T]` (yields dependency, cleans up afterwards)
   - Asynchronous generator contexts: `async def factory() -> AsyncIterator[T]`

---

## 3. Registering Providers into `DIRegistry`

The `DIRegistry` stores the binding between an interface/type and its provider definition:

```python
from agnara.core.di import DIRegistry
from domain import RiskAnalyzer, RiskRules, TaskRepository

registry = DIRegistry()
registry.bind(TaskRepository, provide_task_repository)
registry.bind(RiskRules, provide_risk_rules)
registry.bind(RiskAnalyzer, provide_risk_analyzer)
```

- `registry.bind(Type, Provider)` binds the exact type to the provider.
- `registry.is_bound(Type)` checks if a type has an assigned provider.
- Binding requires a `ProviderDefinition` produced by `@provider`. Passing an undecorated callable raises a `TypeError`.

---

## 4. Compile-Time Graph Compilation

In Agnara, the dependency graph is **compiled before runtime execution starts**.

When `ExecutionPlan.compile(definition, registry)` is invoked:

```python
plan = ExecutionPlan.compile(
    capabilities["dependency_intelligence.prepare_task_plan"],
    registry,
)
```

The compiler executes `compile_dag(registry, [handler])`:

1. **Signature Reflection:** Reads handler annotations via `get_type_hints(handler)`.
2. **Graph Construction:** Identifies which parameters exist in `DIRegistry`.
3. **Sub-dependency Exploration:** Recursively inspects the parameters required by provider functions. For example:
   - `prepare_task_plan` requires `RiskAnalyzer`.
   - `provide_risk_analyzer` requires `RiskRules`.
   - `provide_risk_rules` requires nothing.
4. **Validation Rules:**
   - **All Provider Parameters Must Be Bound:** Unlike capability handlers, providers **cannot** take caller inputs. If a provider declares an unbound parameter, `DependencyResolutionError` is raised immediately.
   - **Cycle Detection:** If providers depend on each other cyclically (e.g. `A -> B -> A`), `DependencyCycleError` is raised with the cycle path.
5. **Separation of Protected vs Public Parameters:**
   - Parameters matching bound dependencies become `plan.dependency_parameters`.
   - Parameters annotated with `ExecutionContext` become `plan.context_parameters`.
   - The union forms `plan.protected_parameters`.
   - Only parameters **outside** `protected_parameters` are compiled into `plan.input_schemas`.

---

## 5. Runtime Resolution via `DIContainer`

At runtime, an `ExecutionContext` couples an `Invocation` with a `DIContainer`:

```python
container = DIContainer(registry)
context = ExecutionContext(
    Invocation(
        capability_id=plan.definition.id,
        payload={"task": "Add OAuth login to the admin portal"},
        metadata={},
    ),
    container,
)
outcome = await invoke(plan, context)
```

During `invoke()`:

1. **Protected Parameter Guard:** Agnara checks:
   ```python
   supplied_protected = plan.protected_parameters.intersection(invocation.payload)
   if supplied_protected:
       raise InvocationError(...)
   ```
2. **Input Validation:** Payload is validated against `plan.input_schemas`.
3. **Resolution via `DIContainer.resolve_dependencies`:**
   - Traverses the compiled dependency list for the handler.
   - Resolves dependencies and their sub-dependencies.
   - Respects `Scope.SINGLETON` (cached across container lifecycle) and `Scope.INVOCATION` (cached per call).
   - Manages generator context entry and teardown using `AsyncExitStack`.
   - Merges caller inputs, resolved dependencies, and context into arguments passed to `handler(**arguments)`.

---

## 6. Failure Modes

| Failure Condition | Diagnostic Exception | When Encountered |
| :--- | :--- | :--- |
| Missing provider for capability argument | `SchemaError` | Compile Time (`ExecutionPlan.compile`) |
| Unbound dependency in a provider | `DependencyResolutionError` | Compile Time (`ExecutionPlan.compile`) |
| Circular dependency among providers | `DependencyCycleError` | Compile Time (`ExecutionPlan.compile`) |
| Caller passes dependency in payload | `InvocationError` | Invocation Start (`invoke`) |
| Caller passes invalid payload type | `ValidationError` | Invocation Start (`invoke` / `invoke_result`) |
