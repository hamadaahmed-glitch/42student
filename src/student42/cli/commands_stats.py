"""
CLI Commands for Skills, Analytics, and Mistake Tracking.
"""

from __future__ import annotations

import typer

from student42.analytics.skill_matrix import SkillMatrix
from student42.cli.ui import TerminalUI, console
from student42.database.connection import get_db_manager
from student42.database.repository import MistakeRepository, StudentRepository

app = typer.Typer(help="View skills mastery matrix and personal mistake database.")


@app.command("skills")
def show_skills() -> None:
    """Displays dynamic skill tree with mastery percentages."""
    db = get_db_manager()
    with db.session() as session:
        student = StudentRepository(session).get_primary_student()
        student_id = student.id if student else 1

    matrix = SkillMatrix(student_id)
    reports = matrix.get_profile_report()
    TerminalUI.render_skills(reports)


@app.command("mistakes")
def show_mistakes() -> None:
    """Queries the personal mistake database and recurrence patterns."""
    db = get_db_manager()
    with db.session() as session:
        repo = MistakeRepository(session)
        mistakes = repo.get_unresolved_mistakes()

    if not mistakes:
        console.print("[green]No unresolved mistakes logged. Clean slate![/green]")
    else:
        TerminalUI.render_mistakes(mistakes)