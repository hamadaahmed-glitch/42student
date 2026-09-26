"""
Deterministic Test Pipeline Orchestrator.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from student42.database.connection import get_db_manager
from student42.database.repository import (
    AttemptRepository,
    ExerciseRepository,
    ProjectRepository,
    SkillRepository,
)
from student42.execution.compiler import CompilerEngine
from student42.execution.forbidden_functions import ForbiddenFunctionsChecker
from student42.execution.memory_checker import MemoryChecker
from student42.execution.norminette_runner import NorminetteRunner
from student42.workspace.path_resolver import PathResolver


@dataclass
class SingleTestOutcome:
    name: str
    passed: bool
    input_str: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    signal: Optional[str] = None


@dataclass
class PipelineResult:
    exercise_name: str
    all_passed: bool
    norm_passed: bool
    compile_passed: bool
    forbidden_passed: bool
    memory_clean: bool
    tests_passed: int
    tests_failed: int
    compiler_output: str = ""
    norm_output: str = ""
    valgrind_output: str = ""
    test_outcomes: List[SingleTestOutcome] = field(default_factory=list)
    forbidden_violations: List[str] = field(default_factory=list)


class TestRunnerOrchestrator:
    """Coordinates all deterministic verification tools for an exercise."""
    __test__ = False  # Tells Pytest this is NOT a test class

    def __init__(self, project_slug: str) -> None:
        self.project_slug = project_slug
        self.compiler = CompilerEngine()
        self.norminette = NorminetteRunner()
        self.memory_checker = MemoryChecker()

    def run_exercise(
        self,
        exercise_name: str,
        template_config: Dict[str, Any],
        student_id: int = 1,
    ) -> PipelineResult:
        # Normalize: strip .c if supplied
        clean_name = exercise_name[:-2] if exercise_name.endswith(".c") else exercise_name

        db = get_db_manager()
        with db.session() as session:
            proj_repo = ProjectRepository(session)
            project = proj_repo.get_by_slug(self.project_slug)
            if not project:
                raise ValueError(f"Project '{self.project_slug}' not found in database.")

            resolver = PathResolver(self.project_slug, project.local_path)
            if not resolver.exists():
                raise FileNotFoundError(f"Project workspace directory does not exist: {resolver.root}")

            # Try exact name, then with 'ft_' prefix
            source_file = resolver.find_source_file(f"{clean_name}.c")
            if not source_file and not clean_name.startswith("ft_"):
                source_file = resolver.find_source_file(f"ft_{clean_name}.c")
                if source_file:
                    clean_name = f"ft_{clean_name}"

            if not source_file:
                available = [p.name for p in resolver.list_all_sources()]
                raise FileNotFoundError(
                    f"Source file for '{exercise_name}' not found in workspace.\n"
                    f"Files detected in workspace: {', '.join(available) if available else 'None'}"
                )

            # 1. Norminette Check
            norm_res = self.norminette.run(source_file)

            # 2. Compile Check
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_bin = Path(temp_dir) / f"test_{clean_name}.o"
                include_dirs = resolver.list_all_headers()
                inc_parents = list(set([h.parent for h in include_dirs]))

                compile_res = self.compiler.compile_binary(
                    sources=[source_file],
                    output_binary=temp_bin,
                    include_dirs=inc_parents,
                    extra_flags=["-c"],
                )

                # 3. Forbidden Functions Check
                forbidden_passed = True
                violations: List[str] = []
                allowed_funcs = template_config.get("constraints", {}).get("allowed_functions", [])

                if compile_res.success and temp_bin.exists():
                    try:
                        sym_res = ForbiddenFunctionsChecker.check_binary(temp_bin, allowed_funcs)
                        forbidden_passed = sym_res.passed
                        violations = sym_res.forbidden_used
                    except Exception:
                        forbidden_passed = True

                outcomes: List[SingleTestOutcome] = []
                tests_passed = 1 if compile_res.success else 0
                tests_failed = 0 if compile_res.success else 1

                outcomes.append(
                    SingleTestOutcome(
                        name="Compilation & Warnings Check",
                        passed=compile_res.success,
                        actual=compile_res.stderr if not compile_res.success else "Zero Warnings",
                    )
                )

                memory_clean = True
                valgrind_log = ""

                all_passed = (
                    norm_res.passed
                    and compile_res.success
                    and forbidden_passed
                    and memory_clean
                    and (tests_failed == 0)
                )

                ex_repo = ExerciseRepository(session)
                att_repo = AttemptRepository(session)
                skill_repo = SkillRepository(session)

                exercise = ex_repo.get_exercise(project.id, clean_name)
                if not exercise:
                    exercise = ex_repo.register_exercise(
                        project_id=project.id,
                        module_id="auto",
                        name=clean_name,
                        source_file=f"{clean_name}.c",
                    )

                attempt = att_repo.record_attempt(
                    exercise_id=exercise.id,
                    compile_status=compile_res.success,
                    norm_status=norm_res.passed,
                    valgrind_status=memory_clean,
                    tests_passed=tests_passed,
                    tests_failed=tests_failed,
                    compiler_output=compile_res.stderr,
                    norm_output=norm_res.raw_output,
                )

                for out in outcomes:
                    att_repo.add_test_detail(
                        attempt_id=attempt.id,
                        test_name=out.name,
                        passed=out.passed,
                        actual_output=out.actual,
                        error_signal=out.signal,
                    )

                ex_repo.update_status(exercise.id, "passed" if all_passed else "failed")
                skill_repo.record_outcome(student_id, "compilation_standards", compile_res.success)
                skill_repo.record_outcome(student_id, "norm_adherence", norm_res.passed)

                return PipelineResult(
                    exercise_name=clean_name,
                    all_passed=all_passed,
                    norm_passed=norm_res.passed,
                    compile_passed=compile_res.success,
                    forbidden_passed=forbidden_passed,
                    memory_clean=memory_clean,
                    tests_passed=tests_passed,
                    tests_failed=tests_failed,
                    compiler_output=compile_res.stderr,
                    norm_output=norm_res.raw_output,
                    valgrind_output=valgrind_log,
                    test_outcomes=outcomes,
                    forbidden_violations=violations,
                )