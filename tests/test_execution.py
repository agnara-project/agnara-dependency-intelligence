"""Tests for runtime capability execution, dependency resolution, and isolation."""

from __future__ import annotations

import asyncio

import pytest
from agnara import Agnara
from agnara.core.di import DIContainer
from agnara.errors import InvocationError, ValidationError
from agnara.execution import (
    ExecutionContext,
    ExecutionPlan,
    Invocation,
    invoke,
    invoke_result,
)
from agnara.execution.result import Failure, FailureCode

from app import (
    compile_application_and_plan,
    prepare_task_plan,
    run_plan,
)
from domain import (
    InMemoryTaskRepository,
    RiskAnalyzer,
    RiskRules,
    TaskPlan,
    TaskRepository,
)


def test_scenario_a_execution() -> None:
    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            task = "Add OAuth login to the admin portal"
            result = await run_plan(task, plan, container)

            assert isinstance(result, TaskPlan)
            assert result.task == task
            assert result.complexity == "medium"
            assert result.risk == "medium"
            assert result.requires_review is False
            assert result.estimated_steps == 4
            related_ids = [t.task_id for t in result.related_tasks]
            assert "HT-101" in related_ids
            assert "HT-102" in related_ids
            assert "Follow standard authentication integration guidelines." in result.recommendation
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_scenario_b_execution() -> None:
    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            task = "Replace production authentication and migrate customer credentials"
            result = await run_plan(task, plan, container)

            assert isinstance(result, TaskPlan)
            assert result.task == task
            assert result.complexity == "high"
            assert result.risk == "critical"
            assert result.requires_review is True
            assert result.estimated_steps == 8
            related_ids = [t.task_id for t in result.related_tasks]
            assert "HT-103" in related_ids
            assert "Requires multi-party review" in result.recommendation
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_caller_payload_contains_only_business_data() -> None:
    """Proof that caller supplies only business input and no dependencies."""

    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            payload = {"task": "Add OAuth login to the admin portal"}

            # Assert that dependencies are NOT in payload
            assert "repository" not in payload
            assert "analyzer" not in payload

            context = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload=payload,
                    metadata={},
                ),
                container,
            )

            result = await invoke(plan, context)
            assert isinstance(result, TaskPlan)
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_runtime_rejects_payload_supplying_protected_parameters() -> None:
    """Proof that caller cannot manually inject runtime-owned dependencies into payload."""

    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            # Attempt to supply 'repository'
            bad_payload_repo = {
                "task": "Add OAuth login to the admin portal",
                "repository": InMemoryTaskRepository(),
            }
            context_repo = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload=bad_payload_repo,
                    metadata={},
                ),
                container,
            )
            with pytest.raises(
                InvocationError,
                match="invocation payload supplies runtime-owned parameter\\(s\\): repository",
            ):
                await invoke(plan, context_repo)

            # Attempt to supply 'analyzer'
            bad_payload_analyzer = {
                "task": "Add OAuth login to the admin portal",
                "analyzer": RiskAnalyzer(RiskRules()),
            }
            context_analyzer = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload=bad_payload_analyzer,
                    metadata={},
                ),
                container,
            )
            with pytest.raises(
                InvocationError,
                match="invocation payload supplies runtime-owned parameter\\(s\\): analyzer",
            ):
                await invoke(plan, context_analyzer)
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_caller_payload_validation_failure() -> None:
    """Agnara schema validation rejects wrong parameter types with canonical failure."""

    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            invalid_context = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload={"task": 12345},  # int instead of str
                    metadata={},
                ),
                container,
            )

            # invoke() raises ValidationError directly
            with pytest.raises(ValidationError, match="expected str, got int"):
                await invoke(plan, invalid_context)

            # invoke_result() wraps into canonical Failure
            canonical_outcome = await invoke_result(plan, invalid_context)
            assert isinstance(canonical_outcome, Failure)
            assert canonical_outcome.code is FailureCode.INVALID_INPUT
            assert canonical_outcome.message == "expected str, got int"
            assert canonical_outcome.details.get("path") == ("task",)
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_missing_required_caller_input() -> None:
    """Missing caller input is rejected by schema validation."""

    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            empty_context = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload={},
                    metadata={},
                ),
                container,
            )
            with pytest.raises(ValidationError, match="required input is missing"):
                await invoke(plan, empty_context)
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_unexpected_payload_input() -> None:
    """Unexpected payload parameters are rejected."""

    async def _test() -> None:
        _capabilities, plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            extra_context = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload={"task": "Valid task", "extra_argument": "unexpected"},
                    metadata={},
                ),
                container,
            )
            with pytest.raises(ValidationError, match="unexpected input"):
                await invoke(plan, extra_context)
        finally:
            await container.aclose()

    asyncio.run(_test())


def test_handler_directly_callable_without_framework() -> None:
    """Capabilities remain ordinary Python callables for direct unit testing."""
    repo = InMemoryTaskRepository()
    analyzer = RiskAnalyzer(RiskRules())

    result = prepare_task_plan(
        task="Add OAuth login to the admin portal",
        repository=repo,
        analyzer=analyzer,
    )
    assert isinstance(result, TaskPlan)
    assert result.risk == "medium"


def test_scope_caching_behavior() -> None:
    """Verify Singleton vs Invocation scope lifecycle caching across repeated executions."""

    async def _test() -> None:
        _capabilities, _plan, registry = compile_application_and_plan()
        container = DIContainer(registry)
        try:
            captured_instances: list[tuple[TaskRepository, RiskAnalyzer]] = []

            test_app = Agnara("test_scopes")

            @test_app.capability
            def probe_cap(
                task: str,
                repository: TaskRepository,
                analyzer: RiskAnalyzer,
            ) -> str:
                captured_instances.append((repository, analyzer))
                return "ok"

            probe_plan = ExecutionPlan.compile(
                test_app.compile()["test_scopes.probe_cap"], container.registry
            )

            # First invocation
            ctx1 = ExecutionContext(
                Invocation(
                    capability_id=probe_plan.definition.id,
                    payload={"task": "call 1"},
                    metadata={},
                ),
                container,
            )
            await invoke(probe_plan, ctx1)

            # Second invocation
            ctx2 = ExecutionContext(
                Invocation(
                    capability_id=probe_plan.definition.id,
                    payload={"task": "call 2"},
                    metadata={},
                ),
                container,
            )
            await invoke(probe_plan, ctx2)

            assert len(captured_instances) == 2
            repo1, analyzer1 = captured_instances[0]
            repo2, analyzer2 = captured_instances[1]

            # Singleton scope: Same repository instance across invocations
            assert repo1 is repo2

            # Invocation scope: Fresh analyzer instance per invocation
            assert analyzer1 is not analyzer2
        finally:
            await container.aclose()

    asyncio.run(_test())
