"""
CLI Commands for Project Management.
"""

from __future__ import annotations

import json
from pathlib import Path
import typer
from rich.table import Table

from student42.cli.ui import console
from student42.core.config import get_paths
from student42.database.connection import get_db_manager
from student42.database.repository import ExerciseRepository, ProjectRepository
from student42.workspace.path_resolver import PathResolver

app = typer.Typer(help="Manage 42 cursus projects and local workspace mappings.")


def _seed_templates_if_needed(session) -> None:
    """Scans config/project_templates and registers any unseeded projects."""
    paths = get_paths()
    proj_repo = ProjectRepository(session)
    ex_repo = ExerciseRepository(session)

    for template_file in paths.templates_dir.glob("*.json"):
        try:
            data = json.loads(template_file.read_text(encoding="utf-8"))
            slug = data["identity"]["slug"]
            if not proj_repo.get_by_slug(slug):
                project = proj_repo.create_or_update_project(
                    slug=slug,
                    name=data["identity"]["name"],
                    tier=data["identity"]["tier"],
                    access_mode=data.get("reference_policy", {}).get("default_mode", "strict"),
                )
                for mod in data.get("curriculum", []):
                    for fn in mod.get("functions", []):
                        ex_repo.register_exercise(
                            project_id=project.id,
                            module_id=mod["module_id"],
                            name=fn["name"],
                            source_file=fn["source_file"],
                            signature=fn.get("signature"),
                        )
        except Exception:
            continue


@app.command("list")
def list_projects() -> None:
    """Lists all available projects and their active status."""
    db = get_db_manager()
    with db.session() as session:
        _seed_templates_if_needed(session)
        repo = ProjectRepository(session)
        projects = repo.list_all()

        table = Table(title="42 Cursus Projects", title_style="bold cyan")
        table.add_column("Slug", style="bold white")
        table.add_column("Name", style="white")
        table.add_column("Tier", style="yellow")
        table.add_column("Access Mode", style="cyan")
        table.add_column("Active", justify="center")

        for p in projects:
            is_active = "[green]▶ ACTIVE[/green]" if p.is_active else "[dim]○[/dim]"
            table.add_row(p.slug, p.name, p.tier, p.access_mode, is_active)

        console.print(table)


@app.command("select")
def select_project(slug: str) -> None:
    """Switches active project context (e.g. libft, ft_printf, get_next_line)."""
    db = get_db_manager()
    with db.session() as session:
        _seed_templates_if_needed(session)
        proj_repo = ProjectRepository(session)
        project = proj_repo.get_by_slug(slug)
        if not project:
            console.print(f"[red]Error: Project '{slug}' not found in registered templates.[/red]")
            raise typer.Exit(code=1)

        proj_repo.set_active_project(slug)
        console.print(f"[bold green]✓ Switched active context to [cyan]{slug}[/cyan][/bold green]")


@app.command("path")
def set_project_path(local_dir: str) -> None:
    """Binds the active project to a directory on your local filesystem."""
    target_path = Path(local_dir).expanduser().resolve()
    if not target_path.exists():
        console.print(f"[red]Error: Path '{target_path}' does not exist on disk.[/red]")
        raise typer.Exit(code=1)

    db = get_db_manager()
    with db.session() as session:
        repo = ProjectRepository(session)
        active = repo.get_active_project()
        if not active:
            console.print("[red]No active project selected. Run '42student project select <slug>' first.[/red]")
            raise typer.Exit(code=1)

        active.local_path = str(target_path)
        console.print(f"[green]✓ Linked [bold]{active.slug}[/bold] to [white]{target_path}[/white][/green]")


@app.command("status")
def project_status() -> None:
    """Displays physical file mapping and exercise completion for active project."""
    db = get_db_manager()
    with db.session() as session:
        repo = ProjectRepository(session)
        active = repo.get_active_project()
        if not active:
            console.print("[red]No active project selected.[/red]")
            raise typer.Exit(code=1)

        resolver = PathResolver(active.slug, active.local_path)
        sources = resolver.list_all_sources()
        headers = resolver.list_all_headers()
        has_makefile = resolver.get_makefile() is not None

        table = Table(title=f"Project Workspace: {active.name}", title_style="bold cyan")
        table.add_column("Attribute", style="bold white")
        table.add_column("Value", style="cyan")

        table.add_row("Filesystem Path", str(resolver.root))
        table.add_row("Root Exists", "[green]YES[/green]" if resolver.exists() else "[red]NO[/red]")
        table.add_row("Makefile Found", "[green]YES[/green]" if has_makefile else "[red]NO[/red]")
        table.add_row("Source Files (.c)", str(len(sources)))
        table.add_row("Header Files (.h)", str(len(headers)))
        table.add_row("Access Mode", active.access_mode)

        console.print(table)