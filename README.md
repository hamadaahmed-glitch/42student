# 42 Student OS (Personal 42 Development & Learning OS)

[![Language](https://img.shields.io/badge/Language-Python%203.11+-blue.svg)](https://www.python.org/)
[![Toolchain](https://img.shields.io/badge/Toolchain-GCC%20%7C%20Norminette%20%7C%20Valgrind-orange.svg)]()
[![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini%202.5-purple.svg)](https://ai.google.dev/)
[![School](https://img.shields.io/badge/School-42%20Network-black.svg)](https://www.42.fr/)

**42 Student OS** is a terminal-centric development environment, deterministic verification runner, and AI-powered learning companion engineered for students across the **42 Network** (from the Piscine, to Libft, through the entire Common Core).

Instead of treating AI as an auto-complete answer machine, 42 Student OS anchors Gemini behind an **immutable pedagogical constitution** and a **graduated 6-tier hint ladder**. It combines local host tools (GCC, Norminette, Valgrind, and Git diffs) with an autonomous Socratic mentor that understands your current project context, failure logs, and learning weaknesses.

---

## Key Features

- **Project Workspace Integration:** Binds directly to your local C repository (e.g., `~/42/Libft`).
- **Deterministic Verification Pipeline:** GCC (`-Wall -Wextra -Werror`) ➔ Norminette ➔ Symbol Check (`nm` for forbidden functions) ➔ Signal-trapping Unit Tests ➔ Valgrind Heap Leak Audits.
- **Pedagogical AI Mentor (Gemini 2.5):**
  - **Socratic Tutor:** Explains CS theory without viewing or writing code.
  - **Systems Debugger:** Analyzes crashes and leaks across a 6-tier hint ladder.
  - **Code Reviewer:** Audits code against Norm rules, line limits, and redundancies.
  - **Adaptive Quizzer:** Generates multiple-choice challenges targeting your weakest skills.
  - **Project Architect:** Audits Makefiles, headers, and whole-repository structure.
- **Reference Gatekeeper:** Manages official subjects and GitHub references with **Strict**, **Study** (body-masked), and **Free** modes.
- **Student Analytics & Bug Database:** Tracks recurring errors (memory leaks, segfaults, boundary flaws) and visualizes your mastery matrix over time.
- **Gamification Engine:** Tracks streaks, XP, level milestones, and daily study missions.

---

## Architecture Overview

```text
               CLI Interface (42student)
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      Verification Engine        AI Agent Subsystem
     (GCC/Norm/Valgrind/nm)   (Gemini + Context Builder)
             │                       │
             └───────────┬───────────┘
                         ▼
             Data & Persistence Layer
               (SQLite + Git Engine)