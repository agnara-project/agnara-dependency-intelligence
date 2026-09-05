"""Tests for Agnara dependency provider declaration and DIRegistry binding."""

from __future__ import annotations

import pytest
from agnara.core.di import DIRegistry, ProviderDefinition, ProviderType, Scope, provider

from app import (
    build_registry,
    provide_risk_analyzer,
    provide_risk_rules,
    provide_task_repository,
)
from domain import (
    InMemoryTaskRepository,
    RiskAnalyzer,
    RiskRules,
    TaskRepository,
)


def test_provider_decorator_attributes() -> None:
    assert isinstance(provide_task_repository, ProviderDefinition)
    assert provide_task_repository.scope is Scope.SINGLETON
    assert provide_task_repository.provider_type is ProviderType.SYNC_FUNCTION
    assert provide_task_repository.return_type is TaskRepository

    assert isinstance(provide_risk_rules, ProviderDefinition)
    assert provide_risk_rules.scope is Scope.SINGLETON
    assert provide_risk_rules.return_type is RiskRules

    assert isinstance(provide_risk_analyzer, ProviderDefinition)
    assert provide_risk_analyzer.scope is Scope.INVOCATION
    assert provide_risk_analyzer.return_type is RiskAnalyzer


def test_provider_requires_return_type_hint() -> None:
    with pytest.raises(TypeError, match="must declare a return type hint"):

        @provider()
        def untyped_provider():  # type: ignore[no-untyped-def]
            return InMemoryTaskRepository()


def test_registry_binding_and_lookup() -> None:
    registry = build_registry()

    assert registry.is_bound(TaskRepository)
    assert registry.is_bound(RiskRules)
    assert registry.is_bound(RiskAnalyzer)
    assert not registry.is_bound(str)

    p_repo = registry.get_provider(TaskRepository)
    assert p_repo is provide_task_repository

    bindings = registry.all_bindings()
    assert len(bindings) == 3
    assert bindings[TaskRepository] is provide_task_repository
    assert bindings[RiskRules] is provide_risk_rules
    assert bindings[RiskAnalyzer] is provide_risk_analyzer


def test_registry_rejects_plain_callable_without_provider_decorator() -> None:
    registry = DIRegistry()

    def plain_factory() -> TaskRepository:
        return InMemoryTaskRepository()

    with pytest.raises(TypeError, match="must be a ProviderDefinition"):
        registry.bind(TaskRepository, plain_factory)  # type: ignore[arg-type]
