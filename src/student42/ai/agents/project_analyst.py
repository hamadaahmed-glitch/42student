"""
Whole-Project Architectural Analyst Agent.
Audits Makefiles, header guards, global code repetition, and structural organization.
"""

from __future__ import annotations

from student42.ai.agents.base import BaseAgent
from student42.ai.schemas import ProjectAudit
from student42.workspace.file_scanner import FileScanner


class ProjectAnalystAgent(BaseAgent):
    """Evaluates holistic project structure and Makefile compliance."""

    SYSTEM_INSTRUCTION = (
        "You are the 42 Senior Software Architect. Conduct a holistic audit of the student's "
        "repository. Examine header organization, Makefile dependency graphs, source separation, "
        "and structural repetition across functions."
    )

    def audit_entire_project(self) -> ProjectAudit:
        """Inspects all project files and Makefiles to generate an architectural audit."""
        sources = self.context_builder.resolver.list_all_sources()
        headers = self.context_builder.resolver.list_all_headers()
        makefile = self.context_builder.resolver.get_makefile()

        sections = [
            f"Project: {self.project_slug}",
            f"Total Source Files: {len(sources)}",
            f"Total Header Files: {len(headers)}",
        ]

        if makefile:
            sections.append(f"Makefile Content:\n```makefile\n{FileScanner.read_file_safe(makefile)}\n```")
        else:
            sections.append("Makefile: NOT FOUND")

        # Sample header content for inspection
        for h in headers[:3]:
            sections.append(f"Header [{h.name}]:\n```c\n{FileScanner.read_file_safe(h)}\n```")

        prompt = (
            "Analyze the overall project architecture based on the repository contents below:\n\n"
            + "\n\n".join(sections)
            + "\n\nProduce an architecture audit with risk items and learning observations."
        )

        return self.client.generate_structured(
            prompt=prompt,
            response_model=ProjectAudit,
            system_instruction=self.SYSTEM_INSTRUCTION,
            use_fast_model=False,
        )