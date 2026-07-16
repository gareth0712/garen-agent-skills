# Project Existence and Verifiability Gates Design

**Date:** 2026-07-16
**Status:** approved design, pending written-spec review
**Owner:** Project Discovery
**Inspired by:** the supplied Software 3.0, jagged-intelligence, and agentic-engineering commentary. The source is inspiration, not an authority or acceptance oracle.

## Problem

Project Discovery can currently challenge a requested solution, but it does not require production or commercial ideas to prove two separate claims:

1. the proposed product adds durable value beyond giving the same raw input directly to a capable current model; and
2. its important outcomes can be verified well enough to support safe agentic iteration.

This permits generic model wrappers or unverifiable product claims to reach Planning. It also risks the opposite mistake: rejecting products that add persistence, workflow integration, private context, repeatability, privacy, offline behavior, collaboration, auditability, safety, or economic value even when a model can imitate one isolated output.

## Goals

- Add a mandatory two-stage challenge for production/commercial greenfield products and substantial new subsystems.
- Ask one sharp, decision-unlocking question at a time until every material claim is evidenced, falsifiable, or owned.
- Permit an explicit user override without falsely claiming Discovery endorsement.
- Permit learning/prototype work to bypass the commercial justification gate with bounded evidence.
- Make every important outcome verifiable through an explicit oracle, metric, fixture set, human boundary, failure model, and rollback.
- Produce mechanically testable artifacts and fresh evaluation evidence.

“Fully justified” is bounded: every material claim in the current scope has evidence, a falsification condition, or a named owner and decision boundary. It is not a claim of absolute completeness.

## Non-goals

- Treating a named researcher, a fixed prompt count, or one model result as product authority.
- Automatically rejecting every product whose isolated output can be reproduced by a model.
- Requiring production/commercial evidence from explicitly bounded learning exercises.
- Selecting detailed architecture, APIs, schemas, deployment, or implementation stages in Discovery.
- Benchmarking every model provider or continuously tracking a leaderboard.
- Modifying existing static Discovery/Planning stage ownership beyond the new handoff fields.

## Activation and intent

The gates activate only when full Project Discovery already applies to:

- a greenfield product, application, platform, service, or system; or
- a substantial new subsystem with materially open outcome, user, scope, or risk framing.

They do not activate for ordinary questions, bug fixes, narrow refactors, copy changes, or well-specified routine work.

Discovery records one intent:

- `production_commercial`; or
- `learning_prototype`.

When intent is unclear and affects gate behavior, Discovery asks one focused question. It does not infer a learning bypass merely because the project is small or called a side project.

## Gate 1: Product Existence Challenge

### Production/commercial path

Discovery compares the proposed product with a direct-model baseline using the same representative raw inputs and requested outcomes.

The baseline record contains:

- model/tool identity and observed date, or `unavailable` with the exact missing capability;
- reproducible input fixture paths or hashes;
- the bounded direct workflow used;
- output/evidence hashes where execution is authorized and available;
- observed success, failure, number of manual steps, repeatability, and uncertainty;
- claims the baseline supports and does not support.

No paid API, external account, credential, upload, or public action is implied. If a valid baseline cannot be executed within current authority, Discovery records `external_evidence` rather than inventing results.

The proposed product must evidence at least one material advantage appropriate to its outcome. Candidate dimensions include:

- persistent state and longitudinal workflow;
- integration with systems of record or action surfaces;
- proprietary/private context with legitimate access controls;
- repeatability, automation, or reduced operator effort;
- collaboration, role separation, or multi-user coordination;
- privacy, offline, residency, or data-minimization constraints;
- auditability, compliance, safety, or bounded recovery;
- measurable quality, latency, reliability, or total economic improvement.

These are evidence dimensions, not an automatic pass list. A claimed advantage includes a validation action and a condition that would falsify it. “Three prompts” may be recorded as a warning signal but is never a universal threshold.

### Learning/prototype path

`learning_prototype` may bypass the existence challenge only when the artifact records:

- the learning or experiment objective;
- the non-commercial boundary;
- why reproducing an existing capability is useful for that objective;
- bounded time/effect limits;
- the trigger that requires a new production/commercial review.

## Gate 2: Outcome Verifiability Challenge

Every material user/system outcome receives one row containing:

| Field | Requirement |
|---|---|
| `outcome_id` | Stable identifier mapped to the current problem/journey |
| `claim` | Exact observable outcome, not a feature label |
| `oracle_or_metric` | Automated oracle/metric or an explicit human rubric |
| `representative_fixtures` | Normal cases with paths, hashes, or reproducible construction |
| `adversarial_fixtures` | Boundary, misuse, degraded, or counterexample cases |
| `acceptable_error` | Allowed uncertainty/error envelope without invented precision |
| `failure_classes` | Stable failure categories and deterministic classification |
| `automatic_verification` | Command, check, or planned observable signal |
| `human_boundary` | What cannot be automated, who decides, and when |
| `rollback_recovery` | Safe rollback, recovery, or containment point |
| `falsification_condition` | Evidence that overturns the current claim |
| `owner_deadline` | Owner and exact decision/validation boundary |

An outcome with no credible automatic oracle may use a bounded human rubric. It may not be labeled automatically verified. If neither an oracle nor a sufficiently specific human rubric exists, the outcome remains insufficient.

## Sharp-question protocol

For production/commercial work with missing evidence:

1. inspect available files, product evidence, model capability, and prior answers first;
2. select the highest-impact unresolved decision;
3. ask exactly one question that names the decision unlocked, why it is material, and the evidence or choice required;
4. persist the question and answer or non-answer;
5. never repeat a substantively answered question;
6. continue until the current-scope material claims satisfy the bounded justification definition, the user overrides, or a genuine external blocker remains.

Questions must challenge the product hypothesis, not pressure the user toward approval. When the user explicitly insists on proceeding, Discovery stops re-litigating the same gate and applies the override state.

## State model

Discovery records gate-local facts plus one aggregate state:

```yaml
product_intent: production_commercial | learning_prototype
existence_gate_state: approved | insufficient | external_evidence | bypassed_learning
verifiability_gate_state: approved | partial | insufficient
product_justification_state: approved | blocked | user_directed_unapproved | bypassed_learning
product_justification_evidence: {path, revision, observed_at}
user_override_evidence: {path, revision, authority, exact_scope} | none
revisit_trigger: {condition} | none
```

Aggregate transitions:

| State | Meaning | Discovery route |
|---|---|---|
| `approved` | Both gates are sufficiently evidenced for current scope | May become Planning-ready if all other Discovery requirements pass |
| `blocked` | A production/commercial material claim remains unjustified or unverifiable and no override exists | `discovery_readiness: not_ready`; ask one sharp question or persist the exact external gate |
| `user_directed_unapproved` | The user explicitly requires continuation despite a failed or insufficient gate | May become Planning-ready if framing is otherwise complete; preserve exact reasons and override evidence everywhere downstream |
| `bypassed_learning` | A bounded learning/prototype bypass satisfies the existence record and its outcomes still pass the verifiability challenge | May become Planning-ready; no production/commercial endorsement is implied |

`discovery_readiness` and `product_justification_state` are independent. `ready + user_directed_unapproved` means the project is framed well enough to plan, not that Discovery recommends building it.

## Durable artifacts and propagation

`DISCOVERY.md` gains:

- `Product intent and justification state`;
- `Direct-model baseline and durable value evidence`;
- `Outcome verifiability matrix`;
- `Sharp questions, answers, and rejected framings`;
- `Override or learning-bypass evidence`.

`AGENT-STATE.md`, `SESSION-HANDOFF.md`, and any readiness route carry the exact aggregate state, evidence revision, override/bypass boundary, and revisit trigger.

When `user_directed_unapproved` proceeds to Planning, the canonical Discovery artifact states that all downstream artifacts must preserve:

- the unapproved state;
- the concrete failed/insufficient claims;
- the user-authorized continuation scope;
- any gates that still block effects or acceptance.

This design changes Project Discovery and its evaluation contract. It does not redo completed static stage integration. A compatibility assertion verifies that the canonical handoff exposes the fields consumers need; broader consumer refactoring is out of scope unless evaluation proves it necessary.

## Failure and safety behavior

- No model baseline is claimed without observed evidence.
- A model baseline that succeeds once does not prove repeatability.
- A product advantage claim without a falsification condition remains insufficient.
- A subjective outcome without a specific human rubric remains insufficient.
- An unavailable external capability opens an evidence gate; it is not silently treated as failure or success.
- User override never changes failed evidence to approved evidence.
- Learning bypass automatically expires at its recorded commercial/production trigger.
- Discovery still does not write production code, deploy, publish, change secrets, or perform unauthorized external actions.

## Verification strategy

### Pre-push contract checks

Add a focused static contract test that fails unless current skill/method/templates/evals encode:

- activation and intent classification;
- both gates and their required fields;
- one-question protocol;
- all four aggregate states and exact readiness relationships;
- honest unavailable-baseline behavior;
- immutable override/bypass evidence;
- no fixed prompt-count threshold;
- output propagation requirements.

Run existing Discovery append/protocol/reference validators before merging so `main` is not knowingly broken.

### Evaluation cases

1. Production generic model wrapper: direct baseline covers the primary outcome and no durable advantage is evidenced → `blocked`.
2. Production workflow product: persistence/integration/audit advantage plus measurable oracle is evidenced → `approved`.
3. Production baseline unavailable: exact external-evidence gate; no fabricated comparison → `blocked` until evidence or override.
4. User insists after failed challenge: exact override → `user_directed_unapproved`, Planning route allowed without endorsement.
5. Learning clone: bounded learning objective and revisit trigger → `bypassed_learning`.
6. Subjective or safety-sensitive outcome: explicit human rubric and boundary, or honest `blocked` if none can be defined.
7. Ordinary scoped bug fix: full Project Discovery and both gates remain inactive.

Each qualifying case verifies real artifact content, state transitions, event-chain/receipt integrity, and representative evidence rather than response prose alone.

### Push then fresh verification

Per user instruction:

1. run only the minimum contract/protocol checks required to avoid pushing a known-broken `main`;
2. commit the implementation intentionally;
3. integrate and push `main`;
4. from the pushed `main` revision, run fresh isolated evaluation workers and independent graders;
5. write a post-push validation report with exact commands, artifact paths, scores, limitations, and revision;
6. if a fresh evaluation fails, preserve the failure, make the narrow repair in a new commit, push it, and rerun only the affected cases.

Warm or reused agents may assist diagnosis but are never labeled cold evidence.

## Acceptance criteria

- Production/commercial Discovery cannot become endorsed without both gates.
- A user can insist and proceed only through explicit `user_directed_unapproved` evidence.
- Learning/prototype bypass is bounded, applies only to product-existence justification, still requires outcome verification, and cannot silently become commercial approval.
- Every material outcome has a verifiability row or is explicitly insufficient.
- No baseline, model capability, metric, or product advantage is invented.
- Routine scoped work does not trigger the gates.
- Static tests pass before `main` push.
- Fresh evaluation and independent grading run against the pushed `main` revision.
- Final report distinguishes approved, overridden-unapproved, and bypassed outcomes without ambiguity.

## Rollback

The feature is documentation/skill/eval logic only. Roll back the dedicated implementation commit(s) if the gates over-trigger, corrupt readiness routing, or fail the post-push evaluation. Preserve the pushed failure artifacts and validation report; do not rewrite evaluation history.
