"""
Executes binaries under Valgrind to detect heap leaks and memory faults.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from student42.core.config import get_settings


@dataclass
class MemoryCheckResult:
    clean: bool
    definitely_lost_bytes: int
    indirectly_lost_bytes: int
    error_count: int
    has_uninitialized_values: bool
    raw_valgrind_log: str


class MemoryChecker:
    """Wraps Valgrind execution and parses leak analysis."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_installed(self) -> bool:
        return shutil.which(self.settings.valgrind_bin) is not None

    def run(self, binary_path: Path, args: Optional[List[str]] = None) -> MemoryCheckResult:
        """Executes binary under full leak tracking and returns diagnostic metrics."""
        if not self.is_installed():
            return MemoryCheckResult(
                clean=False,
                definitely_lost_bytes=0,
                indirectly_lost_bytes=0,
                error_count=1,
                has_uninitialized_values=False,
                raw_valgrind_log=f"Valgrind '{self.settings.valgrind_bin}' not found on PATH.",
            )

        cmd = [
            self.settings.valgrind_bin,
            "--leak-check=full",
            "--show-leak-kinds=all",
            "--track-origins=yes",
            "--error-exitcode=42",
            str(binary_path),
        ]
        if args:
            cmd.extend(args)

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output = proc.stderr # Valgrind writes diagnostics to stderr
        return self._parse_valgrind_output(output)

    def _parse_valgrind_output(self, output: str) -> MemoryCheckResult:
        definitely_lost = 0
        indirectly_lost = 0
        error_count = 0
        uninit_detected = "conditional jump or move depends on uninitialised value" in output.lower()

        # Parse definitely lost bytes
        def_match = re.search(r"definitely lost:\s*([0-9,]+)\s*bytes", output)
        if def_match:
            definitely_lost = int(def_match.group(1).replace(",", ""))

        # Parse indirectly lost bytes
        ind_match = re.search(r"indirectly lost:\s*([0-9,]+)\s*bytes", output)
        if ind_match:
            indirectly_lost = int(ind_match.group(1).replace(",", ""))

        # Parse ERROR SUMMARY
        err_match = re.search(r"ERROR SUMMARY:\s*(\d+)\s*errors", output)
        if err_match:
            error_count = int(err_match.group(1))

        is_clean = (definitely_lost == 0 and indirectly_lost == 0 and error_count == 0)

        return MemoryCheckResult(
            clean=is_clean,
            definitely_lost_bytes=definitely_lost,
            indirectly_lost_bytes=indirectly_lost,
            error_count=error_count,
            has_uninitialized_values=uninit_detected,
            raw_valgrind_log=output.strip(),
        )