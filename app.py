"""Agnara Historical Reference Application #002: Dependency Intelligence.

Demonstrates runtime-owned dependency injection, provider registration into
a DIRegistry, compile-time DAG compilation, and runtime container resolution
using agnara==0.1.0a2 on Python 3.14+.
"""

import asyncio

from agnara import Agnara, Risk
from agnara.capability import FrozenCapabilityRegistry
from agnara.core.di import DIContainer, DIRegistry, Scope, provider
from agnara.errors import InvocationError
from agnara.execution import (
    ExecutionContext,
    ExecutionPlan,
    Invocation,
    invoke,
    invoke_result,
)
from agnara.execution.result import FailureCode

from domain import (
    InMemoryTaskRepository,
    RiskAnalyzer,
    RiskRules,
    TaskPlan,
    TaskRepository,
)

__all__ = [
    "app",
    "build_registry",
    "compile_application_and_plan",
    "prepare_task_plan",
    "provide_risk_analyzer",
    "provide_risk_rules",
    "provide_task_repository",
    "run_plan",
]

# 1. Application Composition Root
app = Agnara("dependency_intelligence")


# 2. Capability Declaration
@app.capability(
    name="prepare_task_plan",
    description="Prepare a deterministic software task execution plan using injected intelligence.",
    scopes=("tasks:plan",),
    risk=Risk.LOW,
    idempotent=True,
)
def prepare_task_plan(
    task: str,
    repository: TaskRepository,
    analyzer: RiskAnalyzer,
) -> TaskPlan:
    """Prepare a deterministic task execution plan.

    The caller provides only `task: str`.
    The runtime supplies `TaskRepository` and `RiskAnalyzer` via dependency injection.
    """
    related = repository.find_related(task)
    assessment = analyzer.analyze(task)

    base_steps = 2
    if related:
        base_steps = max(r.estimated_steps for r in related)

    if assessment.risk_level == "critical":
        base_steps = max(base_steps, 8)
        recommendation = "Requires multi-party review and staged migration window."
    elif assessment.risk_level == "medium":
        base_steps = max(base_steps, 4)
        recommendation = "Follow standard authentication integration guidelines."
    else:
        recommendation = "Standard task execution path."

    return TaskPlan(
        task=task,
        related_tasks=related,
        complexity=assessment.complexity,
        risk=assessment.risk_level,
        estimated_steps=base_steps,
        requires_review=assessment.requires_review,
        recommendation=recommendation,
    )


# 3. Dependency Providers
@provider(scope=Scope.SINGLETON)
def provide_task_repository() -> TaskRepository:
    """Provide a singleton in-memory repository of historical task intelligence."""
    return InMemoryTaskRepository()


@provider(scope=Scope.SINGLETON)
def provide_risk_rules() -> RiskRules:
    """Provide a singleton deterministic rule set for evaluating task risk."""
    return RiskRules()


@provider(scope=Scope.INVOCATION)
def provide_risk_analyzer(rules: RiskRules) -> RiskAnalyzer:
    """Provide an invocation-scoped risk analyzer receiving injected rules."""
    return RiskAnalyzer(rules)


# 4. Registry Binding
def build_registry() -> DIRegistry:
    """Construct and configure the DIRegistry with application providers."""
    registry = DIRegistry()
    registry.bind(TaskRepository, provide_task_repository)
    registry.bind(RiskRules, provide_risk_rules)
    registry.bind(RiskAnalyzer, provide_risk_analyzer)
    return registry


def compile_application_and_plan() -> tuple[FrozenCapabilityRegistry, ExecutionPlan, DIRegistry]:
    """Compile the Agnara application and compile the ExecutionPlan with DI graph."""
    capabilities = app.compile()
    registry = build_registry()
    plan = ExecutionPlan.compile(
        capabilities["dependency_intelligence.prepare_task_plan"],
        registry,
    )
    return capabilities, plan, registry


# 5. Execution Routine
async def run_plan(
    task: str,
    plan: ExecutionPlan,
    container: DIContainer,
) -> TaskPlan:
    """Execute the prepare_task_plan capability with caller-supplied task text."""
    context = ExecutionContext(
        Invocation(
            capability_id=plan.definition.id,
            payload={"task": task},
            metadata={},
        ),
        container,
    )
    return await invoke(plan, context)


async def main() -> None:
    """Run educational scenarios demonstrating dependency injection in Agnara."""
    print("=== Agnara Historical Reference Application #002 ===")
    print("Topic: Dependency Injection & Runtime-Owned Dependencies")
    print("Target Framework: agnara==0.1.0a2 (Python >=3.14)\n")

    _capabilities, plan, registry = compile_application_and_plan()
    container = DIContainer(registry)

    try:
        print("[Compilation Inspection]")
        print(f"Capability ID:        {plan.definition.id}")
        print(f"Direct dependencies:  {[d.__name__ for d in plan.dependencies]}")
        print(f"Protected parameters: {sorted(plan.protected_parameters)}")
        print(f"Required inputs:      {sorted(plan.required_inputs)}")
        print(f"Input schemas:        {list(plan.input_schemas.keys())}\n")

        # Scenario A
        task_a = "Add OAuth login to the admin portal"
        print(f"[Scenario A] Input: {task_a!r}")
        plan_a = await run_plan(task_a, plan, container)
        print(f"  Complexity:       {plan_a.complexity}")
        print(f"  Risk:             {plan_a.risk}")
        print(f"  Estimated steps:  {plan_a.estimated_steps}")
        print(f"  Requires review:  {plan_a.requires_review}")
        print(f"  Related tasks:    {[t.task_id for t in plan_a.related_tasks]}")
        print(f"  Recommendation:   {plan_a.recommendation}\n")

        # Scenario B
        task_b = "Replace production authentication and migrate customer credentials"
        print(f"[Scenario B] Input: {task_b!r}")
        plan_b = await run_plan(task_b, plan, container)
        print(f"  Complexity:       {plan_b.complexity}")
        print(f"  Risk:             {plan_b.risk}")
        print(f"  Estimated steps:  {plan_b.estimated_steps}")
        print(f"  Requires review:  {plan_b.requires_review}")
        print(f"  Related tasks:    {[t.task_id for t in plan_b.related_tasks]}")
        print(f"  Recommendation:   {plan_b.recommendation}\n")

        # Negative Demonstration 1: Caller attempting to supply runtime-owned parameter
        print("[Security/Integrity Demonstration: Rejected Runtime-Owned Parameter]")
        try:
            bad_context = ExecutionContext(
                Invocation(
                    capability_id=plan.definition.id,
                    payload={"task": task_a, "repository": InMemoryTaskRepository()},
                    metadata={},
                ),
                container,
            )
            await invoke(plan, bad_context)
            print("  ERROR: Invocation should have been rejected!")
        except InvocationError as err:
            print(f"  Rejected as expected: {err}\n")

        # Negative Demonstration 2: Caller passing invalid input type
        print("[Schema Validation Demonstration: Invalid Caller Input]")
        invalid_context = ExecutionContext(
            Invocation(
                capability_id=plan.definition.id,
                payload={"task": 99999},
                metadata={},
            ),
            container,
        )
        failure_result = await invoke_result(plan, invalid_context)
        print(f"  Canonical Failure Code:    {failure_result.code}")
        print(f"  Canonical Failure Message: {failure_result.message}")
        print(f"  Error Path Details:        {dict(failure_result.details)}")
        assert failure_result.code is FailureCode.INVALID_INPUT

        print("\nAll demonstration scenarios executed successfully.")
    finally:
        await container.aclose()


if __name__ == "__main__":
    asyncio.run(main())
