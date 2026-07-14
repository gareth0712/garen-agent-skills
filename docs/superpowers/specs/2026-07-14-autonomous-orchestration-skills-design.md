# Autonomous Orchestration Skills Design

## Goal

Create two independently installable Agent Skills:

- `autonomous-planning` turns a bounded goal into a complete, verified, resumable plan by dispatching one fresh planning worker per packet.
- `autonomous-implementation` audits readiness, repairs missing execution planning when necessary, implements one stage at a time, verifies each stage, pauses for UI UAT, and finishes with an independent integration review.

Both skills must work in Claude Code and Codex without depending on harness-specific tool names, exact model availability, or conversation history as durable state.

## Non-goals

- Claiming that a skill can create a new top-level session when the host does not expose that capability.
- Allowing unbounded autonomy, irreversible external actions, deployment, publishing, secret changes, or product decisions without explicit authority.
- Persisting private reasoning, chain-of-thought, full transcripts, secrets, or indiscriminate raw logs.
- Replacing project instructions, tests, code review, or human visual acceptance with agent self-reports.
- Adding a third shared runtime skill. Each requested skill remains usable when installed alone.

## Core decisions

### 1. Semantic orchestration contract

The main workflows use semantic actions rather than hard-coded tools:

1. `discover_capabilities`
2. `spawn_worker`
3. `wait_for_worker`
4. `inspect_artifact`
5. `verify_evidence`
6. `checkpoint_state`
7. `request_human_gate`
8. `finish_or_handoff`

Each skill includes `references/harness-adapters.md`, which maps these actions to the host's available mechanisms. The workflow never pretends an unavailable capability succeeded.

| Capability | Claude Code | Codex | Required fallback |
|---|---|---|---|
| Fresh worker | Agent/subagent mechanism | Collaboration/subagent mechanism | Hard blocker if no isolated worker mechanism exists |
| Sequential wait | Foreground agent result or task wait | Agent wait/status mechanism | Poll only through the host-supported wait mechanism |
| Model selection | Alias or full model ID when supported | Use selector only when exposed | Use the default worker and record requested/effective model |
| Project instructions | Explicitly read `CLAUDE.md` and `AGENTS.md` when present | Explicitly read `AGENTS.md` and `CLAUDE.md` when present | Read every applicable instruction file found in the project hierarchy |
| Context telemetry | Use host-reported usage when exposed | Use host-reported usage when exposed | Enforce artifact and work-unit budgets without estimating hidden context |
| UI observation | Browser, screenshot, or computer-use capability | Browser, screenshot, or computer-use capability | Mark UI verification blocked rather than substituting code inspection |
| New top-level session | Use only if explicitly exposed | Use only if explicitly exposed | Write a continuation command and end cleanly |

The orchestrator must run in the top-level session. If the host forbids nested delegation, invoking either workflow inside a worker is a hard blocker and the worker returns control to its parent.

### 2. Narrow, explicit invocation

These are expensive, state-changing workflows. Their descriptions trigger only when the user explicitly requests autonomous, staged, sequential, long-horizon, or resumable planning/implementation. Ordinary planning and small code edits must not trigger them.

Each skill includes a copyable launcher template. The launcher captures:

- goal and bounded scope;
- stop boundary;
- out-of-scope work;
- allowed external effects;
- commit/checkpoint policy;
- human UAT policy;
- preferred orchestrator and worker models;
- planning artifact or roadmap paths;
- maximum retry policy.

Missing fields receive safe defaults. Only a missing decision that materially changes the product, authorizes irreversible work, or prevents verification may stop the workflow.

### 3. Self-contained, versioned context-rot protocol

Both skills include their own `references/artifact-protocol.md` with protocol identifier `autonomous-artifacts-v1`. This is deliberate vendoring: either skill must remain complete when installed alone. Release validation checks that both copies expose the same required control-plane fields and invariants, while allowing planning- and implementation-specific report fields.

The protocol uses the project's established planning location. If none exists, use:

```text
docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/
├── AGENT-STATE.md
├── SCOPE.md
├── SPEC.md or MASTER-PLAN.md
├── packets/
│   └── P-001.md or S-001.md
├── reports/
│   └── P-001-report.md or S-001-report.md
├── evidence/
└── SESSION-HANDOFF.md
```

`AGENT-STATE.md` is the only control-plane index. It records:

- protocol version and workflow type;
- run ID and repository root;
- harness and discovered capabilities;
- requested and effective models;
- baseline Git SHA and pre-existing dirty paths, when Git exists;
- scope and stop-boundary paths;
- packet/stage table with `pending`, `in_progress`, `verified`, `blocked`, or `superseded` status;
- current session budget and completed weight;
- retry counters;
- UAT state;
- next action and exact continuation command.

Only the orchestrator updates `AGENT-STATE.md`. A worker writes its packet report and evidence first, returns at most ten lines, then the orchestrator independently samples the artifact and updates state. This ordering prevents a false `verified` status when the report is missing or incomplete.

A worker report preserves the complete reusable work product: conclusions, decisions, assumptions, source paths, commands, relevant output excerpts, changed files, failures, verification evidence, and recommended next action. It excludes hidden reasoning, full chat transcripts, secrets, and unbounded logs. Large raw output remains outside Git when possible; the report stores a redacted excerpt and reproducible command.

After compaction or resumption, conversation summaries are untrusted. Rebuild state from `AGENT-STATE.md`, packet/report artifacts, `SCOPE.md`, and Git history or filesystem evidence before dispatching another worker.

### 4. Work sizing and multi-session cutover

Every planning packet and implementation stage must have one primary outcome, explicit inputs, an observable completion criterion, verification, fallback, and no unresolved dependency on a later unit.

Assign a weight before dispatch:

| Size | Weight | Boundary |
|---|---:|---|
| Small | 1 | One behavior or decision, one subsystem, direct verification |
| Medium | 2 | One outcome across at most two coupled subsystems, integration verification |
| Large | Invalid | Multiple primary outcomes, three or more coupled subsystems, unknown interface, or unbounded verification; split first |

The default session budget is six weight units. Reduce it to four when the session includes high-risk data changes, security-sensitive behavior, external integrations, or UI stages. Before dispatch, if the next unit would exceed the remaining budget, write `SESSION-HANDOFF.md`, update the continuation command, and end the session.

Also cut over after the current unit when:

- the host reports at least 50% context usage;
- compaction occurred;
- two remediation cycles were needed in the session;
- the orchestrator can no longer decide the next action from `AGENT-STATE.md` plus the current report alone.

The six-unit ceiling is a safety maximum, not a target. The orchestrator may stop earlier but may not compress work or lower verification to fit more units.

### 5. Bounded autonomy and gates

Autonomy applies only inside the recorded scope and granted permissions.

Continue without asking for reversible implementation choices that project evidence can resolve. Stop only for:

- a material product decision with no safe reversible default;
- credentials, permissions, or external state the host cannot access;
- irreversible or public action not explicitly authorized;
- destructive migration or data-loss risk without an approved recovery plan;
- UI UAT after automatic UI verification;
- unavailable verification required by the task contract;
- two evidence-driven remediation cycles that leave the same unit unverified.

UI UAT and manual session restart mean the workflow is resumable and bounded-autonomous, not literally unattended across every environment.

### 6. Model policy

Model names are preferences, not assumed capabilities.

- Planning launcher default: request Fable-class/highest-reasoning orchestrator and planning workers.
- Implementation launcher default: request a highest-reasoning orchestrator and Sonnet-class high-effort implementation workers.
- Use exact model IDs only after the host confirms support.
- Record `requested_model`, `effective_model`, and fallback reason per worker.
- Lack of model selection is not a blocker unless the user marked the exact model as required.

This keeps the skills usable in Claude Code, where per-agent model selection may exist, and Codex, where the active collaboration API may not expose a model selector.

## Autonomous planning state machine

1. **Bootstrap** — discover capabilities, instructions, repository state, existing plans, scope, and prior run artifacts.
2. **Rehydrate** — reconcile `AGENT-STATE.md`, reports, checkboxes, and Git/filesystem evidence; repair stale status before continuing.
3. **Readiness review** — dispatch one read-only worker to perform current-state reconstruction and a blind-spot pass.
4. **Decompose** — produce ordered planning packets with dependency edges, weights, and Task Contracts. Split every Large packet.
5. **Plan sequentially** — dispatch exactly one planning worker for the current packet. The worker writes its report before returning.
6. **Accept packet** — inspect the report, verify cited project evidence, update the master plan and state, then checkpoint according to policy.
7. **Review plan** — dispatch an independent final reviewer for completeness, internal consistency, feasibility, verification coverage, and scope leakage.
8. **Repair** — convert each critical review finding into a bounded repair packet and run it through the same gate.
9. **Finish or hand off** — produce an execution-ready plan, evidence index, assumptions, unresolved human gates, and exact continuation command.

The planning skill may write planning artifacts but must not implement product code.

## Autonomous implementation state machine

1. **Bootstrap and rehydrate** — perform the same evidence-first reconstruction and dirty-tree inventory.
2. **Implementation readiness** — dispatch one read-only worker to return `READY` or `NEEDS_PLANNING`, with evidence.
3. **Planning repair** — when necessary, create sequential planning-repair packets inside this skill so it remains standalone. Large missing planning is split and may consume an entire session.
4. **Freeze execution spec** — write the stage list and Task Contracts, then checkpoint it separately when commits are authorized.
5. **Implement stage** — dispatch one implementation worker with the verbatim contract, required instruction paths, report path, and ten-line return contract.
6. **Automatic acceptance** — independently inspect changed artifacts, rerun representative verification, and sample a real affected flow. Worker `done` is not evidence.
7. **Remediate** — diagnose before retrying. Allow at most two evidence-driven remediation cycles. Roll back only when the workspace is unsafe or the approach is invalid; otherwise preserve useful work and repair it.
8. **UI UAT** — after automatic UI acceptance, present screenshots or a live URL and wait for human approval before the next stage.
9. **Checkpoint** — create a path-limited stage commit only when authorized; otherwise record a reversible filesystem/Git checkpoint without touching unrelated dirty paths.
10. **Integration acceptance** — dispatch an independent reviewer to verify cross-stage contracts, tests/build, affected flows, and scope. Critical findings become repair stages.
11. **Finish or hand off** — report verified stages, evidence paths, changed files, assumptions, residual gates, rollback points, and continuation command.

## Verification principles

- Agent reports are claims until checked against files, Git, commands, screenshots, or observed behavior.
- Every unit has a concrete verification recipe and expected signal before dispatch.
- Exit code alone is insufficient; inspect representative output artifacts.
- Follow the repository's test policy. New behavior receives appropriate tests unless the project explicitly documents an exception.
- Built-in read-only agents that omit project memory must receive explicit instruction-file paths in their Task Contract.
- Verification commands and evidence paths use portable forward-slash paths in artifacts; shell invocation adapts quoting to the active OS.
- Checkpoints never stage or commit unrelated user changes.

## Skill package layout

Each skill remains below 500 lines in `SKILL.md` and points directly to one-level references:

```text
skills/autonomous-planning/
├── SKILL.md
├── references/
│   ├── artifact-protocol.md
│   ├── harness-adapters.md
│   ├── launcher-template.md
│   ├── state-templates.md
│   └── work-sizing.md
└── evals/evals.json

skills/autonomous-implementation/
├── SKILL.md
├── references/
│   ├── artifact-protocol.md
│   ├── harness-adapters.md
│   ├── launcher-template.md
│   ├── state-templates.md
│   └── work-sizing.md
└── evals/evals.json
```

No runtime script is planned because orchestration capability discovery and state updates depend on host tools and project policy. Deterministic structural checks belong in repository validation commands rather than inside either installed skill.

## Test-driven validation

Create and validate one skill at a time.

### `autonomous-planning`

Run three fresh-agent scenarios without the skill, capture exact failures, then rerun with the skill:

1. A large cross-subsystem request that tempts a single-session plan and shallow packets.
2. A resumed run after compaction with a stale checkbox and contradictory Git evidence.
3. A Codex-like harness without model selection or context telemetry.

Assertions cover artifact creation, state reconciliation, Large-unit splitting, session budget enforcement, ten-line returns, model fallback recording, and absence of product-code edits.

### `autonomous-implementation`

After planning passes its deployment gate, repeat the RED/GREEN cycle with:

1. A small non-UI change with tests and a real-flow check.
2. A mixed UI/non-UI scope that exceeds one session and requires UAT.
3. A dirty worktree with failed verification, retry pressure, and unavailable preferred model selection.

Assertions cover readiness judgment, planning repair, stage sizing, preservation of unrelated changes, independent evidence sampling, retry limits, UAT pause, integration review, and lossless handoff.

For both skills:

- use isolated fixtures or output-only workspaces;
- run a cold-start worker that has no prior memory and only the skill files;
- write gap reports before editing the skill;
- remove temporary fixtures after testing;
- validate frontmatter and directory naming with `npx skills-ref validate`;
- inspect every generated `SKILL.md`, reference, eval file, and representative agent output;
- record any model-coverage limitation rather than claiming unrun coverage.

## Rejected alternatives

### Shared third core skill

Rejected because installing either requested skill alone would leave a hidden runtime dependency, and user-invoked or disabled skills may not be preloadable by workers in every host.

### One combined planning/implementation skill

Rejected because the invocation branches, side-effect permissions, and completion criteria differ. Combining them increases loaded context and raises the risk that planning drifts into implementation.

### Claude-specific prompts

Rejected because exact Agent tool names, model aliases, built-in agent behavior, and skill preloading do not carry over to Codex. Harness adapters preserve the same semantics without pretending the APIs are identical.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Protocol copies drift | Same protocol ID, required-field assertions, and cross-skill release comparison |
| Agent rushes to fit a session | Large units are invalid; session budget is a ceiling; verification cannot be reduced |
| Artifact directory pollutes source history | Prefer established planning location; commit only concise control/report artifacts when authorized |
| Full logs expose secrets or bloat Git | Redacted excerpts plus reproducible commands; raw logs remain outside Git |
| Orchestrator trusts summaries after compaction | Reconcile state from artifacts and Git/filesystem evidence before dispatch |
| Preferred model unavailable | Record requested/effective model and use capability fallback |
| Sequential work wastes time | Preserve sequential state-changing stages; allow only explicitly independent read-only discovery to opt into parallel execution |
| Rollback erases audit trail | Preserve control artifacts and use stage-local repair/revert rather than destructive reset |
| Human assumes true unattended multi-session execution | Launcher and finish report state whether restart is automatic or requires the continuation command |

## Completion criteria

The feature is complete when both independently installable skills pass their cold-start and adversarial evaluations, validate against the Agent Skills specification, preserve the same context-rot invariants, demonstrate Claude/Codex capability fallback in representative outputs, and include copyable one-prompt launchers.
