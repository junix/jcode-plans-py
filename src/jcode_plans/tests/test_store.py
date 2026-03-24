from __future__ import annotations

from pathlib import Path

from jcode_plans import PlanStore


def test_plan_store_creates_expected_template(tmp_path: Path) -> None:
    working_dir = tmp_path / "project"
    working_dir.mkdir()

    store = PlanStore(working_dir, letta_home=tmp_path / ".letta")
    plan_file = store.create_plan_file("test")

    content = plan_file.read_text()
    assert "# Implementation Plan" in content
    assert "## Verification" in content


def test_plan_store_filters_by_project(tmp_path: Path) -> None:
    working_dir = tmp_path / "project"
    working_dir.mkdir()

    store = PlanStore(working_dir, letta_home=tmp_path / ".letta")
    store.create_plan_file("backend-api")
    store.create_plan_file("frontend-ui")
    store.create_plan_file("backend-api")

    backend_plans = store.list_plans("backend-api")
    frontend_plans = store.list_plans("frontend-ui")

    assert len(backend_plans) == 2
    assert len(frontend_plans) == 1
