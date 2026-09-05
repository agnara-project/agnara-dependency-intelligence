"""Domain models, repositories, and services for dependency intelligence.

This module defines pure domain structures and services without framework or
transport coupling. They model task planning, historical task retrieval,
and deterministic risk evaluation.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

__all__ = [
    "HistoricalTask",
    "InMemoryTaskRepository",
    "RiskAnalyzer",
    "RiskAssessment",
    "RiskRules",
    "TaskPlan",
    "TaskRepository",
]


@dataclass(frozen=True, slots=True)
class HistoricalTask:
    """A record of a completed software task used for contextual intelligence."""

    task_id: str
    title: str
    category: str
    complexity: str
    estimated_steps: int
    keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    """The outcome of evaluating a task description against risk rules."""

    risk_level: str
    complexity: str
    requires_review: bool
    score: int
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TaskPlan:
    """A deterministic execution plan compiled for a software task."""

    task: str
    related_tasks: tuple[HistoricalTask, ...]
    complexity: str
    risk: str
    estimated_steps: int
    requires_review: bool
    recommendation: str


class TaskRepository(ABC):
    """Abstract contract for historical task intelligence retrieval."""

    @abstractmethod
    def find_related(self, task: str) -> tuple[HistoricalTask, ...]:
        """Find historical tasks related to the proposed task description."""


class InMemoryTaskRepository(TaskRepository):
    """Deterministic in-memory repository containing reference tasks."""

    def __init__(self, tasks: tuple[HistoricalTask, ...] | None = None) -> None:
        if tasks is None:
            self._tasks: tuple[HistoricalTask, ...] = (
                HistoricalTask(
                    task_id="HT-101",
                    title="Add OAuth login to the admin portal",
                    category="authentication",
                    complexity="medium",
                    estimated_steps=4,
                    keywords=("oauth", "login", "admin", "authentication"),
                ),
                HistoricalTask(
                    task_id="HT-102",
                    title="Implement session timeout for admin users",
                    category="authentication",
                    complexity="low",
                    estimated_steps=2,
                    keywords=("session", "timeout", "admin", "authentication"),
                ),
                HistoricalTask(
                    task_id="HT-103",
                    title="Replace production authentication and migrate customer credentials",
                    category="security-migration",
                    complexity="high",
                    estimated_steps=8,
                    keywords=(
                        "production",
                        "migrate",
                        "credentials",
                        "authentication",
                        "security",
                    ),
                ),
                HistoricalTask(
                    task_id="HT-104",
                    title="Upgrade database connection pool size",
                    category="infrastructure",
                    complexity="low",
                    estimated_steps=2,
                    keywords=("database", "connection", "pool", "infrastructure"),
                ),
                HistoricalTask(
                    task_id="HT-105",
                    title="Add customer export CSV endpoint",
                    category="feature",
                    complexity="low",
                    estimated_steps=3,
                    keywords=("customer", "export", "csv", "endpoint"),
                ),
            )
        else:
            self._tasks = tasks

    def find_related(self, task: str) -> tuple[HistoricalTask, ...]:
        """Find historical tasks that share tokens with the input description."""
        tokens = set(re.findall(r"\b\w+\b", task.lower()))
        matches: list[HistoricalTask] = []
        for historical in self._tasks:
            shared = tokens.intersection(historical.keywords)
            if shared:
                matches.append(historical)
        return tuple(matches)


class RiskRules:
    """Deterministic rule set for computing complexity, risk, and review mandates."""

    CRITICAL_MARKERS: frozenset[str] = frozenset(
        {
            "production",
            "migrate",
            "credentials",
            "secret",
            "drop",
            "delete",
        }
    )
    MEDIUM_MARKERS: frozenset[str] = frozenset(
        {
            "oauth",
            "auth",
            "authentication",
            "login",
            "admin",
            "session",
            "permission",
        }
    )

    def evaluate(self, task: str) -> RiskAssessment:
        words = set(re.findall(r"\b\w+\b", task.lower()))
        critical_hits = sorted(words.intersection(self.CRITICAL_MARKERS))
        medium_hits = sorted(words.intersection(self.MEDIUM_MARKERS))

        reasons: list[str] = []
        score = (len(critical_hits) * 30) + (len(medium_hits) * 10)

        if critical_hits:
            reasons.append(f"Contains critical operation marker(s): {', '.join(critical_hits)}")
        if medium_hits:
            reasons.append(f"Contains sensitive feature marker(s): {', '.join(medium_hits)}")

        if critical_hits:
            risk_level = "critical"
            complexity = "high"
            requires_review = True
        elif medium_hits:
            risk_level = "medium"
            complexity = "medium"
            requires_review = False
        else:
            risk_level = "low"
            complexity = "low"
            requires_review = False
            reasons.append("Standard task with no sensitive keywords detected.")

        return RiskAssessment(
            risk_level=risk_level,
            complexity=complexity,
            requires_review=requires_review,
            score=score,
            reasons=tuple(reasons),
        )


class RiskAnalyzer:
    """Domain service that computes a risk assessment using injected rules."""

    def __init__(self, rules: RiskRules) -> None:
        self._rules = rules

    @property
    def rules(self) -> RiskRules:
        return self._rules

    def analyze(self, task: str) -> RiskAssessment:
        return self._rules.evaluate(task)
