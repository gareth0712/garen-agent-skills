# Autonomous Orchestration Skills Design

## Goal

Create three independently installable Agent Skills that form one artifact-driven pipeline:

- `autonomous-project-discovery` turns an ambiguous greenfield project or major new subsystem into a bounded, evidence-backed project framing and a planning-readiness decision.
- `autonomous-planning` turns a bounded goal into a complete, verified, resumable plan by dispatching one fresh planning worker per packet.
- `autonomous-implementation` audits readiness, repairs missing execution planning when necessary, implements one stage at a time, verifies each stage, pauses for UI UAT, and finishes with an independent integration review.

All three skills must work in Claude Code and Codex without depending on harness-specific tool names, exact model availability, or conversation history as durable state.

## Non-goals

- Claiming that a skill can create a new top-level session when the host does not expose that capability.
- Allowing unbounded autonomy, irreversible external actions, deployment, publishing, secret changes, or product decisions without explicit authority.
- Persisting private reasoning, chain-of-thought, full transcripts, secrets, or indiscriminate raw logs.
- Replacing project instructions, tests, code review, or human visual acceptance with agent self-reports.
- Treating Discovery as mandatory ceremony for small, well-specified work in an understood existing project.
- Claiming that a blind-spot pass can enumerate every unknown unknown; it is a project-specific risk-reduction method, not proof of completeness.
- Adding a shared runtime dependency. Each pipeline skill remains usable when installed alone and communicates through durable artifacts.

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
8. `route_stage`
9. `finish_or_handoff`

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

The orchestrator must run in the top-level session. If the host forbids nested delegation, invoking any pipeline workflow inside a worker is a hard blocker and the worker returns control to its parent.

### 2. Narrow, explicit invocation

These are expensive workflows. Their descriptions use mutually exclusive leading conditions:

- Discovery triggers for an insufficiently framed greenfield project, product, repository, or substantial new subsystem; it also triggers when the user asks to explore whether an idea should exist.
- Planning triggers when the user requests an executable plan and a current discovery artifact or equivalent framing is available.
- Implementation triggers when the user requests execution and a current approved plan or equivalent execution specification is available.

Ordinary questions, small bug fixes, narrow refactors, copy changes, and fully specified components must not trigger the full pipeline.

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

All three skills include their own `references/artifact-protocol.md` with protocol identifier `autonomous-artifacts-v2`. This is deliberate vendoring: any skill must remain complete when installed alone. Release validation checks that all copies expose the same required control-plane fields and invariants, while allowing stage-specific report fields.

The protocol uses the project's established planning location. If none exists, use:

```text
docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/
├── AGENT-STATE.md
├── SCOPE.md
├── DISCOVERY.md
├── MASTER-PLAN.md
├── IMPLEMENTATION-NOTES.md
├── packets/
│   └── D-001.md, P-001.md, or I-001.md
├── reports/
│   └── D-001-report.md, P-001-report.md, or I-001-report.md
├── evidence/
└── SESSION-HANDOFF.md
```

`AGENT-STATE.md` is the only control-plane index. It records:

- protocol version and workflow type;
- active pipeline stage and readiness state for Discovery, Planning, and Implementation;
- run ID and repository root;
- harness and discovered capabilities;
- requested and effective models;
- baseline Git SHA and pre-existing dirty paths, when Git exists;
- scope and stop-boundary paths;
- discovery, planning, and implementation artifact paths, revision identifiers, freshness evidence, and supersession links;
- packet/stage table with `pending`, `in_progress`, `verified`, `blocked`, or `superseded` status;
- current session budget and completed weight;
- retry counters;
- UAT state;
- next action and exact continuation command.

Only the orchestrator updates `AGENT-STATE.md`. A worker writes its packet report and evidence first, returns at most ten lines, then the orchestrator independently samples the artifact and updates state. This ordering prevents a false `verified` status when the report is missing or incomplete.

A worker report preserves the complete reusable work product: conclusions, decisions, assumptions, source paths, commands, relevant output excerpts, changed files, failures, verification evidence, and recommended next action. It excludes hidden reasoning, full chat transcripts, secrets, and unbounded logs. Large raw output remains outside Git when possible; the report stores a redacted excerpt and reproducible command.

After compaction, resumption, or a stage handoff, conversation summaries are untrusted. Rebuild state from `AGENT-STATE.md`, stage artifacts, packet/report artifacts, `SCOPE.md`, and Git history or filesystem evidence before dispatching another worker. A downstream stage must validate both the existence and freshness of its upstream artifact; filename presence alone is not readiness.

### 4. Work sizing and multi-session cutover

Every discovery packet, planning packet, and implementation stage must have one primary outcome, explicit inputs, an observable completion criterion, verification, fallback, and no unresolved dependency on a later unit.

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

- Discovery and Planning launcher default: request Fable-class/highest-reasoning orchestrator and workers.
- Implementation launcher default: request a highest-reasoning orchestrator and Sonnet-class high-effort implementation workers.
- Use exact model IDs only after the host confirms support.
- Record `requested_model`, `effective_model`, and fallback reason per worker.
- Lack of model selection is not a blocker unless the user marked the exact model as required.

This keeps the skills usable in Claude Code, where per-agent model selection may exist, and Codex, where the active collaboration API may not expose a model selector.

## Pipeline ownership

| Responsibility | Discovery | Planning | Implementation |
|---|---|---|---|
| Underlying problem and project framing | Owns | Consumes; routes back if invalid | Must not redefine |
| Users, outcomes, scope, non-goals, hard constraints | Owns | Refines only within delegated authority | Enforces |
| Four unknown classes and blind-spot search | Owns project-wide pass | Owns newly exposed planning unknowns | Records newly exposed implementation unknowns |
| Cheap research spikes, examples, or prototypes | Owns when needed to clarify framing | Owns when needed to choose architecture | May run only plan-authorized implementation spikes |
| Architecture, interfaces, data models, milestones | Provides constraints | Owns | Implements; deviations require routing policy |
| Detailed tests, migration, deployment, verification plan | Supplies acceptance intent | Owns | Executes and records actual results |
| Product code and production changes | Forbidden | Forbidden | Owns within approved plan |
| Artifact freshness and repository contradiction checks | Own stage input | Own stage input and Discovery input | Own all upstream inputs |
| User approval | High-impact framing and prototype reactions | High-impact architecture or delegation gaps | UI UAT and high-impact deviations |

No stage repeats an upstream stage wholesale. It performs a narrow sufficiency/freshness gate, then either proceeds or routes backward with a concrete contradiction or missing decision.

## Shared decision policy

Classify uncertain decisions by impact, reversibility, evidence, confidence, urgency, and owner.

- Low-impact and easily reversible: the active stage decides and records the result briefly.
- Medium-impact but reversible: the active stage may decide only when its upstream artifact delegated that authority; otherwise it proposes a bounded choice.
- High-impact, security-sensitive, legally sensitive, user-facing, expensive, or difficult to reverse: require explicit approval unless a current upstream artifact already grants that exact authority.
- Repository evidence contradicts an artifact: mark the artifact stale, preserve the contradiction as evidence, and route to the owning stage.
- A new unknown changes problem framing: route to Discovery.
- A new unknown changes architecture, interfaces, sequencing, migration, or verification: route to Planning.
- A new unknown is local, reversible, and within an existing contract: Implementation decides and records it.

Asking the user whenever anything is uncertain is not autonomy. Asking is reserved for high-impact decisions that evidence, research, or a cheap prototype cannot resolve safely.

## Activation and routing

| Request/evidence state | First stage | Next behavior |
|---|---|---|
| Greenfield build/design/architect/scaffold request without current framing | Discovery | Continue to Planning only after readiness; continue to Implementation only when the original request includes execution |
| Explore whether a project should exist | Discovery | Stop after Discovery unless the user also requested planning/building |
| Plan a project with a current Discovery artifact or equivalent framing | Planning | Validate freshness, then plan |
| Plan a project with insufficient or stale framing | Discovery | Run full or targeted Discovery, then return to Planning |
| Implement a current approved plan | Implementation | Validate Discovery/Planning consistency, then execute |
| Implement without a sufficient plan | Planning | Create/repair plan before Implementation |
| Small bug fix or narrow specified change | Neither full Discovery nor autonomous Planning by default | Use ordinary implementation workflow unless the user explicitly invokes this pipeline |
| Major subsystem in an existing product | Targeted or full Discovery based on uncertainty and blast radius | Record why the selected depth is sufficient |
| Continued implementation with current artifacts | Implementation | Rehydrate and continue; do not restart upstream stages |
| New offline/security/data requirement invalidates architecture | Planning or Discovery | Route by whether framing or only architecture changed |

An equivalent artifact is accepted when it contains the required upstream decisions and freshness evidence, even if it has a different filename. This prevents process bureaucracy while preserving readiness gates.

## Autonomous project discovery state machine

1. **Bootstrap and rehydrate** — discover capabilities, instructions, repository/reference territory, existing artifacts, and prior state before asking questions.
2. **Select depth** — choose `skip`, `targeted`, or `full` Discovery from greenfield status, ambiguity, blast radius, irreversibility, and artifact freshness. Record the evidence.
3. **Establish framing** — separate explicit facts, assumptions, proposals, rejected approaches, stakeholders, desired outcomes, constraints, existing assets, and non-goals.
4. **Map unknowns** — classify Known Knowns, Known Unknowns, Unknown Knowns, and candidate Unknown Unknowns. Connect every retained item to a decision it may change.
5. **Decompose discovery** — create sequential, weighted packets for repository inspection, domain research, framing challenges, blind spots, or cheap prototypes. Split every Large packet.
6. **Resolve packets** — dispatch one worker per packet. Independent read-only scouts may run in parallel only when their outputs are isolated and the primary packet remains the single acceptance unit.
7. **Elicit unknown knowns** — use examples, diagrams, mock outputs, wireframes, or disposable prototypes only when user reaction will materially reduce uncertainty. Pause for reaction when preference cannot be inferred.
8. **Challenge framing** — compare the requested solution with simpler validation paths, existing tools, separated products, experiments, and alternative framings. Be direct about contradictions or excessive scope.
9. **Prioritize decisions** — label each open item `must_resolve_before_planning`, `resolve_before_implementation`, `planner_may_propose`, `implementation_may_decide`, `defer`, `experiment`, or `explicit_approval`.
10. **Assess readiness** — Planning is ready when the problem/outcome are clear, scope is bounded, primary journeys and hard constraints are known, architecture-changing ambiguities are resolved or delegated, dangerous assumptions are visible, and every remaining unknown has an owner.
11. **Finish or continue** — write `DISCOVERY.md`, update state and artifact lineage, then either stop, hand off to Planning, or create the next bounded Discovery packet.

Discovery may produce disposable prototypes or experiments in an isolated scratch location, but it must not create production implementation. A research action is valid only when it unlocks a named decision; otherwise it is exploration without a stopping condition and must be dropped.

## Autonomous planning state machine

1. **Bootstrap and rehydrate** — discover capabilities and reconcile state, artifact lineage, reports, Git/filesystem evidence, and current repository instructions.
2. **Discovery sufficiency gate** — validate that `DISCOVERY.md` or an equivalent artifact is current and contains enough framing. Route to full or targeted Discovery when it does not.
3. **Planning readiness review** — dispatch one read-only worker to identify architecture-shaping decisions, repository contradictions, inherited assumptions, and planning-specific unknowns without repeating broad project discovery.
4. **Decompose** — produce ordered planning packets with dependency edges, weights, and Task Contracts. Split every Large packet.
5. **Plan sequentially** — dispatch exactly one planning worker for the current packet. The worker writes its report before returning.
6. **Accept packet** — inspect the report, verify cited project evidence, update `MASTER-PLAN.md` and state, then checkpoint according to policy.
7. **Review plan** — dispatch an independent final reviewer for Discovery alignment, completeness, internal consistency, feasibility, verification coverage, and scope leakage.
8. **Repair or route** — critical planning defects become bounded repair packets; material framing defects route to Discovery.
9. **Implementation readiness gate** — require architecture, interfaces, data model, sequencing, verification, migration/deployment implications, and delegated decision boundaries when relevant.
10. **Finish or hand off** — produce an execution-ready plan, evidence index, inherited assumptions, unresolved human gates, and exact continuation command.

The planning skill may write planning artifacts but must not implement product code.

## Autonomous implementation state machine

1. **Bootstrap and rehydrate** — perform the same evidence-first reconstruction, artifact-lineage validation, and dirty-tree inventory.
2. **Implementation readiness** — dispatch one read-only worker to validate Discovery/Planning consistency against the repository and return `READY`, `NEEDS_PLANNING`, or `NEEDS_DISCOVERY`, with evidence.
3. **Route upstream** — missing mechanical detail may become a bounded planning repair; architecture-changing gaps route to Planning and framing-changing gaps route to Discovery. Implementation does not silently absorb upstream ownership.
4. **Freeze execution spec** — write the stage list and Task Contracts, then checkpoint it separately when commits are authorized.
5. **Implement stage** — dispatch one implementation worker with the verbatim contract, required instruction paths, report path, and ten-line return contract.
6. **Automatic acceptance** — independently inspect changed artifacts, rerun representative verification, and sample a real affected flow. Worker `done` is not evidence.
7. **Remediate** — diagnose before retrying. Allow at most two evidence-driven remediation cycles. Roll back only when the workspace is unsafe or the approach is invalid; otherwise preserve useful work and repair it.
8. **UI UAT** — after automatic UI acceptance, present screenshots or a live URL and wait for human approval before the next stage.
9. **Checkpoint** — create a path-limited stage commit only when authorized; otherwise record a reversible filesystem/Git checkpoint without touching unrelated dirty paths.
10. **Integration acceptance** — dispatch an independent reviewer to verify Discovery intent, Planning contracts, cross-stage consistency, tests/build, affected flows, and scope. Findings route to the stage that owns them.
11. **Finish or hand off** — update `IMPLEMENTATION-NOTES.md` and report verified stages, evidence paths, changed files, deviations from plan, assumptions, residual gates, rollback points, and continuation command.

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
skills/autonomous-project-discovery/
├── SKILL.md
├── references/
│   ├── artifact-protocol.md
│   ├── discovery-method.md
│   ├── harness-adapters.md
│   ├── launcher-template.md
│   ├── state-templates.md
│   └── work-sizing.md
└── evals/evals.json

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

No runtime script is planned because orchestration capability discovery and state updates depend on host tools and project policy. Deterministic structural checks belong in repository validation commands rather than inside an installed skill.

## Test-driven validation

Create and validate one skill at a time in pipeline order.

### `autonomous-project-discovery`

Run three fresh-agent scenarios without the skill, capture exact failures, then rerun with the skill:

1. An underspecified greenfield AI product that tempts premature architecture and implementation.
2. A major subsystem request inside an existing repository that requires choosing targeted versus full Discovery.
3. A preference-heavy project where a cheap example or prototype exposes an Unknown Known and context telemetry/model selection are unavailable.

Assertions cover activation depth, repository/reference inspection, facts versus assumptions, four unknown classes, project-specific blind spots, decision ownership, anti-endless-research criteria, `DISCOVERY.md`, planning readiness, ten-line returns, model fallback recording, and absence of production code.

### `autonomous-planning`

Run three fresh-agent scenarios without the skill, capture exact failures, then rerun with the skill:

1. A large cross-subsystem request with a current Discovery artifact that tempts a single-session plan and shallow packets.
2. A resumed run after compaction with a stale Discovery revision, stale checkbox, and contradictory Git evidence.
3. A Codex-like harness without model selection or context telemetry, plus an equivalent discovery brief with a non-standard filename.

Assertions cover Discovery sufficiency/freshness, backward routing, artifact creation, state reconciliation, Large-unit splitting, session budget enforcement, ten-line returns, model fallback recording, and absence of product-code edits.

### `autonomous-implementation`

After planning passes its deployment gate, repeat the RED/GREEN cycle with:

1. A small non-UI change with tests and a real-flow check.
2. A mixed UI/non-UI scope that exceeds one session and requires UAT.
3. A dirty worktree with failed verification, retry pressure, and unavailable preferred model selection.

Assertions cover upstream-artifact consistency, stage ownership routing, readiness judgment, planning repair, stage sizing, preservation of unrelated changes, independent evidence sampling, retry limits, UAT pause, integration review, plan-deviation reporting, and lossless handoff.

For all three skills:

- use isolated fixtures or output-only workspaces;
- run a cold-start worker that has no prior memory and only the skill files;
- write gap reports before editing the skill;
- remove temporary fixtures after testing;
- validate frontmatter and directory naming with `npx skills-ref validate`;
- inspect every generated `SKILL.md`, reference, eval file, and representative agent output;
- record any model-coverage limitation rather than claiming unrun coverage.

### Activation and routing evaluation matrix

| Prompt | First activation | Required artifact | Follow-up |
|---|---|---|---|
| “Build me a new AI agent platform.” | Discovery | `DISCOVERY.md` | Planning, then Implementation after both readiness gates |
| “Help me explore whether I should build a personal OS.” | Discovery | `DISCOVERY.md` | Stop after Discovery unless later requested |
| “Create an implementation plan for the project described in project-discovery.md.” | Planning | Current Discovery artifact or documented equivalent | Planning only unless execution is requested |
| “Implement the approved plan in implementation-plan.md.” | Implementation | Current plan; Discovery evidence when referenced by the plan | Execute after consistency gate |
| “Fix the incorrect loading state in the existing dashboard.” | No full pipeline by default | None | Ordinary scoped implementation |
| “Add a new billing subsystem to the existing SaaS.” | Targeted or full Discovery | Discovery depth decision plus `DISCOVERY.md` when needed | Planning after readiness |
| “Continue yesterday’s implementation.” | Implementation | `AGENT-STATE.md` plus current upstream artifacts | Rehydrate and continue |
| “The current architecture no longer supports the newly required offline mode.” | Planning, or Discovery if product framing changes | Contradiction report | Re-plan or rediscover before Implementation resumes |

## Rejected alternatives

### Shared third core skill

Rejected because installing any pipeline skill alone would leave a hidden runtime dependency, and user-invoked or disabled skills may not be preloadable by workers in every host.

### Discovery folded into Planning

Rejected because problem framing and executable system design have different activation rules, outputs, user gates, and stopping conditions. Folding them together makes broad ideation repeat on every planning request and encourages premature architecture.

### One combined pipeline skill

Rejected because Discovery, Planning, and Implementation have different side-effect permissions and completion criteria. Combining them increases loaded context, makes activation less precise, and raises the risk that an upstream stage rushes to reach visible implementation.

### Claude-specific prompts

Rejected because exact Agent tool names, model aliases, built-in agent behavior, and skill preloading do not carry over to Codex. Harness adapters preserve the same semantics without pretending the APIs are identical.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Protocol copies drift | Same protocol ID, required-field assertions, and cross-skill release comparison |
| Discovery becomes endless research or questioning | Every packet must unlock a named decision; readiness is based on owned manageable uncertainty, not zero uncertainty |
| Discovery over-triggers on routine work | Explicit `skip`, `targeted`, and `full` depth gate plus activation matrix |
| Unknown Unknowns create false completeness claims | Report candidate blind spots and confidence; never claim enumeration is complete |
| Downstream skill trusts a stale filename | Validate artifact lineage, content sufficiency, and repository freshness before proceeding |
| Agent rushes to fit a session | Large units are invalid; session budget is a ceiling; verification cannot be reduced |
| Artifact directory pollutes source history | Prefer established planning location; commit only concise control/report artifacts when authorized |
| Full logs expose secrets or bloat Git | Redacted excerpts plus reproducible commands; raw logs remain outside Git |
| Orchestrator trusts summaries after compaction | Reconcile state from artifacts and Git/filesystem evidence before dispatch |
| Preferred model unavailable | Record requested/effective model and use capability fallback |
| Sequential work wastes time | Preserve sequential state-changing stages; allow only explicitly independent read-only discovery to opt into parallel execution |
| Rollback erases audit trail | Preserve control artifacts and use stage-local repair/revert rather than destructive reset |
| Human assumes true unattended multi-session execution | Launcher and finish report state whether restart is automatic or requires the continuation command |

## Completion criteria

The feature is complete when all three independently installable skills pass their cold-start, adversarial, and activation/routing evaluations; validate against the Agent Skills specification; preserve the same context-rot invariants and artifact lineage; demonstrate Claude/Codex capability fallback and backward routing in representative outputs; and include copyable one-prompt launchers.
