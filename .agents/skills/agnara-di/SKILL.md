---
name: agnara-di
description: Guide for authoring, compiling, and testing Agnara 0.1.0a2 dependency injection.
---

# Agnara DI Skill

Use this skill when inspecting, authoring, or verifying dependency injection components in `agnara==0.1.0a2`.

## 1. Permitted Public DI APIs

Import DI components from `agnara.core.di`:

```python
from agnara.core.di import (
    DIContainer,
    DependencyCycleError,
    DependencyResolutionError,
    DIRegistry,
    ProviderDefinition,
    ProviderType,
    Scope,
    compile_dag,
    provider,
)
```

Import execution components from `agnara.execution`:

```python
from agnara.execution import (
    ExecutionContext,
    ExecutionPlan,
    Invocation,
    invoke,
    invoke_result,
)
```

## 2. Declaring Providers

- Always annotate factory return types explicitly.
- Choose appropriate scopes:
  - `Scope.SINGLETON`: Shared for the life of `DIContainer`.
  - `Scope.INVOCATION`: Fresh instance per capability execution.

```python
@provider(scope=Scope.SINGLETON)
def provide_task_repository() -> TaskRepository:
    return InMemoryTaskRepository()


@provider(scope=Scope.INVOCATION)
def provide_risk_analyzer(rules: RiskRules) -> RiskAnalyzer:
    return RiskAnalyzer(rules)
```

## 3. Registering into `DIRegistry`

```python
registry = DIRegistry()
registry.bind(TaskRepository, provide_task_repository)
registry.bind(RiskRules, provide_risk_rules)
registry.bind(RiskAnalyzer, provide_risk_analyzer)
```

## 4. Compiling the Graph

Compile the plan before runtime:

```python
plan = ExecutionPlan.compile(capability_def, registry)
```

- Verify that parameters bound in `registry` appear in `plan.protected_parameters` and `plan.dependencies`.
- Verify that only caller inputs remain in `plan.input_schemas`.

## 5. Avoiding Manual Injection

Never inject dependencies into `Invocation.payload`:

```python
# WRONG (violates runtime parameter protection):
Invocation(capability_id=..., payload={"task": "...", "repository": repo})

# CORRECT (business data only):
Invocation(capability_id=..., payload={"task": "..."}, metadata={})
```
