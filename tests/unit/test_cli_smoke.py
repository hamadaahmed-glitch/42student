"""
CLI Smoke tests verifying all Typer subcommands register correctly.
"""

from __future__ import annotations

from typer.testing import CliRunner

from student42.main import app

runner = CliRunner()


def test_cli_subcommands_registration():
    """Validates that all Typer sub-applications (ref, project, test, ai, stats, session) are registered."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "project" in result.stdout
    assert "test" in result.stdout
    assert "ai" in result.stdout
    assert "ref" in result.stdout
    assert "stats" in result.stdout
    assert "session" in result.stdout
    assert "init" in result.stdout
    assert "profile" in result.stdout


def test_ref_help_command():
    """Validates that '42student ref --help' executes without AttributeError."""
    result = runner.invoke(app, ["ref", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "add" in result.stdout
    assert "mode" in result.stdout
    assert "unlock" in result.stdout