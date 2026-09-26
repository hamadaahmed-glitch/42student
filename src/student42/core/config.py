"""
Core Configuration Engine for 42 Student OS.
Handles environment loading, path resolution, tool validation, and application settings.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppPaths:
    """Manages all file system paths used by the OS."""

    def __init__(self, base_override: Path | None = None) -> None:
        if base_override:
            self.root = base_override.resolve()
        elif os.getenv("STUDENT42_HOME"):
            self.root = Path(os.getenv("STUDENT42_HOME")).expanduser().resolve()
        else:
            self.root = Path.home() / ".42student"

        # Derived Application Paths
        self.data_dir = self.root / "data"
        self.cache_dir = self.root / "cache"
        self.logs_dir = self.root / "logs"
        self.references_dir = self.root / "references"
        self.database_file = self.data_dir / "student42.db"

        # Static / Package Configuration Paths (points to package root)
        self.package_root = Path(__file__).resolve().parent.parent.parent.parent
        self.config_dir = self.package_root / "config"
        self.constitutions_dir = self.config_dir / "constitutions"
        self.templates_dir = self.config_dir / "project_templates"

    def ensure_directories(self) -> None:
        """Create runtime directory trees if they do not exist."""
        for path in [
            self.root,
            self.data_dir,
            self.cache_dir,
            self.logs_dir,
            self.references_dir / "official",
            self.references_dir / "github",
            self.references_dir / "local_notes",
        ]:
            path.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application Settings Schema and Environment Loader."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini API Credentials
    gemini_api_key: str = Field(
        default="",
        alias="GEMINI_API_KEY",
        description="Google Gemini API secret key",
    )
    gemini_primary_model: str = Field(
        default="gemini-2.5-pro",
        alias="GEMINI_PRIMARY_MODEL",
    )
    gemini_fast_model: str = Field(
        default="gemini-2.5-flash",
        alias="GEMINI_FAST_MODEL",
    )

    # Runtime Environment
    app_env: Literal["development", "production", "testing"] = Field(
        default="development",
        alias="APP_ENV",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    # Workspaces
    default_workspace_dir: Path = Field(
        default_factory=lambda: Path.home() / "42",
        alias="STUDENT42_WORKSPACE_DIR",
    )

    # C Toolchain Settings
    cc: str = Field(default="gcc", alias="CC")
    cflags: str = Field(default="-Wall -Wextra -Werror", alias="CFLAGS")
    norminette_bin: str = Field(default="norminette", alias="NORMINETTE_BIN")
    valgrind_bin: str = Field(default="valgrind", alias="VALGRIND_BIN")

    # Pedagogical Controls
    default_reference_mode: Literal["strict", "study", "free"] = "strict"
    daily_xp_target: int = Field(default=500, alias="DAILY_XP_TARGET")
    streak_grace_hours: int = Field(default=24, alias="STREAK_GRACE_HOURS")

    def validate_toolchain(self) -> dict[str, bool]:
        """Checks if host compilation and linting binaries are installed."""
        return {
            "compiler": shutil.which(self.cc) is not None,
            "norminette": shutil.which(self.norminette_bin) is not None,
            "valgrind": shutil.which(self.valgrind_bin) is not None,
            "git": shutil.which("git") is not None,
        }


# Singleton accessor
_paths_instance: AppPaths | None = None
_settings_instance: Settings | None = None


def get_paths(base_override: Path | None = None) -> AppPaths:
    """Returns singleton instance of system paths."""
    global _paths_instance
    if _paths_instance is None or base_override is not None:
        _paths_instance = AppPaths(base_override=base_override)
        _paths_instance.ensure_directories()
    return _paths_instance


def get_settings() -> Settings:
    """Returns singleton instance of runtime settings."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance