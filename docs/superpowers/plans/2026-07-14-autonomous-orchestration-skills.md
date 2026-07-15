# Autonomous Orchestration Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a Claude Code/Codex-compatible pipeline of `autonomous-project-discovery`, `autonomous-planning`, and `autonomous-implementation` skills with durable context-rot protection and evidence-based stage routing.

**Architecture:** Each skill is an independently installable package with a narrow activation description and a stage-specific state machine. The packages communicate through `DISCOVERY.md`, `MASTER-PLAN.md`, `IMPLEMENTATION-NOTES.md`, and one shared `AGENT-STATE.md` contract; each vendors the byte-identical `autonomous-artifacts-v2` protocol so no runtime dependency exists. Validation follows RED/GREEN/REFACTOR one skill at a time, then tests the three-stage pipeline together.

**Tech Stack:** Agent Skills Markdown/YAML, JSON eval definitions, Git, `pnpm dlx skills-ref`, Garen Skill Creator evaluation scripts, Codex collaboration agents.

## Global Constraints

- Apply [the approved design spec](../specs/2026-07-14-autonomous-orchestration-skills-design.md) verbatim when it conflicts with this task breakdown.
- Preserve all unrelated working-tree changes; stage and commit only paths owned by the current task.
- Use `pnpm`; do not modify lockfiles, `.env*`, CI secrets, tool-managed caches, or generated project memory.
- Use `apply_patch` for file edits.
- Create and validate one skill completely before drafting the next skill.
- Run baseline scenarios without the skill before writing each `SKILL.md`.
- Every cold-start worker prompt must state: “You have no prior memory. You can only use what is in the skill files.”
- Worker outputs go to the skill's sibling `*-workspace/` evaluation directory and return at most ten lines to the orchestrator.
- Evaluation workspaces remain uncommitted; committed deliverables are skill packages, eval definitions, design/plan documents, and concise validation evidence intentionally included in the skills.
- Never request or persist hidden chain-of-thought. Persist conclusions, assumptions, decisions, commands, relevant output excerpts, failures, and verification evidence.
- `references/artifact-protocol.md` must be byte-identical across all three skills and identify `autonomous-artifacts-v2`.
- Each `SKILL.md` stays below 500 lines and links every required reference directly, one level deep.
- Exact model selection is capability-based. Record requested/effective model and fallback reason; never claim an unavailable model ran.
- Do not report a skill complete until a fresh worker has cold-started it, gaps are written, fixes are applied, validators pass, and representative outputs are inspected.

---

## File map

### Discovery package

- `skills/autonomous-project-discovery/SKILL.md` — activation, ownership, state machine, readiness, routing, and completion criteria.
- `skills/autonomous-project-discovery/references/artifact-protocol.md` — shared durable-state and ten-line worker-return contract.
- `skills/autonomous-project-discovery/references/discovery-method.md` — four unknown classes, blind-spot method, framing challenge, prototype/interview rules, readiness rubric.
- `skills/autonomous-project-discovery/references/harness-adapters.md` — semantic action mapping and Claude Code/Codex fallbacks.
- `skills/autonomous-project-discovery/references/launcher-template.md` — one-prompt launcher.
- `skills/autonomous-project-discovery/references/state-templates.md` — `AGENT-STATE.md`, `DISCOVERY.md`, packet, report, and handoff templates.
- `skills/autonomous-project-discovery/references/work-sizing.md` — Small/Medium/Large rules and session cutover.
- `skills/autonomous-project-discovery/evals/evals.json` — three behavior evals and assertions.

### Planning package

- `skills/autonomous-planning/SKILL.md` — Discovery sufficiency gate, planning packet loop, review, readiness, backward routing.
- `skills/autonomous-planning/references/artifact-protocol.md` — byte-identical shared protocol.
- `skills/autonomous-planning/references/harness-adapters.md` — semantic action mapping and fallbacks.
- `skills/autonomous-planning/references/launcher-template.md` — one-prompt launcher.
- `skills/autonomous-planning/references/planning-method.md` — planning ownership, architecture/interfaces/data/migration/testing/deployment coverage.
- `skills/autonomous-planning/references/state-templates.md` — `AGENT-STATE.md`, `MASTER-PLAN.md`, packet, report, review, and handoff templates.
- `skills/autonomous-planning/references/work-sizing.md` — planning packet sizing and session cutover.
- `skills/autonomous-planning/evals/evals.json` — three behavior evals and assertions.

### Implementation package

- `skills/autonomous-implementation/SKILL.md` — readiness, sequential stage loop, verification, UI UAT, retry, integration review, upstream routing.
- `skills/autonomous-implementation/references/artifact-protocol.md` — byte-identical shared protocol.
- `skills/autonomous-implementation/references/harness-adapters.md` — semantic action mapping and fallbacks.
- `skills/autonomous-implementation/references/implementation-method.md` — Task Contract dispatch, automatic acceptance, remediation, checkpoint, and integration rules.
- `skills/autonomous-implementation/references/launcher-template.md` — one-prompt launcher.
- `skills/autonomous-implementation/references/state-templates.md` — `AGENT-STATE.md`, stage, report, UAT, integration, notes, and handoff templates.
- `skills/autonomous-implementation/references/work-sizing.md` — implementation stage sizing and session cutover.
- `skills/autonomous-implementation/evals/evals.json` — three behavior evals and assertions.

---

### Task 1: RED baseline for Autonomous Project Discovery

**Files:**
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/baseline-greenfield/without_skill/outputs/response.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/baseline-major-subsystem/without_skill/outputs/response.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/baseline-unknown-known/without_skill/outputs/response.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/baseline-gaps.md`

**Interfaces:**
- Consumes: approved design spec, attachment requirements, current repository as read-only evidence.
- Produces: exact baseline failures/rationalizations that the Discovery skill must correct.

- [ ] **Step 1: Dispatch three fresh no-skill baseline workers**

Use the three Discovery scenarios from the design spec. Instruct each worker to write its full reusable response to its assigned `without_skill/outputs/response.md`, modify no production path, and return only verdict/path/summary.

- [ ] **Step 2: Inspect all three baseline artifacts**

Read each `response.md`. Record whether it prematurely plans/builds, emits generic checklists, asks broad questionnaires, misses artifact/readiness/session controls, or claims full autonomy without user gates.

- [ ] **Step 3: Write the RED gap report**

Write `baseline-gaps.md` with a table containing `scenario`, `observed behavior`, `exact rationalization or omission`, `required skill behavior`, and `future assertion`. Completion signal: every drafted Discovery rule traces to at least one observed failure or an explicit user requirement.

### Task 2: GREEN draft of Autonomous Project Discovery

**Files:**
- Create all files under `skills/autonomous-project-discovery/` listed in the file map.

**Interfaces:**
- Consumes: Task 1 gap report and approved design.
- Produces: a standalone Discovery skill whose output is a current `DISCOVERY.md` plus planning-readiness state.

- [ ] **Step 1: Write `evals/evals.json` from the RED scenarios**

Use schema fields `skill_name`, `id`, `prompt`, `expected_output`, `files`, and `expectations`. Expectations must objectively cover depth selection, evidence inspection, facts/assumptions separation, four unknown classes, decision ownership, planning readiness, context-rot artifacts, model fallback, and no production implementation.

- [ ] **Step 2: Write the shared protocol and supporting references**

The protocol must define single-writer `AGENT-STATE.md`, artifact-before-state ordering, upstream artifact lineage/freshness, ten-line returns, report content, secret/log redaction, compaction recovery, and continuation commands. `discovery-method.md` must make every research packet unlock a named decision and define `skip`, `targeted`, and `full` depth.

- [ ] **Step 3: Write `SKILL.md`**

Frontmatter name is `autonomous-project-discovery`. Description begins with `Use when` and triggers on insufficiently framed greenfield or substantial new-project work without summarizing the workflow. The body must require all references before dispatch, define bounded autonomy, stage ownership, readiness, backward/forward routing, and explicit completion criteria.

- [ ] **Step 4: Run structural validators**

Run:

```powershell
pnpm dlx skills-ref validate ./skills/autonomous-project-discovery
python C:/Users/garet/.agents/skills/garen-skill-creator/scripts/quick_validate.py ./skills/autonomous-project-discovery
```

Expected: both exit 0. If the validators disagree on supported frontmatter, use only specification-supported fields and record the discrepancy.

### Task 3: VERIFY/REFACTOR Autonomous Project Discovery

**Files:**
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/*/with_skill/outputs/response.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/*/grading.json`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/benchmark.json`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/benchmark.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/gaps.md`
- Create: `skills/autonomous-project-discovery-workspace/iteration-1/review.html`
- Modify: Discovery skill files only when a written gap requires a fix.

**Interfaces:**
- Consumes: Discovery draft and the same prompts used in Task 1.
- Produces: cold-start evidence, formal grades, fixed gaps, static reviewer, and a validated Discovery package.

- [ ] **Step 1: Dispatch fresh with-skill workers**

Each prompt must include the skill path, no-prior-memory statement, assigned output path, and required report on clear/vague/guessed instructions. Do not let a worker modify the skill itself.

- [ ] **Step 2: Grade and aggregate**

Write schema-correct `grading.json` files with `text`, `passed`, and `evidence`. Run:

```powershell
python -m scripts.aggregate_benchmark S:/git/15-skills/garen-agent-skills/skills/autonomous-project-discovery-workspace/iteration-1 --skill-name autonomous-project-discovery
```

Run from `C:/Users/garet/.agents/skills/garen-skill-creator`. Expected: `benchmark.json` and `benchmark.md` are created.

- [ ] **Step 3: Generate the static reviewer before self-revision**

Run:

```powershell
python C:/Users/garet/.agents/skills/garen-skill-creator/eval-viewer/generate_review.py S:/git/15-skills/garen-agent-skills/skills/autonomous-project-discovery-workspace/iteration-1 --skill-name autonomous-project-discovery --benchmark S:/git/15-skills/garen-agent-skills/skills/autonomous-project-discovery-workspace/iteration-1/benchmark.json --static S:/git/15-skills/garen-agent-skills/skills/autonomous-project-discovery-workspace/iteration-1/review.html
```

Expected: a standalone `review.html` rendering every baseline and with-skill output.

- [ ] **Step 4: Capture and fix gaps**

Write `gaps.md` before editing. Fix only observed failures, rerun affected cold-start cases, and inspect representative `DISCOVERY.md`/state output. Completion signal: all critical assertions pass and no new rationalization remains.

- [ ] **Step 5: Commit the Discovery package**

Stage only `skills/autonomous-project-discovery/`. Commit message:

```text
feat(skills): add autonomous project discovery
```

### Task 4: RED/GREEN Autonomous Planning

**Files:**
- Create baseline outputs and `baseline-gaps.md` under `skills/autonomous-planning-workspace/iteration-1/`.
- Create all files under `skills/autonomous-planning/` listed in the file map.

**Interfaces:**
- Consumes: validated Discovery package and representative current/stale/equivalent Discovery artifacts.
- Produces: standalone Planning skill whose output is a current execution-ready `MASTER-PLAN.md`.

- [ ] **Step 1: Run three no-skill Planning baselines**

Test a current discovery artifact, a stale contradictory artifact after compaction, and a non-standard equivalent artifact in a Codex-like capability set. Capture premature bypass, repeated discovery, missing freshness checks, oversized packets, or missing handoff state.

- [ ] **Step 2: Write baseline gaps, then `evals/evals.json`**

Every assertion must trace to an observed baseline gap or an explicit design requirement. Include Discovery sufficiency/freshness, backward routing, packet sizing, session budget, independent review, and implementation readiness.

- [ ] **Step 3: Draft Planning package**

Require `autonomous-artifacts-v2`, accept sufficient equivalent artifacts, forbid broad project re-discovery, produce exact Task Contracts, route framing defects to Discovery, and forbid product-code edits.

- [ ] **Step 4: Validate draft**

Run `pnpm dlx skills-ref validate ./skills/autonomous-planning` and the Garen quick validator. Expected: exit 0.

### Task 5: VERIFY/REFACTOR Autonomous Planning

**Files:**
- Create with-skill outputs, grades, benchmark, `gaps.md`, and static `review.html` under `skills/autonomous-planning-workspace/iteration-1/`.
- Modify Planning skill files only from written gaps.

**Interfaces:**
- Consumes: Task 4 draft and identical baseline prompts.
- Produces: validated Planning package and evidence that stale framing cannot be silently bypassed.

- [ ] **Step 1: Run three fresh cold-start Planning workers**

Require no prior memory, skill-only guidance, output artifacts, ten-line return, and a clear/vague/guessed instruction report.

- [ ] **Step 2: Grade, aggregate, and generate static reviewer**

Use the same schema and commands as Task 3 with skill name/path changed to `autonomous-planning`.

- [ ] **Step 3: Write gaps, fix, and rerun affected cases**

Inspect `MASTER-PLAN.md`, `AGENT-STATE.md`, stale-artifact contradiction report, session handoff, and absence of product changes.

- [ ] **Step 4: Commit the Planning package**

Commit message:

```text
feat(skills): add autonomous planning
```

### Task 6: RED/GREEN Autonomous Implementation

**Files:**
- Create baseline outputs and `baseline-gaps.md` under `skills/autonomous-implementation-workspace/iteration-1/`.
- Create all files under `skills/autonomous-implementation/` listed in the file map.

**Interfaces:**
- Consumes: validated Discovery/Planning packages and representative current/stale upstream artifacts.
- Produces: standalone Implementation skill that executes only current plans and records `IMPLEMENTATION-NOTES.md`.

- [ ] **Step 1: Run three no-skill Implementation baselines**

Test a small non-UI stage, a multi-session UI/non-UI plan requiring UAT, and a dirty worktree with failed verification plus unavailable model selection. Capture self-report trust, scope leakage, missing real-flow checks, blind retries, missing UAT, and incorrect upstream ownership.

- [ ] **Step 2: Write baseline gaps, then `evals/evals.json`**

Cover upstream consistency, `READY`/`NEEDS_PLANNING`/`NEEDS_DISCOVERY`, stage sizing, unrelated-change preservation, automatic evidence sampling, retry limits, UI UAT, integration review, deviations, and handoff.

- [ ] **Step 3: Draft Implementation package**

Require verbatim Task Contracts, one worker per state-changing stage, evidence-first acceptance, at most two diagnosis-driven remediation cycles, stage-local rollback, path-limited checkpoints, UI UAT, independent integration review, and upstream routing by ownership.

- [ ] **Step 4: Validate draft**

Run `pnpm dlx skills-ref validate ./skills/autonomous-implementation` and the Garen quick validator. Expected: exit 0.

### Task 7: VERIFY/REFACTOR Autonomous Implementation

**Files:**
- Create with-skill outputs, grades, benchmark, `gaps.md`, and static `review.html` under `skills/autonomous-implementation-workspace/iteration-1/`.
- Modify Implementation skill files only from written gaps.

**Interfaces:**
- Consumes: Task 6 draft and identical baseline prompts.
- Produces: validated Implementation package and evidence of gates, retries, UAT, and upstream routing.

- [ ] **Step 1: Run three fresh cold-start Implementation workers**

Require no prior memory, skill-only guidance, isolated fixture/output paths, ten-line return, and a clear/vague/guessed instruction report.

- [ ] **Step 2: Grade, aggregate, and generate static reviewer**

Use the Task 3 process with skill name/path changed to `autonomous-implementation`.

- [ ] **Step 3: Write gaps, fix, and rerun affected cases**

Inspect real stage reports, verification evidence, UAT state, dirty-path inventory, integration findings, `IMPLEMENTATION-NOTES.md`, and continuation command.

- [ ] **Step 4: Commit the Implementation package**

Commit message:

```text
feat(skills): add autonomous implementation
```

### Task 8: Three-stage integration and activation validation

**Files:**
- Modify: any of the three packages only when integration evidence identifies a concrete defect.
- Create: `docs/superpowers/validation/autonomous-orchestration-validation.md`

**Interfaces:**
- Consumes: all three validated packages.
- Produces: cross-package verification evidence and final responsibility/routing assessment.

- [ ] **Step 1: Compare shared protocol copies**

Run:

```powershell
Get-FileHash skills/autonomous-project-discovery/references/artifact-protocol.md
Get-FileHash skills/autonomous-planning/references/artifact-protocol.md
Get-FileHash skills/autonomous-implementation/references/artifact-protocol.md
```

Expected: identical hashes and `autonomous-artifacts-v2` present in every file.

- [ ] **Step 2: Run all package validators**

Run `pnpm dlx skills-ref validate` for each package and the Garen quick validator for each package. Expected: six successful validations.

- [ ] **Step 3: Execute the eight-case activation/routing matrix**

Use fresh agents to classify each prompt from the design spec. Verify first activation, required upstream artifact, follow-up stage, small-task skip, equivalent-artifact handling, resumption, and backward routing.

- [ ] **Step 4: Run an independent pipeline reviewer**

The reviewer reads all three `SKILL.md` files and required references, then reports unowned responsibilities, duplication, contradictory authority, competing activation descriptions, context-rot drift, unsafe autonomous decisions, and unsupported Claude/Codex assumptions.

- [ ] **Step 5: Fix critical findings and rerun affected validations**

Write findings to the validation report before editing. Do not fix style-only preferences. Completion signal: no critical responsibility/routing/context-rot issue remains.

- [ ] **Step 6: Write and inspect final validation report**

`autonomous-orchestration-validation.md` must include commands and exit signals, representative artifact samples, evaluation limitations, activation table results, responsibility matrix verdict, known assumptions, and rollback commit IDs.

- [ ] **Step 7: Commit integration fixes and validation evidence**

Commit message:

```text
test(skills): validate autonomous orchestration pipeline
```

## Self-review result

- Spec coverage: every Discovery, Planning, Implementation, context-rot, cross-harness, activation, routing, sizing, UAT, and validation requirement maps to a task above.
- Placeholder scan: the plan contains no unresolved implementation placeholder; angle-bracket-style runtime values appear only in the approved artifact naming convention, not as missing design decisions.
- Interface consistency: Discovery produces `DISCOVERY.md`; Planning consumes it and produces `MASTER-PLAN.md`; Implementation consumes both and produces `IMPLEMENTATION-NOTES.md`; all three share `AGENT-STATE.md` under `autonomous-artifacts-v2`.
