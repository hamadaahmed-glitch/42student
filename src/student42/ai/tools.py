"""
Gemini Function Calling Tool Definitions and Local Dispatcher.
Enables Gemini to inspect files, run tests, and check Norminette autonomously.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List

from google.genai import types

from student42.execution.norminette_runner import NorminetteRunner
from student42.workspace.file_scanner import FileScanner
from student42.workspace.git_engine import GitEngine
from student42.workspace.path_resolver import PathResolver


class AgentToolRegistry:
    """Provides callable host tools for Gemini Function Calling."""

    def __init__(self, project_slug: str, workspace_root: Optional[str] = None) -> None:
        self.project_slug = project_slug
        self.resolver = PathResolver(project_slug, workspace_root)
        self.git_engine = GitEngine(self.resolver.root)
        self.norminette = NorminetteRunner()

    def read_source_file(self, relative_path: str) -> str:
        """Reads the content of any source file or header in the project workspace."""
        try:
            target = self.resolver.resolve_relative_path(relative_path)
            if not target.exists():
                return f"Error: File '{relative_path}' does not exist."
            return FileScanner.read_file_safe(target)
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def list_project_files(self) -> str:
        """Lists all C sources, headers, and Makefiles in the workspace."""
        if not self.resolver.exists():
            return "Error: Workspace does not exist."
        sources = [str(p.relative_to(self.resolver.root)) for p in self.resolver.list_all_sources()]
        headers = [str(p.relative_to(self.resolver.root)) for p in self.resolver.list_all_headers()]
        has_makefile = self.resolver.get_makefile() is not None
        return json.dumps({
            "sources": sources,
            "headers": headers,
            "has_makefile": has_makefile
        })

    def run_norminette(self, relative_path: str) -> str:
        """Runs the 42 Norminette checker on a specific file."""
        try:
            target = self.resolver.resolve_relative_path(relative_path)
            res = self.norminette.run(target)
            return json.dumps({
                "passed": res.passed,
                "errors": [
                    {
                        "code": e.error_code,
                        "line": e.line,
                        "col": e.column,
                        "description": e.description
                    }
                    for e in res.errors
                ]
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_git_diff(self, relative_path: str) -> str:
        """Gets unstaged or committed git changes for a specific file."""
        diff = self.git_engine.get_file_diff(relative_path)
        return diff if diff else "No git changes detected."

    def get_dispatch_map(self) -> Dict[str, Callable[..., Any]]:
        """Maps tool names to Python methods."""
        return {
            "read_source_file": self.read_source_file,
            "list_project_files": self.list_project_files,
            "run_norminette": self.run_norminette,
            "get_git_diff": self.get_git_diff,
        }

    @staticmethod
    def get_tool_declarations() -> List[types.Tool]:
        """Returns Gemini function calling declarations using google-genai types."""
        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="read_source_file",
                        description="Read the entire text content of a source file or header in the student workspace.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "relative_path": types.Schema(
                                    type=types.Type.STRING,
                                    description="Relative path to file, e.g., 'ft_strlen.c' or 'libft.h'",
                                )
                            },
                            required=["relative_path"],
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="list_project_files",
                        description="List all available C files, headers, and Makefile status in workspace.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={},
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="run_norminette",
                        description="Run the official 42 Norminette on a file and return error tokens.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "relative_path": types.Schema(
                                    type=types.Type.STRING,
                                    description="Relative path of file to check, e.g. 'ft_split.c'",
                                )
                            },
                            required=["relative_path"],
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="get_git_diff",
                        description="Inspect current uncommitted or recent git changes for a file.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "relative_path": types.Schema(
                                    type=types.Type.STRING,
                                    description="Relative path to inspect diff, e.g. 'ft_memcpy.c'",
                                )
                            },
                            required=["relative_path"],
                        ),
                    ),
                ]
            )
        ]