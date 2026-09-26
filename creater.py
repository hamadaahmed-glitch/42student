from pathlib import Path

# Base root folder
BASE_DIR = Path("42student")

# Directories (including empty ones that need to exist)
DIRECTORIES = [
    BASE_DIR / "config/constitutions",
    BASE_DIR / "config/project_templates/piscine",
    BASE_DIR / "data/cache",
    BASE_DIR / "data/logs",
    BASE_DIR / "references/official",
    BASE_DIR / "references/github",
    BASE_DIR / "references/local_notes",
    BASE_DIR / "src/student42/cli",
    BASE_DIR / "src/student42/core",
    BASE_DIR / "src/student42/database",
    BASE_DIR / "src/student42/workspace",
    BASE_DIR / "src/student42/execution",
    BASE_DIR / "src/student42/references",
    BASE_DIR / "src/student42/analytics",
    BASE_DIR / "src/student42/ai/agents",
    BASE_DIR / "tests/unit",
    BASE_DIR / "tests/integration",
]

# Files to create
FILES = [
    # Root files
    BASE_DIR / ".env.example",
    BASE_DIR / ".gitignore",
    BASE_DIR / "README.md",
    BASE_DIR / "pyproject.toml",
    # Config
    BASE_DIR / "config/constitutions/base_constitution.md",
    BASE_DIR / "config/constitutions/libft_constitution.md",
    BASE_DIR / "config/project_templates/piscine/c00.json",
    BASE_DIR / "config/project_templates/piscine/c01.json",
    BASE_DIR / "config/project_templates/libft.json",
    BASE_DIR / "config/project_templates/ft_printf.json",
    BASE_DIR / "config/project_templates/get_next_line.json",
    # Data
    BASE_DIR / "data/42student.db",
    BASE_DIR / "data/logs/test_runs.log",
    BASE_DIR / "data/logs/ai_interactions.log",
    # Src - Entry
    BASE_DIR / "src/student42/__init__.py",
    BASE_DIR / "src/student42/main.py",
    # Src - CLI
    BASE_DIR / "src/student42/cli/__init__.py",
    BASE_DIR / "src/student42/cli/ui.py",
    BASE_DIR / "src/student42/cli/commands_project.py",
    BASE_DIR / "src/student42/cli/commands_test.py",
    BASE_DIR / "src/student42/cli/commands_ai.py",
    BASE_DIR / "src/student42/cli/commands_ref.py",
    BASE_DIR / "src/student42/cli/commands_stats.py",
    BASE_DIR / "src/student42/cli/commands_session.py",
    # Src - Core
    BASE_DIR / "src/student42/core/__init__.py",
    BASE_DIR / "src/student42/core/config.py",
    BASE_DIR / "src/student42/core/session_controller.py",
    BASE_DIR / "src/student42/core/profile_manager.py",
    # Src - Database
    BASE_DIR / "src/student42/database/__init__.py",
    BASE_DIR / "src/student42/database/connection.py",
    BASE_DIR / "src/student42/database/models.py",
    BASE_DIR / "src/student42/database/repository.py",
    # Src - Workspace
    BASE_DIR / "src/student42/workspace/__init__.py",
    BASE_DIR / "src/student42/workspace/path_resolver.py",
    BASE_DIR / "src/student42/workspace/file_scanner.py",
    BASE_DIR / "src/student42/workspace/git_engine.py",
    # Src - Execution
    BASE_DIR / "src/student42/execution/__init__.py",
    BASE_DIR / "src/student42/execution/compiler.py",
    BASE_DIR / "src/student42/execution/norminette_runner.py",
    BASE_DIR / "src/student42/execution/test_runner.py",
    BASE_DIR / "src/student42/execution/memory_checker.py",
    BASE_DIR / "src/student42/execution/forbidden_functions.py",
    # Src - References
    BASE_DIR / "src/student42/references/__init__.py",
    BASE_DIR / "src/student42/references/reference_manager.py",
    BASE_DIR / "src/student42/references/access_controller.py",
    # Src - Analytics
    BASE_DIR / "src/student42/analytics/__init__.py",
    BASE_DIR / "src/student42/analytics/mistake_tracker.py",
    BASE_DIR / "src/student42/analytics/skill_matrix.py",
    BASE_DIR / "src/student42/analytics/mission_generator.py",
    # Src - AI
    BASE_DIR / "src/student42/ai/__init__.py",
    BASE_DIR / "src/student42/ai/client.py",
    BASE_DIR / "src/student42/ai/context_builder.py",
    BASE_DIR / "src/student42/ai/schemas.py",
    BASE_DIR / "src/student42/ai/ladder.py",
    BASE_DIR / "src/student42/ai/tools.py",
    # Src - AI Agents
    BASE_DIR / "src/student42/ai/agents/base.py",
    BASE_DIR / "src/student42/ai/agents/tutor.py",
    BASE_DIR / "src/student42/ai/agents/debugger.py",
    BASE_DIR / "src/student42/ai/agents/reviewer.py",
    BASE_DIR / "src/student42/ai/agents/quizzer.py",
    BASE_DIR / "src/student42/ai/agents/project_analyst.py",
]


def create_structure():
    print("Creating project structure...")

    # Create directories
    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)

    # Create files
    for file_path in FILES:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)

    print("Project creation complete.\n")


def verify_structure():
    print("Verifying folder structure...")
    missing_items = []

    # Verify directories
    for directory in DIRECTORIES:
        if not directory.is_dir():
            missing_items.append(f"[DIR MISSING]  {directory}")

    # Verify files
    for file_path in FILES:
        if not file_path.is_file():
            missing_items.append(f"[FILE MISSING] {file_path}")

    # Results reporting
    total_expected = len(DIRECTORIES) + len(FILES)
    if missing_items:
        print(f"Verification FAILED. {len(missing_items)} items missing:\n")
        for item in missing_items:
            print(f"  - {item}")
    else:
        print(f"Verification SUCCESS! All {total_expected} items created and confirmed.")


if __name__ == "__main__":
    create_structure()
    verify_structure()