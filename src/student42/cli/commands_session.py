"""
CLI Commands for Timed Study Sessions and Daily Missions.
"""

from __future__ import annotations

import typer
from rich.table import Table

from student42.cli.ui import console
from student42.core.session_controller import SessionController
from student42.database.connection import get_db_manager
from student42.database.repository import ProjectRepository

app = typer.Typer(help="Control timed study sessions and view daily missions.")

_active_session_controller: SessionController | None = None


def _get_controller() -> SessionController:
    global _active_session_controller
    if _active_session_controller is None:
        db = get_db_manager()
        with db.session() as session:
            proj = ProjectRepository(session).get_active_project()
            slug = proj.slug if proj else "libft"
        _active_session_controller = SessionController(slug)
    return _active_session_controller


@app.command("start")
def start_session() -> None:
    """Begins a timed study session."""
    ctrl = _get_controller()
    sid = ctrl.start_session()
    console.print(f"[bold green]▶ Study Session #{sid} started. Good luck cadet![/bold green]")


@app.command("stop")
def stop_session(functions_done: int = 0, hints_used: int = 0) -> None:
    """Concludes active study session and credits earned XP."""
    ctrl = _get_controller()
    try:
        session = ctrl.end_session(functions_completed=functions_done, hints_used=hints_used)
        console.print(f"[bold green]■ Session concluded! +{session.xp_earned} XP awarded.[/bold green]")
    except RuntimeError as e:
        console.print(f"[red]{str(e)}[/red]")


@app.command("daily")
def daily_missions() -> None:
    """Displays today's weakness-targeted study missions."""
    ctrl = _get_controller()
    missions = ctrl.get_daily_missions()

    table = Table(title="Daily Learning Missions", title_style="bold yellow")
    table.add_column("Mission", style="bold white")
    table.add_column("Objective", style="dim")
    table.add_column("Reward", justify="right", style="green")

    for m in missions:
        table.add_row(m.title, m.description, f"+{m.target_xp} XP")

    console.print(table)