"""
Scans and parses C codebases for function signatures, header includes, and Makefile targets.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


class FileScanner:
    """Inspects file contents for static analysis and context building."""

    @staticmethod
    def read_file_safe(file_path: Path) -> str:
        """Reads file safely with fallback decoding."""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1", errors="replace")

    @classmethod
    def extract_includes(cls, source_file: Path) -> List[str]:
        """Extracts all #include directives from a C file."""
        content = cls.read_file_safe(source_file)
        pattern = r'#\s*include\s*[<"]([^>"]+)[>"]'
        return re.findall(pattern, content)

    @classmethod
    def has_forbidden_include(cls, source_file: Path, forbidden: List[str]) -> List[str]:
        """Checks if a file includes forbidden headers like <stdio.h>."""
        includes = cls.extract_includes(source_file)
        violations = []
        for inc in includes:
            basename = Path(inc).name
            if basename in forbidden:
                violations.append(inc)
        return violations

    @classmethod
    def parse_makefile_rules(cls, makefile_path: Path) -> Dict[str, bool]:
        """Checks for required 42 Makefile targets: all, clean, fclean, re, bonus."""
        required = ["all", "clean", "fclean", "re", "bonus"]
        rules = {rule: False for rule in required}

        if not makefile_path.exists():
            return rules

        content = cls.read_file_safe(makefile_path)
        for rule in required:
            # Matches rule definitions like: all: or clean:
            if re.search(rf"^{rule}\s*:", content, re.MULTILINE):
                rules[rule] = True

        return rules

    @classmethod
    def get_function_line_count(cls, source_file: Path) -> Dict[str, int]:
        """Estimates function line lengths to verify Norm compliance (<= 25 lines)."""
        content = cls.read_file_safe(source_file)
        lines = content.splitlines()
        functions: Dict[str, int] = {}
        inside_function = False
        current_func_name = ""
        current_lines = 0
        brace_balance = 0

        func_decl_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_* \t]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{?$")

        for line in lines:
            stripped = line.strip()

            if not inside_function:
                match = func_decl_pattern.match(stripped)
                if match and not stripped.startswith("typedef"):
                    current_func_name = match.group(1)
                    inside_function = True
                    current_lines = 0
                    brace_balance = line.count("{") - line.count("}")
                    continue

            if inside_function:
                brace_balance += line.count("{") - line.count("}")
                current_lines += 1

                if brace_balance <= 0:
                    functions[current_func_name] = current_lines
                    inside_function = False
                    current_func_name = ""
                    brace_balance = 0

        return functions