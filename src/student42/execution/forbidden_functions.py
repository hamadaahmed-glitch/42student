"""
Scans compiled C binaries using `nm` to catch unauthorized library symbols.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set


@dataclass
class ForbiddenCheckResult:
    passed: bool
    forbidden_used: List[str]
    raw_symbols: List[str]


class ForbiddenFunctionsChecker:
    """Verifies that an object or library binary only links allowed external symbols."""

    # Internal system / glibc / compiler symbols that are safe to ignore
    SYSTEM_ALLOWLIST = {
        "__stack_chk_fail",
        "__errno_location",
        "_GLOBAL_OFFSET_TABLE_",
        "__libc_start_main",
    }

    @staticmethod
    def is_nm_available() -> bool:
        return shutil.which("nm") is not None

    @classmethod
    def check_binary(cls, binary_path: Path, allowed_functions: List[str]) -> ForbiddenCheckResult:
        """Inspects dynamic undefined symbols in binary against allowed function names."""
        if not cls.is_nm_available():
            raise RuntimeError("Symbol analyzer `nm` is not installed on this host.")

        # Run nm -u to list undefined external symbols required by this binary
        cmd = ["nm", "-u", str(binary_path)]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Failed to inspect symbols: {proc.stderr}")

        allowed_set: Set[str] = set(allowed_functions) | cls.SYSTEM_ALLOWLIST
        symbols: List[str] = []
        forbidden_found: List[str] = []

        for line in proc.stdout.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # Format usually: '                 U symbol_name' or just 'U symbol_name'
            parts = line_str.split()
            sym = parts[-1]
            # Strip glibc versioning tags like write@@GLIBC_2.2.5
            clean_sym = sym.split("@")[0]
            symbols.append(clean_sym)

            if clean_sym not in allowed_set and not clean_sym.startswith("__"):
                forbidden_found.append(clean_sym)

        return ForbiddenCheckResult(
            passed=(len(forbidden_found) == 0),
            forbidden_used=sorted(list(set(forbidden_found))),
            raw_symbols=symbols,
        )