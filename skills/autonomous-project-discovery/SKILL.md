---
name: autonomous-project-discovery
description: Use when an insufficiently framed greenfield project, product, repository, or substantial new subsystem needs exploration before planning; skip for small, well-specified work in an understood existing project.
---

# Autonomous Project Discovery

## Purpose

Turn project fog into a bounded, evidence-backed framing and an explicit Planning-readiness decision. Discovery owns the problem, users, outcomes, scope, non-goals, hard constraints, acceptance intent, and project-wide uncertainty. Planning owns detailed architecture, interfaces, data models, milestones, migration, deployment, and verification design.

Discovery produces canonical `DISCOVERY.md` and `AGENT-STATE.md`. It may create isolated disposable examples or prototypes that unlock a named decision, but it does not create production implementation.

## Required references

Before dispatching any worker, read all six references completely:

1. [Artifact protocol](references/artifact-protocol.md) — run root, lineage, single-writer state, report ordering, recovery, and worker return contract.
2. [Discovery method](references/discovery-method.md) — territory inspection, depth, unknowns, decision policy, user gates, readiness, and stop condition.
3. [Harness adapters](references/harness-adapters.md) — map semantic actions to capabilities actually exposed by the host.
4. [Launcher template](references/launcher-template.md) — collect authority and safe defaults when starting a run.
5. [State templates](references/state-templates.md) — write complete control, scope, discovery, packet, report, and handoff artifacts.
6. [Work sizing](references/work-sizing.md) — size packets, order dependencies, enforce budgets, and cut over safely.

Treat those files as binding parts of this skill. If they conflict, apply the safer boundary and record the conflict as `blocked`; do not invent a compatibility behavior.

## Activation boundary

Use this workflow for:

- an insufficiently framed greenfield project, product, or repository;
- a substantial new subsystem whose outcome, users, scope, risks, or constraints remain materially ambiguous;
- a request to explore whether an idea should exist;
- stale or insufficient framing routed backward by Planning or Implementation.

Do not activate the full workflow for ordinary questions, small bug fixes, narrow refactors, copy changes, or well-specified work in an understood existing project. If invoked and the evidence supports `skip`, record the depth decision and route to the ordinary scoped workflow.

Run the orchestrator in the top-level session. If this skill is invoked inside a worker and the host forbids nested delegation, return a hard blocker to the parent instead of pretending orchestration occurred.

## Invariants

- Use protocol `autonomous-artifacts-v2`; durable files, not conversation memory, carry state.
- `AGENT-STATE.md` has one writer: the orchestrator.
- Use only these Discovery depths: `skip`, `targeted`, `full`.
- Use only these unknown classes: `known_known`, `known_unknown`, `unknown_known`, `candidate_unknown_unknown`.
- Every retained unknown or research/prototype packet names a non-empty `decision_unlocked`, an owner, and an allowed disposition.
- A research action exists only when it unlocks a named decision. Drop open-ended exploration.
- A worker writes its reusable report and evidence before returning. The orchestrator inspects them before changing the packet to `verified`.
- Worker returns contain at most ten lines. They point to durable artifacts; they do not reproduce the work.
- Never request or persist chain-of-thought, secrets, full transcripts, or unbounded logs. Store conclusions, assumptions, decisions, redacted excerpts, commands, and reproducible evidence.
- Preferred models and context telemetry are optional capabilities. Record requested/effective values and fallbacks; never claim unavailable capabilities ran.
- Manual restart and user preference/UAT gates are real pauses. Describe the run as resumable bounded autonomy, not literal unattended multi-session execution.

## Workflow

### 1. Bootstrap or rehydrate

Discover host capabilities, applicable `AGENTS.md`/`CLAUDE.md`, repository root, established planning location, Git/filesystem state, relevant references, existing artifacts, and prior run state. On resume or after compaction, distrust the conversation summary and reconstruct from the protocol artifacts and repository evidence.

Completion criterion: capabilities and fallbacks are recorded, the run root is known, pre-existing dirty paths are inventoried when Git exists, and existing artifact freshness has been checked.

### 2. Inspect territory before interviewing

Read the cheapest high-signal repository, product, domain, and reference evidence. Separate explicit facts from assumptions and proposals. Do not ask the user for information the available tools can observe.

Completion criterion: every framing claim has evidence, is labeled as an assumption/proposal, or is listed as an owned unknown.

### 3. Select Discovery depth

Apply the factor gate in `discovery-method.md` to greenfield status, ambiguity, blast radius, irreversibility, and artifact freshness. Record exactly one of `skip`, `targeted`, or `full`, with evidence for every factor.

Completion criterion: `AGENT-STATE.md` and `DISCOVERY.md` agree on the selected depth and its evidence.

### 4. Establish the framing

Record stakeholders, users, underlying problem, desired outcomes, scope, non-goals, constraints, existing assets, primary journeys, acceptance intent, facts, assumptions, proposals, and rejected framings. Challenge the requested solution against simpler validation paths and direct contradictions.

Keep architecture candidates at the level needed to expose constraints or decisions. Do not select detailed components, API/data contracts, implementation stages, or detailed test/deployment plans; route those to Planning.

Completion criterion: the problem and outcome are testable, scope has a stop boundary, and proposals are not presented as facts.

### 5. Map and prioritize uncertainty

Classify retained items with the four exact unknown classes. Search for project-specific blind spots rather than claiming exhaustive unknown-unknown coverage. Give every item a `decision_unlocked`, owner, and allowed disposition.

Use one focused user question only when a material decision cannot be resolved safely from evidence, research, or a cheap disposable example. For preference-heavy `unknown_known` items, show meaningfully different examples or prototypes and wait for reaction.

Completion criterion: every remaining uncertainty is connected to a decision, owner, and stopping disposition.

### 6. Decompose bounded packets

Create sequential `D-###` packets for only the inspections, framing challenges, research, or prototypes still needed. Each packet has one primary outcome, explicit inputs, `decision_unlocked`, Small/1 or Medium/2 sizing, dependencies, observable completion, verification, and fallback. Split every Large unit before dispatch.

Independent read-only scouts may run in parallel only when their outputs are isolated and one primary packet remains the acceptance unit. State-changing work stays sequential.

Completion criterion: every pending packet is dispatchable without depending on a later packet, and the next packet fits the session budget.

### 7. Resolve and accept one packet

Dispatch one fresh worker with the packet verbatim, applicable instruction paths, output/report paths, capability/model record, and the ten-line return contract. Wait using only the host-supported mechanism.

The worker writes reusable artifacts first. Independently inspect representative output and cited evidence; rerun a relevant check when available. Only then update `AGENT-STATE.md` to `verified`. Diagnose failures before a bounded retry; apply the circuit breaker in `work-sizing.md`.

Completion criterion: the packet is `verified`, `blocked`, or `superseded` with inspectable evidence and an explicit next action.

### 8. Assess Planning readiness

Write exactly one summary line in `DISCOVERY.md`: `Planning readiness: READY` or `Planning readiness: NOT_READY`.

Set `discovery_readiness` in `AGENT-STATE.md` to exactly one of:

- `ready`: framing is current and satisfies the readiness rubric;
- `not_ready`: a named blocking decision, packet, or human gate remains;
- `stale`: current repository/reference evidence contradicts the artifact revision.

Planning readiness means the problem/outcome are clear, scope is bounded, primary journeys and hard constraints are known, architecture-changing ambiguity is resolved or explicitly delegated, dangerous assumptions are visible, and every remaining unknown has an owner. It does not mean zero uncertainty.

Completion criterion: the readiness value, evidence, blocker list, and route agree across `DISCOVERY.md` and `AGENT-STATE.md`.

### 9. Finish, route, or hand off

Use these testable routes:

| State | Route |
|---|---|
| `skip` | Record why ordinary scoped work is sufficient; do not create Planning packets. |
| `ready` and only exploration was requested | Stop after Discovery and preserve the exact continuation command. |
| `ready` and planning/building was requested | Route to Planning; never jump directly to Implementation. |
| `not_ready` with a resolvable packet | Continue bounded Discovery. |
| `not_ready` with a material preference/product decision | Request one focused human gate, persist the pause, and stop. |
| `stale` or framing-changing contradiction | Set `next_stage: DISCOVERY`, preserve supersession evidence, and rediscover only the affected scope. |
| Architecture/interface/sequencing detail only | Preserve Discovery framing and route the question to Planning. |

Before a required session cutover, write `SESSION-HANDOFF.md`, update `continuation_command`, and end cleanly. Never compress work, reduce verification, or silently cross a user gate to fit the session.

## Bounded authority

Proceed autonomously only inside recorded scope and permissions. Low-impact reversible framing choices may be decided and recorded. Medium-impact reversible choices require delegated authority. High-impact, security/legal-sensitive, user-facing, expensive, difficult-to-reverse, destructive, public, or credential-dependent choices require explicit authority unless the current artifact grants that exact choice.

Discovery may write run artifacts and isolated disposable prototypes. It may not modify product code, perform deployment/publishing, change secrets, commit unless authorized, or decide detailed system design owned by Planning.

## Completion checklist

Discovery is complete only when:

- canonical `AGENT-STATE.md`, `SCOPE.md`, and `DISCOVERY.md` are current and mutually consistent;
- the depth gate and territory evidence are recorded;
- facts, assumptions, proposals, and rejected framings are distinguishable;
- retained unknowns use the exact class/owner/disposition contract;
- every retained packet/report/evidence artifact has been sampled by the orchestrator;
- readiness and the backward/forward route are explicit and testable;
- no production implementation or Planning-owned detail was silently created;
- the exact continuation command and whether restart is manual are honest;
- representative artifacts, not exit codes or worker self-reports alone, support the verdict.
