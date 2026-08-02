from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_ROOT = REPO_ROOT / "skills" / "autonomous-project-discovery"
ACTIVE_ROUTING_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "CLAUDE.md",
    *DISCOVERY_ROOT.rglob("*.md"),
    *DISCOVERY_ROOT.rglob("*.json"),
]
REMOVED_SKILLS = ("autonomous-planning", "autonomous-implementation")


def test_removed_lifecycle_skills_are_not_shipped_or_installed_locally() -> None:
    for skill_name in REMOVED_SKILLS:
        assert not (REPO_ROOT / "skills" / skill_name / "SKILL.md").exists()
        assert not (REPO_ROOT / ".agents" / "skills" / skill_name / "SKILL.md").exists()
        assert not (REPO_ROOT / ".claude" / "skills" / skill_name / "SKILL.md").exists()

    lock = json.loads((REPO_ROOT / "skills-lock.json").read_text(encoding="utf-8"))
    assert not (set(REMOVED_SKILLS) & lock["skills"].keys())


def test_discovery_routes_ready_builds_to_ordinary_scoped_workflow() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in ACTIVE_ROUTING_FILES)
    for skill_name in REMOVED_SKILLS:
        assert skill_name not in combined

    skill_text = (DISCOVERY_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "ordinary scoped workflow" in skill_text
    assert "planning, delegation, TDD, and review" in skill_text
    assert "next_stage: SCOPED_WORKFLOW" in skill_text
