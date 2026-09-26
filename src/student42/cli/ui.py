"""
Rich Terminal UI Formatter.
Renders dashboards, diagnostic panels, test output matrices, and skills graphs.
"""

from __future__ import annotations

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from student42.ai.schemas import AIDiagnosis, ProjectAudit, QuizQuestion
from student42.analytics.skill_matrix import SkillReport
from student42.database.models import Mistake, Student
from student42.execution.test_runner import PipelineResult

console = Console()


class TerminalUI:
    """Renders formatted console output for the 42 Student OS."""

    @staticmethod
    def render_banner(student: Student, active_project_name: str) -> None:
        """Renders the primary student operating system dashboard banner."""
        banner_text = Text()
        banner_text.append("╔════════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner_text.append("║                           42 STUDENT OS                            ║\n", style="bold cyan")
        banner_text.append("╠════════════════════════════════════════════════════════════════════╣\n", style="bold cyan")
        banner_text.append(f"  Student:  {student.username:<18} School:  42 {student.campus}\n", style="bold white")
        banner_text.append(f"  Level:    {student.level:<18.2f} Streak:  {student.current_streak} days\n", style="bold yellow")
        banner_text.append(f"  XP:       {student.xp:<18} Active:  {active_project_name}\n", style="bold green")
        banner_text.append("╚════════════════════════════════════════════════════════════════════╝", style="bold cyan")
        console.print(banner_text)

    @staticmethod
    def render_pipeline_result(result: PipelineResult) -> None:
        """Displays test run outcomes, norm status, and memory reports in a table."""
        status_color = "green" if result.all_passed else "red"
        status_text = "PASS" if result.all_passed else "FAIL"

        table = Table(title=f"Verification Pipeline: {result.exercise_name} [{status_text}]", title_style=f"bold {status_color}")
        table.add_column("Stage", style="bold white")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")

        # Norminette
        norm_status = "[green]✓ PASS[/green]" if result.norm_passed else "[red]✗ FAIL[/red]"
        norm_details = "Norme compliant" if result.norm_passed else "Norminette violations found"
        table.add_row("Norminette", norm_status, norm_details)

        # Compilation
        compile_status = "[green]✓ PASS[/green]" if result.compile_passed else "[red]✗ FAIL[/red]"
        compile_details = "Zero warnings (-Wall -Wextra -Werror)" if result.compile_passed else "Compilation error"
        table.add_row("Compiler (GCC)", compile_status, compile_details)

        # Forbidden Functions
        forb_status = "[green]✓ PASS[/green]" if result.forbidden_passed else "[red]✗ FAIL[/red]"
        forb_details = "Only allowed symbols used" if result.forbidden_passed else f"Forbidden: {', '.join(result.forbidden_violations)}"
        table.add_row("Forbidden Check", forb_status, forb_details)

        # Unit Tests
        test_status = "[green]✓ PASS[/green]" if result.tests_failed == 0 else f"[red]✗ {result.tests_failed} FAILED[/red]"
        test_details = f"{result.tests_passed} passed, {result.tests_failed} failed"
        table.add_row("Unit Tests", test_status, test_details)

        # Valgrind
        mem_status = "[green]✓ CLEAN[/green]" if result.memory_clean else "[red]✗ LEAKS DETECTED[/red]"
        mem_details = "0 bytes lost, 0 errors" if result.memory_clean else "Memory leaks or invalid reads"
        table.add_row("Valgrind Leak Check", mem_status, mem_details)

        console.print(table)

        if not result.norm_passed and result.norm_output:
            console.print(Panel(result.norm_output, title="Norminette Diagnostic", border_style="red"))
        if not result.compile_passed and result.compiler_output:
            console.print(Panel(result.compiler_output, title="Compiler Errors", border_style="red"))

    @staticmethod
    def render_diagnosis(diag: AIDiagnosis) -> None:
        """Renders AI diagnosis according to progressive hint ladder."""
        severity_colors = {
            "info": "blue",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red",
        }
        color = severity_colors.get(diag.severity, "cyan")

        content = Text()
        content.append(f"Problem Category:  {diag.problem_type.upper()}\n", style="bold white")
        content.append(f"Severity:          {diag.severity.upper()}\n\n", style=f"bold {color}")
        content.append("Theoretical Concept:\n", style="bold cyan")
        content.append(f"{diag.concept_explained}\n\n", style="white")
        content.append("Observation:\n", style="bold cyan")
        content.append(f"{diag.observation}\n\n", style="white")
        content.append(f"Hint [Tier {diag.hint_level}]:\n", style="bold yellow")
        content.append(f"{diag.hint_content}\n\n", style="bold white")
        content.append("Next Recommended Action:\n", style="bold green")
        content.append(f"{diag.suggested_action}", style="green")

        console.print(Panel(content, title=f"Gemini Mentor Diagnostic (Hint Tier {diag.hint_level})", border_style=color))

    @staticmethod
    def render_skills(reports: List[SkillReport]) -> None:
        """Displays visual skill tree mastery bars."""
        table = Table(title="Systems Concept Mastery Tree", title_style="bold cyan")
        table.add_column("Concept", style="bold white")
        table.add_column("Mastery", justify="left")
        table.add_column("Percentage", justify="right")
        table.add_column("Tests", justify="right")
        table.add_column("Status", justify="center")

        for r in reports:
            bar_len = 20
            filled = int((r.mastery_percentage / 100.0) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            status = "[red]WEAKNESS[/red]" if r.is_weakness else "[green]STABLE[/green]"
            color = "red" if r.is_weakness else "green"

            table.add_row(
                r.concept.replace("_", " ").title(),
                f"[{color}]{bar}[/{color}]",
                f"{r.mastery_percentage:.1f}%",
                str(r.total_tests),
                status,
            )

        console.print(table)

    @staticmethod
    def render_mistakes(mistakes: List[Mistake]) -> None:
        """Renders personal bug database."""
        table = Table(title="Personal Bug & Mistake Database", title_style="bold red")
        table.add_column("Category", style="bold yellow")
        table.add_column("Occurrences", justify="center", style="bold white")
        table.add_column("Latest Error Sample", style="white")
        table.add_column("Root Cause / Explanation", style="dim")

        for m in mistakes:
            table.add_row(
                m.category,
                str(m.occurrences),
                m.raw_error[:60] + "..." if len(m.raw_error) > 60 else m.raw_error,
                (m.root_cause[:60] + "...") if m.root_cause else "Pending diagnosis",
            )

        console.print(table)

    @staticmethod
    def render_audit(audit: ProjectAudit) -> None:
        """Displays project architectural audit."""
        content = Text()
        content.append(f"Architecture Quality Score: {audit.architecture_score} / 100\n\n", style="bold green")

        if audit.norm_risks:
            content.append("Norminette Risks:\n", style="bold yellow")
            for r in audit.norm_risks:
                content.append(f" • {r}\n", style="yellow")
            content.append("\n")

        if audit.memory_risks:
            content.append("Memory Management Risks:\n", style="bold red")
            for m in audit.memory_risks:
                content.append(f" • {m}\n", style="red")
            content.append("\n")

        if audit.makefile_issues:
            content.append("Makefile Integrity:\n", style="bold cyan")
            for issue in audit.makefile_issues:
                content.append(f" • {issue}\n", style="cyan")
            content.append("\n")

        content.append("Learning Observation:\n", style="bold white")
        content.append(audit.learning_observation, style="dim white")

        console.print(Panel(content, title="Architectural Repository Audit", border_style="cyan"))