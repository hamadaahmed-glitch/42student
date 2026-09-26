"""
Main Application Entrypoint for 42 Student OS.
Binds all subcommand modules and handles initialization.
"""

from __future__ import annotations

import typer

from student42.cli import (
    commands_ai,
    commands_project,
    commands_ref,
    commands_session,
    commands_stats,
    commands_test,
)
from student42.cli.ui import TerminalUI, console
from student42.core.profile_manager import ProfileManager
from student42.database.connection import get_db_manager
from student42.database.repository import ProjectRepository

app = typer.Typer(
    name="42student",
    help="42 Student OS: AI-powered terminal development & learning environment for 42 School.",
    no_args_is_help=True,
)

# Register Subcommand Groups
app.add_typer(commands_project.app, name="project")
app.add_typer(commands_test.app, name="test")
app.add_typer(commands_ai.app, name="ai")
app.add_typer(commands_ref.app, name="ref")
app.add_typer(commands_stats.app, name="stats")
app.add_typer(commands_session.app, name="session")


@app.command("init")
def initialize(username: str = "cadet", campus: str = "Benguerir") -> None:
    """Initializes your local 42 Student OS profile and database."""
    db = get_db_manager()
    db.init_db()

    profile = ProfileManager(username=username, campus=campus)
    student = profile.get_profile()

    console.print(f"[bold green]✓ Initialized 42 Student OS for [cyan]{student.username}[/cyan] ({student.campus})[/bold green]")
    console.print("[dim]Run '42student profile' or '42student project select libft' to start.[/dim]")


@app.command("profile")
def show_profile() -> None:
    """Displays student profile status, streak, XP, and active project banner."""
    profile = ProfileManager()
    student = profile.get_profile()

    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        active_slug = proj.name if proj else "None (select a project)"

    TerminalUI.render_banner(student, active_slug)


if __name__ == "__main__":
    app()