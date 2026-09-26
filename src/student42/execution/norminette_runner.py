"""
Executes Norminette CLI and parses output into structured diagnostic errors.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from student42.core.config import get_settings


@dataclass
class NormError:
    file_path: str
    line: int
    column: int
    error_code: str
    description: str


@dataclass
class NormResult:
    passed: bool
    errors: List[NormError]
    raw_output: str


class NorminetteRunner:
    """Runs the official 42 Norminette checker on files or directories."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def is_installed(self) -> bool:
        return shutil.which(self.settings.norminette_bin) is not None

    def run(self, target: Path) -> NormResult:
        """Runs norminette against a file or folder and parses the errors."""
        if not self.is_installed():
            return NormResult(
                passed=False,
                errors=[
                    NormError(
                        file_path=str(target),
                        line=0,
                        column=0,
                        error_code="NORMINETTE_NOT_FOUND",
                        description=f"Norminette executable '{self.settings.norminette_bin}' not found on PATH.",
                    )
                ],
                raw_output="",
            )

        cmd = [self.settings.norminette_bin, str(target)]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output = proc.stdout + proc.stderr
        errors = self._parse_output(output)
        return NormResult(
            passed=(len(errors) == 0),
            errors=errors,
            raw_output=output.strip(),
        )

    def _parse_output(self, raw_output: str) -> List[NormError]:
        """
        Parses output in the format:
        Error: TOO_MANY_LINES (line:  26, col:   1): Function has more than 25 lines
        """
        errors: List[NormError] = []
        current_file = ""
        error_pattern = re.compile(
            r"Error:\s+([A-Z_]+)\s+\(line:\s*(\d+),\s*col:\s*(\d+)\):\s*(.+)"
        )

        for line in raw_output.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # File header lines: path/to/file.c: Error! or path/to/file.c: OK!
            if line_str.endswith(": Error!") or line_str.endswith(": OK!"):
                current_file = line_str.split(":")[0].strip()
                continue

            match = error_pattern.search(line_str)
            if match:
                errors.append(
                    NormError(
                        file_path=current_file,
                        error_code=match.group(1),
                        line=int(match.group(2)),
                        column=int(match.group(3)),
                        description=match.group(4).strip(),
                    )
                )

        return errors