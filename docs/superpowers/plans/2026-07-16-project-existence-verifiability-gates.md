# Project Existence and Verifiability Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-backed product-existence and outcome-verifiability gates to `autonomous-project-discovery`, then push the verified skill to `main` before running fresh isolated evaluations and independent grading.

**Architecture:** Project Discovery will classify product intent, run a direct-model/product-value challenge, and require one verifiability row per material outcome. Gate-local states feed an independent aggregate `product_justification_state`, allowing honest `user_directed_unapproved` continuation and bounded learning bypass without changing `discovery_readiness` semantics. Static contract tests run before push; fresh state-changing evaluations and read-only graders run only from the pushed `main` revision.

**Tech Stack:** Markdown skill contracts, JSON eval manifests, Python 3 contract tests, Git, Codex fresh-agent evaluation artifacts.

## Global Constraints

- Production/commercial greenfield products and substantial new subsystems must run both gates.
- Learning/prototype work may bypass only the product-existence challenge; outcome verification remains mandatory.
- Ask exactly one sharp decision-unlocking question at a time after inspecting available evidence.
- `user_directed_unapproved` permits Planning continuation only with exact override evidence and preserved non-endorsement reasons.
- Never invent a model baseline, metric, product advantage, prompt-count threshold, or external capability.
- Do not modify fixture-source files, shared artifact protocol, append-event implementation, lockfiles, dependencies, secrets, or completed static stage-integration artifacts.
- Production edits remain sequential. Only isolated read-only grading/review may run in parallel.
- Run minimum contract/protocol checks before updating `main`; run fresh evaluation and full verification from the pushed `main` revision.

---

## File Structure

- Create `skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py`: mechanical cross-file contract for activation, states, readiness routes, gate fields, question protocol, and eval cases.
- Create `skills/autonomous-project-discovery/evals/viability-evals.json`: seven executable-ready behavior cases, separate from the existing stage-routing classifier.
- Modify `skills/autonomous-project-discovery/SKILL.md`: binding workflow and completion rules.
- Modify `skills/autonomous-project-discovery/references/discovery-method.md`: decision method, baseline evidence, value dimensions, sharp questions, and state derivation.
- Modify `skills/autonomous-project-discovery/references/state-templates.md`: canonical fields and artifact sections.
- Modify `skills/autonomous-project-discovery/references/launcher-template.md`: launcher policy for intent, external baseline authority, override, and learning bypass.
- Modify `skills/autonomous-project-discovery/evals/evals.json`: five qualifying full-run prompts and expectations.
- Create `docs/superpowers/validation/project-existence-verifiability-gates-validation.md`: post-push evidence report.

---

### Task 1: Bind the two-gate workflow and artifact schema

**Files:**
- Create: `skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py`
- Modify: `skills/autonomous-project-discovery/SKILL.md`
- Modify: `skills/autonomous-project-discovery/references/discovery-method.md`
- Modify: `skills/autonomous-project-discovery/references/state-templates.md`
- Modify: `skills/autonomous-project-discovery/references/launcher-template.md`

**Interfaces:**
- Consumes: existing `discovery_depth`, `discovery_readiness`, focused-question, gate, and `DISCOVERY.md`/`AGENT-STATE.md` contracts.
- Produces: `product_intent`, `existence_gate_state`, `verifiability_gate_state`, `product_justification_state`, evidence/override/revisit fields, two canonical Discovery sections, and exact readiness transitions.

- [ ] **Step 1: Write the failing cross-file contract test**

Create the following file:

```python
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
states = {case["expected_product_justification_state"] for case in cases["cases"]}
assert states == {"approved", "blocked", "user_directed_unapproved", "bypassed_learning"}
assert next(case for case in cases["cases"] if case["id"] == 7)["should_activate_gates"] is False

evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
for eval_id in (4, 5, 6, 7, 8):
    item = next(entry for entry in evals if entry["id"] == eval_id)
    joined = "\n".join(item["expectations"])
    assert "product_justification_state" in joined
    assert "Outcome verifiability matrix" in joined

print("product existence and verifiability contract tests: PASS")
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py
```

Expected: exit `1`; the first failure names missing two-gate contract text or missing `viability-evals.json`.

- [ ] **Step 3: Add the binding workflow to `SKILL.md`**

After `### 4. Establish the framing`, insert two numbered subsections before uncertainty mapping. Use this exact normative content:

```markdown
### 5. Run the Product Existence Challenge

For every greenfield product or substantial new subsystem at `targeted` or `full` depth, record `product_intent` as `production_commercial` or `learning_prototype`. Production/commercial work compares the same representative raw inputs and requested outcomes with an observed direct-model baseline. Record the model/tool identity and date or `unavailable`, fixture paths/hashes, bounded workflow, output evidence, repeatability/manual steps, supported and unsupported claims, material product advantages, validation actions, and falsification conditions. No external execution, paid API, upload, credential, or model result is implied. If current authority or capability cannot produce the baseline, use `existence_gate_state: external_evidence`; never invent it. There is no universal prompt-count threshold.

Material advantages may include persistent state, system-of-record/action integration, legitimate private context, repeatability, collaboration, privacy/offline constraints, auditability, safety/recovery, or measured economic value. Listing a dimension is not evidence.

`learning_prototype` may use `existence_gate_state: bypassed_learning` only with a learning objective, non-commercial boundary, reason, bounded effects/time, and revisit trigger. The learning/prototype bypass applies only to product-existence justification; outcome verification remains mandatory. The bypass expires when its recorded production/commercial revisit trigger is reached.

### 6. Run the Outcome Verifiability Challenge

For every material outcome, persist a stable outcome ID, observable claim, oracle or human rubric, representative and adversarial fixtures, acceptable error without invented precision, deterministic failure classes, automatic verification signal, human boundary, rollback/recovery, falsification condition, owner, and deadline. Never label a human-only judgment automatically verified. If neither an oracle nor a specific human rubric exists, use `verifiability_gate_state: insufficient`.

For missing production/commercial evidence, inspect observable evidence first and ask one sharp decision-unlocking question at a time. Persist the decision, why it is material, required evidence, answer or non-answer, and never repeat a substantively answered question. Questions challenge the product hypothesis without pressuring the user toward approval. Continue until every current-scope material claim is evidenced, falsifiable, or owned; the user explicitly overrides; or a genuine external blocker remains. After an explicit override, stop re-litigating the same gate.

Derive `product_justification_state` independently from `discovery_readiness`: `approved`, `blocked`, `user_directed_unapproved`, or `bypassed_learning`. `blocked` is `not_ready`. An exact user insistence may set `user_directed_unapproved` and permit Planning readiness when all other framing is complete, but every downstream handoff preserves the failed claims, exact override scope, and non-endorsement. `bypassed_learning` may be ready only when outcome verification passes. Routine `skip` work does not activate either gate.
```

Renumber the existing uncertainty/packet/readiness headings while preserving their contents. Add completion-checklist bullets requiring both canonical gate artifacts and exact override/bypass propagation.

- [ ] **Step 4: Add the decision method**

In `references/discovery-method.md`, add `## Product existence and outcome verifiability` after the framing ledger. Define the direct-model baseline fields, the eight value dimensions, the neutral one-question protocol, override stop condition, bypass-expiry trigger, the outcome-row fields, and this state rule:

```markdown
`ready + user_directed_unapproved` means the product is framed well enough for Planning under the user's exact override; it does not mean Discovery endorses building it. `bypassed_learning` bypasses only commercial existence justification and still requires an approved verifiability gate. When a baseline cannot be observed within authority, record `external_evidence`; absence of evidence is neither success nor failure evidence.
```

- [ ] **Step 5: Extend canonical templates**

Add the following exact fields to the `AGENT-STATE.md` template and repeat their evidence boundaries in `DISCOVERY.md` and `SESSION-HANDOFF.md`:

```yaml
product_intent: {production_commercial | learning_prototype}
existence_gate_state: {approved | insufficient | external_evidence | bypassed_learning}
verifiability_gate_state: {approved | partial | insufficient}
product_justification_state: {approved | blocked | user_directed_unapproved | bypassed_learning}
product_justification_evidence:
  path: {evidence path}
  revision: {stable revision or digest}
  observed_at: {timezone-aware ISO-8601}
user_override_evidence:
  path: {durable request/gate path | none}
  revision: {stable revision | none}
  authority: {user/product authority | none}
  exact_scope: {continued scope | none}
revisit_trigger: {measurable condition | none}
```

Add `## Product intent and justification state`, `## Direct-model baseline and durable value evidence`, `## Outcome verifiability matrix`, `## Sharp questions, answers, and rejected framings`, and `## Override or learning-bypass evidence` to the `DISCOVERY.md` template. The `SESSION-HANDOFF.md` template must carry the aggregate state, evidence revision, concrete failed/insufficient claims, exact override or bypass boundary, effect-blocking gates, and revisit trigger. The matrix column order is exactly:

```markdown
| outcome_id | claim | oracle_or_metric | representative_fixtures | adversarial_fixtures | acceptable_error | failure_classes | automatic_verification | human_boundary | rollback_recovery | falsification_condition | owner_deadline |
```

- [ ] **Step 6: Extend the launcher policy**

Add these four fields under Goal/Scope and Authority:

```markdown
- Product intent: {production_commercial | learning_prototype | determine from one focused question after evidence inspection}
- Direct-model baseline authority: read-only local evidence only; external model/API execution requires separately recorded authority
- User override policy: if I explicitly insist after an insufficient gate, continue as `user_directed_unapproved`; preserve the failed claims and never call the project approved
- Learning/prototype bypass policy: bypass product-existence justification only with a learning objective, non-commercial boundary, bounded effects/time, and revisit trigger; outcome verification remains mandatory
```

- [ ] **Step 7: Run the test and verify the expected remaining failure**

Run the same Python command. Expected: it now fails only because `viability-evals.json` or eval IDs `4`–`7` do not exist. This proves the core contract is green before adding eval data.

- [ ] **Step 8: Commit the core workflow**

```powershell
git add -- skills/autonomous-project-discovery/SKILL.md skills/autonomous-project-discovery/references/discovery-method.md skills/autonomous-project-discovery/references/state-templates.md skills/autonomous-project-discovery/references/launcher-template.md skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py
git diff --cached --check
git commit -m "feat(discovery): add product justification gates"
```

Expected: commit succeeds; no fixture, protocol, lockfile, or unrelated path is staged.

---

### Task 2: Add executable evaluation cases

**Files:**
- Create: `skills/autonomous-project-discovery/evals/viability-evals.json`
- Modify: `skills/autonomous-project-discovery/evals/evals.json`
- Test: `skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py`

**Interfaces:**
- Consumes: the four aggregate states and canonical matrix fields from Task 1.
- Produces: seven classification cases and five full artifact-producing evals with exact expected routes.

- [ ] **Step 1: Create the seven-case behavior contract**

Create valid JSON with `skill_name`, `evaluation_mode: "executable_behavior_contract"`, and these exact cases:

```json
{
  "skill_name": "autonomous-project-discovery",
  "evaluation_mode": "executable_behavior_contract",
  "cases": [
    {"id": 1, "intent": "production_commercial", "scenario": "generic menu-photo model wrapper with an observed direct-model baseline covering the primary output and no evidenced durable advantage", "should_activate_gates": true, "expected_product_justification_state": "blocked", "expected_discovery_readiness": "not_ready"},
    {"id": 2, "intent": "production_commercial", "scenario": "the same insufficient wrapper after the user explicitly insists on continuing within a named scope", "should_activate_gates": true, "expected_product_justification_state": "user_directed_unapproved", "expected_discovery_readiness": "ready_if_other_framing_complete"},
    {"id": 3, "intent": "learning_prototype", "scenario": "a bounded clone built to learn OCR/evaluation with a non-commercial boundary and commercial revisit trigger", "should_activate_gates": true, "expected_product_justification_state": "bypassed_learning", "expected_discovery_readiness": "ready_if_verifiability_approved"},
    {"id": 4, "intent": "production_commercial", "scenario": "regulated multi-user workflow with persistence, system-of-record actions, audit/recovery evidence, and measurable outcome oracles", "should_activate_gates": true, "expected_product_justification_state": "approved", "expected_discovery_readiness": "ready_if_other_framing_complete"},
    {"id": 5, "intent": "production_commercial", "scenario": "direct-model execution is unavailable and no current baseline evidence is supplied", "should_activate_gates": true, "expected_product_justification_state": "blocked", "expected_discovery_readiness": "not_ready"},
    {"id": 6, "intent": "production_commercial", "scenario": "subjective coaching outcome has no automatic oracle but has a named evaluator, blinded rubric, disagreement handling, and rollback boundary", "should_activate_gates": true, "expected_product_justification_state": "approved", "expected_discovery_readiness": "ready_if_other_framing_complete"},
    {"id": 7, "intent": "not_applicable", "scenario": "fix an incorrect loading state in an understood existing dashboard", "should_activate_gates": false, "expected_product_justification_state": "not_applicable_skip", "expected_discovery_readiness": "ordinary_scoped_workflow"}
  ]
}
```

- [ ] **Step 2: Add five full-run eval entries**

Append IDs `4`–`8` to `evals.json`:

- Eval 4: production generic wrapper with supplied bounded baseline evidence, no override. Expect `blocked`, `not_ready`, one sharp question, no invented product value.
- Eval 5: production product whose direct-model execution is unavailable and has no supplied baseline. Expect `blocked`, `not_ready`, an exact `external_evidence` gate, and no fabricated comparison.
- Eval 6: the failed generic-wrapper challenge plus explicit exact-scope insistence. Expect `user_directed_unapproved`, exact override evidence, Planning route when otherwise ready, and preserved failed claims.
- Eval 7: bounded learning OCR/evaluation clone. Expect `bypassed_learning`, a non-commercial boundary and revisit trigger, plus a fully populated outcome matrix; never bypass verifiability.
- Eval 8: production regulated workflow with supplied persistence/integration/audit/recovery evidence, explicit automated oracles, and one subjective outcome with a named evaluator, blinded rubric, disagreement handling, and rollback boundary. Expect `approved` without selecting Planning-owned architecture or mislabeling the human judgment as automatic.

Every entry must include these expectations verbatim where applicable:

```text
DISCOVERY.md contains Product intent and justification state, Direct-model baseline and durable value evidence, Outcome verifiability matrix, and Sharp questions, answers, and rejected framings.
AGENT-STATE.md records product_intent, existence_gate_state, verifiability_gate_state, product_justification_state, product_justification_evidence, exact override evidence or none, and revisit_trigger or none.
No model execution, baseline result, product advantage, metric, external effect, or fixed prompt-count threshold is invented.
Every material outcome row contains all twelve canonical fields and distinguishes automatic verification from the named human boundary.
```

Use no `files` fixture for these prompts; each prompt itself supplies bounded evidence and explicitly forbids external model/API execution.

- [ ] **Step 3: Run focused JSON and contract validation**

```powershell
python -m json.tool skills/autonomous-project-discovery/evals/evals.json > $null
python -m json.tool skills/autonomous-project-discovery/evals/viability-evals.json > $null
python skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py
```

Expected: all commands exit `0`; final line is `product existence and verifiability contract tests: PASS`.

- [ ] **Step 4: Commit the eval contract**

```powershell
git add -- skills/autonomous-project-discovery/evals/evals.json skills/autonomous-project-discovery/evals/viability-evals.json
git diff --cached --check
git commit -m "test(discovery): cover product justification states"
```

Expected: only the two eval JSON files are committed; the test file remains in the prior core commit.

---

### Task 3: Run minimum pre-push validation

**Files:**
- Verify only: `skills/autonomous-project-discovery/**`

**Interfaces:**
- Consumes: Tasks 1–2 production commits.
- Produces: minimum static evidence that `main` will not knowingly receive a broken skill or protocol contract.

- [ ] **Step 1: Run focused and existing Discovery tests**

```powershell
python skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py
python skills/autonomous-project-discovery/evals/test_append_event.py
python skills/autonomous-project-discovery/evals/test_run_audit.py
python skills/garen-skill-creator/scripts/quick_validate.py skills/autonomous-project-discovery
```

Expected: four exit codes `0`; append-event suite reports all cases passed; quick validator prints `Skill is valid!`.

- [ ] **Step 2: Validate JSON and whitespace**

```powershell
python -m json.tool skills/autonomous-project-discovery/evals/evals.json > $null
python -m json.tool skills/autonomous-project-discovery/evals/activation-evals.json > $null
python -m json.tool skills/autonomous-project-discovery/evals/viability-evals.json > $null
git diff --check origin/main...HEAD
```

Expected: exit `0`; no JSON or whitespace error.

- [ ] **Step 3: Record the validated feature SHA**

```powershell
$featureSha = git rev-parse HEAD
git status --short
Write-Output "FEATURE_SHA=$featureSha"
```

Expected: no tracked production changes; untracked eval workspaces may remain outside the staged scope.

---

### Task 4: Integrate and push `main` before evaluation

**Files:**
- No new production file; Git integration only.

**Interfaces:**
- Consumes: reviewed feature SHA from Task 3 and explicit user authority to push `main`.
- Produces: remote `main` containing the feature before fresh evaluation begins.

- [ ] **Step 1: Read the branch-finishing skill and inspect both worktrees**

Read `superpowers:finishing-a-development-branch`. Verify current branch, worktree linkage, dirty state, and remote URL. Do not reset or discard unrelated user changes.

- [ ] **Step 2: Fetch current remote main and prove fast-forward ancestry**

```powershell
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

Expected: both exit `0`. If ancestry fails, merge `origin/main` into the feature branch, resolve only in-scope conflicts, rerun Task 3, and repeat this step.

- [ ] **Step 3: Push the feature branch tip directly to remote main**

```powershell
$pushedSha = git rev-parse HEAD
git push origin HEAD:main
git ls-remote origin refs/heads/main
Write-Output "PUSHED_SHA=$pushedSha"
```

Expected: push succeeds and `ls-remote` reports the same SHA. No evaluation worker starts before this equality is observed.

- [ ] **Step 4: Pin post-push evaluation inputs**

Record the pushed SHA, UTC timestamp, `git status --short`, and hashes of `SKILL.md`, four references, the test, and both eval JSON files in an isolated evaluation evidence artifact. This is the cold-evidence source revision.

---

### Task 5: Run post-push fresh evaluation, grading, and final report

**Files:**
- Create: isolated run roots under `skills/autonomous-project-discovery-workspace/iteration-3/`
- Create: `docs/superpowers/validation/project-existence-verifiability-gates-validation.md`

**Interfaces:**
- Consumes: the pushed `main` SHA and eval IDs `4`–`8`.
- Produces: fresh artifact-producing runs, independent grading, a validation verdict, and a pushed report-only commit.

- [ ] **Step 1: Request a fresh read-only implementation review from pushed main**

The reviewer must rehydrate only from the pushed `main` SHA and committed spec, inspect the exact implementation diff, and report CRITICAL/IMPORTANT/MINOR findings for activation, override truth, learning bypass/expiry, verifiability completeness, handoff propagation, stage ownership, and regression risk. Any concrete finding is fixed with a new narrow commit and pushed before artifact-producing evaluation starts. A reused reviewer may close its own findings but is not labeled cold evidence.

- [ ] **Step 2: Run qualifying evaluations sequentially from pushed main**

For eval IDs `4`, `5`, `6`, `7`, and `8`, dispatch a fresh top-level evaluator with `fork_turns=none`. Each evaluator must:

- rehydrate only from the pushed main SHA, current skill, its prompt, and its isolated run root;
- use fresh sequential Discovery workers;
- write canonical `AGENT-STATE.md`, `SCOPE.md`, `DISCOVERY.md`, `EVENTS.jsonl`, packets/reports/evidence/gates/handoff as required;
- avoid external model/API execution unless the prompt supplies authority;
- verify event chain/anchor, immutable receipts, state/readiness consistency, and representative outcome rows;
- never read prior eval runs, grading, or warm reports.

State-changing eval runs remain sequential. Preserve every failed attempt and retry honestly.

- [ ] **Step 3: Run independent read-only graders in parallel**

After all five run roots are terminal, use one new grader identity per run. Each grader reads the exact corresponding expectations from `evals.json`, recomputes artifact facts, and writes `grading.json` with one boolean and evidence path per expectation plus total score. Baselines or reused reviewers are comparison-only and never labeled cold.

Expected minimum: every gate-specific expectation passes. A failure triggers only a narrow production repair commit pushed to `main`, then a fresh rerun of the affected eval and a new grader identity.

- [ ] **Step 4: Verify the non-qualifying activation boundary**

Mechanically inspect `viability-evals.json` case `7` and `activation-evals.json` existing routine-fix case. Run a fresh read-only classifier and require:

```text
should_activate_gates=false
first_stage=Ordinary scoped implementation
competing_owner=ordinary scoped workflow
```

This dynamic result is distinct from the existing static integration evidence.

- [ ] **Step 5: Write the final validation report**

The report contains:

- pushed and evaluated main SHA;
- exact commands and exit signals;
- per-eval state/readiness/score and representative artifact links;
- event counts/tips/full-file hashes and receipt checks;
- proof of no invented external/model evidence;
- override and learning-bypass propagation samples;
- activation negative case;
- limitations, warm-vs-cold evidence labels, rollback or repair commit(s), and final verdict.

- [ ] **Step 6: Run final verification against the evaluated skill SHA**

Repeat Task 3 tests plus `git diff --check`. Read `superpowers:verification-before-completion` before claiming success. Inspect representative real artifacts, not only exit codes or grader summaries. If the pushed feature over-triggers routine work, corrupts readiness routing, or cannot preserve truthful override/bypass evidence, revert the dedicated implementation commits in a new commit, preserve all failure artifacts, push the rollback, and report failure instead of weakening the gates.

- [ ] **Step 7: Commit and push the report-only change**

```powershell
git add -- docs/superpowers/validation/project-existence-verifiability-gates-validation.md
git diff --cached --check
git commit -m "docs(discovery): report viability gate validation"
git push origin HEAD:main
git ls-remote origin refs/heads/main
```

Expected: the final push changes only the validation report relative to the evaluated skill SHA; remote main equals local HEAD.

---

## Completion Boundary

This plan is complete only when the skill is present on remote `main`, all qualifying fresh evaluations and independent graders are terminal, the routine-work negative case passes, the validation report is pushed, and no unresolved CRITICAL or IMPORTANT finding remains. Afterward, resume the pre-existing autonomous-orchestration Tasks 5/7/8 work from its durable handoff without redoing completed Discovery or static integration.
