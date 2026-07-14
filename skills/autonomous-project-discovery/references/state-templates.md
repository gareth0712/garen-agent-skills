# Discovery State Templates

Replace every brace-delimited value with observed run data before accepting an artifact. Remove optional rows that truly do not apply and record the reason in `Assumptions and omissions`; never leave unresolved placeholders. Use forward-slash artifact paths.

## Contents

- [`AGENT-STATE.md`](#agent-statemd)
- [`SCOPE.md`](#scopemd)
- [`DISCOVERY.md`](#discoverymd)
- [`packets/D-###.md`](#packetsd-md)
- [`reports/D-###-report.md`](#reportsd--reportmd)
- [`SESSION-HANDOFF.md`](#session-handoffmd)

## `AGENT-STATE.md`

Only the top-level orchestrator writes this file.

```markdown
# Agent State

protocol_version: autonomous-artifacts-v2
workflow_type: discovery
active_pipeline_stage: DISCOVERY
run_id: {YYYYMMDD-goal-slug-N}
repository_root: {absolute repository or project root}
run_root: {project-relative planning/run path}
updated_at: {ISO-8601 timestamp}

## Harness and capabilities

harness: {Claude Code | Codex | generic host name}
restart_mode: {automatic only when explicitly supported | manual}
context_telemetry: {reported percentage | unavailable}

| capability | status | observed evidence | fallback |
|---|---|---|---|
| fresh_isolated_worker | {available | unavailable | unknown} | {host surface inspected} | {hard blocker when unavailable} |
| model_selection | {available | unavailable | unknown} | {host surface inspected} | {host_default when unavailable} |
| context_telemetry | {available | unavailable | unknown} | {host signal inspected} | {weight budget without estimation} |
| ui_observation | {available | unavailable | unknown} | {host surface inspected} | {human gate when required} |
| new_top_level_session | {available | unavailable | unknown} | {host surface inspected} | {manual continuation command} |

## Models

orchestrator_requested_model: {user preference or highest-reasoning preference}
orchestrator_effective_model: {confirmed model ID | host_default}
orchestrator_fallback_reason: {none when confirmed | observed selector limitation}

## Instructions and repository baseline

applicable_instruction_paths:
- {project-relative instruction path, or none_found after an explicit search}

baseline_git_sha: {Git SHA | not_a_git_repository}
repository_revision: {current Git SHA, content digest, or dated filesystem revision}
pre_existing_dirty_paths:
- {path present before this run, or none_observed}

## Scope and authority

scope_path: SCOPE.md
stop_boundary: {observable Discovery stop boundary}
risk_mode: {normal | high_risk | ui}
allowed_external_effects: {bounded list | none}
commit_policy: {not_authorized | path_limited_authorized}

## Pipeline readiness

discovery_depth: {skip | targeted | full}
discovery_readiness: {ready | not_ready | stale}
planning_readiness: not_assessed
implementation_readiness: not_assessed
next_stage: {DISCOVERY | PLANNING | STOP}

## Artifact lineage

discovery_artifact_path: DISCOVERY.md
discovery_revision: {stable revision or digest}
repository_revision_at_discovery: {revision inspected by DISCOVERY.md}
derived_from: {source artifact revision | none_for_initial_discovery}
freshness_evidence: {paths/revisions/commands proving currency}
supersedes: {prior discovery revision | none_for_initial_revision}

planning_artifact_path: {current equivalent path | none_created}
planning_revision: {current revision | not_assessed}
implementation_artifact_path: {current equivalent path | none_created}
implementation_revision: {current revision | not_assessed}

## Session control

session_budget: {6 | 4}
completed_weight: {sum of verified packet weights}
next_packet_weight: {1 | 2 | none}
remediation_cycles_this_session: {0 | 1 | 2}

## Packets

| packet | decision_unlocked | size | weight | dependencies | status | report | evidence | requested_model | effective_model | fallback_reason | retry_count |
|---|---|---|---:|---|---|---|---|---|---|---|---:|
| D-001 | {named decision} | {Small | Medium} | {1 | 2} | {verified packet IDs | none} | {pending | in_progress | verified | blocked | superseded} | reports/D-001-report.md | evidence/{bounded evidence path} | {requested preference} | {confirmed model ID | host_default} | {none when confirmed | non-empty observed reason} | {0 | 1 | 2} |

## Human gates and UAT

uat_state: {not_required | pending_preference_reaction | approved | rejected}
pending_human_gate: {one material question and decision | none}
gate_evidence_path: {artifact path | none}

## Next action

next_action: {one evidence-based action}
continuation_command: {exact safely quoted host command/action naming this skill, run root, and next action}
blockers:
- {named blocker with owner and recovery route, or none}

## Assumptions and omissions

- {explicit assumption, owner, validation path, and effect if false, or none}
```

## `SCOPE.md`

```markdown
# Discovery Scope

run_id: {run ID}
scope_revision: {stable revision or digest}
updated_at: {ISO-8601 timestamp}

## Goal and evidence

- Desired outcome: {observable project outcome}
- Why now: {evidence or explicitly unverified motivation}
- Underlying problem hypothesis: {problem statement without assuming the requested solution}

## In scope

- {bounded product, repository, subsystem, user, or decision surface}

## Out of scope

- {explicitly excluded adjacent work}

## Stop boundary

Discovery stops after a current `DISCOVERY.md`, an explicit Planning-readiness decision, and a durable next route. It does not produce production code or Planning-owned detailed architecture, interfaces, data contracts, milestones, migration, deployment, or verification plans.

## Authority

- Reversible artifact choices: {delegated boundary}
- Disposable prototypes: {allowed isolated path and limits | not_authorized}
- Read-only external research: {allowed sources/decision boundary | not_authorized}
- Commits/checkpoints: {not_authorized | exact authorized paths}
- Irreversible/public/destructive effects: {exact authority | not_authorized}
- Credentials/secrets: never persist; {availability boundary}

## Human gates

- Product/preference approval: {one-question policy and owner}
- Security/legal/expensive decisions: {approval owner}
- UI/prototype reaction: {required evidence and pause behavior | not_required}
- Manual restart: {required | host-confirmed automatic action}

## Acceptance

- {observable framing/readiness criteria}
- {representative artifact/evidence sampling required}
```

## `DISCOVERY.md`

```markdown
# Discovery

run_id: {run ID}
discovery_revision: {stable revision or digest}
repository_revision: {revision inspected}
derived_from: {source revision | none_for_initial_discovery}
supersedes: {prior discovery revision | none_for_initial_revision}
freshness_evidence: {paths/revisions/commands proving currency}
updated_at: {ISO-8601 timestamp}

## Executive framing

- Underlying problem: {evidence-backed problem}
- Desired outcome: {observable outcome}
- Why this initiative may or may not exist: {direct evidence-backed challenge}
- Selected depth: {skip | targeted | full}

## Depth evidence

| factor | finding | source path/excerpt or not_applicable reason |
|---|---|---|
| greenfield_status | {finding} | {evidence} |
| ambiguity | {finding} | {evidence} |
| blast_radius | {finding} | {evidence} |
| irreversibility | {finding} | {evidence} |
| artifact_freshness | {finding} | {evidence} |

## Stakeholders, users, and outcomes

| stakeholder/user | need or impact | desired outcome | evidence/confidence |
|---|---|---|---|
| {specific group} | {need/impact} | {observable outcome} | {source and confidence} |

## Primary journeys and acceptance intent

| journey | start and desired finish | acceptance intent | unresolved framing |
|---|---|---|---|
| {user journey} | {bounded start/finish} | {observable intent, not detailed test design} | {owned item | none} |

## Scope, non-goals, and constraints

### In scope
- {bounded item}

### Non-goals
- {excluded item}

### Hard constraints
- {constraint with source}

### Existing assets and dependencies
- {asset/dependency with source and freshness}

## Framing ledger

### Explicit facts
- {fact and evidence}

### Evidence-backed inferences
- {inference, evidence, and confidence}

### Assumptions to test
- {assumption, owner, and effect if false}

### Proposals
- {proposal and decision owner}

### Rejected framings
- {rejected framing and evidence-based reason}

## Unknowns and decision ownership

| unknown | class | decision_unlocked | owner | disposition | confidence/evidence | falsification or next signal |
|---|---|---|---|---|---|---|
| {retained item} | {known_known | known_unknown | unknown_known | candidate_unknown_unknown} | {named decision} | {role/person/stage} | {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval} | {bounded evidence} | {observable signal} |

## Project-specific blind spots

| candidate blind spot | project evidence making it plausible | decision_unlocked | confidence | cheapest falsification |
|---|---|---|---|---|
| {candidate, without completeness claim} | {specific source/intersection} | {named decision} | {low | medium | high} | {bounded signal} |

## Framing challenge

- Requested solution versus underlying problem: {finding}
- Simpler validation path or existing alternative: {finding}
- Contradictions/excess scope: {finding}
- Boundary handed to Planning: {constraints/decision questions only; no selected detailed architecture/API/data/stages}

## Research and prototype packets

| packet | action | decision_unlocked | owner | disposition | stop condition | artifact/report |
|---|---|---|---|---|---|---|
| D-001 | {bounded inspection/research/disposable example} | {named decision} | {owner} | {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval} | {observable stopping signal} | {packet and report paths} |

## Decisions and delegated uncertainty

| decision | outcome or bounded alternatives | authority/evidence | downstream owner |
|---|---|---|---|
| {named decision} | {outcome or choices} | {source/approval} | {Discovery | Planning | Implementation | user role} |

## Planning readiness evidence

- Problem/outcome clarity: {pass/fail evidence}
- Bounded scope and stop boundary: {pass/fail evidence}
- Primary journeys and hard constraints: {pass/fail evidence}
- Framing-changing ambiguity: {resolved/blocker}
- Architecture-changing ambiguity: {resolved or explicitly delegated/blocker}
- Dangerous assumptions: {visible with owners/blocker}
- Remaining unknown ownership: {all owned/blocker}

Planning readiness: {READY | NOT_READY}

## Route and residual uncertainty

- Current `discovery_readiness`: {ready | not_ready | stale}
- Next stage: {DISCOVERY | PLANNING | STOP}
- Residual owned uncertainty: {items, owners, dispositions}
- Human/external gates: {material gate | none}
- Exact continuation command: {safely quoted command/action}
```

## `packets/D-###.md`

```markdown
# Discovery Packet D-{sequence}

packet_id: D-{sequence}
primary_outcome: {one observable outcome}
decision_unlocked: {one named decision}
owner: {orchestrator-assigned owner}
disposition: {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval}
size: {Small | Medium}
weight: {1 | 2}
requested_model: {preference}
report_path: reports/D-{sequence}-report.md
evidence_root: evidence/D-{sequence}/

## Goal

{One bounded outcome and why it unlocks the named decision.}

## Inputs and freshness

- {source path/revision}
- {applicable instruction path}
- Dependencies: {verified D packet IDs | none}

## Scope and stop boundary

- In scope: {bounded evidence/prototype surface}
- Out of scope: production implementation and Planning-owned detailed design
- Stop when: {observable signal or bounded negative result}

## Authority and side effects

- Allowed writes: {assigned report/evidence and isolated scratch paths}
- External effects: {read-only bounded research | none}
- Commit/public/destructive/secret changes: not authorized unless this packet cites exact scope authority

## Completion and verification

- Completion criterion: {artifact/result that decides or narrows `decision_unlocked`}
- Verification command/read/UI observation: {reproducible check}
- Expected signal: {observable pass/fail evidence}
- Artifact sampling: {representative output the orchestrator must open}

## Fallback and retry

- On unavailable capability: {recorded fallback or blocker}
- On failure: preserve evidence, diagnose, and change one bounded variable
- Maximum remediation cycles: 2

## Worker report and return

Write the complete reusable report before returning. Return at most ten lines containing verdict, report path, evidence paths, changed paths, verification summary, and blocker/next action. Do not return chain-of-thought, secrets, full transcripts, or unbounded logs.
```

## `reports/D-###-report.md`

```markdown
# Discovery Packet D-{sequence} Report

packet_id: D-{sequence}
verdict: {PASS | FAIL | BLOCKED}
decision_unlocked: {named decision}
report_revision: {stable revision or digest}
completed_at: {ISO-8601 timestamp}

## Outcome and conclusions

- Primary outcome: {result}
- Decision enabled or narrowed: {result and confidence}
- Recommended route: {Discovery packet | human gate | Planning | stop}

## Decisions and assumptions

| item | type | outcome | owner | effect if false |
|---|---|---|---|---|
| {item} | {decision | assumption | residual unknown} | {result} | {owner} | {impact} |

## Sources and evidence

| source path/revision | relevant bounded excerpt or observation | freshness |
|---|---|---|
| {path/revision} | {redacted relevant signal} | {current/stale finding} |

## Commands and verification

| command/read/observation | expected signal | observed signal | evidence path |
|---|---|---|---|
| {reproducible check} | {expected} | {bounded result} | evidence/D-{sequence}/{artifact} |

## Created or changed files

- {assigned artifact path and purpose, or none}

## Intentionally untouched

- Production code, unrelated dirty paths, secrets, and unapproved external state.

## Failures, fallbacks, and retries

- Failure/limitation: {observed condition | none}
- Fallback used: {recorded fallback | none}
- Retry count: {0 | 1 | 2}
- Requested/effective model: {requested} / {confirmed ID | host_default}
- Model fallback reason: {none when confirmed | observed limitation}

## Residual uncertainty and next action

- {item, owner, allowed disposition, and next signal, or none}

## Redaction statement

This report contains conclusions and bounded evidence only. Secrets, chain-of-thought, full transcripts, and unbounded logs were neither requested nor persisted.
```

## `SESSION-HANDOFF.md`

```markdown
# Session Handoff

protocol_version: autonomous-artifacts-v2
run_id: {run ID}
handoff_revision: {stable revision or digest}
created_at: {ISO-8601 timestamp}
restart_mode: {manual | host-confirmed automatic action}

## Verified state

- Current Discovery revision: {revision}
- Repository revision/freshness evidence: {revision and evidence paths}
- Verified packets and weights: {IDs and weights}
- `completed_weight` / `session_budget`: {number} / {6 or 4}
- Representative artifacts inspected: {paths and observed signals}

## Active or blocked state

- Active packet: {packet ID | none}
- Unsupported status downgraded during reconciliation: {finding | none}
- Blocker/human gate: {condition, owner, recovery | none}
- Pre-existing dirty paths to preserve: {paths | none_observed}

## Next action

- Owning stage: {DISCOVERY | PLANNING | STOP}
- Exact next action: {one evidence-based action}
- Required files to read first: AGENT-STATE.md, SCOPE.md, DISCOVERY.md, {active packet/report paths}
- Exact continuation command: {safely quoted command/action naming skill, run root, and next action}

## Recovery note

On resume, distrust conversation summaries. Reconcile packet status, reports, evidence, Git/filesystem state, lineage, and budget before dispatching a worker.
```
