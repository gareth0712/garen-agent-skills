# Discovery Method

## Start with territory, not a questionnaire

Inspect applicable project instructions, repository structure, current product behavior, planning artifacts, relevant references, Git/filesystem state, and available observation tools before asking the user anything. Prefer evidence that can invalidate framing cheaply. Label each statement as an explicit fact, evidence-backed inference, assumption, proposal, rejected approach, or retained unknown.

Do not ask the user to paste logs, screenshots, file contents, or repository facts that tools can observe. When the project is not a repository, inspect the supplied brief, examples, market/domain references, and existing assets with the same evidence discipline.

## Depth gate

The core `discovery_depth` enum is exactly:

- `skip`: existing work is understood, small, well specified, reversible, current, and contains no material framing ambiguity;
- `targeted`: a substantial subsystem or stale slice has bounded uncertainty in identifiable areas while the surrounding product framing remains current;
- `full`: greenfield work, broad ambiguity, large blast radius, difficult-to-reverse choices, or missing/stale framing could change whether or what to build.

Record a factor-by-factor decision:

| factor | evidence question |
|---|---|
| `greenfield_status` | Is there current product/repository framing to inherit? |
| `ambiguity` | Could plausible interpretations change users, outcomes, or scope? |
| `blast_radius` | How many product areas, stakeholders, or external systems may be affected? |
| `irreversibility` | Are decisions public, expensive, regulated, destructive, or hard to undo? |
| `artifact_freshness` | Does current evidence still support the framing revision? |

Every row cites a source path/excerpt or `not_applicable` with a reason. One high-impact factor may justify a deeper pass; do not average away risk. When `skip` applies, record why and return to ordinary scoped work rather than turning Discovery into ceremony.

## Framing ledger

Maintain co-located sections for:

- underlying problem and evidence it exists;
- stakeholders, users, affected non-users, and desired outcomes;
- primary journeys and acceptance intent;
- scope, non-goals, stop boundary, and granted authority;
- hard constraints, existing assets, and dependencies;
- explicit facts, assumptions to test, proposals, and rejected framings;
- dangerous assumptions that could invalidate the initiative.

Challenge solution-first requests. Compare the requested solution with a simpler validation path, an existing tool, a smaller experiment, a separated product, or a different framing when evidence makes that credible. Be direct about contradictions and excessive scope. Discovery may state design constraints or compare alternatives only far enough to frame a later decision; Planning selects architecture, interfaces, data models, milestones, and detailed verification.

## Product existence and outcome verifiability

Activate both challenges for greenfield products and materially ambiguous substantial new subsystems at `targeted` or `full` depth. Do not activate them for `skip` work. Record `product_intent` as `production_commercial` or `learning_prototype`; if intent remains materially ambiguous after evidence inspection, ask one focused question. Project size, a side-project label, or low initial user count is not evidence of learning intent.

### Direct-model baseline and durable value

For `production_commercial`, compare the proposed workflow with a Direct-model baseline using the same representative raw inputs and requested outcomes. Persist:

- observed model/tool identity and date, or `unavailable` plus the exact capability/authority gap;
- reproducible fixture paths or hashes, bounded direct workflow, and output/evidence hashes when execution is authorized;
- observed success/failure, manual steps, repeatability, uncertainty, and supported/unsupported claims;
- each claimed product advantage, its validation action, and its `falsification_condition`.

Current authority never implies a paid API, external account, credential, upload, or public effect. When the baseline cannot be observed within authority, record `existence_gate_state: external_evidence`; absence of evidence is neither success nor failure evidence. Never synthesize a baseline from model reputation or a named researcher's view. A fixed prompt count may be a recorded warning signal but is not a universal approval threshold.

A production/commercial pass requires evidence of at least one material advantage appropriate to the outcome. Candidate dimensions are persistent state/longitudinal workflow, system-of-record or action integration, legitimately accessed private context, repeatability/automation/operator effort, collaboration/role coordination, privacy/offline/residency/data minimization, audit/compliance/safety/recovery, or measured quality/latency/reliability/economic improvement. A label without observed evidence and a falsification condition remains insufficient.

For `learning_prototype`, `existence_gate_state: bypassed_learning` requires a learning objective, non-commercial boundary, reason the reproduction serves that objective, bounded time/effects, and a measurable production/commercial revisit trigger. The bypass expires at that trigger. It never bypasses the outcome challenge.

### Outcome rows and sharp questions

Create one row per material outcome with these exact fields: `outcome_id`, `claim`, `oracle_or_metric`, `representative_fixtures`, `adversarial_fixtures`, `acceptable_error`, `failure_classes`, `automatic_verification`, `human_boundary`, `rollback_recovery`, `falsification_condition`, and `owner_deadline`. The row frames observable acceptance; Planning still owns detailed test architecture and implementation sequencing.

An outcome without a credible automatic oracle may use a specific human rubric naming who judges, when, and how disagreement is handled. It may not be labeled automatically verified. If neither an oracle nor a specific rubric exists, set `verifiability_gate_state: insufficient`; use `partial` when only a proper subset of material outcomes passes.

For a missing production/commercial claim, inspect evidence first and ask exactly one sharp decision-unlocking question at a time. Record the decision unlocked, why it is material, evidence/choice required, and answer or non-answer. Do not repeat a substantively answered question or pressure the user toward approval. Stop asking about the same failed gate after an explicit override; preserve the result instead.

### Aggregate state and readiness

Derive `product_justification_state` separately from `discovery_readiness`:

| aggregate state | required gate facts | readiness effect |
|---|---|---|
| `approved` | `production_commercial`; existence and verifiability are both `approved` | May be `ready` when the ordinary rubric also passes |
| `blocked` | A production/commercial material claim is insufficient/unavailable, or any required outcome remains partial/insufficient, with no exact override | Must be `not_ready` |
| `user_directed_unapproved` | The authorized user explicitly insists on a named continuation scope after a failed/insufficient gate | May be `ready` when other framing passes; preserve failed claims and non-endorsement |
| `bypassed_learning` | The bounded learning record passes and verifiability is `approved` | May be `ready`; gives no production/commercial endorsement |

`ready + user_directed_unapproved` means the product is framed well enough for Planning under the user's exact override; it does not mean Discovery endorses building it. `bypassed_learning` bypasses only commercial existence justification and still requires an approved verifiability gate. Every readiness route carries the aggregate state, evidence revision, override/bypass boundary, failed claims, effect-blocking gates, and revisit trigger.

## Four unknown classes

Classify every retained item with exactly one value:

- `known_known`: verified knowledge that supports a named decision;
- `known_unknown`: an explicit gap whose answer may change a named decision;
- `unknown_known`: tacit preference or knowledge likely to surface through reaction to a concrete example;
- `candidate_unknown_unknown`: a project-specific blind spot hypothesis, never a claim of complete enumeration.

Every retained row contains `unknown`, `class`, `decision_unlocked`, `owner`, and `disposition`. Even a `known_known` names the decision it supports. Empty decision or owner fields mean the row is not actionable and must be repaired or dropped.

## Project-specific blind-spot pass

Search the intersections that are credible for this project: users and incentives, failure modes and recovery, privacy/security/legal duties, accessibility and inclusion, data provenance/retention, operational ownership, external integrations, distribution/adoption, offline/degraded behavior, abuse, cost, and preference-sensitive UI. Tie each candidate to concrete territory evidence and a decision it might change.

A generic risk checklist is not evidence. Retain a `candidate_unknown_unknown` only when the project's domain, assets, constraints, or dependencies make it plausible. State confidence and the cheapest falsification path; never claim all unknown unknowns were found.

## Decision and research policy

Classify an uncertain decision by impact, reversibility, available evidence, confidence, urgency, and owner.

- Low impact and easily reversible: Discovery may decide and record it.
- Medium impact but reversible: Discovery may decide only when authority is explicitly delegated; otherwise propose a bounded choice.
- High impact, security/legal-sensitive, user-facing, expensive, or difficult to reverse: require explicit approval unless current scope grants that exact authority.
- Repository evidence contradicts framing: mark the artifact `stale` and route to Discovery.
- Architecture/interface/data/sequencing/migration/verification detail: route to Planning.

Allowed dispositions are exactly:

- `must_resolve_before_planning`
- `resolve_before_implementation`
- `planner_may_propose`
- `implementation_may_decide`
- `defer`
- `experiment`
- `explicit_approval`

A research, inspection, or prototype action exists only when it has a non-empty `decision_unlocked`. Define the competing outcomes, bounded source/fixture set, evidence signal, time/work-unit boundary, owner, disposition, and stop condition before dispatch. If the result would not change a named decision, drop the action.

## Unknown-known prototypes and interview gate

Use a diagram, mock output, wireframe, worked example, or disposable prototype when seeing concrete alternatives is the cheapest way to surface tacit knowledge. Keep it isolated from production, visibly disposable, and limited to the decision it unlocks. Present meaningfully different alternatives rather than cosmetic variations.

Inspect first, then ask at most one focused question at a time. Ask only when the answer materially changes product framing, grants irreversible authority, or resolves a preference that evidence and a cheap prototype cannot infer. Record the question, decision, offered alternatives, safe default if one exists, and pause state. Never replace evidence gathering with a broad questionnaire.

Persist every human or external pause at canonical `gates/G-###.md`. Human-decision types are `preference`, `product_decision`, `authority`, `uat`, and `security_legal`; `external_evidence` names the external evidence owner. `AGENT-STATE.md` points to that one gate path. Keep prototype and supporting evidence as fields inside the gate rather than inventing a second gate location or shape.

Operational preflight/recovery blockers use the same canonical artifact with type `capability`, `environment`, or `internal_recovery`, an explicit non-human owner when applicable, and a falsifiable recovery check. They are not human preference gates: do not manufacture a focused product question or set `pending_human_gate` merely because a tool, path, dependency, or internal recovery failed. Conversely, never relabel a product, authority, UAT, security, or legal decision as operational to avoid the real human gate.

## Readiness rubric and routes

`discovery_readiness` is the current Discovery artifact's handoff/entry readiness for Planning. Set it to one of `ready`, `not_ready`, or `stale`:

| value | observable test | route |
|---|---|---|
| `ready` | Problem/outcome are clear; scope and stop boundary are bounded; primary journeys and hard constraints are known; framing-changing ambiguity is resolved; architecture-changing ambiguity is resolved or delegated; dangerous assumptions are visible; every remaining unknown has an owner and disposition. | Stop after Discovery if only exploration was requested; otherwise route to Planning. |
| `not_ready` | A named framing decision, required evidence packet, or material human preference/authority gate fails the ready test. | Continue a bounded Discovery packet or pause for one focused human gate. |
| `stale` | Current repository/reference evidence contradicts the recorded discovery revision. | Preserve contradiction/supersession evidence, set `next_stage: DISCOVERY`, and refresh only the affected framing. |

Derive exactly one summary line in `DISCOVERY.md`: `ready` => `Planning readiness: READY`; `not_ready` or `stale` => `Planning readiness: NOT_READY`. The separate `planning_readiness` field describes an actual Planning artifact's readiness for its downstream stage and stays `not_assessed` until Planning exists.

## Stop condition

Discovery stops when uncertainty is manageable and owned, not when it reaches zero. Stop when the readiness rubric passes, or when the next progress requires a persisted human/external gate. Continue only while a bounded action can unlock a named decision. Do not research merely because more information exists, repeat an upstream pass wholesale, or drift into Planning-owned design and production implementation.
