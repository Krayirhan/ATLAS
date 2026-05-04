"""Models for the read-only agent layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(slots=True)
class AgentContextSource:
    source_type: str
    label: str
    path: str
    char_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentRunRequest:
    project_name: str
    question: str = ""
    provider: str | None = None
    show_sources: bool = False
    show_context: bool = False


@dataclass(slots=True)
class AgentRunResult:
    agent_name: str
    project_name: str
    status: str
    answer: str
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemorySnapshot:
    project_name: str
    project_type: str
    root: str
    knowledge_path: str
    current_status: str
    risks: str
    next_sprints: str
    release_status: str
    recent_reports: list[str]
    decisions: list[tuple[str, str]]
    context_sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectQARequest:
    project_name: str
    question: str
    provider: str | None = None
    show_sources: bool = False
    show_context: bool = False


@dataclass(slots=True)
class ProjectQAResult:
    agent_name: str
    project_name: str
    status: str
    answer: str
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PlannedFileImpact:
    path: str
    reason: str


@dataclass(slots=True)
class PlanRisk:
    title: str
    detail: str


@dataclass(slots=True)
class PlanAcceptanceCriterion:
    text: str


@dataclass(slots=True)
class PlanTestStep:
    text: str


@dataclass(slots=True)
class SprintPlanSection:
    title: str
    items: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SprintPlan:
    sprint_name: str
    objective: str
    scope: list[str]
    out_of_scope: list[str]
    expected_files: list[PlannedFileImpact]
    risks: list[PlanRisk]
    acceptance_criteria: list[PlanAcceptanceCriterion]
    test_plan: list[PlanTestStep]
    validation_commands: list[str]
    next_dependency: str


@dataclass(slots=True)
class PlannerRequest:
    project_name: str
    goal: str
    provider: str | None = None
    max_sprints: int = 1
    include_files: bool = True
    include_risks: bool = True
    include_tests: bool = True
    language: str = "tr"
    constraints: list[str] = field(default_factory=list)
    show_sources: bool = False
    as_json: bool = False


@dataclass(slots=True)
class PlannerResult:
    agent_name: str
    project_name: str
    goal: str
    status: str
    plan_summary: str
    proposed_sprints: list[SprintPlan]
    risks: list[PlanRisk]
    assumptions: list[str]
    out_of_scope: list[str]
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


ReviewScope = Literal["safety", "ai-layer", "config", "mcp", "tests", "docs", "architecture", "all-light"]
ReviewSeverity = Literal["critical", "high", "medium", "low", "info"]


@dataclass(slots=True)
class ReviewRecommendation:
    title: str
    text: str


@dataclass(slots=True)
class ReviewTestSuggestion:
    text: str


@dataclass(slots=True)
class CodeReviewFinding:
    severity: ReviewSeverity
    category: str
    title: str
    description: str
    affected_file: str
    evidence: str
    recommendation: str
    test_suggestion: str


@dataclass(slots=True)
class CodeReviewRequest:
    project_name: str
    scope: ReviewScope
    provider: str | None = None
    files: list[str] = field(default_factory=list)
    focus: str = ""
    max_files: int = 12
    max_chars_per_file: int = 2000
    include_tests: bool = True
    include_security: bool = True
    include_architecture: bool = True
    language: str = "tr"
    constraints: list[str] = field(default_factory=list)
    show_sources: bool = False
    as_json: bool = False


@dataclass(slots=True)
class CodeReviewResult:
    agent_name: str
    project_name: str
    scope: ReviewScope
    status: str
    summary: str
    findings: list[CodeReviewFinding]
    recommendations: list[ReviewRecommendation]
    test_suggestions: list[ReviewTestSuggestion]
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


AgentTaskType = Literal[
    "project_status",
    "project_question",
    "sprint_plan",
    "code_review",
    "security_review",
    "approval_check",
    "documentation_question",
    "report_question",
    "unknown",
]
AgentResponseMode = Literal["answer", "plan", "review", "approval_preview", "mixed", "refusal_or_warning"]


@dataclass(slots=True)
class AgentRouteDecision:
    task_type: AgentTaskType
    selected_agents: list[str]
    reason: str
    confidence: float
    requires_approval_check: bool
    blocked_by_policy: bool = False


@dataclass(slots=True)
class AgentOrchestrationStep:
    step_name: str
    agent_name: str
    purpose: str
    status: str
    summary: str


@dataclass(slots=True)
class AgentSafetySummary:
    read_only: bool
    can_write_files: bool
    can_run_commands: bool
    can_call_tools: bool
    approval_token_production: bool = False


@dataclass(slots=True)
class MainAgentRequest:
    project_name: str
    user_message: str
    provider: str | None = None
    preferred_mode: str = "auto"
    allow_multi_agent: bool = True
    show_sources: bool = False
    show_routing: bool = False
    language: str = "tr"
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MainAgentResult:
    agent_name: str
    project_name: str
    task_type: AgentTaskType
    response_mode: AgentResponseMode
    route: AgentRouteDecision
    answer: str
    summary: str
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    safety: AgentSafetySummary | None = None
    sub_results: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
