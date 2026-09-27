"""CLI module exports for 42 Student OS."""

from student42.cli import (
    commands_ai,
    commands_project,
    commands_ref,
    commands_session,
    commands_stats,
    commands_test,
    ui,
)

__all__ = [
    "ui",
    "commands_project",
    "commands_test",
    "commands_ai",
    "commands_ref",
    "commands_session",
    "commands_stats",
]