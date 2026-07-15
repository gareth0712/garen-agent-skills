# Planning Method

## Ownership boundary

Planning converts current product framing into executable system design. It owns architecture, component boundaries, interfaces, data models, workflows, sequencing, migration, deployment, observability, testing, verification, rollback, and implementation Task Contracts. Discovery owns the problem, users, outcomes, scope, non-goals, hard constraints, primary journeys, acceptance intent, and framing-changing uncertainty. Implementation owns product changes within a current contract.

Do not repeat Discovery wholesale. Apply a narrow field-level sufficiency/freshness gate, preserve accepted framing verbatim where possible, and route only a concrete framing defect backward. Do not write product code or leave architecture-changing decisions to Implementation.

## Discovery sufficiency and freshness

Accept `DISCOVERY.md` or a differently named equivalent only when its content supplies:

- users/stakeholders, underlying problem, desired outcomes, and why the initiative exists;
- bounded scope, non-goals, stop boundary, authority, and hard constraints;
- primary journeys and acceptance intent;
- facts versus assumptions/proposals, dangerous assumptions, and rejected framing where material;
- residual unknowns with owners and allowed downstream dispositions;
- stable artifact revision, source/repository revision, `derived_from`/supersession lineage, and reproducible freshness evidence.

Map equivalent fields explicitly. A name match without content is insufficient; a content match with current lineage is valid. Compare recorded revisions with current Git/filesystem/reference evidence and inspect known contradiction paths plus pre-existing dirty changes.

Classify the result:

- `CURRENT`: all Planning-entry framing is sufficient and current.
- `INSUFFICIENT`: a product/framing-owned decision required for design is absent.
- `STALE`: current evidence contradicts a product/framing-owned decision.

`INSUFFICIENT` and `STALE` route only the affected scope to Discovery with the missing field or contradiction, owner, and evidence. An architecture, interface, data, workflow, sequencing, migration, deployment, or verification gap in otherwise current framing stays in Planning.

## Evidence before architecture

Read every applicable `AGENTS.md` and `CLAUDE.md`, then inspect only the repository surfaces needed for the decision being planned. High-signal surfaces may include existing architecture docs, code boundaries, API schemas, database schema/migrations, authentication and authorization, background jobs, tests, package/build configuration, deployment/rollback mechanisms, observability, feature flags, and current dirty paths.

Every design claim is one of:

- evidence-backed fact with path/revision;
- bounded inference with confidence;
- proposal with decision owner;
- assumption with owner, validation signal, and effect if false;
- unavailable evidence with a route and readiness impact.

Do not invent a stack, convention, service, environment, or capability because it is common. Do not postpone all repository inspection to an implementation “Stage 0” while declaring the plan complete.

## Planning-specific decision ledger

Classify each unresolved Planning decision by impact, reversibility, evidence, confidence, urgency, and owner:

- Low-impact and easily reversible: Planning may decide and record it.
- Medium-impact but reversible: Planning may decide only when current Discovery/scope delegates that authority; otherwise propose bounded alternatives.
- High-impact, security/legal-sensitive, public, expensive, destructive, user-facing, or difficult to reverse: require explicit approval unless current framing grants that exact authority.
- Framing-changing: route to Discovery.
- Local reversible implementation detail inside a complete contract: delegate explicitly to Implementation.

Every retained decision names its resolution deadline: `before_plan_review`, `before_implementation`, `implementation_may_decide`, `human_gate`, or `defer`. Vague “TBD” entries are invalid.

## Coverage ledger

For the requested scope, decide whether each surface is `required`, `not_applicable` with reason, or `blocked` with owner:

| surface | required planning output |
|---|---|
| Architecture | Components, responsibilities, boundaries, dependency direction, and rejected alternatives. |
| Interfaces | API/event/job/file contracts, error semantics, idempotency, compatibility/versioning, and ownership. |
| Data | Entities, invariants, lifecycle, access/retention, consistency, indexing/performance assumptions, and recovery. |
| Workflows | User/system flows, degraded paths, retries, authorization, and operational ownership. |
| Migration | Schema/data/config transition, backfill, compatibility window, rollback/recovery, and validation. |
| Testing | Unit/integration/contract/e2e or other relevant levels tied to risks and acceptance intent. |
| Verification | Exact commands, observable outputs, artifact sampling, and at least one representative affected flow where relevant. |
| Deployment | Environments, ordering, feature flags/canary when available, observability, rollback trigger, and owner. |
| Cross-cutting | Security, privacy, accessibility, reliability, performance, cost, telemetry, and compliance when relevant. |

Do not add irrelevant ceremony. `not_applicable` requires a brief evidence-based reason; omission is not the same as not applicable.

## Packet design

Each `P-###` packet has one primary Planning outcome, current inputs, dependencies, Small/1 or Medium/2 size, decision authority, observable completion, verification, fallback, and no unresolved dependency on a later packet. Split a unit when it has multiple outcomes, three or more coupled subsystems, an unknown interface, or unbounded verification.

Planning packets are sequential. A worker writes only its assigned report/evidence and bounded scratch output; the orchestrator accepts the result and updates shared artifacts. Independent final review is its own packet after synthesis, not an author self-check disguised as independence.

## Exact implementation Task Contracts

Every implementation stage in `MASTER-PLAN.md` uses this contract:

1. `Stage ID and title`
2. `Goal` — one observable primary outcome.
3. `Inputs and freshness` — upstream revisions, instruction paths, required files/surfaces.
4. `Dependencies` — verified prior stages and external prerequisites.
5. `In scope / Out of scope` — explicit boundaries.
6. `Owned changes` — expected product/test/docs/migration surfaces; not permission to touch unrelated files.
7. `Allowed side effects` — exact filesystem, database, network, deployment, messaging, or external effects authorized for this stage. Default external, irreversible, destructive, live-data, and public effects to `none/not_authorized` unless the contract cites current exact authority. Owned paths do not imply side-effect authority.
8. `Decision authority` — exact local choices Implementation may make and choices that route backward or require approval.
9. `Implementation constraints` — interface/data/security/compatibility invariants.
10. `Verification` — reproducible commands/reads/UI observations, expected signals, representative real flow, and evidence paths.
11. `Fallback / rollback` — safe checkpoint and recovery signal; no destructive reset of unrelated work.
12. `UAT and external gates` — `[UI]` or `[non-UI]`, human acceptance criteria, credentials/external state, and whether each gate is required before Implementation starts or only before a named downstream stage may complete.
13. `Completion and stop` — objective acceptance and when not to continue.

Stages must be Small/1 or Medium/2 under the implementation sizing rubric. If a contract cannot be verified independently or has multiple primary outcomes, split it before readiness.

## Execution approval semantics

Technical readiness and execution approval answer different questions. `planning_readiness` says whether the design is complete and current; `planning_approval_state` says whether a named authority currently permits Implementation to execute the exact plan revision, bounded scope, stop boundary, and side effects.

Use exactly these states:

- `not_requested`: the user requested Planning only. Do not open an approval gate merely to finish a planning-only request, and do not route to Implementation.
- `delegated_execution_authority`: the same current request explicitly included execution, its durable request/scope artifact names the granting authority, and the final Task Contracts do not exceed that bounded scope or side-effect authority.
- `approval_required`: execution is requested but authority is absent, ambiguous, stale, or narrower than the exact plan/side effects. Open one canonical pre-Implementation `authority`, `product_decision`, or `security_legal` gate as appropriate.
- `explicitly_approved`: the named authority resolved that gate for the exact current plan revision, execution scope, stop boundary, and side effects.

Persist one exact mapping in state, `MASTER-PLAN.md`, and handoff:

```yaml
planning_approval_state: not_requested | delegated_execution_authority | approval_required | explicitly_approved
planning_approval_evidence:
  path: SCOPE.md | durable request artifact | gates/G-###.md | none
  revision: stable revision/digest | none
  authority: named user/role | none
```

For delegated authority, `SCOPE.md` or a cited durable request artifact preserves a bounded record of the execution request, authority, covered stage scope/stop boundary, and exact side-effect ceiling. For explicit approval, the gate preserves the accepted plan revision and the same boundaries. The independent reviewer verifies the mapping but cannot grant it. The Planning orchestrator cannot approve its own plan by marking it ready.

The mapping is current only when the evidence exists, its revision is reproducible, its authority is named, and it covers the exact current planning revision and every Task Contract side effect. A superseding plan or changed scope/authority/side effect invalidates the mapping; set `approval_required` when execution remains requested, otherwise `not_requested`. Never infer approval from silence, plan readiness, review PASS, an old checkbox, or worker `done`.

## Independent plan review

Use a fresh worker that did not author the full plan. It checks:

- alignment with accepted Discovery framing and authority;
- current repository evidence and explicit unavailable evidence;
- architecture/interface/data/workflow consistency;
- dependency order, stage size, migration/rollback/deployment safety;
- testing and representative-flow verification coverage;
- Task Contract completeness and implementability without chat history;
- unresolved decision owners, human/external gates, and scope leakage;
- absence of product-code changes.

Classify findings `CRITICAL`, `IMPORTANT`, or `MINOR`. Dispositions are `open`, `verified_repair`, `routed`, or `accepted_risk`. A CRITICAL finding closes only through `verified_repair` or `routed` to the owning stage with durable evidence; it can never use `accepted_risk`. Any `accepted_risk` requires named authority and explicit readiness impact. A critical Planning-owned finding becomes a bounded repair packet; a framing finding routes to Discovery. `planning_readiness: ready` requires zero unresolved critical findings and explicit evidence-backed disposition of important findings.

## Readiness

`planning_readiness: ready` requires a current accepted Discovery source, current repository evidence, resolved/delegated Planning decisions, complete relevant coverage, Small/Medium implementation contracts, independent review, and no unresolved critical finding. `not_ready` names the packet/gate/finding that blocks execution. `stale` names newer evidence that contradicts a Planning-owned decision.

`implementation_readiness: ready` additionally requires that the requested execution scope is represented by current exact Task Contracts and every gate required before Implementation starts is resolved. Correctly owned downstream UI UAT or external gates may remain scheduled in their exact Task Contracts without blocking start; they block only crossing the named later stage boundary. Persist these separately as `pre_implementation_blocking_gates` and `scheduled_downstream_gates`. Readiness does not mean zero uncertainty; it means uncertainty has an explicit owner, authority, deadline, and route.

Route to Implementation only when `planning_approval_state` is `delegated_execution_authority` or `explicitly_approved` and the three approval-evidence fields are current. `not_requested` stops after Planning. `approval_required` keeps the canonical approval gate in `pre_implementation_blocking_gates` and prevents Implementation start. Do not change `planning_readiness` merely because a planning-only run is not approved for execution; preserve the separate dimensions.
