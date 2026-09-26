"""
CLI Commands for Reference Solution Management.
"""

from __future__ import annotations

import typer
from rich.table import Table

from student42.cli.ui import console
from student42.database.connection import get_db_manager
from student42.database.repository import ProjectRepository, ReferenceRepository
from student42.references.reference_manager import ReferenceManager

app = typer.Typer(help="Manage official subject PDFs, external GitHub repos, and notes.")


@app.command("list")
def list_references() -> None:
    """Lists all registered reference repositories and subjects."""
    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        if not proj:
            console.print("[red]No active project selected.[/red]")
            raise typer.Exit(code=1)

        ref_repo = ReferenceRepository(session)
        refs = ref_repo.list_references(proj.id)

        table = Table(title=f"References: {proj.name}", title_style="bold cyan")
        table.add_column("ID", style="bold white")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", justify="center")

        for r in refs:
            status = "[red]🔒 LOCKED[/red]" if r.is_locked else "[green]🔓 UNLOCKED[/green]"
            table.add_row(str(r.id), r.ref_type, r.name, status)

        console.print(table)


@app.command("add")
def add_github_repo(repo_url: str, name: str, tags: str | None = None) -> None:
    """Clones a GitHub reference solution into managed local storage."""
    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        if not proj:
            console.print("[red]No active project selected.[/red]")
            raise typer.Exit(code=1)
        proj_id = proj.id

    manager = ReferenceManager(proj_id)
    with console.status(f"[bold cyan]Cloning reference repo '{name}'..."):
        item = manager.register_github_repo(repo_url, name, tags)

    console.print(f"[bold green]✓ Cloned and registered reference repo: {item.name}[/bold green]")