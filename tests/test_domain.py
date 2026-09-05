"""Unit tests for the domain layer of Agnara Dependency Intelligence."""

from __future__ import annotations

from domain import (
    HistoricalTask,
    InMemoryTaskRepository,
    RiskAnalyzer,
    RiskRules,
    TaskPlan,
)


def test_historical_task_creation() -> None:
    task = HistoricalTask(
        task_id="HT-999",
        title="Sample task",
        category="testing",
        complexity="low",
        estimated_steps=1,
        keywords=("sample", "testing"),
    )
    assert task.task_id == "HT-999"
    assert task.title == "Sample task"
    assert task.complexity == "low"
    assert task.estimated_steps == 1


def test_in_memory_repository_find_related() -> None:
    repo = InMemoryTaskRepository()

    # Matches HT-101 and HT-102 via 'oauth', 'login', 'admin'
    matches_oauth = repo.find_related("Add OAuth login to the admin portal")
    matched_ids = [t.task_id for t in matches_oauth]
    assert "HT-101" in matched_ids
    assert "HT-102" in matched_ids
    assert "HT-104" not in matched_ids

    # Unrelated task
    matches_unrelated = repo.find_related("Paint the office conference room blue")
    assert len(matches_unrelated) == 0


def test_risk_rules_scenario_a_medium_risk() -> None:
    rules = RiskRules()
    assessment = rules.evaluate("Add OAuth login to the admin portal")
    assert assessment.risk_level == "medium"
    assert assessment.complexity == "medium"
    assert assessment.requires_review is False
    assert assessment.score >= 10
    assert any("sensitive" in reason.lower() for reason in assessment.reasons)


def test_risk_rules_scenario_b_critical_risk() -> None:
    rules = RiskRules()
    assessment = rules.evaluate(
        "Replace production authentication and migrate customer credentials"
    )
    assert assessment.risk_level == "critical"
    assert assessment.complexity == "high"
    assert assessment.requires_review is True
    assert assessment.score >= 30
    assert any("critical" in reason.lower() for reason in assessment.reasons)


def test_risk_rules_low_risk() -> None:
    rules = RiskRules()
    assessment = rules.evaluate("Update typos in the project documentation")
    assert assessment.risk_level == "low"
    assert assessment.complexity == "low"
    assert assessment.requires_review is False
    assert assessment.score == 0


def test_risk_analyzer_delegates_to_rules() -> None:
    rules = RiskRules()
    analyzer = RiskAnalyzer(rules)
    assert analyzer.rules is rules

    result = analyzer.analyze("Add OAuth login to the admin portal")
    assert result.risk_level == "medium"
    assert result.complexity == "medium"


def test_task_plan_dataclass() -> None:
    plan = TaskPlan(
        task="Test task",
        related_tasks=(),
        complexity="low",
        risk="low",
        estimated_steps=2,
        requires_review=False,
        recommendation="Proceed normally.",
    )
    assert plan.task == "Test task"
    assert plan.complexity == "low"
    assert plan.requires_review is False
