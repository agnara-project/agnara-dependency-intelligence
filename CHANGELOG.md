# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-05

### Added

- Initial release of **Agnara Historical Reference Application #002**.
- Pinned to the frozen `agnara==0.1.0a2` PyPI release on Python `>=3.14`.
- Pure domain layer in `domain.py`:
  - `HistoricalTask`, `RiskAssessment`, and `TaskPlan` domain structures.
  - `TaskRepository` interface and `InMemoryTaskRepository` implementation with deterministic task records.
  - `RiskRules` domain rule set and `RiskAnalyzer` domain service.
- Primary capability `dependency_intelligence.prepare_task_plan` demonstrating:
  - Separation between caller-owned input (`task: str`) and runtime-owned dependencies (`TaskRepository`, `RiskAnalyzer`).
  - Provider declarations with `@provider(scope=Scope.SINGLETON)` and `@provider(scope=Scope.INVOCATION)`.
  - Nested DI resolution (`RiskAnalyzer` depending on `RiskRules`).
  - Provider registration into `DIRegistry`.
  - Static DAG graph compilation via `ExecutionPlan.compile()`.
  - Runtime execution and lifecycle resolution via `DIContainer` and `ExecutionContext`.
  - Automatic rejection of caller attempts to supply runtime-owned parameters (`InvocationError`).
  - Strict caller input validation via `StandardSchemaAdapter`.
- Comprehensive educational test suite verifying DI compilation, isolation, validation, and scope lifecycle caching.
- Documentation suite in `docs/` covering dependency injection, capabilities, development, history, and testing.
- Agent handbook `AGENTS.md` and `.agents/skills/` for AI pair programmers.
- GitHub Actions CI workflow for Ubuntu and Windows on Python 3.14.
