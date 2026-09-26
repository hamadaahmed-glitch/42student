"""
CLI Commands for Running Deterministic Tests, Norminette, and Memory Audits.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
import typer

from student42.cli.ui import TerminalUI, console
from student42.core.config import get_paths
from student42.core.profile_manager import ProfileManager
from student42.database.connection import get_db_manager
from student42.database.repository import AttemptRepository, ExerciseRepository, ProjectRepository
from student42.execution.norminette_runner import NorminetteRunner
from student42.execution.test_runner import TestRunnerOrchestrator
from student42.workspace.path_resolver import PathResolver

app = typer.Typer(help="Execute local tests, Norminette checks, and memory verifications.")


@app.command("run")
def run_test(exercise_name: str) -> None:
    """Compiles and runs the full verification pipeline on a specific exercise."""
    db = get_db_manager()
    paths = get_paths()

    with db.session() as session:
        proj_repo = ProjectRepository(session)
        active = proj_repo.get_active_project()
        if not active:
            console.print("[red]No active project. Select one with '42student project select <slug>'.[/red]")
            raise typer.Exit(code=1)
        slug = active.slug

    template_file = paths.templates_dir / f"{slug}.json"
    template_config = json.loads(template_file.read_text(encoding="utf-8")) if template_file.exists() else {}

    orchestrator = TestRunnerOrchestrator(slug)
    with console.status(f"[bold cyan]Running verification for {exercise_name}..."):
        result = orchestrator.run_exercise(exercise_name, template_config)

    TerminalUI.render_pipeline_result(result)

    if result.all_passed:
        profile = ProfileManager()
        xp, level_up = profile.award_xp("function_cleared")
        console.print(f"[bold green]✓ Function passed all checks! +{xp} XP gained.[/bold green]")
        if level_up > 0:
            console.print("[bold yellow]★ LEVEL UP! You crossed a level boundary! ★[/bold yellow]")


@app.command("norm")
def run_norm(file_name: Optional[str] = None) -> None:
    """Runs Norminette on a single file or the whole active workspace."""
    db = get_db_manager()
    with db.session() as session:
        active = ProjectRepository(session).get_active_project()
        if not active:
            console.print("[red]No active project selected.[/red]")
            raise typer.Exit(code=1)

        resolver = PathResolver(active.slug, active.local_path)

    runner = NorminetteRunner()
    target_path = resolver.find_source_file(file_name) if file_name else resolver.root
    if not target_path or not target_path.exists():
        console.print(f"[red]Target path '{file_name or resolver.root}' not found.[/red]")
        raise typer.Exit(code=1)

    with console.status("[bold cyan]Running Norminette..."):
        res = runner.run(target_path)

    if res.passed:
        console.print(f"[bold green]✓ Norminette OK: {target_path.name}[/bold green]")
    else:
        console.print(f"[bold red]✗ Norminette Errors found in {target_path.name}:[/bold red]")
        for err in res.errors:
            console.print(f"  [red]• Line {err.line}, Col {err.column}: {err.error_code} - {err.description}[/red]")


@app.command("history")
def test_history(exercise_name: str) -> None:
    """Shows past test attempts and failure rates for a function."""
    db = get_db_manager()
    with db.session() as session:
        proj = ProjectRepository(session).get_active_project()
        if not proj:
            console.print("[red]No active project selected.[/red]")
            raise typer.Exit(code=1)

        ex = ExerciseRepository(session).get_exercise(proj.id, exercise_name)
        if not ex:
            console.print(f"[red]Exercise '{exercise_name}' has no logged attempts.[/red]")
            raise typer.Exit(code=1)

        attempts = AttemptRepository(session).get_latest_attempts(ex.id, limit=5)
        console.print(f"[bold cyan]Attempt History for {exercise_name}:[/bold cyan]")
        for i, a in enumerate(attempts, 1):
            status = "[green]PASS[/green]" if a.tests_failed == 0 and a.compile_status else "[red]FAIL[/red]"
            console.print(f"  #{i} [{a.timestamp.strftime('%Y-%m-%d %H:%M')}] {status} | Passed: {a.tests_passed} Failed: {a.tests_failed}")