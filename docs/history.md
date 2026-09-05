# Historical Context & Scope

## The Agnara Learning Sequence

The Agnara reference application curriculum is organized as an evolutionary sequence of standalone reference repositories:

```text
#001 — Agnara Task Intelligence
Capabilities, Schema Inference, ExecutionPlan, Invocation, Input Validation, Success / Failure

        ↓

#002 — Agnara Dependency Intelligence (This Repository)
Public inputs vs Runtime-owned dependencies, Providers, DIRegistry, DAG compilation, DIContainer

        ↓

#003 — Agnara Secure Operations
Scopes, Principals, Risk, Policies, Confirmation, Execution governance
```

---

## Historical Scope

This repository intentionally preserves the **`agnara==0.1.0a2`** dependency-injection baseline.

Its purpose is to demonstrate:
- The strict separation between caller-owned capability inputs and runtime-owned dependencies.
- Provider declaration using `@provider` with explicit scopes (`Scope.SINGLETON`, `Scope.INVOCATION`).
- Provider registration using `DIRegistry`.
- Compile-time dependency graph compilation and cycle detection via `ExecutionPlan.compile()`.
- Runtime resolution and lifecycle management via `DIContainer`.

It is not intended to evolve into a showcase of every future Agnara capability. More advanced execution-governance concepts are demonstrated by subsequent Historical Reference Applications.

This repository will **not** add HTTP transports, Model Context Protocol (MCP), Agent-to-Agent (A2A), Event streaming, background tasks, external databases, or LLM integrations.

---

## Historical Baseline Record

| Dimension | Value |
| :--- | :--- |
| **Historical Reference Application** | `#002` |
| **Application Name** | `Agnara Dependency Intelligence` |
| **Application Version** | `0.1.0` |
| **Primary Topic** | `Dependency Injection and runtime-owned dependencies` |
| **Framework** | `Agnara` |
| **Agnara Release** | `0.1.0a2` |
| **Python Requirement** | `>=3.14` |
| **Observed Environment** | `CPython 3.14.4` |
| **Distribution Source** | PyPI (`https://pypi.org/project/agnara/`) |
| **Repository Organization** | `agnara-project` |
| **Canonical Repository URL** | `https://github.com/agnara-project/agnara-dependency-intelligence` |
| **Upstream Framework URL** | `https://github.com/Blandskron/agnara` |
| **Preceding Reference Application**| `#001` (`https://github.com/agnara-project/agnara-task-intelligence`) |
