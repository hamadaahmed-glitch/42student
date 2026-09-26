"""
CLI Commands for Gemini AI Agents (Tutor, Debugger, Reviewer, Quiz, and Project Analyst).
"""

from __future__ import annotations

import typer

from student42.ai.agents.debugger import DebuggerAgent
from student42.ai.agents.project_analyst import ProjectAnalystAgent
from student42.ai.agents.quizzer import QuizzerAgent
from student42.ai.agents.reviewer import CodeReviewerAgent
from student42.ai.agents.tutor import TutorAgent
from student42.cli.ui import TerminalUI, console
from student42.database.connection import get_db_manager
from student42.database.repository import AttemptRepository, ExerciseRepository, ProjectRepository

app = typer.Typer(help="Engage Gemini AI mentor for debugging, theory, and architecture audits.")


def _get_active_slug() -> str:
    db = get_db_manager()
    with db.session() as session:
        active = ProjectRepository(session).get_active_project()
        if not active:
            console.print("[red]No active project selected. Run '42student project select <slug>' first.[/red]")
            raise typer.Exit(code=1)
        return active.slug


@app.command("tutor")
def ask_tutor(topic: str, exercise: str | None = None) -> None:
    """Asks the Socratic Tutor for a theoretical explanation of a low-level topic."""
    slug = _get_active_slug()
    agent = TutorAgent(slug)

    with console.status(f"[bold cyan]Consulting Socratic Tutor regarding '{topic}'..."):
        diag = agent.explain_concept(topic=topic, exercise_name=exercise)

    TerminalUI.render_diagnosis(diag)


@app.command("debug")
def debug_failure(exercise: str, hint_level: int = 1) -> None:
    """Diagnoses latest compiler error, crash, or memory leak for a function."""
    slug = _get_active_slug()
    db = get_db_manager()

    with db.session() as session:
        proj = ProjectRepository(session).get_by_slug(slug)
        ex = ExerciseRepository(session).get_exercise(proj.id, exercise) if proj else None
        attempts = AttemptRepository(session).get_latest_attempts(ex.id, limit=1) if ex else []
        latest = attempts[0] if attempts else None

    agent = DebuggerAgent(slug)
    with console.status(f"[bold cyan]Analyzing diagnostics for {exercise} (Hint Tier {hint_level})..."):
        diag = agent.diagnose_failure(
            exercise_name=exercise,
            hint_level=hint_level,
            compiler_log=latest.compiler_output if latest else None,
            norm_log=latest.norm_output if latest else None,
        )

    TerminalUI.render_diagnosis(diag)


@app.command("review")
def review_code(exercise: str) -> None:
    """Audits your source file against Norminette, code style, and potential risks."""
    slug = _get_active_slug()
    agent = CodeReviewerAgent(slug)

    with console.status(f"[bold cyan]Reviewing code architecture for {exercise}.c..."):
        diag = agent.review_exercise(exercise)

    TerminalUI.render_diagnosis(diag)


@app.command("quiz")
def take_quiz(concept: str | None = None) -> None:
    """Generates a technical 4-choice multiple-choice challenge."""
    slug = _get_active_slug()
    agent = QuizzerAgent(slug)

    with console.status("[bold cyan]Generating targeted low-level challenge..."):
        quiz = agent.generate_quiz(concept)

    console.print(f"\n[bold yellow]Target Concept:[/bold yellow] {quiz.concept}\n")
    console.print(f"[bold white]{quiz.question}[/bold white]\n")

    if quiz.code_context:
        console.print(f"[dim]```c\n{quiz.code_context}\n```[/dim]\n")

    for i, opt in enumerate(quiz.options):
        console.print(f"  [cyan]{i + 1})[/cyan] {opt}")

    ans_str = typer.prompt("\nSelect correct option (1-4)", type=int)
    if (ans_str - 1) == quiz.correct_option_index:
        console.print("[bold green]\n✓ CORRECT![/bold green]")
        console.print(f"[dim]{quiz.explanation}[/dim]")
    else:
        correct_txt = quiz.options[quiz.correct_option_index]
        console.print(f"[bold red]\n✗ INCORRECT. Correct answer: {quiz.correct_option_index + 1}) {correct_txt}[/bold red]")
        console.print(f"[dim]{quiz.explanation}[/dim]")


@app.command("analyze")
def analyze_project() -> None:
    """Performs whole-repository architectural review on Makefiles, headers, and files."""
    slug = _get_active_slug()
    agent = ProjectAnalystAgent(slug)

    with console.status("[bold cyan]Executing whole-repository architecture review..."):
        audit = agent.audit_entire_project()

    TerminalUI.render_audit(audit)