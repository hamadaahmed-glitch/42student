"""
CLI Commands for Reference Solution Management.
"""

from __future__ import annotations

from typing import Optional
import typer
from rich.table import Table

from student42.cli.ui import console
from student42.database.connection import get_db_manager
from student42.database.repository import ProjectRepository, ReferenceRepository
from student42.references.reference_manager import ReferenceManager

# Typer sub-application instance required by main.py
app = typer.Typer(help="Manage official subject PDFs, external GitHub repos, and notes.")


@app.command("list")
def list_references() -> None:
    """Lists all registered reference repositories and subjects."""
    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        if not proj:
            console.print("[red]No active project selected. Run '42student project select <slug>' first.[/red]")
            raise typer.Exit(code=1)

        ref_repo = ReferenceRepository(session)
        refs = ref_repo.list_references(proj.id)

        table = Table(title=f"References: {proj.name}", title_style="bold cyan")
        table.add_column("ID", style="bold white")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", justify="center")

        if not refs:
            table.add_row("-", "None", "No references registered yet", "[dim]Use 'ref add' to register[/dim]")
        else:
            for r in refs:
                status = "[red]🔒 LOCKED[/red]" if r.is_locked else "[green]🔓 UNLOCKED[/green]"
                table.add_row(str(r.id), r.ref_type, r.name, status)

        console.print(table)


@app.command("add")
def add_github_repo(
    repo_url: str = typer.Argument(..., help="GitHub repository URL or local path"),
    name: str = typer.Argument(..., help="Name for this reference reference (e.g., peer_libft)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags (e.g., linked_lists,pointers)"),
) -> None:
    """Clones a GitHub reference solution into managed local storage."""
    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        if not proj:
            console.print("[red]No active project selected. Run '42student project select <slug>' first.[/red]")
            raise typer.Exit(code=1)
        proj_id = proj.id

    manager = ReferenceManager(proj_id)
    try:
        with console.status(f"[bold cyan]Cloning reference repo '{name}'..."):
            item = manager.register_github_repo(repo_url, name, tags)
        console.print(f"[bold green]✓ Cloned and registered reference repo: [white]{item.name}[/white][/bold green]")
    except Exception as e:
        console.print(f"[bold red]Reference Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("mode")
def set_access_mode(
    mode: str = typer.Argument(..., help="Access policy: strict | study | free")
) -> None:
    """Updates the reference access policy (strict, study, or free)."""
    valid_modes = ["strict", "study", "free"]
    clean_mode = mode.lower().strip()

    if clean_mode not in valid_modes:
        console.print(f"[red]Invalid mode '{mode}'. Choose from: {', '.join(valid_modes)}[/red]")
        raise typer.Exit(code=1)

    db = get_db_manager()
    with db.session() as session:
        proj_repo = ProjectRepository(session)
        proj = proj_repo.get_active_project()
        if not proj:
            console.print("[red]No active project selected. Select one first.[/red]")
            raise typer.Exit(code=1)

        proj.access_mode = clean_mode
        console.print(f"[bold green]✓ Reference access mode set to [cyan]{clean_mode.upper()}[/cyan] for {proj.name}[/bold green]")


@app.command("unlock")
def unlock_reference(
    ref_id: int = typer.Argument(..., help="Database ID of the reference to unlock")
) -> None:
    """Manually unlocks a reference item."""
    db = get_db_manager()
    with db.session() as session:
        ref_repo = ReferenceRepository(session)
        ref_repo.unlock_reference(ref_id)
        console.print(f"[bold green]✓ Unlocked reference ID #{ref_id}[/bold green]")