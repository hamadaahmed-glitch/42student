"""
GCC and Make execution engine.
Compiles C code with strict 42 flags (-Wall -Wextra -Werror) and captures diagnostics.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from student42.core.config import get_settings


@dataclass
class CompilationResult:
    success: bool
    returncode: int
    command: List[str]
    stdout: str
    stderr: str
    duration_sec: float
    output_artifact: Optional[Path] = None


class CompilerEngine:
    """Manages compilation processes for Make targets and single exercise binaries."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def run_make(self, workspace_path: Path, target: str = "all") -> CompilationResult:
        """Executes a target inside the workspace Makefile."""
        cmd = ["make", "-C", str(workspace_path), target]
        start_time = time.perf_counter()

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        duration = time.perf_counter() - start_time

        return CompilationResult(
            success=(proc.returncode == 0),
            returncode=proc.returncode,
            command=cmd,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_sec=round(duration, 3),
        )

    def compile_binary(
        self,
        sources: List[Path],
        output_binary: Path,
        include_dirs: Optional[List[Path]] = None,
        extra_flags: Optional[List[str]] = None,
    ) -> CompilationResult:
        """Compiles a specific binary directly using configured compiler."""
        flags = self.settings.cflags.split()
        if extra_flags:
            flags.extend(extra_flags)

        cmd = [self.settings.cc] + flags

        if include_dirs:
            for inc in include_dirs:
                cmd.extend(["-I", str(inc)])

        cmd.extend([str(s) for s in sources])
        cmd.extend(["-o", str(output_binary)])

        start_time = time.perf_counter()
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        duration = time.perf_counter() - start_time

        return CompilationResult(
            success=(proc.returncode == 0),
            returncode=proc.returncode,
            command=cmd,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_sec=round(duration, 3),
            output_artifact=output_binary if proc.returncode == 0 else None,
        )