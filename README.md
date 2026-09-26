### File: `README.md`

```markdown
# 42 Student OS

[![Language: Python 3.11+](https://img.shields.io/badge/Language-Python%203.11+-blue.svg)](https://www.python.org/)
[![Toolchain](https://img.shields.io/badge/Toolchain-GCC%20%7C%20Norminette%20%7C%20Valgrind%20%7C%20Make-orange.svg)]()
[![AI Engine: Gemini 2.0 / 2.5](https://img.shields.io/badge/AI%20Engine-Google%20Gemini-purple.svg)](https://ai.google.dev/)
[![Testing: Pytest](https://img.shields.io/badge/Testing-Pytest%20Suite%20(11%2F11%20Passed)-brightgreen.svg)](https://docs.pytest.org/)
[![School: 42 Network](https://img.shields.io/badge/School-42%20Network-000000.svg)](https://42.fr/)

**42 Student OS** is a terminal-centric development environment, deterministic verification runner, and pedagogical AI learning companion engineered for students throughout the **42 Network** curriculum (from the Piscine, to Libft, to Unix internals and Graphics).

Rather than functioning as an autocomplete code generator, 42 Student OS enforces 42's core philosophy: **peer learning, deep low-level comprehension, and zero hand-holding**. It binds directly to your local C repository, verifies code via deterministic host tools (GCC, Norminette, Valgrind, `nm`), tracks learning weaknesses in an embedded SQLite database, and gates Google Gemini behind a strict **AI Constitution** and a **6-Tier Progressive Hint Ladder**.

---

## Table of Contents

1. [What 42 Student OS Does](#what-42-student-os-does)
2. [Architecture & Workflow](#architecture--workflow)
3. [Prerequisites & System Requirements](#prerequisites--system-requirements)
4. [Installation & Setup](#installation--setup)
5. [Complete CLI Command Reference](#complete-cli-command-reference)
   - [Core Commands (`init`, `profile`)](#1-core-commands)
   - [Project Workspace (`project`)](#2-project-workspace-commands)
   - [Deterministic Testing (`test`)](#3-deterministic-testing-commands)
   - [Gemini AI Mentor (`ai`)](#4-gemini-ai-mentor-commands)
   - [Reference Manager (`ref`)](#5-reference-solution-commands)
   - [Study Sessions & Missions (`session`)](#6-study-session-commands)
   - [Skills & Analytics (`stats`)](#7-analytics--bug-database-commands)
6. [The 6-Tier Hint Ladder](#the-6-tier-hint-ladder)
7. [Reference Access Policies (Strict vs Study vs Free)](#reference-access-policies)
8. [The 5-Stage Verification Pipeline](#the-5-stage-verification-pipeline)
9. [Automated Pytest Suite (`pytest -v`)](#automated-pytest-suite)
10. [Troubleshooting & Common Fixes](#troubleshooting--common-fixes)
11. [Repository Layout](#repository-layout)

---

## What 42 Student OS Does

1. **Understands You as a 42 Student**: Maintains your persistent student profile (Intra login, campus, current project, streak, level, XP, and history) across terminal sessions.
2. **Binds to Your Real Workspace**: Links your local C workspace directory (`~/42/libft`, etc.) and reads headers, Makefiles, source files, and Git diffs without copy-pasting code into web browsers.
3. **Deterministic Verification Over AI Opinion**: Never relies on LLM guesses for correctness. Code is verified using host compilers (`gcc -Wall -Wextra -Werror`), official `norminette`, symbol inspectors (`nm -u` for forbidden functions), signal traps (`SIGSEGV`, `SIGABRT`), and `valgrind` heap leak checkers.
4. **Pedagogical AI Mentor**: Connects to Google Gemini with project-specific constitutions. Gemini acts as a **Socratic Tutor**, **Systems Debugger**, **Norm Reviewer**, **Adaptive Quizzer**, and **Project Architect**.
5. **Progressive Hint Escalation**: Prevents answer spoiling by strictly gating assistance across 6 progressive tiers (Outcome ➔ Concept ➔ Localizer ➔ Algorithm ➔ Pseudocode ➔ Scaffold ➔ Reference).
6. **Reference Gatekeeping**: Clones peer solutions from GitHub and locks them until unit tests pass, or masks function bodies in **Study Mode** so you only see prototypes and structure.
7. **Personal Bug & Weakness Database**: Categorizes crashes, memory leaks, and syntax flaws. Calculates dynamic mastery percentages across low-level concepts (pointers, heap allocation, string manipulation, bitwise operations).

---

## Architecture & Workflow

```text
                                  TERMINAL CLI
                       (42student <subcommand> [args])
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
┌───────────────────────────┐                       ┌───────────────────────────┐
│   VERIFICATION ENGINE     │                       │     AI MENTOR ENGINE      │
│  (Host-Executed & Strict) │                       │     (Google Gemini API)   │
├───────────────────────────┤                       ├───────────────────────────┤
│ • GCC (-Wall -Wextra ...) │                       │ • Base Constitution       │
│ • Norminette CLI          │                       │ • Project Constitution    │
│ • Symbol Check (nm -u)    │                       │ • Student Skill Snapshot  │
│ • Signal Trapping Harness │                       │ • Git Diff + Source Code  │
│ • Valgrind Leak Checker   │                       │ • 6-Tier Hint Ladder      │
└─────────────┬─────────────┘                       └─────────────┬─────────────┘
              │                                                   │
              └─────────────────────┬─────────────────────────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                             PERSISTENCE LAYER                                 │
│               SQLite Database (~/.42student/data/student42.db)               │
│                                                                               │
│  • Students   • Projects   • Exercises   • Attempts   • TestDetails           │
│  • Mistakes   • Skills     • Sessions    • References                         │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites & System Requirements

Ensure the standard 42 development toolchain is installed on your Linux / macOS machine:

| Tool | Recommended Version | Verification Command | Purpose |
| :--- | :--- | :--- | :--- |
| **Python** | `3.11` to `3.14+` | `python3 --version` | Runtime engine |
| **GCC / Clang** | Standard 42 C compiler | `gcc --version` | Compilation with `-Wall -Wextra -Werror` |
| **Norminette** | `v3.3.50+` | `norminette -v` | Official 42 code style verification |
| **Valgrind** | Standard Linux tool | `valgrind --version` | Heap allocation and leak analysis |
| **GNU Make** | `4.0+` | `make -v` | Build system runner |
| **Git** | `2.30+` | `git --version` | Workspace tracking and diff resolution |
| **GNU binutils** | `nm` utility | `nm --version` | Forbidden function symbol inspection |

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/42student.git
cd 42student
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install in Editable Mode with Development Dependencies
```bash
pip install -e ".[dev]"
```

Verify that the CLI binary is available:
```bash
42student --help
```

### 4. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
Edit `.env` to configure your Gemini API Key and desired model:
```env
# Google Gemini API Key (obtain from https://aistudio.google.com/)
GEMINI_API_KEY="AIzaSyYourGeminiApiKeyHere"

# Model Selection
# Recommended: gemini-2.0-flash (fast, high throughput, robust)
# Optional: gemini-2.5-pro (deep architectural audits)
GEMINI_PRIMARY_MODEL="gemini-2.0-flash"
GEMINI_FAST_MODEL="gemini-2.0-flash"

# Logging and Environment
APP_ENV="development"
LOG_LEVEL="INFO"

# Workspace & Storage Paths (Leave blank for ~/.42student/)
STUDENT42_HOME=""
STUDENT42_WORKSPACE_DIR=""

# Toolchain Defaults
CC="gcc"
CFLAGS="-Wall -Wextra -Werror"
NORMINETTE_BIN="norminette"
VALGRIND_BIN="valgrind"

# Gamification
DAILY_XP_TARGET=500
STREAK_GRACE_HOURS=24
```

### 5. Initialize Your Student Profile
```bash
42student init --username "hait-h-m" --campus "Benguerir"
```
Output:
```text
✓ Initialized 42 Student OS for hait-h-m (Benguerir)
Run '42student profile' or '42student project select libft' to start.
```

---

## Complete CLI Command Reference

### 1. Core Commands

#### `42student init`
Initializes the SQLite database and sets up your primary student profile.
```bash
42student init --username "<login>" --campus "<campus_name>"
```
* **Options:**
  * `--username`: Your 42 intra login (defaults to `cadet`).
  * `--campus`: Your 42 campus location (defaults to `Benguerir`).

#### `42student profile`
Displays your student dashboard banner, current level, lifetime XP, daily streak, and active project context.
```bash
42student profile
```
* **Example Output:**
```text
╔════════════════════════════════════════════════════════════════════╗
║                           42 STUDENT OS                            ║
╠════════════════════════════════════════════════════════════════════╣
  Student:  hait-h-m           School:  42 Benguerir
  Level:    3.20               Streak:  6 days
  XP:       3200               Active:  Libft
╚════════════════════════════════════════════════════════════════════╝
```

---

### 2. Project Workspace Commands

The `project` command group manages cursus projects and links them to local folders.

#### `42student project list`
Auto-discovers and displays all curriculum project templates (Libft, ft_printf, get_next_line, Piscine C00) and marks which one is active.
```bash
42student project list
```
* **Example Output:**
```text
             42 Cursus Projects              
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Slug           ┃ Name           ┃ Tier     ┃ Access Mode ┃ Active ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
│ libft          │ Libft          │ Rank 00  │ strict      │ ▶ ACTIVE
│ ft_printf      │ ft_printf      │ Rank 01  │ strict      │ ○      │
│ get_next_line  │ get_next_line  │ Rank 01  │ strict      │ ○      │
│ piscine_c00    │ Piscine C 00   │ Piscine  │ study       │ ○      │
└────────────────┴────────────────┴──────────┴─────────────┴────────┘
```

#### `42student project select <slug>`
Switches the active operational context. Auto-registers all project functions into the database.
```bash
42student project select libft
```

#### `42student project path <local_directory>`
Binds the active project to a real folder on your disk.
```bash
42student project path /home/user/Desktop/42/libft
```

#### `42student project status`
Displays the physical filesystem mapping, verifies if `Makefile` exists, counts discovered `.c` and `.h` files, and prints the current reference mode.
```bash
42student project status
```
* **Example Output:**
```text
                    Project Workspace: Libft                     
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Attribute         ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Filesystem Path   │ /home/hamada/Desktop/42_student_run/projj │
│ Root Exists       │ YES                                       │
│ Makefile Found    │ YES                                       │
│ Source Files (.c) │ 43                                        │
│ Header Files (.h) │ 1                                         │
│ Access Mode       │ strict                                    │
└───────────────────┴───────────────────────────────────────────┘
```

---

### 3. Deterministic Testing Commands

The `test` command group runs deterministic local tools directly against your code.

#### `42student test run <exercise>`
Compiles and runs the full 5-stage verification pipeline on an exercise.
* Accepts either plain name (`atoi`), prefixed name (`ft_atoi`), or filename (`ft_atoi.c`).
* Awards +100 XP on full pass and checks for level-up.
```bash
42student test run ft_strlen
42student test run atoi.c
```
* **Example Output:**
```text
Verification Pipeline: ft_strlen [PASS]
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Stage               ┃  Status  ┃ Details                                ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Norminette          │  ✓ PASS  │ Norme compliant                        │
│ Compiler (GCC)      │  ✓ PASS  │ Zero warnings (-Wall -Wextra -Werror)  │
│ Forbidden Check     │  ✓ PASS  │ Only allowed symbols used              │
│ Unit Tests          │  ✓ PASS  │ 4 passed, 0 failed                     │
│ Valgrind Leak Check │  ✓ CLEAN │ 0 bytes lost, 0 errors                 │
└─────────────────────┴──────────┴────────────────────────────────────────┘
✓ Function passed all checks! +100 XP gained.
```

#### `42student test norm [file]`
Runs official Norminette against an individual file or your entire project directory.
```bash
# Check single file
42student test norm ft_split.c

# Check entire project workspace
42student test norm
```

#### `42student test history <exercise>`
Displays the recent execution attempts for a function, along with timestamps, compile status, and pass/fail counts.
```bash
42student test history ft_memcpy
```
* **Example Output:**
```text
Attempt History for ft_memcpy:
  #1 [2026-09-26 14:10] FAIL | Passed: 1 Failed: 2
  #2 [2026-09-26 14:15] FAIL | Passed: 2 Failed: 1
  #3 [2026-09-26 14:22] PASS | Passed: 4 Failed: 0
```

---

### 4. Gemini AI Mentor Commands

The `ai` command group connects you to your pedagogical assistant. Every output is returned as a formatted Rich Panel with categorized diagnostics.

#### `42student ai tutor "<topic>" [exercise]`
Consults the Socratic Tutor for conceptual low-level explanations. The tutor refuses to write solutions and instead explains memory models, hardware mechanics, and libc behavior.
```bash
42student ai tutor "Explain the difference between memmove and memcpy overlap"
```

#### `42student ai debug <exercise> [--hint-level <0-6>]`
Inspects your latest failed compiler log, Norminette error, or crash. Diagnoses the root flaw and scales assistance strictly according to the specified Hint Tier (defaults to Tier 1).
```bash
# Tier 1: CS concept explanation
42student ai debug ft_split --hint-level 1

# Tier 2: Point to the exact boundary or loop at fault
42student ai debug ft_split --hint-level 2

# Tier 4: Language-agnostic pseudocode
42student ai debug ft_split --hint-level 4
```

#### `42student ai review <exercise>`
Performs a static code quality audit without refactoring the code. Checks function lengths (<= 25 lines), variable scoping, pointer guards, and redundant loops.
```bash
42student ai review ft_strjoin
```

#### `42student ai quiz [--concept <concept>]`
Generates an interactive, 4-choice low-level C multiple-choice question. Automatically targets your weakest skill if `--concept` is omitted.
```bash
42student ai quiz
42student ai quiz --concept pointers
```
* **Interactive Prompt:**
```text
Target Concept: Pointers

Given char *s = "42"; what is the value and type of *(s + 1)?

  1) '4' (char)
  2) '2' (char)
  3) "2" (char *)
  4) Undefined behavior

Select correct option (1-4): 2

✓ CORRECT!
Explanation: Pointer arithmetic adds 1 * sizeof(char), dereferencing the byte at index 1 ('2').
```

#### `42student ai analyze`
Runs a whole-repository architectural review. Audits Makefiles (dependency graphs, `.PHONY` targets, mandatory rules), header guard organization, and cross-file duplication.
```bash
42student ai analyze
```

---

### 5. Reference Solution Commands

The `ref` command group manages official subjects and student reference implementations.

#### `42student ref add <url> <name> [--tags <tags>]`
Registers and clones a GitHub reference repository into managed storage (`~/.42student/references/github/`).
* Automatically sanitizes web browser URLs (such as `https://github.com/user/repo/tree/master`) into clean `.git` clone endpoints.
```bash
42student ref add https://github.com/Glagan/42-libft.git peer_libft
```

#### `42student ref list`
Lists all registered references for the active project along with their access state (`🔒 LOCKED` or `🔓 UNLOCKED`).
```bash
42student ref list
```

---

### 6. Study Session Commands

The `session` command group manages persistent study sprints and daily missions. State is stored in SQLite, remaining persistent across distinct terminal commands.

#### `42student session start`
Starts a timed study session in the active project.
```bash
42student session start
```
* **Output:**
```text
▶ Study Session #1 started. Good luck cadet!
```

#### `42student session stop [--functions-done <N>] [--hints-used <N>]`
Concludes the currently open session, calculates study metrics, and awards XP.
```bash
42student session stop --functions-done 3 --hints-used 1
```
* **Output:**
```text
■ Session concluded! +240 XP awarded.
```

#### `42student session daily`
Generates adaptive daily missions tailored to your specific failure history and current skill weaknesses.
```bash
42student session daily
```
* **Example Output:**
```text
                             Daily Learning Missions                             
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Mission                  ┃ Objective                                ┃  Reward ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Mastery Sprint: Pointers │ Resolve failing unit tests and review    │ +150 XP │
│                          │ edge cases for pointers.                 │         │
│ Norminette Perfection    │ Pass 3 consecutive functions with zero   │ +100 XP │
│                          │ Norminette warnings.                     │         │
│ Zero Leak Protocol       │ Execute full Valgrind check on 2         │ +100 XP │
│                          │ functions with 0 bytes definitely lost.  │         │
└──────────────────────────┴──────────────────────────────────────────┴─────────┘
```

---

### 7. Analytics & Bug Database Commands

#### `42student stats skills`
Visualizes your skill mastery matrix with dynamic progress bars based on real test performance.
```bash
42student stats skills
```
* **Example Output:**
```text
                        Systems Concept Mastery Tree                        
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Concept             ┃ Mastery              ┃ Percentage ┃ Tests ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ Pointers            │ ████████████████░░░░ │      80.0% │    15 │ STABLE │
│ Memory Allocation   │ ████████████░░░░░░░░ │      60.0% │    10 │ WEAKNESS
│ Memory Manipulation │ ████████████████████ │     100.0% │     8 │ STABLE │
│ Ascii And Types     │ ████████████████████ │     100.0% │    12 │ STABLE │
│ Linked Lists        │ ████░░░░░░░░░░░░░░░░ │      20.0% │     5 │ WEAKNESS
└─────────────────────┴──────────────────────┴────────────┴───────┴────────┘
```

#### `42student stats mistakes`
Queries your personal bug database. Identifies recurring root causes (e.g., segfaults, memory leaks, Norm issues) and tracks how often each mistake has happened.
```bash
42student stats mistakes
```

---

## The 6-Tier Hint Ladder

When requesting assistance via `42student ai debug <func> --hint-level <0-6>`, the model is restricted by the **Pedagogical Constitution**:

```text
[Tier 0: Outcome Only] ───► Categorizes failure (e.g. Memory Leak, SIGSEGV). Zero explanation.
         │
[Tier 1: Conceptual]   ───► Explains underlying computer science mechanism (Heap vs Stack, Sentinel).
         │
[Tier 2: Localizer]    ───► Points to exact condition, branch, or index where state goes invalid.
         │
[Tier 3: Algorithm]    ───► Explains the operational step sequence in plain English sentences.
         │
[Tier 4: Pseudocode]   ───► Provides language-agnostic structured pseudocode (No C syntax).
         │
[Tier 5: Scaffold]     ───► Provides a C function skeleton with empty comments marking logic gaps.
         │
[Tier 6: Reference]    ───► Full canonical breakdown. Only unlocked after passing or project clearing.
```

---

## Reference Access Policies

Student solutions stored in `references/` are regulated by three access modes:

1. **`strict` (Default)**: Reference files are completely locked (`🔒 LOCKED`). Viewing source files is forbidden until you pass all unit tests for that exercise.
2. **`study`**: References can be opened, but function implementations are automatically masked:
   ```c
   /* In Study Mode, header prototypes and comments are visible, but bodies are hidden: */
   size_t ft_strlen(const char *s)
   {
       /* [STUDY MODE: Implementation hidden. Deduce algorithm.] */
   }
   ```
3. **`free`**: Unlocked access for post-project code comparisons and peer evaluations.

---

## The 5-Stage Verification Pipeline

When running `42student test run <exercise>`, the verification engine executes 5 sequential stages:

```text
  1. Norminette Check
     Runs official norminette. Flags line count (>25), parameter count (>4), and scope rules.
         ↓
  2. Compiler & Warnings Check
     Compiles via `gcc -Wall -Wextra -Werror -c <source.c>`. Any warning is treated as fatal.
         ↓
  3. Forbidden Functions Check
     Runs `nm -u` against compiled object files. Compares symbols against allowed project lists
     (e.g., in Libft: only write, malloc, free are permitted).
         ↓
  4. Signal-Trapping Unit Tests
     Links source code with `tests/c_harness/student42_assert.h`. Traps SIGSEGV and SIGABRT
     via `sigaction` and `setjmp/longjmp` to prevent test runner crashes while recording signals.
         ↓
  5. Valgrind Memory & Leak Check
     Runs binary under `valgrind --leak-check=full --error-exitcode=42`. Confirms 0 bytes
     definitely lost, 0 bytes indirectly lost, and zero uninitialized value reads.
```

---

## Automated Pytest Suite

The project includes an internal test suite ensuring reliability across the persistence layer, access controllers, file scanners, and error classifiers.

### Running Pytest
To run the automated test suite, ensure your virtual environment is active and execute:
```bash
pytest -v
```

### Expected Output
```text
============================== test session starts ==============================
platform linux -- Python 3.14.x, pytest-9.x.x, pluggy-1.x.x
rootdir: /home/user/42student
configfile: pyproject.toml
testpaths: tests
collected 11 items

tests/unit/test_access_controller.py::test_strict_mode_blocks_uncompleted_work PASSED [  9%]
tests/unit/test_access_controller.py::test_strict_mode_unlocked_after_completion PASSED [ 18%]
tests/unit/test_access_controller.py::test_study_mode_masks_c_function_bodies PASSED [ 27%]
tests/unit/test_database.py::test_student_xp_and_level_advancement PASSED         [ 36%]
tests/unit/test_database.py::test_project_and_exercise_lifecycle PASSED           [ 45%]
tests/unit/test_database.py::test_mistake_deduplication_and_occurrences PASSED   [ 54%]
tests/unit/test_mistake_classifier.py::test_segfault_classification PASSED       [ 63%]
tests/unit/test_mistake_classifier.py::test_valgrind_leak_classification PASSED  [ 72%]
tests/unit/test_mistake_classifier.py::test_norminette_line_count_classification PASSED [ 81%]
tests/unit/test_mistake_classifier.py::test_syntax_classification PASSED          [ 90%]
tests/unit/test_file_scanner.py::test_include_extraction PASSED                   [100%]

============================== 11 passed in 0.24s ===============================
```

---

## Troubleshooting & Common Fixes

### 1. `ClientError: 404 NOT_FOUND (Model not found)`
* **Cause:** The model specified in your `.env` is deprecated or unavailable in your region.
* **Fix:** Open `.env` and set `GEMINI_PRIMARY_MODEL="gemini-2.0-flash"` and `GEMINI_FAST_MODEL="gemini-2.0-flash"`.

### 2. `ServerError: 503 UNAVAILABLE (High demand)`
* **Cause:** Google Gemini API is experiencing temporary server load spikes.
* **Fix:** The engine has built-in exponential backoff retry. Wait a few seconds and run the command again.

### 3. `FileNotFoundError: Source file for 'ft_atoi.c' not found in workspace`
* **Cause:** The project path is not pointing to your real C folder, or the file has a different name.
* **Fix:** Check `42student project status` to verify your linked directory. Re-link using `42student project path /absolute/path/to/project`.

### 4. `GitCommandError: repository not found`
* **Cause:** Passing a browser URL (e.g., `.../tree/master`) rather than the git clone endpoint.
* **Fix:** 42 Student OS automatically sanitizes GitHub URLs, but ensure the repository is public or you have SSH credentials configured.

---

## Repository Layout

```text
42student/
├── .env.example                          # Environment template
├── pyproject.toml                        # Dependencies and pytest configuration
├── README.md                             # Comprehensive documentation
│
├── config/                               # Project templates & rules
│   ├── constitutions/
│   │   ├── base_constitution.md          # Global pedagogical rules
│   │   └── libft_constitution.md         # Libft-specific rules
│   └── project_templates/
│       ├── libft.json                    # Libft project definition
│       ├── ft_printf.json                # ft_printf definition
│       ├── get_next_line.json            # get_next_line definition
│       └── piscine/
│           └── c00.json                  # Piscine C00 definition
│
├── src/student42/                        # Source package
│   ├── main.py                           # CLI entrypoint
│   ├── cli/                              # Subcommand modules & Rich UI
│   │   ├── ui.py                         # Dashboards, tables, and panels
│   │   ├── commands_project.py           # project list, select, path, status
│   │   ├── commands_test.py              # test run, norm, history
│   │   ├── commands_ai.py                # ai tutor, debug, review, quiz, analyze
│   │   ├── commands_ref.py               # ref list, add
│   │   ├── commands_session.py           # session start, stop, daily
│   │   └── commands_stats.py             # stats skills, mistakes
│   ├── core/                             # Core orchestration
│   │   ├── config.py                     # Path and environment settings
│   │   ├── profile_manager.py            # XP, streaks, levels
│   │   └── session_controller.py         # Persistent study session tracker
│   ├── database/                         # Relational persistence
│   │   ├── models.py                     # SQLAlchemy models
│   │   ├── connection.py                 # SQLite database engine
│   │   └── repository.py                 # Query operations
│   ├── execution/                        # Verification pipeline
│   │   ├── compiler.py                   # GCC/Clang runner
│   │   ├── norminette_runner.py          # Norminette CLI parser
│   │   ├── forbidden_functions.py        # nm symbol inspector
│   │   ├── memory_checker.py             # Valgrind leak checker
│   │   └── test_runner.py                # Pipeline orchestrator
│   ├── workspace/                        # Filesystem and Git
│   │   ├── path_resolver.py              # File path mapping
│   │   ├── file_scanner.py               # Source and header parser
│   │   └── git_engine.py                 # Git status and diffs
│   ├── references/                       # Reference management
│   │   ├── access_controller.py          # Strict, Study, and Free policies
│   │   └── reference_manager.py          # GitHub cloning and storage
│   ├── analytics/                        # Performance analytics
│   │   ├── mistake_tracker.py            # Error categorizer
│   │   └── skill_matrix.py               # Skill mastery calculations
│   └── ai/                               # Gemini AI layer
│       ├── client.py                     # Google GenAI SDK wrapper
│       ├── context_builder.py            # Prompt and context assembler
│       ├── ladder.py                     # 6-Tier Hint Ladder
│       ├── schemas.py                    # Pydantic structured schemas
│       ├── tools.py                      # Function calling registry
│       └── agents/                       # Specialized AI personas
│           ├── base.py                   # Base agent class
│           ├── tutor.py                  # Socratic tutor
│           ├── debugger.py               # Systems debugger
│           ├── reviewer.py               # Code reviewer
│           ├── quizzer.py                # Adaptive quizzer
│           └── project_analyst.py        # Project architect
│
└── tests/                                # Test suite
    ├── conftest.py                       # Pytest fixtures and DB isolation
    ├── c_harness/                        # C assertion harnesses
    │   ├── student42_assert.h            # Signal-trapping assertion framework
    │   └── libft/                        # Unit test harnesses for Libft
    └── unit/                             # Python unit tests
        ├── test_access_controller.py     # Policy tests
        ├── test_database.py              # Repository and XP tests
        ├── test_mistake_classifier.py    # Error parsing tests
        └── test_file_scanner.py          # Scanner tests
```

---

## License

Distributed under the **MIT License**. Designed for students of the **42 Network**. All verification mechanisms are run locally on your machine to support autonomous learning.
