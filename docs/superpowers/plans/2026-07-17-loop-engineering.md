# Loop Engineering Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and test a `loop-engineering` skill that interviews users only for loop-worthy tasks and returns a bounded, evidence-driven GPT loop prompt.

**Architecture:** A single runtime `SKILL.md` owns task suitability, the phased interview, feasibility checks, and prompt synthesis. `evals/evals.json` defines four behavioral cases; evaluation outputs live in a sibling workspace so runtime guidance stays small. No rendering script or provider-specific command is needed.

**Tech Stack:** Agent Skills Markdown/YAML, JSON evaluation fixtures, Python validation and benchmark scripts from `skills/garen-skill-creator`.

## Global Constraints

- The generated prompt is platform-agnostic and must not emit Claude Code `/goal`, `/loop`, or `/schedule` commands.
- Simple tasks bypass the comprehensive questionnaire.
- Loop-worthy tasks use a complete phased interview but skip facts already provided.
- Objective evidence is preferred; subjective work requires an explicit rubric and pass threshold.
- Every generated loop has a hard iteration, time, or token cap.
- Exhausted, blocked, unsafe, or incapable loops exit as `INCOMPLETE`, never disguised as success.
- The skill produces a prompt but never executes the user's underlying task.
- Do not modify `README.md`, existing skills, lockfiles, generated files, or unrelated dirty worktree content.

---

## File Structure

- Create `skills/loop-engineering/SKILL.md` — runtime suitability gate, interview protocol, feasibility checks, and output contract.
- Create `skills/loop-engineering/evals/evals.json` — four representative behavior cases and their objective expectations.
- Create `skills/loop-engineering-workspace/iteration-1/` during evaluation — baseline, with-skill, cold-start, grading, benchmark, and review artifacts; do not include this directory in the skill package.
- Create a packaged artifact outside the runtime directory during final verification; `package_skill.py` excludes `evals/` by design.

### Task 1: RED evaluation contract

**Files:**
- Create: `skills/loop-engineering/evals/evals.json`
- Create during runs: `skills/loop-engineering-workspace/iteration-1/<eval-name>/eval_metadata.json`
- Create during runs: `skills/loop-engineering-workspace/iteration-1/<eval-name>/without_skill/outputs/response.md`
- Create during runs: `skills/loop-engineering-workspace/iteration-1/<eval-name>/without_skill/timing.json`

**Interfaces:**
- Consumes: Approved design at `docs/superpowers/specs/2026-07-17-loop-engineering-design.md`.
- Produces: Stable prompts used by paired baseline, with-skill, grading, and cold-start runs.

- [ ] **Step 1: Create evaluation prompts without expectations**

Create `skills/loop-engineering/evals/evals.json` with this initial content:

```json
{
  "skill_name": "loop-engineering",
  "evals": [
    {
      "id": 1,
      "prompt": "I want a reusable GPT loop prompt for this task: fix one spelling mistake in README.md and verify the word is corrected.",
      "expected_output": "Recognize that the task is too small for a loop and avoid a comprehensive interview.",
      "files": []
    },
    {
      "id": 2,
      "prompt": "Help me construct a reusable GPT loop prompt that raises our homepage Lighthouse performance score to at least 90. I have not provided the repository, current score, available tools, protected behavior, or attempt budget.",
      "expected_output": "Ask a phased set of missing questions instead of prematurely generating the final loop prompt.",
      "files": []
    },
    {
      "id": 3,
      "prompt": "Create a GPT loop prompt for iteratively improving a landing-page hero until it feels premium. The executing GPT can edit the project and take screenshots. Use at most four iterations.",
      "expected_output": "Elicit a concrete quality rubric, evaluator, and pass threshold before generating the prompt.",
      "files": []
    },
    {
      "id": 4,
      "prompt": "Write a pure GPT prompt that checks competitor pricing every hour forever. The target chat has no scheduler, browser, API, or persistent process.",
      "expected_output": "Explain that a prompt alone cannot supply persistence or unavailable tools and do not fabricate a working loop.",
      "files": []
    }
  ]
}
```

- [ ] **Step 2: Validate the evaluation JSON**

Run:

```powershell
Get-Content -Raw skills\loop-engineering\evals\evals.json | ConvertFrom-Json | Out-Null
```

Expected: exit code `0` and no output.

- [ ] **Step 3: Fix the evaluation directory names**

Use these descriptive directories for all later paired runs:

```text
simple-task-gate
verifiable-coding-loop
subjective-quality-loop
impossible-environment
```

The RED hypotheses are that an unguided response may over-engineer the simple task, emit a final prompt before collecting critical information, accept vague quality, omit a hard failure exit, or pretend prompt text can provide unavailable persistence. Do not claim these failures until the baseline responses are captured.

- [ ] **Step 4: Prepare the objective expectations for insertion during the paired runs**

Use these exact checks when Step 2 of Task 3 adds an `expectations` array to every eval:

```text
Eval 1
- The response explicitly says the task does not justify a loop or recommends a normal one-pass prompt.
- The response does not ask the full six-category loop questionnaire.

Eval 2
- The response asks for missing environment, verification, safety, and hard-cap information before producing a final prompt.
- Questions are grouped by phase and do not repeat facts already supplied.

Eval 3
- The response identifies "premium" as non-verifiable without a rubric.
- The response asks for or proposes an evaluator, scoring criteria, and pass threshold.
- The response preserves the supplied four-iteration hard cap.

Eval 4
- The response states that prompt text alone cannot run hourly forever.
- The response identifies the missing scheduler and observation capability.
- The response does not present the requested pure prompt as an actually working persistent loop.
```

- [ ] **Step 5: Commit the prompt-only evaluation contract**

```powershell
git add skills\loop-engineering\evals\evals.json
git commit -m "test(loop-engineering): define behavioral evals"
```

Expected: the commit contains only the prompt-only `evals/evals.json`; workspace evidence does not exist yet.

### Task 2: GREEN minimal runtime skill

**Files:**
- Create: `skills/loop-engineering/SKILL.md`

**Interfaces:**
- Consumes: Approved design, eval prompts, and explicit RED hypotheses from Task 1.
- Produces: A self-contained runtime protocol used by with-skill and cold-start agents.

- [ ] **Step 1: Write the minimal skill that addresses the approved requirements and RED hypotheses**

Create `skills/loop-engineering/SKILL.md`. Its frontmatter and opening must be:

```markdown
---
name: loop-engineering
description: Use when a user wants to design an iterative GPT prompt, asks an agent to keep working until a measurable result is reached, or describes complex work that needs repeated action, verification, diagnosis, and revision. Determines whether a loop is justified, interviews for missing success evidence and boundaries, and produces a bounded platform-agnostic loop prompt. Also use when a request risks premature completion, repeated failed attempts, vague quality targets, or invented persistence.
---

# Loop Engineering

## Overview

Design a loop only when evidence from one attempt must determine the next. A useful loop is bounded control flow around work and verification; repeated wording without state, evidence, and termination is not a loop.

This skill authors the prompt. It does not execute the task or create scheduling, persistence, tools, or permissions that the target GPT environment does not have.

## Workflow

1. Extract facts already supplied by the user.
2. Apply the suitability gate.
3. For a loop-worthy task, complete the phased interview.
4. Run the feasibility check.
5. Return exactly one copyable prompt and no executed task result.
```

The remainder must implement these approved sections without placeholders:

```text
Suitability gate
  Strong signals: repeated measurement/revision, explicit threshold,
  changing observable state, queue exhaustion, evidence-dependent attempts.
  Supporting signals: dependent stages, uncertain path, multiple criteria,
  recovery, premature-completion risk.
  Bypass factual questions, deterministic rewrites, one-step transforms,
  and isolated changes with one obvious verification.

Phased interview
  Outcome and scope
  Inputs and environment
  Verification
  Iteration strategy
  Safety and recovery
  Budget and termination

Feasibility check
  Every mandatory criterion maps to evidence.
  Tools, inputs, and permissions exist.
  No contradictory constraints.
  At least one hard cap and one failure exit exist.
  Scheduling and unavailable capabilities are never invented.

Generated prompt
  Role and mission
  Context and capabilities
  Acceptance criteria mapped to evidence
  Loop state
  Preflight
  Inspect -> Plan -> Act -> Verify -> Diagnose -> Adapt
  Strategy-change rule
  SUCCESS exit
  INCOMPLETE exit
  Final evidence report
```

Include one complete example for a measurable coding task. Keep the file under 500 lines and do not add supporting runtime files unless testing proves they are needed.

- [ ] **Step 2: Validate metadata immediately**

Run:

```powershell
python skills\garen-skill-creator\scripts\quick_validate.py skills\loop-engineering
npx skills-ref validate .\skills\loop-engineering
```

Expected output includes `Skill is valid!` and the Agent Skills validator reports success. If `npx` needs a download or network is unavailable, record that limitation and keep the local Python result; do not modify a lockfile.

- [ ] **Step 3: Inspect runtime guidance for required invariants**

Run:

```powershell
rg -n "Suitability|Outcome|Environment|Verification|Safety|Budget|SUCCESS|INCOMPLETE|hard cap|fabricat|scheduler|persistent" skills\loop-engineering\SKILL.md
(Get-Content skills\loop-engineering\SKILL.md).Count
```

Expected: every invariant has a matching line and line count is below `500`.

- [ ] **Step 4: Commit the GREEN skill**

```powershell
git add skills\loop-engineering\SKILL.md
git commit -m "feat(loop-engineering): add bounded prompt workflow"
```

Expected: the commit contains only `SKILL.md`.

### Task 3: Paired RED/GREEN runs and cold-start validation

**Files:**
- Create during runs: `skills/loop-engineering-workspace/iteration-1/<eval-name>/with_skill/outputs/response.md`
- Create during runs: `skills/loop-engineering-workspace/iteration-1/<eval-name>/with_skill/timing.json`
- Create: `skills/loop-engineering-workspace/iteration-1/cold-start-report.md`
- Modify when gaps exist: `skills/loop-engineering/SKILL.md`

**Interfaces:**
- Consumes: `skills/loop-engineering/SKILL.md` and all four eval prompts.
- Produces: Representative outputs, timing, and a written gap list for grading and refactoring.

- [ ] **Step 1: Start the first matched baseline and with-skill pair**

For the first eval, spawn two fresh agents in the same root turn. The baseline agent receives the exact eval prompt and no skill. The with-skill agent receives the exact eval prompt plus this instruction:

```text
Use only the skill at S:\git\15-skills\garen-agent-skills\skills\loop-engineering\SKILL.md to handle the user prompt. Treat this as a fresh conversation. Save the verbatim user-facing response to the assigned with_skill/outputs/response.md path. Do not execute the underlying task.
```

Capture available token and duration data immediately in each `timing.json`. If the platform does not expose either metric, write `null` plus a `measurement_note` rather than inventing a value.

- [ ] **Step 2: Add objective expectations while the first pair runs**

Add the exact expectations prepared in Task 1 to `evals/evals.json`, and mirror them into each eval's `eval_metadata.json`. This preserves the `garen-skill-creator` requirement to draft assertions while executions are in progress rather than tailoring them after seeing outputs.

- [ ] **Step 3: Run the remaining matched pairs**

For each remaining eval, spawn its baseline and with-skill agents in the same root turn. Wait for a pair to finish before starting the next pair because the platform exposes four total concurrency slots including the root agent. Record `paired waves used because the platform permits three child agents` in benchmark notes; do not compare runs from unmatched prompts.

- [ ] **Step 4: Capture baseline failures verbatim**

Create `skills/loop-engineering-workspace/iteration-1/baseline-gaps.md` with columns for eval name, failed expectation, exact response excerpt, and the skill instruction that counters it. Do not treat a RED hypothesis as a confirmed gap without response evidence.

- [ ] **Step 5: Run an adversarial cold-start test**

Dispatch a fresh agent with this exact preamble:

```text
You have no prior memory. You can only use what is in the skill file.
Apply the full workflow independently to all four evaluation prompts. For each,
report which steps were clear and actionable, which were vague or missing, and
which decisions required guessing rather than following the skill. Quote the
instruction that supported each decision. Save the report to
skills/loop-engineering-workspace/iteration-1/cold-start-report.md.
```

- [ ] **Step 6: Write the concrete gap list**

In `cold-start-report.md`, add a final table with columns:

```text
Gap | Evidence | Runtime consequence | Required SKILL.md change | Status
```

Every vague, missing, or guessed behavior must appear in the table. Use `none found` only if the report contains direct evidence for every approved requirement.

- [ ] **Step 7: REFACTOR each actionable gap**

Edit `SKILL.md` narrowly. Typical acceptable fixes are a clearer gate threshold, an explicit batching rule, a feasibility failure branch, or a stricter output template. Do not add provider-specific syntax, scripts, or extra abstractions.

- [ ] **Step 8: Rerun affected evals and inspect the actual response**

Run the affected prompt with the revised skill and overwrite only that eval's `with_skill/outputs/response.md`. Read the final file directly and confirm the cited gap is absent; an agent's self-assessment alone is insufficient.

- [ ] **Step 9: Commit expectations and the tested refactor**

```powershell
git add skills\loop-engineering\evals\evals.json skills\loop-engineering\SKILL.md
git commit -m "test(loop-engineering): verify cold-start behavior"
```

Expected: the commit always records the finalized expectations; it includes `SKILL.md` only when cold-start evidence required a runtime change.

### Task 4: Grade, compare, and generate the review viewer

**Files:**
- Create: `skills/loop-engineering-workspace/iteration-1/<eval-name>/<configuration>/grading.json`
- Create: `skills/loop-engineering-workspace/iteration-1/benchmark.json`
- Create: `skills/loop-engineering-workspace/iteration-1/benchmark.md`
- Create: `skills/loop-engineering-workspace/iteration-1/analysis.md`
- Create: `skills/loop-engineering-workspace/iteration-1/review.html`

**Interfaces:**
- Consumes: Baseline and with-skill responses plus the expectations in `evals.json`.
- Produces: Evidence-backed pass rates and a static human-review artifact.

- [ ] **Step 1: Grade every response against exact expectations**

Each `grading.json` must use:

```json
{
  "expectations": [
    {
      "text": "Exact expectation from evals.json",
      "passed": true,
      "evidence": "Direct quote or precise location in response.md"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "total": 1,
    "pass_rate": 1.0
  }
}
```

Read `skills/garen-skill-creator/agents/grader.md` before grading. Mark an expectation failed when evidence is absent or ambiguous.

- [ ] **Step 2: Aggregate the benchmark**

Run from the creator directory so Python imports resolve:

```powershell
Push-Location skills\garen-skill-creator
python -m scripts.aggregate_benchmark ..\loop-engineering-workspace\iteration-1 --skill-name loop-engineering
Pop-Location
```

Expected: `benchmark.json` and `benchmark.md` exist and contain both `with_skill` and `without_skill` configurations.

- [ ] **Step 3: Perform the analyst pass**

Read `skills/garen-skill-creator/agents/analyzer.md`, the complete benchmark, and representative response files. Save `analysis.md` covering non-discriminating expectations, high-variance cases, behavior hidden by averages, and time/token trade-offs. Do not infer timing comparisons from missing metrics.

- [ ] **Step 4: Generate the static viewer**

Run:

```powershell
python skills\garen-skill-creator\eval-viewer\generate_review.py skills\loop-engineering-workspace\iteration-1 --skill-name loop-engineering --benchmark skills\loop-engineering-workspace\iteration-1\benchmark.json --static skills\loop-engineering-workspace\iteration-1\review.html
```

Expected: `review.html` exists and contains the four eval names plus benchmark data. Inspect the generated file before sharing it.

### Task 5: Final validation and packaging

**Files:**
- Verify: `skills/loop-engineering/SKILL.md`
- Verify: `skills/loop-engineering/evals/evals.json`
- Create outside runtime directory: `skills/loop-engineering-workspace/artifacts/loop-engineering.skill`

**Interfaces:**
- Consumes: Final skill and test evidence.
- Produces: A validated repo skill and distributable package.

- [ ] **Step 1: Run all structural checks**

```powershell
python skills\garen-skill-creator\scripts\quick_validate.py skills\loop-engineering
npx skills-ref validate .\skills\loop-engineering
git diff --check -- skills\loop-engineering
```

Expected: both validators succeed and `git diff --check` has no output. Record an explicit exception if the network-dependent validator cannot run.

- [ ] **Step 2: Inspect representative real outputs**

Read at minimum:

```text
simple-task-gate/with_skill/outputs/response.md
verifiable-coding-loop/with_skill/outputs/response.md
impossible-environment/with_skill/outputs/response.md
```

Confirm the first bypasses the questionnaire, the second asks only missing phased questions, and the third refuses fake persistence. Also verify that any final prompt produced by a fully specified rerun is one Markdown block containing loop state, hard cap, `SUCCESS`, `INCOMPLETE`, and evidence rules.

- [ ] **Step 3: Package the skill**

```powershell
python skills\garen-skill-creator\scripts\package_skill.py skills\loop-engineering skills\loop-engineering-workspace\artifacts
```

Expected: package validation succeeds, `loop-engineering.skill` exists, and console output shows `evals` was skipped.

- [ ] **Step 4: Review final Git scope**

```powershell
git status --short
git log -4 --oneline
```

Expected: implementation commits contain only `skills/loop-engineering/SKILL.md` and `skills/loop-engineering/evals/evals.json`; unrelated pre-existing changes remain untouched. Workspace outputs and package artifacts remain uncommitted review evidence.

- [ ] **Step 5: Report evidence and request human review**

Provide links to `SKILL.md`, `evals.json`, `review.html`, and the packaged `.skill` artifact. Report actual validator results and benchmark pass rates. Do not claim final satisfaction until the user has inspected the viewer or explicitly accepts the inline evidence.
