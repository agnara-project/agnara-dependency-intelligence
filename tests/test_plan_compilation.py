"""Tests for compile-time dependency graph and ExecutionPlan compilation."""

from __future__ import annotations

import pytest
from agnara import Agnara, Risk
from agnara.core.di import (
    DependencyCycleError,
    DependencyResolutionError,
    DIRegistry,
    Scope,
    provider,
)
from agnara.errors import SchemaError
from agnara.execution import ExecutionPlan

from app import (
    compile_application_and_plan,
    provide_risk_analyzer,
)
from domain import (
    RiskAnalyzer,
    TaskRepository,
)


class ServiceA:
    pass


class ServiceB:
    pass


@provider(scope=Scope.INVOCATION)
def provide_cycle_a(b: ServiceB) -> ServiceA:
    return ServiceA()


@provider(scope=Scope.INVOCATION)
def provide_cycle_b(a: ServiceA) -> ServiceB:
    return ServiceB()


def test_execution_plan_compilation_success() -> None:
    _capabilities, plan, _registry = compile_application_and_plan()

    assert str(plan.definition.id) == "dependency_intelligence.prepare_task_plan"
    assert plan.definition.id.namespace == "dependency_intelligence"
    assert plan.definition.id.name == "prepare_task_plan"
    assert plan.definition.scopes == frozenset({"tasks:plan"})
    assert plan.definition.risk is Risk.LOW
    from agnara.capability.metadata import Idempotency

    assert plan.definition.idempotency is Idempotency.YES

    # Verify dependencies inferred from signature and registry
    assert plan.dependencies == (TaskRepository, RiskAnalyzer)
    assert plan.dependency_parameters == frozenset({"repository", "analyzer"})
    assert plan.protected_parameters == frozenset({"repository", "analyzer"})

    # Verify caller-owned inputs
    assert plan.required_inputs == frozenset({"task"})
    assert set(plan.input_schemas.keys()) == {"task"}


def test_missing_provider_causes_schema_compilation_failure() -> None:
    """If a capability parameter is not in DIRegistry, Agnara treats it as caller input.

    Because arbitrary non-dataclass interfaces are not valid caller JSON/input types,
    StandardSchemaAdapter rejects them at plan compilation time.
    """
    empty_registry = DIRegistry()
    test_app = Agnara("test_missing")

    @test_app.capability
    def sample_cap(task: str, repository: TaskRepository) -> str:
        return task

    caps = test_app.compile()

    with pytest.raises(SchemaError, match="not supported by StandardSchemaAdapter"):
        ExecutionPlan.compile(caps["test_missing.sample_cap"], empty_registry)


def test_unbound_subdependency_in_provider_raises_dependency_resolution_error() -> None:
    """If a provider requires an argument that is not registered, compile_dag fails."""
    broken_registry = DIRegistry()
    # Bind RiskAnalyzer, but do NOT bind RiskRules which it requires!
    broken_registry.bind(RiskAnalyzer, provide_risk_analyzer)

    test_app = Agnara("test_unbound_provider")

    @test_app.capability
    def sample_cap(analyzer: RiskAnalyzer) -> str:
        return "ok"

    caps = test_app.compile()

    with pytest.raises(
        DependencyResolutionError, match="requires unbound parameter 'rules' of type"
    ):
        ExecutionPlan.compile(caps["test_unbound_provider.sample_cap"], broken_registry)


def test_cyclic_dependencies_raise_dependency_cycle_error() -> None:
    """If providers form a circular dependency, compile_dag detects and raises."""
    test_app = Agnara("test_cycle")

    cycle_registry = DIRegistry()
    cycle_registry.bind(ServiceA, provide_cycle_a)
    cycle_registry.bind(ServiceB, provide_cycle_b)

    @test_app.capability
    def cap_with_cycle(a: ServiceA) -> str:
        return "ok"

    caps = test_app.compile()

    with pytest.raises(DependencyCycleError, match="Dependency cycle detected"):
        ExecutionPlan.compile(caps["test_cycle.cap_with_cycle"], cycle_registry)
