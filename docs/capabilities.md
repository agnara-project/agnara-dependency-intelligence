# Capability Specification

This document details the primary capability declared in **Agnara Historical Reference Application #002**.

---

## `dependency_intelligence.prepare_task_plan`

Analyzes proposed software tasks and compiles a deterministic execution plan incorporating historical repository insights and automated risk rules.

### Capability Metadata

- **Namespace:** `dependency_intelligence`
- **Name:** `prepare_task_plan`
- **Qualified Identifier:** `dependency_intelligence.prepare_task_plan`
- **Description:** `"Prepare a deterministic software task execution plan using injected intelligence."`
- **Scopes:** `("tasks:plan",)`
- **Risk Level:** `Risk.LOW`
- **Confirmation:** `Confirmation.NEVER`
- **Idempotency:** `Idempotency.YES`

---

### Signature

```python
def prepare_task_plan(
    task: str,
    repository: TaskRepository,
    analyzer: RiskAnalyzer,
) -> TaskPlan: ...
```

---

### Parameters

| Name | Type | Classification | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `task` | `str` | **Caller-Owned** | `Invocation.payload["task"]` | Plain-text description of the task to plan. |
| `repository` | `TaskRepository` | **Runtime-Owned** | `DIRegistry` / `provide_task_repository` | In-memory repository of historical software tasks. |
| `analyzer` | `RiskAnalyzer` | **Runtime-Owned** | `DIRegistry` / `provide_risk_analyzer` | Risk analysis service configured with `RiskRules`. |

---

### Return Value

Returns a `TaskPlan` dataclass instance:

```python
@dataclass(frozen=True, slots=True)
class TaskPlan:
    task: str
    related_tasks: tuple[HistoricalTask, ...]
    complexity: str
    risk: str
    estimated_steps: int
    requires_review: bool
    recommendation: str
```

---

### Direct Testability

Because Agnara's `@app.capability` decorator returns the underlying callable without wrapping or mutating it, `prepare_task_plan` remains a regular Python function that can be tested directly in unit tests without starting the framework or creating an `ExecutionContext`:

```python
repo = InMemoryTaskRepository()
analyzer = RiskAnalyzer(RiskRules())

plan = prepare_task_plan(
    task="Add OAuth login to the admin portal",
    repository=repo,
    analyzer=analyzer,
)
assert plan.complexity == "medium"
```
