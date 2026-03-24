"""Filesystem-backed plan document storage."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jcode_conf.config import LETTA_HOME


def _resolve_letta_home(letta_home: Path | None = None) -> Path:
    if letta_home is not None:
        return letta_home.expanduser().resolve()
    return LETTA_HOME


def _sanitize_project_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    return name.strip("-") or "project"


@dataclass(frozen=True)
class PlanStore:
    working_dir: Path
    letta_home: Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "working_dir", self.working_dir.expanduser().resolve())
        object.__setattr__(self, "letta_home", _resolve_letta_home(self.letta_home))

    @property
    def plans_dir(self) -> Path:
        return Path(self.letta_home) / "plans"  # type: ignore[arg-type]

    def ensure_initialized(self) -> None:
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def create_plan_file(self, project_name: str | None = None) -> Path:
        self.ensure_initialized()

        project = _sanitize_project_name(project_name or self.working_dir.name)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        plan_id = uuid.uuid4().hex[:8]
        path = self.plans_dir / f"{project}-{ts}-{plan_id}.md"

        path.write_text(self._default_template(project), encoding="utf-8")
        return path

    def list_plans(self, project_name: str | None = None) -> list[Path]:
        self.ensure_initialized()
        paths = list(self.plans_dir.glob("*.md"))

        if project_name:
            needle = _sanitize_project_name(project_name)
            paths = [p for p in paths if needle in p.name]

        paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return paths

    @staticmethod
    def _default_template(project: str) -> str:
        return (
            "# Implementation Plan\n\n"
            f"**Project**: {project}\n\n"
            "## Overview\n\n"
            "## Requirements\n\n"
            "## Analysis\n\n"
            "## Proposed Changes\n\n"
            "## Implementation Steps\n\n"
            "## Verification\n\n"
            "## Notes\n"
        )
