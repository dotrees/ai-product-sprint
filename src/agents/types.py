"""Shared types for AI Product Sprint agents."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SprintContract:
    """Sprint 协商一致的完成标准.

    在每个 Sprint 开始前，Generator 和 Evaluator 协商达成一致。
    """
    generator_goals: list[str] = field(default_factory=list)
    evaluator_criteria: list[str] = field(default_factory=list)
    test_commands: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式供 Agent 阅读."""
        lines = ["## Sprint Contract\n"]
        lines.append("### Generator Goals\n")
        for goal in self.generator_goals:
            lines.append(f"- {goal}")
        lines.append("\n### Evaluator Criteria\n")
        for criterion in self.evaluator_criteria:
            lines.append(f"- {criterion}")
        if self.test_commands:
            lines.append("\n### Test Commands\n")
            for cmd in self.test_commands:
                lines.append(f"- {cmd}")
        return "\n".join(lines)


@dataclass
class EvalResult:
    """Evaluator 的测试结果."""
    passed: bool
    report: str
    bugs: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式."""
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [f"## Evaluation Result: {status}\n"]
        lines.append(f"\n### Report\n{self.report}\n")
        if self.bugs:
            lines.append("\n### Bugs Found\n")
            for bug in self.bugs:
                lines.append(f"- {bug}\n")
        return "\n".join(lines)


@dataclass
class SprintResult:
    """Sprint 的最终结果."""
    success: bool
    message: str
    files_changed: list[str] = field(default_factory=list)
    issues: Optional[list[str]] = None

    def to_markdown(self) -> str:
        """转换为 Markdown 格式."""
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        lines = [f"## Sprint Result: {status}\n"]
        lines.append(f"\n### Message\n{self.message}\n")
        if self.files_changed:
            lines.append("\n### Files Changed\n")
            for f in self.files_changed:
                lines.append(f"- {f}\n")
        if self.issues:
            lines.append("\n### Issues\n")
            for issue in self.issues:
                lines.append(f"- {issue}\n")
        return "\n".join(lines)


@dataclass
class ProductSpec:
    """产品规格（由 Planner 生成）."""
    name: str
    description: str
    frontend_features: list[str] = field(default_factory=list)
    backend_features: list[str] = field(default_factory=list)
    tech_stack: dict[str, str] = field(default_factory=dict)
    pages: list[str] = field(default_factory=list)
    data_models: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """转换为 Markdown 格式."""
        lines = [f"# {self.name}\n"]
        lines.append(f"\n{self.description}\n")
        lines.append("\n## Tech Stack\n")
        for key, value in self.tech_stack.items():
            lines.append(f"- **{key}**: {value}\n")
        if self.frontend_features:
            lines.append("\n## Frontend Features\n")
            for f in self.frontend_features:
                lines.append(f"- {f}\n")
        if self.backend_features:
            lines.append("\n## Backend Features\n")
            for f in self.backend_features:
                lines.append(f"- {f}\n")
        if self.pages:
            lines.append("\n## Pages\n")
            for p in self.pages:
                lines.append(f"- {p}\n")
        if self.data_models:
            lines.append("\n## Data Models\n")
            for m in self.data_models:
                lines.append(f"- {m}\n")
        return "\n".join(lines)
