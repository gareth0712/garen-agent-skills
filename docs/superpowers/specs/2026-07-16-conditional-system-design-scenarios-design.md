# Conditional System-Design Scenarios

Date: 2026-07-16
Status: approved direction; written-spec review pending

## Goal

Extend Autonomous Planning so a large or high-risk system plan explains how the same product could evolve across Small, Medium, and Enterprise architecture profiles. The comparison must cover scalability, resilience, and the other system-design concerns that materially affect architecture without forcing enterprise complexity onto ordinary small work.

## Scenario model

There is no universal industry-standard user-count boundary for Small, Medium, or Enterprise architecture. Organization size and registered users are business descriptors; technical architecture is driven by workload, criticality, reliability, data, geography, compliance, operations, and cost. The plan therefore uses these evidence-based profiles:

| Scenario | Planning profile |
|---|---|
| Small / Baseline | Modest or not-yet-proven workload, limited operational staffing, and no evidence that strict availability, recovery, regulatory, geographic, or isolation constraints require more complex topology. |
| Medium / Growth and HA | Sustained or forecast growth plus one or more measured bottlenecks, stronger availability/recovery needs, multiple runtime instances, material asynchronous work, growing data, or an explicit on-call responsibility. |
| Enterprise / High-scale or mission-critical | One or more dominant constraints such as very high or globally distributed workload, strict SLO/RTO/RPO, critical or regulated data, strong tenant/failure isolation, complex organizational ownership, or dedicated reliability/security operations. |

User count remains one workload input, never the tier definition. Each plan names the available metric, such as registered users, MAU, DAU, or concurrent users. If it is unknown or ambiguous, Planning records an explicit assumption and validation action.

Every scenario defines or marks unknown the complete workload/risk envelope: concurrent users, request/transaction rate, peak-to-average ratio, payload size, read/write mix, data volume and growth, tenant skew, geographic distribution, availability and latency SLOs, durability, RTO/RPO, compliance, operational ownership, and cost constraints. A system with 500 highly concurrent financial users can require the Enterprise / mission-critical profile, while one with 20,000 occasional readers may remain technically simpler.

The profiles are comparison lenses, not a claim that every organization progresses through identical architecture. The plan recommends the profile whose dominant constraints match current evidence and shows the other two as bounded alternatives.

## Conditional activation

The scenario matrix activates when the user explicitly asks for system architecture, scale, resilience, or tier comparison. Without an explicit request, any one of these material concerns in current Discovery/equivalent evidence also activates it:

- multiple coupled subsystems or external integrations;
- rapid growth, burst traffic, high concurrency, large or fast-growing data;
- critical data, money movement, strict correctness, availability, latency, durability, RTO, or RPO;
- multi-tenant isolation, multi-region operation, regulated data, abuse exposure, or material vendor limits;
- non-trivial on-call, disaster-recovery, migration, or cost risk.

Otherwise Planning keeps the existing lean plan and does not manufacture three architectures.

## Planning output

The final `MASTER-PLAN.md` gains one bounded `System design scenario matrix` when activated. It keeps functional scope and core invariants constant, describes a recommended current scenario, and expresses the other scenarios as architectural deltas rather than three duplicated implementation plans.

Each scenario covers, when relevant:

| Domain | Required comparison |
|---|---|
| Workload and SLOs | User metrics, concurrency, throughput, burst, data growth, availability, latency percentiles, correctness, durability, freshness, and error budget. |
| Components and compute | Boundaries, deployment topology, stateless/stateful responsibilities, scale-up/scale-out approach, headroom, and limiting resource. |
| Data and distributed behavior | Ownership, indexing, partitioning/hot-key risk, replication, consistency, transaction boundary, ordering, deduplication, retention, and schema evolution. |
| Performance controls | Caching, batching, queues, asynchronous work, quotas, admission control, and capacity/load-test evidence. |
| Resilience | Failure domains, redundancy, timeouts, bounded retries with backoff/jitter, idempotency, circuit breakers, bulkheads, backpressure, load shedding, and graceful degradation. |
| Recovery | Backup/restore, failover/failback, RTO/RPO, reconciliation, and disaster-recovery exercise. |
| Operations | Telemetry, SLI/SLO alerts, dashboards, runbooks, ownership/on-call, deploy/canary/rollback, incident response, and debuggability. |
| Trust and lifecycle | Security, privacy, compliance, abuse prevention, accessibility/localization when applicable, compatibility, maintainability, testability, and vendor lock-in. |
| Cost and evolution | Main cost drivers, expected cost curve, service/vendor limits, upgrade triggers, reversible decisions, and migration path to the next scenario. |

Every applicable domain receives one disposition:

- `required`: supported by current evidence or an explicit assumption and included in the plan;
- `not_applicable`: includes bounded evidence explaining why;
- `deferred`: names the owner, validation action, measurable trigger, and decision deadline.

Unknown values remain assumptions with a falsification method and threshold. Planning must not invent precise traffic, SLO, capacity, or cost numbers.

## Architecture rules

- The three scenarios compare the same product and safety requirements; they are not permission to weaken correctness, security, privacy, or recovery at smaller size.
- No universal numeric threshold selects a topology. The workload/risk envelope and dominant constraints choose the recommendation.
- Small may use a modular monolith and managed services when that is the simplest evidence-backed design.
- Medium introduces only the bottleneck-driven deltas justified by measured limits, such as horizontal stateless scaling, caching, queues, read replicas, or stronger operational controls.
- Enterprise does not automatically mean microservices, Kubernetes, sharding, or multi-region. Those appear only when failure isolation, independent scaling, organizational boundaries, SLOs, data locality, or measured capacity require them.
- Each transition names measurable upgrade triggers, compatibility needs, migration/backfill steps, rollback/recovery, and the decisions that should remain reversible.
- Implementation Task Contracts cover only the approved current scenario unless the execution request explicitly authorizes future-tier work.

## Review and validation

The fresh final Planning reviewer must verify:

1. conditional activation is justified and does not over-design an ordinary small task;
2. all three architecture profiles are present, and available user metrics are defined or explicitly unknown;
3. dominant workload, SLO, recovery, data, compliance, operations, and cost evidence drives the recommendation;
4. every applicable domain is `required`, evidenced `not_applicable`, or owned/triggered `deferred`;
5. scenario deltas, upgrade triggers, migration, resilience, recovery, operations, security, and cost trade-offs are internally consistent;
6. Task Contracts implement only the authorized current scenario.

Validation will add an executable contract test for activation, the three evidence-based profiles, workload/risk envelope, disposition semantics, no-universal-threshold and no-invented-numbers rules, and reviewer checks. A behavior-eval assertion will require a qualifying architecture case to emit the matrix while a narrow small-task activation case continues to skip the full pipeline.

## Rejected alternatives

- Always-on enterprise checklist: rejected because it adds noise and premature infrastructure to small, well-understood changes.
- Three complete independent plans: rejected because duplicated requirements drift; one baseline plus explicit deltas makes comparison and migration clearer.
- Fixed user-count bands or user-count-only architecture selection: rejected because concurrency, workload shape, data, SLOs, recovery, compliance, operations, and cost can dominate audience size.
- Mandatory microservices or multi-region at the Enterprise label: rejected because these are costly mechanisms, not scale guarantees.
