#!/usr/bin/env python3
"""
42 Student OS - Official Desktop GUI Application.
A complete, thread-safe, 42-themed graphical control center for 42 students.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add 'src' directory to Python path so student42 packages are importable directly
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Import backend subsystems
from student42.ai.agents.debugger import DebuggerAgent
from student42.ai.agents.project_analyst import ProjectAnalystAgent
from student42.ai.agents.quizzer import QuizzerAgent
from student42.ai.agents.reviewer import CodeReviewerAgent
from student42.ai.agents.tutor import TutorAgent
from student42.ai.schemas import AIDiagnosis, ProjectAudit, QuizQuestion
from student42.analytics.skill_matrix import SkillMatrix
from student42.core.config import get_paths, get_settings
from student42.core.profile_manager import ProfileManager
from student42.core.session_controller import SessionController
from student42.database.connection import get_db_manager
from student42.database.models import Mistake, ReferenceItem
from student42.database.repository import (
    AttemptRepository,
    ExerciseRepository,
    MistakeRepository,
    ProjectRepository,
    ReferenceRepository,
)
from student42.execution.norminette_runner import NorminetteRunner
from student42.execution.test_runner import PipelineResult, TestRunnerOrchestrator
from student42.references.reference_manager import ReferenceManager
from student42.workspace.path_resolver import PathResolver

# ==============================================================================
# 42 COLOR PALETTE & DESIGN TOKENS
# ==============================================================================
BG_DARK = "#0B0E14"       # Deep workspace background
BG_PANEL = "#161B22"      # Card and container background
BG_ELEVATED = "#21262D"   # Inputs, selected items, elevated panels
ACCENT_TEAL = "#00BABC"   # 42 School Official Teal / Cyan
ACCENT_HOVER = "#00D2D4"  # Lighter teal for hover
TEXT_WHITE = "#F0F6FC"    # Primary typography
TEXT_MUTED = "#8B949E"    # Secondary typography / labels
BORDER_COLOR = "#30363D"  # Subtle structural dividers
STATUS_GREEN = "#2EA043"  # Pass / Active
STATUS_RED = "#F85149"    # Fail / Error
STATUS_YELLOW = "#D29922" # Warnings / Strict


class Student42App(tk.Tk):
    """Main Application Window for 42 Student OS."""

    def __init__(self) -> None:
        super().__init__()
        self.title("42 Student OS - Personal Development & Learning Environment")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(bg=BG_DARK)

        # Ensure database is initialized
        self.db = get_db_manager()
        self.db.init_db()

        # Core controllers
        self.profile_mgr = ProfileManager()
        self.current_student = self.profile_mgr.get_profile()
        self.session_ctrl: Optional[SessionController] = None
        self.session_timer_running = False
        self.session_start_epoch = 0.0

        # Active state
        self.active_project_slug = "libft"
        self._sync_active_project()

        # Setup custom styles and layouts
        self._setup_styles()
        self._build_header()
        self._build_body()

        # Initial view load
        self.show_dashboard_page()
        self.refresh_profile_header()

    # ==========================================================================
    # STYLING & THEME
    # ==========================================================================
    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        # Global backgrounds
        style.configure(".", background=BG_DARK, foreground=TEXT_WHITE, font=("Segoe UI", 10))
        style.configure("TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=BG_PANEL, relief="flat")
        style.configure("Elevated.TFrame", background=BG_ELEVATED, relief="flat")

        # Labels
        style.configure("TLabel", background=BG_PANEL, foreground=TEXT_WHITE, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG_PANEL, foreground=TEXT_WHITE, font=("Segoe UI", 15, "bold"))
        style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_WHITE, font=("Segoe UI", 12, "bold"))
        style.configure("Sub.TLabel", background=BG_PANEL, foreground=TEXT_MUTED, font=("Segoe UI", 9))
        style.configure("Teal.TLabel", background=BG_PANEL, foreground=ACCENT_TEAL, font=("Segoe UI", 10, "bold"))

        # Buttons
        style.configure(
            "Primary.TButton",
            background=ACCENT_TEAL,
            foreground="#000000",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            relief="flat",
        )
        style.map("Primary.TButton", background=[("active", ACCENT_HOVER)])

        style.configure(
            "Nav.TButton",
            background=BG_PANEL,
            foreground=TEXT_WHITE,
            font=("Segoe UI", 10),
            padding=8,
            relief="flat",
            anchor="w",
        )
        style.map("Nav.TButton", background=[("active", BG_ELEVATED)])

        # Treeviews (Tables)
        style.configure(
            "Treeview",
            background=BG_PANEL,
            foreground=TEXT_WHITE,
            fieldbackground=BG_PANEL,
            rowheight=26,
            font=("Segoe UI", 9),
            bordercolor=BORDER_COLOR,
        )
        style.configure("Treeview.Heading", background=BG_ELEVATED, foreground=TEXT_WHITE, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT_TEAL)], foreground=[("selected", "#000000")])

    # ==========================================================================
    # HEADER (STUDENT BADGE & STATS)
    # ==========================================================================
    def _build_header(self) -> None:
        self.header_frame = tk.Frame(self, bg=BG_PANEL, height=70, bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Brand / Logo
        brand_frame = tk.Frame(self.header_frame, bg=BG_PANEL)
        brand_frame.pack(side=tk.LEFT, padx=20, pady=12)

        lbl_42 = tk.Label(brand_frame, text="42", font=("Segoe UI", 20, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL)
        lbl_42.pack(side=tk.LEFT)
        lbl_sub = tk.Label(brand_frame, text=" STUDENT OS", font=("Segoe UI", 12, "bold"), fg=TEXT_WHITE, bg=BG_PANEL)
        lbl_sub.pack(side=tk.LEFT, padx=5)

        # Right-side stats pill
        self.stats_frame = tk.Frame(self.header_frame, bg=BG_PANEL)
        self.stats_frame.pack(side=tk.RIGHT, padx=20, pady=12)

        self.lbl_profile_info = tk.Label(
            self.stats_frame,
            text="",
            font=("Segoe UI", 10),
            fg=TEXT_WHITE,
            bg=BG_PANEL,
        )
        self.lbl_profile_info.pack(side=tk.RIGHT, padx=10)

    def refresh_profile_header(self) -> None:
        self.current_student = self.profile_mgr.get_profile()
        p_text = (
            f"👤 Cadet: {self.current_student.username}  |  "
            f"📍 {self.current_student.campus}  |  "
            f"⭐ Level: {self.current_student.level:.2f}  |  "
            f"🔥 Streak: {self.current_student.current_streak} days  |  "
            f"⚡ XP: {self.current_student.xp}  |  "
            f"▶ [{self.active_project_slug.upper()}]"
        )
        self.lbl_profile_info.config(text=p_text)

    # ==========================================================================
    # BODY & SIDEBAR NAVIGATION
    # ==========================================================================
    def _build_body(self) -> None:
        self.body_container = tk.Frame(self, bg=BG_DARK)
        self.body_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.body_container, bg=BG_PANEL, width=220, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        nav_items = [
            ("🚀  Dashboard", self.show_dashboard_page),
            ("📁  Project Workspace", self.show_project_page),
            ("⚡  Test Pipeline", self.show_test_page),
            ("🧠  Gemini AI Mentor", self.show_ai_page),
            ("⏱  Study Sprints", self.show_session_page),
            ("📊  Skills & Bugs", self.show_skills_page),
            ("📚  References", self.show_ref_page),
        ]

        tk.Label(self.sidebar, text="NAVIGATION", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", padx=16, pady=(16, 8))

        for text, cmd in nav_items:
            btn = ttk.Button(self.sidebar, text=text, style="Nav.TButton", command=cmd)
            btn.pack(fill=tk.X, padx=10, pady=3)

        # Status Bar at bottom of sidebar
        self.lbl_system_status = tk.Label(self.sidebar, text="● System Ready", font=("Segoe UI", 8), fg=STATUS_GREEN, bg=BG_PANEL)
        self.lbl_system_status.pack(side=tk.BOTTOM, pady=16)

        # Main Dynamic Content Area
        self.content_area = tk.Frame(self.body_container, bg=BG_DARK, padx=20, pady=20)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _clear_content(self) -> None:
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def _sync_active_project(self) -> None:
        with self.db.session() as session:
            proj_repo = ProjectRepository(session)
            active = proj_repo.get_active_project()
            if active:
                self.active_project_slug = active.slug
            else:
                proj = proj_repo.get_by_slug("libft")
                if proj:
                    proj_repo.set_active_project("libft")
                    self.active_project_slug = "libft"

    def set_busy(self, message: str) -> None:
        self.lbl_system_status.config(text=f"◌ {message}", fg=STATUS_YELLOW)
        self.update_idletasks()

    def set_idle(self) -> None:
        self.lbl_system_status.config(text="● System Ready", fg=STATUS_GREEN)
        self.update_idletasks()

    # ==========================================================================
    # PAGE 1: DASHBOARD
    # ==========================================================================
    def show_dashboard_page(self) -> None:
        self._clear_content()

        # Welcome row
        welcome_frame = tk.Frame(self.content_area, bg=BG_DARK)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(welcome_frame, text=f"Welcome back, {self.current_student.username}!", font=("Segoe UI", 18, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")
        tk.Label(welcome_frame, text="Your 42 development & learning environment is active.", font=("Segoe UI", 10), fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w")

        # KPI Card Grid
        cards_row = tk.Frame(self.content_area, bg=BG_DARK)
        cards_row.pack(fill=tk.X, pady=(0, 20))

        # KPI 1: Level
        c1 = tk.Frame(cards_row, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(c1, text="RANK LEVEL", font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        tk.Label(c1, text=f"{self.current_student.level:.2f}", font=("Segoe UI", 24, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w", pady=4)
        tk.Label(c1, text=f"Total: {self.current_student.xp} XP", font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w")

        # KPI 2: Active Project
        c2 = tk.Frame(cards_row, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(c2, text="CURRENT FOCUS", font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        tk.Label(c2, text=self.active_project_slug.upper(), font=("Segoe UI", 24, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w", pady=4)
        with self.db.session() as session:
            proj = ProjectRepository(session).get_by_slug(self.active_project_slug)
            p_mode = proj.access_mode if proj else "strict"
        tk.Label(c2, text=f"Mode: {p_mode.upper()}", font=("Segoe UI", 9), fg=STATUS_YELLOW, bg=BG_PANEL).pack(anchor="w")

        # KPI 3: Streak
        c3 = tk.Frame(cards_row, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        tk.Label(c3, text="STUDY STREAK", font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")
        tk.Label(c3, text=f"{self.current_student.current_streak} DAYS", font=("Segoe UI", 24, "bold"), fg=STATUS_GREEN, bg=BG_PANEL).pack(anchor="w", pady=4)
        tk.Label(c3, text="Keep the rhythm going!", font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w")

        # Daily Missions Section
        mission_frame = tk.Frame(self.content_area, bg=BG_PANEL, padx=20, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        mission_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(mission_frame, text="Today's Adaptive Missions", font=("Segoe UI", 12, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        ctrl = SessionController(self.active_project_slug)
        missions = ctrl.get_daily_missions(self.current_student.id)

        for m in missions:
            mf = tk.Frame(mission_frame, bg=BG_ELEVATED, padx=12, pady=10)
            mf.pack(fill=tk.X, pady=4)
            tk.Label(mf, text=f"🎯  {m.title}", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_ELEVATED).pack(side=tk.LEFT)
            tk.Label(mf, text=f" - {m.description}", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_ELEVATED).pack(side=tk.LEFT)
            tk.Label(mf, text=f"+{m.target_xp} XP", font=("Segoe UI", 9, "bold"), fg=STATUS_GREEN, bg=BG_ELEVATED).pack(side=tk.RIGHT)

    # ==========================================================================
    # PAGE 2: PROJECT WORKSPACE
    # ==========================================================================
    def show_project_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Project Workspace Manager", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")
        tk.Label(header, text="Switch projects, configure paths, and adjust access modes.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w")

        main_box = tk.Frame(self.content_area, bg=BG_PANEL, padx=20, pady=20, highlightthickness=1, highlightbackground=BORDER_COLOR)
        main_box.pack(fill=tk.BOTH, expand=True)

        # Row 1: Select Active Project
        row1 = tk.Frame(main_box, bg=BG_PANEL)
        row1.pack(fill=tk.X, pady=8)
        tk.Label(row1, text="Active Project:", width=18, anchor="w", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(side=tk.LEFT)

        with self.db.session() as session:
            projects = ProjectRepository(session).list_all()
            project_slugs = [p.slug for p in projects] or ["libft", "ft_printf", "get_next_line", "piscine_c00"]

        self.cmb_project = ttk.Combobox(row1, values=project_slugs, state="readonly", width=25)
        self.cmb_project.set(self.active_project_slug)
        self.cmb_project.pack(side=tk.LEFT, padx=8)

        btn_activate = ttk.Button(row1, text="Activate Project", style="Primary.TButton", command=self._on_activate_project)
        btn_activate.pack(side=tk.LEFT, padx=8)

        # Row 2: Filesystem Path
        row2 = tk.Frame(main_box, bg=BG_PANEL)
        row2.pack(fill=tk.X, pady=8)
        tk.Label(row2, text="Local Path:", width=18, anchor="w", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(side=tk.LEFT)

        with self.db.session() as session:
            active_p = ProjectRepository(session).get_by_slug(self.active_project_slug)
            curr_path = active_p.local_path if active_p and active_p.local_path else str(Path.home() / "42" / self.active_project_slug)

        self.ent_path = tk.Entry(row2, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", width=50)
        self.ent_path.insert(0, curr_path)
        self.ent_path.pack(side=tk.LEFT, padx=8)

        btn_browse = ttk.Button(row2, text="Browse...", command=self._on_browse_path)
        btn_browse.pack(side=tk.LEFT, padx=4)

        btn_save_path = ttk.Button(row2, text="Save Path", command=self._on_save_path)
        btn_save_path.pack(side=tk.LEFT, padx=4)

        # Row 3: Reference Mode
        row3 = tk.Frame(main_box, bg=BG_PANEL)
        row3.pack(fill=tk.X, pady=8)
        tk.Label(row3, text="Reference Policy:", width=18, anchor="w", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(side=tk.LEFT)

        self.cmb_mode = ttk.Combobox(row3, values=["strict", "study", "free"], state="readonly", width=25)
        curr_mode = active_p.access_mode if active_p else "strict"
        self.cmb_mode.set(curr_mode)
        self.cmb_mode.pack(side=tk.LEFT, padx=8)

        btn_save_mode = ttk.Button(row3, text="Apply Policy", command=self._on_save_mode)
        btn_save_mode.pack(side=tk.LEFT, padx=8)

        # Divider
        tk.Frame(main_box, bg=BORDER_COLOR, height=1).pack(fill=tk.X, pady=16)

        # Workspace Inspection Output Box
        tk.Label(main_box, text="Workspace Diagnostics", font=("Segoe UI", 11, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")

        self.txt_project_status = tk.Text(main_box, bg=BG_ELEVATED, fg=TEXT_WHITE, font=("Consolas", 10), height=10, relief="flat", padx=10, pady=10)
        self.txt_project_status.pack(fill=tk.BOTH, expand=True, pady=8)

        self._refresh_workspace_status_text()

    def _on_activate_project(self) -> None:
        target = self.cmb_project.get()
        with self.db.session() as session:
            ProjectRepository(session).set_active_project(target)
        self.active_project_slug = target
        self.refresh_profile_header()
        self.show_project_page()

    def _on_browse_path(self) -> None:
        chosen = filedialog.askdirectory(title="Select Local 42 Project Folder")
        if chosen:
            self.ent_path.delete(0, tk.END)
            self.ent_path.insert(0, chosen)
            self._on_save_path()

    def _on_save_path(self) -> None:
        new_path = self.ent_path.get().strip()
        with self.db.session() as session:
            active = ProjectRepository(session).get_active_project()
            if active:
                active.local_path = new_path
        messagebox.showinfo("Workspace Updated", f"Bound {self.active_project_slug} to:\n{new_path}")
        self._refresh_workspace_status_text()

    def _on_save_mode(self) -> None:
        new_mode = self.cmb_mode.get()
        with self.db.session() as session:
            active = ProjectRepository(session).get_active_project()
            if active:
                active.access_mode = new_mode
        messagebox.showinfo("Policy Updated", f"Reference policy changed to: {new_mode.upper()}")
        self.refresh_profile_header()

    def _refresh_workspace_status_text(self) -> None:
        with self.db.session() as session:
            active = ProjectRepository(session).get_active_project()
            p_path = active.local_path if active else None

        resolver = PathResolver(self.active_project_slug, p_path)
        sources = resolver.list_all_sources()
        headers = resolver.list_all_headers()
        has_makefile = resolver.get_makefile() is not None

        content = [
            f"Physical Path:     {resolver.root}",
            f"Directory Exists:  {'YES' if resolver.exists() else 'NO'}",
            f"Makefile Found:    {'YES' if has_makefile else 'NO'}",
            f"Source Files (.c): {len(sources)}",
            f"Header Files (.h): {len(headers)}",
            "----------------------------------------------------------------",
            "Detected C Source Files:",
        ]
        if sources:
            for s in sources[:12]:
                content.append(f"  • {s.name}")
            if len(sources) > 12:
                content.append(f"  ... and {len(sources) - 12} more files.")
        else:
            content.append("  (No .c files found in current directory)")

        self.txt_project_status.delete("1.0", tk.END)
        self.txt_project_status.insert(tk.END, "\n".join(content))

    # ==========================================================================
    # PAGE 3: TEST PIPELINE & NORMINETTE
    # ==========================================================================
    def show_test_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Deterministic Verification Pipeline", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")
        tk.Label(header, text="Execute GCC warnings, Norminette, Forbidden symbols, Unit Tests, and Valgrind.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w")

        # Top Control Card
        ctrl_card = tk.Frame(self.content_area, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        ctrl_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(ctrl_card, text="Target Function:", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(side=tk.LEFT)

        self.ent_test_func = tk.Entry(ctrl_card, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", width=22)
        self.ent_test_func.insert(0, "ft_atoi")
        self.ent_test_func.pack(side=tk.LEFT, padx=10)

        btn_run_pipeline = ttk.Button(ctrl_card, text="⚡ Run Full Pipeline", style="Primary.TButton", command=self._threaded_run_pipeline)
        btn_run_pipeline.pack(side=tk.LEFT, padx=6)

        btn_run_norm = ttk.Button(ctrl_card, text="Check Norminette", command=self._threaded_run_norminette)
        btn_run_norm.pack(side=tk.LEFT, padx=6)

        # Status Badges Bar
        self.badges_frame = tk.Frame(ctrl_card, bg=BG_PANEL)
        self.badges_frame.pack(side=tk.RIGHT, padx=10)

        self.badge_labels = {}
        for name in ["Norminette", "GCC", "Symbols", "Tests", "Valgrind"]:
            lbl = tk.Label(self.badges_frame, text=f" {name}: -- ", font=("Consolas", 9, "bold"), bg=BG_ELEVATED, fg=TEXT_MUTED, padx=6, pady=3)
            lbl.pack(side=tk.LEFT, padx=3)
            self.badge_labels[name] = lbl

        # Terminal Output Box
        output_frame = tk.Frame(self.content_area, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        output_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(output_frame, text="Execution & Diagnostic Terminal", font=("Segoe UI", 11, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w", pady=(0, 8))

        self.txt_test_log = tk.Text(output_frame, bg="#0D1117", fg=TEXT_WHITE, font=("Consolas", 10), relief="flat", padx=12, pady=12)
        self.txt_test_log.pack(fill=tk.BOTH, expand=True)

    def _threaded_run_pipeline(self) -> None:
        func_name = self.ent_test_func.get().strip()
        if not func_name:
            messagebox.showwarning("Input Required", "Enter a function name (e.g. ft_atoi)")
            return

        self.set_busy(f"Verifying {func_name}...")
        self.txt_test_log.delete("1.0", tk.END)
        self.txt_test_log.insert(tk.END, f">> Running 5-Stage Verification Pipeline for {func_name}...\n")

        for b in self.badge_labels.values():
            b.config(bg=BG_ELEVATED, fg=TEXT_MUTED, text=b.cget("text").split(":")[0] + ": RUNNING")

        def worker():
            try:
                paths = get_paths()
                template_file = paths.templates_dir / f"{self.active_project_slug}.json"
                import json
                t_cfg = json.loads(template_file.read_text(encoding="utf-8")) if template_file.exists() else {}

                orchestrator = TestRunnerOrchestrator(self.active_project_slug)
                result = orchestrator.run_exercise(func_name, t_cfg, self.current_student.id)

                self.after(0, self._render_pipeline_result, result)
            except Exception as e:
                self.after(0, self._render_pipeline_error, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _render_pipeline_result(self, result: PipelineResult) -> None:
        self.set_idle()

        # Update Badges
        self._set_badge("Norminette", result.norm_passed)
        self._set_badge("GCC", result.compile_passed)
        self._set_badge("Symbols", result.forbidden_passed)
        self._set_badge("Tests", result.tests_failed == 0)
        self._set_badge("Valgrind", result.memory_clean)

        log = [
            f"=== VERIFICATION RESULT: {result.exercise_name} [{'PASS' if result.all_passed else 'FAIL'}] ===",
            f"Norminette Passed:       {result.norm_passed}",
            f"Compilation Clean:       {result.compile_passed}",
            f"Forbidden Symbols Clean: {result.forbidden_passed}",
            f"Unit Tests Passed:       {result.tests_passed} (Failed: {result.tests_failed})",
            f"Valgrind Memory Clean:   {result.memory_clean}",
            "\n--- COMPILER / BUILD LOG ---",
            result.compiler_output or "(Zero warnings/errors)",
            "\n--- NORMINETTE DIAGNOSTIC ---",
            result.norm_output or "(Norme compliant)",
        ]

        if result.all_passed:
            xp, _ = self.profile_mgr.award_xp("function_cleared")
            log.append(f"\n★ EXERCISE CLEARED! +{xp} XP Awarded ★")
            self.refresh_profile_header()

        self.txt_test_log.delete("1.0", tk.END)
        self.txt_test_log.insert(tk.END, "\n".join(log))

    def _render_pipeline_error(self, err_msg: str) -> None:
        self.set_idle()
        for b in self.badge_labels.values():
            b.config(bg=STATUS_RED, fg=TEXT_WHITE, text=b.cget("text").split(":")[0] + ": ERROR")
        self.txt_test_log.delete("1.0", tk.END)
        self.txt_test_log.insert(tk.END, f"[FATAL ERROR]\n{err_msg}")

    def _set_badge(self, name: str, passed: bool) -> None:
        color = STATUS_GREEN if passed else STATUS_RED
        text = f" {name}: {'PASS' if passed else 'FAIL'} "
        self.badge_labels[name].config(bg=color, fg="#FFFFFF", text=text)

    def _threaded_run_norminette(self) -> None:
        self.set_busy("Running Norminette...")
        self.txt_test_log.delete("1.0", tk.END)
        self.txt_test_log.insert(tk.END, ">> Executing Norminette across workspace...\n")

        def worker():
            with self.db.session() as session:
                active = ProjectRepository(session).get_active_project()
                p_path = active.local_path if active else None
            resolver = PathResolver(self.active_project_slug, p_path)
            runner = NorminetteRunner()
            res = runner.run(resolver.root)

            def update_ui():
                self.set_idle()
                self._set_badge("Norminette", res.passed)
                self.txt_test_log.delete("1.0", tk.END)
                if res.passed:
                    self.txt_test_log.insert(tk.END, "✓ Norminette OK: All source files strictly comply with 42 Norm.")
                else:
                    out = ["✗ Norminette Violations Found:\n"]
                    for err in res.errors:
                        out.append(f"Line {err.line}, Col {err.column}: [{err.error_code}] {err.description}")
                    self.txt_test_log.insert(tk.END, "\n".join(out))

            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    # ==========================================================================
    # PAGE 4: GEMINI AI MENTOR HUB
    # ==========================================================================
    def show_ai_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Gemini Socratic AI Mentor Hub", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")
        tk.Label(header, text="Gated pedagogical guidance across Tutor, Debugger, Reviewer, and Quizzer personas.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w")

        # Tab navigation for AI modes
        ai_tabs = tk.Frame(self.content_area, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER_COLOR)
        ai_tabs.pack(fill=tk.X, pady=(0, 12))

        btn_tutor = ttk.Button(ai_tabs, text="Socratic Tutor", command=self._build_ai_tutor_ui)
        btn_tutor.pack(side=tk.LEFT, padx=8, pady=8)

        btn_debug = ttk.Button(ai_tabs, text="Debugger (Hint Ladder)", command=self._build_ai_debug_ui)
        btn_debug.pack(side=tk.LEFT, padx=8, pady=8)

        btn_quiz = ttk.Button(ai_tabs, text="Interactive Quiz", command=self._build_ai_quiz_ui)
        btn_quiz.pack(side=tk.LEFT, padx=8, pady=8)

        btn_audit = ttk.Button(ai_tabs, text="Repository Architecture Audit", command=self._build_ai_audit_ui)
        btn_audit.pack(side=tk.LEFT, padx=8, pady=8)

        # Dynamic AI Work Area
        self.ai_work_area = tk.Frame(self.content_area, bg=BG_PANEL, padx=20, pady=20, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.ai_work_area.pack(fill=tk.BOTH, expand=True)

        self._build_ai_tutor_ui()

    def _build_ai_tutor_ui(self) -> None:
        for w in self.ai_work_area.winfo_children():
            w.destroy()

        tk.Label(self.ai_work_area, text="Socratic Theoretical Tutor", font=("Segoe UI", 12, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")
        tk.Label(self.ai_work_area, text="Ask conceptual questions regarding pointers, stack/heap layout, or libc rules. The tutor guides without spoiling code.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        input_frame = tk.Frame(self.ai_work_area, bg=BG_PANEL)
        input_frame.pack(fill=tk.X, pady=8)

        self.ent_ai_prompt = tk.Entry(input_frame, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", font=("Segoe UI", 10))
        self.ent_ai_prompt.insert(0, "Explain the difference between memmove and memcpy overlap")
        self.ent_ai_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        btn_ask = ttk.Button(input_frame, text="Consult Tutor", style="Primary.TButton", command=self._threaded_ask_tutor)
        btn_ask.pack(side=tk.RIGHT)

        self.txt_ai_response = tk.Text(self.ai_work_area, bg=BG_ELEVATED, fg=TEXT_WHITE, font=("Segoe UI", 10), wrap=tk.WORD, relief="flat", padx=14, pady=14)
        self.txt_ai_response.pack(fill=tk.BOTH, expand=True, pady=10)

    def _threaded_ask_tutor(self) -> None:
        topic = self.ent_ai_prompt.get().strip()
        if not topic:
            return

        self.set_busy("Consulting Socratic Tutor...")
        self.txt_ai_response.delete("1.0", tk.END)
        self.txt_ai_response.insert(tk.END, "Consulting Gemini AI Mentor... Please hold...\n")

        def worker():
            try:
                agent = TutorAgent(self.active_project_slug, self.current_student.id)
                diag = agent.explain_concept(topic=topic)
                self.after(0, self._render_ai_diagnosis, diag)
            except Exception as e:
                self.after(0, lambda: self.txt_ai_response.insert(tk.END, f"\n[AI Error]: {str(e)}"))
            finally:
                self.after(0, self.set_idle)

        threading.Thread(target=worker, daemon=True).start()

    def _build_ai_debug_ui(self) -> None:
        for w in self.ai_work_area.winfo_children():
            w.destroy()

        tk.Label(self.ai_work_area, text="Systems Debugger with 6-Tier Hint Ladder", font=("Segoe UI", 12, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")

        bar = tk.Frame(self.ai_work_area, bg=BG_PANEL)
        bar.pack(fill=tk.X, pady=8)

        tk.Label(bar, text="Function:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT)
        self.ent_debug_fn = tk.Entry(bar, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", width=16)
        self.ent_debug_fn.insert(0, "ft_atoi")
        self.ent_debug_fn.pack(side=tk.LEFT, padx=8)

        tk.Label(bar, text="Hint Tier:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=(10, 4))
        self.cmb_ladder = ttk.Combobox(bar, values=["Tier 0 (Outcome)", "Tier 1 (Concept)", "Tier 2 (Localizer)", "Tier 3 (Algorithm)", "Tier 4 (Pseudocode)", "Tier 5 (Scaffold)"], state="readonly", width=22)
        self.cmb_ladder.set("Tier 1 (Concept)")
        self.cmb_ladder.pack(side=tk.LEFT, padx=6)

        btn_run = ttk.Button(bar, text="Diagnose Issue", style="Primary.TButton", command=self._threaded_ai_debug)
        btn_run.pack(side=tk.LEFT, padx=10)

        self.txt_ai_response = tk.Text(self.ai_work_area, bg=BG_ELEVATED, fg=TEXT_WHITE, font=("Segoe UI", 10), wrap=tk.WORD, relief="flat", padx=14, pady=14)
        self.txt_ai_response.pack(fill=tk.BOTH, expand=True, pady=10)

    def _threaded_ai_debug(self) -> None:
        fn = self.ent_debug_fn.get().strip()
        tier_idx = int(self.cmb_ladder.get().split()[1])

        self.set_busy(f"Debugging {fn} (Tier {tier_idx})...")
        self.txt_ai_response.delete("1.0", tk.END)
        self.txt_ai_response.insert(tk.END, f"Analyzing diagnostics for {fn} via Hint Tier {tier_idx}...\n")

        def worker():
            try:
                with self.db.session() as session:
                    proj = ProjectRepository(session).get_by_slug(self.active_project_slug)
                    ex = ExerciseRepository(session).get_exercise(proj.id, fn) if proj else None
                    attempts = AttemptRepository(session).get_latest_attempts(ex.id, limit=1) if ex else []
                    latest = attempts[0] if attempts else None

                agent = DebuggerAgent(self.active_project_slug, self.current_student.id)
                diag = agent.diagnose_failure(
                    exercise_name=fn,
                    hint_level=tier_idx,
                    compiler_log=latest.compiler_output if latest else None,
                    norm_log=latest.norm_output if latest else None,
                )
                self.after(0, self._render_ai_diagnosis, diag)
            except Exception as e:
                self.after(0, lambda: self.txt_ai_response.insert(tk.END, f"\n[Debugger Error]: {str(e)}"))
            finally:
                self.after(0, self.set_idle)

        threading.Thread(target=worker, daemon=True).start()

    def _render_ai_diagnosis(self, diag: AIDiagnosis) -> None:
        self.txt_ai_response.delete("1.0", tk.END)
        content = [
            f"PROBLEM CATEGORY:  {diag.problem_type.upper()}",
            f"SEVERITY:          {diag.severity.upper()}",
            "----------------------------------------------------------------",
            f"THEORETICAL CONCEPT:\n{diag.concept_explained}\n",
            f"OBSERVATION:\n{diag.observation}\n",
            f"PROGRESSIVE HINT [TIER {diag.hint_level}]:\n{diag.hint_content}\n",
            f"NEXT RECOMMENDED ACTION:\n{diag.suggested_action}",
        ]
        self.txt_ai_response.insert(tk.END, "\n".join(content))

    def _build_ai_quiz_ui(self) -> None:
        for w in self.ai_work_area.winfo_children():
            w.destroy()

        tk.Label(self.ai_work_area, text="Interactive Low-Level C Quiz", font=("Segoe UI", 12, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")

        bar = tk.Frame(self.ai_work_area, bg=BG_PANEL)
        bar.pack(fill=tk.X, pady=8)

        tk.Label(bar, text="Target Concept:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT)
        self.cmb_quiz_concept = ttk.Combobox(bar, values=["pointers", "memory_allocation", "ascii_and_types", "linked_lists"], state="readonly", width=22)
        self.cmb_quiz_concept.set("pointers")
        self.cmb_quiz_concept.pack(side=tk.LEFT, padx=8)

        btn_gen = ttk.Button(bar, text="Generate Challenge", style="Primary.TButton", command=self._threaded_gen_quiz)
        btn_gen.pack(side=tk.LEFT, padx=10)

        self.quiz_container = tk.Frame(self.ai_work_area, bg=BG_PANEL)
        self.quiz_container.pack(fill=tk.BOTH, expand=True, pady=10)

    def _threaded_gen_quiz(self) -> None:
        concept = self.cmb_quiz_concept.get()
        self.set_busy(f"Generating quiz for {concept}...")
        for w in self.quiz_container.winfo_children():
            w.destroy()

        lbl_loading = tk.Label(self.quiz_container, text="Generating targeted challenge from Gemini AI...", bg=BG_PANEL, fg=TEXT_MUTED)
        lbl_loading.pack(anchor="w", pady=10)

        def worker():
            try:
                agent = QuizzerAgent(self.active_project_slug, self.current_student.id)
                quiz = agent.generate_quiz(concept)
                self.after(0, self._render_quiz_interactive, quiz)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Quiz Error", str(e)))
            finally:
                self.after(0, self.set_idle)

        threading.Thread(target=worker, daemon=True).start()

    def _render_quiz_interactive(self, quiz: QuizQuestion) -> None:
        for w in self.quiz_container.winfo_children():
            w.destroy()

        tk.Label(self.quiz_container, text=f"Target: {quiz.concept.upper()}", font=("Segoe UI", 9, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")
        tk.Label(self.quiz_container, text=quiz.question, font=("Segoe UI", 11, "bold"), fg=TEXT_WHITE, bg=BG_PANEL, wraplength=700, justify=tk.LEFT).pack(anchor="w", pady=6)

        if quiz.code_context:
            snippet_box = tk.Text(self.quiz_container, bg=BG_ELEVATED, fg=TEXT_WHITE, font=("Consolas", 10), height=5, relief="flat", padx=10, pady=8)
            snippet_box.insert(tk.END, quiz.code_context)
            snippet_box.pack(fill=tk.X, pady=6)

        self.quiz_selected_idx = tk.IntVar(value=-1)

        for i, opt in enumerate(quiz.options):
            rb = tk.Radiobutton(
                self.quiz_container,
                text=opt,
                variable=self.quiz_selected_idx,
                value=i,
                bg=BG_PANEL,
                fg=TEXT_WHITE,
                selectcolor=BG_ELEVATED,
                activebackground=BG_PANEL,
                activeforeground=ACCENT_TEAL,
                font=("Segoe UI", 10),
            )
            rb.pack(anchor="w", padx=10, pady=3)

        btn_submit = ttk.Button(self.quiz_container, text="Submit Answer", style="Primary.TButton", command=lambda: self._evaluate_quiz(quiz))
        btn_submit.pack(anchor="w", pady=12)

        self.lbl_quiz_feedback = tk.Label(self.quiz_container, text="", font=("Segoe UI", 10), bg=BG_PANEL, justify=tk.LEFT, wraplength=700)
        self.lbl_quiz_feedback.pack(anchor="w", pady=4)

    def _evaluate_quiz(self, quiz: QuizQuestion) -> None:
        chosen = self.quiz_selected_idx.get()
        if chosen == -1:
            messagebox.showwarning("Select Answer", "Please choose an option before submitting.")
            return

        if chosen == quiz.correct_option_index:
            self.lbl_quiz_feedback.config(text=f"✓ CORRECT!\n\nExplanation:\n{quiz.explanation}", fg=STATUS_GREEN)
            xp, _ = self.profile_mgr.award_xp("quiz_correct")
            self.refresh_profile_header()
        else:
            correct_txt = quiz.options[quiz.correct_option_index]
            self.lbl_quiz_feedback.config(text=f"✗ INCORRECT.\nCorrect option was #{quiz.correct_option_index + 1}: {correct_txt}\n\nExplanation:\n{quiz.explanation}", fg=STATUS_RED)

    def _build_ai_audit_ui(self) -> None:
        for w in self.ai_work_area.winfo_children():
            w.destroy()

        tk.Label(self.ai_work_area, text="Repository Architecture Audit", font=("Segoe UI", 12, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w")
        tk.Label(self.ai_work_area, text="Gemini examines your Makefile dependencies, header organization, and cross-file code repetition.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        btn_run = ttk.Button(self.ai_work_area, text="Run Architectural Audit", style="Primary.TButton", command=self._threaded_run_audit)
        btn_run.pack(anchor="w", pady=6)

        self.txt_ai_response = tk.Text(self.ai_work_area, bg=BG_ELEVATED, fg=TEXT_WHITE, font=("Segoe UI", 10), wrap=tk.WORD, relief="flat", padx=14, pady=14)
        self.txt_ai_response.pack(fill=tk.BOTH, expand=True, pady=10)

    def _threaded_run_audit(self) -> None:
        self.set_busy("Auditing repository architecture...")
        self.txt_ai_response.delete("1.0", tk.END)
        self.txt_ai_response.insert(tk.END, "Analyzing all headers, Makefiles, and project structures...\n")

        def worker():
            try:
                agent = ProjectAnalystAgent(self.active_project_slug, self.current_student.id)
                audit: ProjectAudit = agent.audit_entire_project()

                def update_ui():
                    self.set_idle()
                    self.txt_ai_response.delete("1.0", tk.END)
                    lines = [
                        f"ARCHITECTURE QUALITY SCORE: {audit.architecture_score} / 100",
                        "================================================================",
                        "\nNORMINETTE RISKS:",
                    ]
                    for r in audit.norm_risks:
                        lines.append(f"  • {r}")
                    lines.append("\nMEMORY MANAGEMENT RISKS:")
                    for m in audit.memory_risks:
                        lines.append(f"  • {m}")
                    lines.append("\nMAKEFILE DEFECTS:")
                    for mk in audit.makefile_issues:
                        lines.append(f"  • {mk}")
                    lines.append(f"\nLEARNING OBSERVATION:\n{audit.learning_observation}")

                    self.txt_ai_response.insert(tk.END, "\n".join(lines))

                self.after(0, update_ui)
            except Exception as e:
                self.after(0, lambda: self.txt_ai_response.insert(tk.END, f"\n[Audit Error]: {str(e)}"))
            finally:
                self.after(0, self.set_idle)

        threading.Thread(target=worker, daemon=True).start()

    # ==========================================================================
    # PAGE 5: STUDY SESSIONS
    # ==========================================================================
    def show_session_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Timed Study Sprints", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")
        tk.Label(header, text="Track focus periods, accumulate XP, and maintain your learning streak.", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w")

        card = tk.Frame(self.content_area, bg=BG_PANEL, padx=20, pady=20, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.pack(fill=tk.BOTH, expand=True)

        self.lbl_timer = tk.Label(card, text="00:00:00", font=("Consolas", 36, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL)
        self.lbl_timer.pack(pady=20)

        btn_bar = tk.Frame(card, bg=BG_PANEL)
        btn_bar.pack(pady=10)

        self.btn_session_toggle = ttk.Button(btn_bar, text="▶ Start Sprint", style="Primary.TButton", command=self._toggle_session)
        self.btn_session_toggle.pack(side=tk.LEFT, padx=10)

        # Counter Inputs
        cnt_bar = tk.Frame(card, bg=BG_PANEL)
        cnt_bar.pack(pady=16)

        tk.Label(cnt_bar, text="Functions Cleared:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT)
        self.spn_funcs = tk.Spinbox(cnt_bar, from_=0, to=50, width=5, bg=BG_ELEVATED, fg=TEXT_WHITE, buttonbackground=BG_ELEVATED)
        self.spn_funcs.pack(side=tk.LEFT, padx=8)

        tk.Label(cnt_bar, text="Hints Requested:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=(16, 0))
        self.spn_hints = tk.Spinbox(cnt_bar, from_=0, to=50, width=5, bg=BG_ELEVATED, fg=TEXT_WHITE, buttonbackground=BG_ELEVATED)
        self.spn_hints.pack(side=tk.LEFT, padx=8)

        self.lbl_session_info = tk.Label(card, text="Session status: Ready to sprint.", font=("Segoe UI", 10), bg=BG_PANEL, fg=TEXT_MUTED)
        self.lbl_session_info.pack(pady=10)

        self._check_ongoing_session()

    def _check_ongoing_session(self) -> None:
        ctrl = SessionController(self.active_project_slug)
        ongoing = ctrl.get_open_session()
        if ongoing:
            self.session_timer_running = True
            # Calculate elapsed time from ongoing.start_time
            now = datetime.now(timezone.utc)
            st = ongoing.start_time
            if st.tzinfo is None:
                st = st.replace(tzinfo=timezone.utc)
            elapsed = (now - st).total_seconds()
            self.session_start_epoch = time.time() - elapsed
            self.btn_session_toggle.config(text="■ Conclude Session")
            self.lbl_session_info.config(text=f"Session #{ongoing.id} currently active.", fg=STATUS_GREEN)
            self._update_timer()

    def _toggle_session(self) -> None:
        ctrl = SessionController(self.active_project_slug)

        if not self.session_timer_running:
            # Start
            sid = ctrl.start_session()
            self.session_timer_running = True
            self.session_start_epoch = time.time()
            self.btn_session_toggle.config(text="■ Conclude Session")
            self.lbl_session_info.config(text=f"Session #{sid} running.", fg=STATUS_GREEN)
            self._update_timer()
        else:
            # Stop
            f_done = int(self.spn_funcs.get())
            h_used = int(self.spn_hints.get())
            try:
                rec = ctrl.end_session(functions_completed=f_done, hints_used=h_used)
                self.session_timer_running = False
                self.btn_session_toggle.config(text="▶ Start Sprint")
                self.lbl_session_info.config(text=f"Sprint completed! +{rec.xp_earned} XP Awarded.", fg=STATUS_GREEN)
                self.refresh_profile_header()
            except Exception as e:
                messagebox.showerror("Session Error", str(e))

    def _update_timer(self) -> None:
        if self.session_timer_running:
            elapsed = int(time.time() - self.session_start_epoch)
            hrs = elapsed // 3600
            mins = (elapsed % 3600) // 60
            secs = elapsed % 60
            self.lbl_timer.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
            self.after(1000, self._update_timer)

    # ==========================================================================
    # PAGE 6: SKILLS & BUGS
    # ==========================================================================
    def show_skills_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Systems Concept Mastery & Personal Bug Database", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")

        # Two-column layout
        grid = tk.Frame(self.content_area, bg=BG_DARK)
        grid.pack(fill=tk.BOTH, expand=True)

        # Left Column: Skills
        left_col = tk.Frame(grid, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_col, text="Skill Tree Mastery", font=("Segoe UI", 12, "bold"), fg=ACCENT_TEAL, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        matrix = SkillMatrix(self.current_student.id)
        reports = matrix.get_profile_report()

        for r in reports:
            sf = tk.Frame(left_col, bg=BG_PANEL)
            sf.pack(fill=tk.X, pady=6)

            tk.Label(sf, text=r.concept.replace("_", " ").title(), font=("Segoe UI", 9, "bold"), fg=TEXT_WHITE, bg=BG_PANEL).pack(anchor="w")

            bar_frame = tk.Frame(sf, bg=BG_ELEVATED, height=12)
            bar_frame.pack(fill=tk.X, pady=3)

            # Fill bar
            pct = max(0.0, min(100.0, r.mastery_percentage))
            fill_color = STATUS_RED if r.is_weakness else STATUS_GREEN

            fill_bar = tk.Frame(bar_frame, bg=fill_color, width=int(pct * 2.5), height=12)
            fill_bar.pack(side=tk.LEFT)

            tk.Label(sf, text=f"{pct:.1f}% ({r.total_tests} attempts)  [{'WEAKNESS' if r.is_weakness else 'STABLE'}]", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")

        # Right Column: Mistakes
        right_col = tk.Frame(grid, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(right_col, text="Personal Bug Database", font=("Segoe UI", 12, "bold"), fg=STATUS_RED, bg=BG_PANEL).pack(anchor="w", pady=(0, 10))

        tree = ttk.Treeview(right_col, columns=("cat", "occ", "error"), show="headings", height=12)
        tree.heading("cat", text="Category")
        tree.heading("occ", text="Count")
        tree.heading("error", text="Raw Error")

        tree.column("cat", width=120)
        tree.column("occ", width=50, anchor="center")
        tree.column("error", width=220)
        tree.pack(fill=tk.BOTH, expand=True)

        with self.db.session() as session:
            mistakes = MistakeRepository(session).get_unresolved_mistakes()
            for m in mistakes:
                tree.insert("", tk.END, values=(m.category, m.occurrences, m.raw_error[:60]))

    # ==========================================================================
    # PAGE 7: REFERENCES
    # ==========================================================================
    def show_ref_page(self) -> None:
        self._clear_content()

        header = tk.Frame(self.content_area, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(header, text="Reference Solutions & Official Subjects", font=("Segoe UI", 16, "bold"), fg=TEXT_WHITE, bg=BG_DARK).pack(anchor="w")

        card = tk.Frame(self.content_area, bg=BG_PANEL, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.pack(fill=tk.BOTH, expand=True)

        # Clone Form
        form = tk.Frame(card, bg=BG_PANEL)
        form.pack(fill=tk.X, pady=(0, 16))

        tk.Label(form, text="Git URL:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT)
        self.ent_ref_url = tk.Entry(form, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", width=35)
        self.ent_ref_url.insert(0, "https://github.com/Glagan/42-libft.git")
        self.ent_ref_url.pack(side=tk.LEFT, padx=8)

        tk.Label(form, text="Name:", bg=BG_PANEL, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=(8, 0))
        self.ent_ref_name = tk.Entry(form, bg=BG_ELEVATED, fg=TEXT_WHITE, insertbackground=TEXT_WHITE, relief="flat", width=16)
        self.ent_ref_name.insert(0, "peer_libft")
        self.ent_ref_name.pack(side=tk.LEFT, padx=8)

        btn_add = ttk.Button(form, text="Clone Reference", style="Primary.TButton", command=self._on_add_reference)
        btn_add.pack(side=tk.LEFT, padx=8)

        # Table
        self.tree_refs = ttk.Treeview(card, columns=("id", "type", "name", "status"), show="headings", height=10)
        self.tree_refs.heading("id", text="ID")
        self.tree_refs.heading("type", text="Type")
        self.tree_refs.heading("name", text="Name")
        self.tree_refs.heading("status", text="Policy Status")

        self.tree_refs.column("id", width=40, anchor="center")
        self.tree_refs.column("type", width=100)
        self.tree_refs.column("name", width=200)
        self.tree_refs.column("status", width=100, anchor="center")
        self.tree_refs.pack(fill=tk.BOTH, expand=True, pady=10)

        self._refresh_refs_table()

    def _refresh_refs_table(self) -> None:
        for item in self.tree_refs.get_children():
            self.tree_refs.delete(item)

        with self.db.session() as session:
            proj = ProjectRepository(session).get_active_project()
            if proj:
                refs = ReferenceRepository(session).list_references(proj.id)
                for r in refs:
                    st = "🔒 LOCKED" if r.is_locked else "🔓 UNLOCKED"
                    self.tree_refs.insert("", tk.END, values=(r.id, r.ref_type, r.name, st))

    def _on_add_reference(self) -> None:
        url = self.ent_ref_url.get().strip()
        name = self.ent_ref_name.get().strip()
        if not url or not name:
            messagebox.showwarning("Input Required", "Specify both URL and Name.")
            return

        self.set_busy(f"Cloning reference repo {name}...")

        def worker():
            try:
                with self.db.session() as session:
                    proj = ProjectRepository(session).get_active_project()
                    proj_id = proj.id if proj else 1

                mgr = ReferenceManager(proj_id)
                mgr.register_github_repo(url, name)
                self.after(0, self._refresh_refs_table)
                self.after(0, lambda: messagebox.showinfo("Cloned", f"Successfully registered reference: {name}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Clone Failed", str(e)))
            finally:
                self.after(0, self.set_idle)

        threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    app = Student42App()
    app.mainloop()


if __name__ == "__main__":
    main()