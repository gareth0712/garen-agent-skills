from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, *needles: str) -> str:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path.relative_to(ROOT)} missing: {missing}"
    return text


skill = require(
    ROOT / "SKILL.md",
    "Product Existence Challenge",
    "Outcome Verifiability Challenge",
    "production_commercial",
    "learning_prototype",
    "user_directed_unapproved",
    "bypassed_learning",
    "one sharp",
    "no universal prompt-count threshold",
    "same representative raw inputs and requested outcomes",
    "The bypass expires",
    "stop re-litigating the same gate",
)
method = require(
    ROOT / "references" / "discovery-method.md",
    "Direct-model baseline",
    "persistent state",
    "falsification_condition",
    "human_boundary",
    "external_evidence",
)
templates = require(
    ROOT / "references" / "state-templates.md",
    "product_intent: {production_commercial | learning_prototype}",
    "existence_gate_state: {approved | insufficient | external_evidence | bypassed_learning}",
    "verifiability_gate_state: {approved | partial | insufficient}",
    "product_justification_state: {approved | blocked | user_directed_unapproved | bypassed_learning}",
    "## Product intent and justification state",
    "## Outcome verifiability matrix",
    "## Override or learning-bypass evidence",
    "SESSION-HANDOFF.md",
)
launcher = require(
    ROOT / "references" / "launcher-template.md",
    "Product intent",
    "Direct-model baseline authority",
    "User override policy",
    "Learning/prototype bypass policy",
)

handoff_match = re.search(
    r"## `SESSION-HANDOFF\.md`\s+```markdown(?P<body>.*?)```",
    templates,
    re.S,
)
assert handoff_match, "state-templates.md missing SESSION-HANDOFF.md template body"
handoff = handoff_match.group("body")
for needle in (
    "product_justification_state",
    "product_justification_evidence",
    "failed/insufficient claims",
    "override or bypass boundary",
    "effect-blocking gates",
    "revisit_trigger",
):
    assert needle in handoff, f"SESSION-HANDOFF.md template missing: {needle}"

for text in (skill, method, templates, launcher):
    assert not re.search(r"(?:exactly|fewer than|at most) three prompts", text, re.I)

assert "learning/prototype bypass applies only to product-existence justification" in skill
assert "outcome verification remains mandatory" in skill
assert "ready + user_directed_unapproved" in method
assert "does not mean Discovery endorses building it" in method

cases = json.loads((ROOT / "evals" / "viability-evals.json").read_text(encoding="utf-8"))
assert [case["id"] for case in cases["cases"]] == list(range(1, 8))
states = {
    case["expected_product_justification_state"]
    for case in cases["cases"]
    if case["should_activate_gates"]
}
assert states == {"approved", "blocked", "user_directed_unapproved", "bypassed_learning"}
assert next(case for case in cases["cases"] if case["id"] == 7)["should_activate_gates"] is False

evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
for eval_id in (4, 5, 6, 7, 8):
    item = next(entry for entry in evals if entry["id"] == eval_id)
    joined = "\n".join(item["expectations"])
    assert "product_justification_state" in joined
    assert "Outcome verifiability matrix" in joined

print("product existence and verifiability contract tests: PASS")
