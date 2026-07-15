# Conditional System-Design Scenarios

Date: 2026-07-16  
Status: approved direction; written-spec review pending

## Goal

Extend Autonomous Planning so a large or high-risk system plan explains how the same product could evolve across Small, Medium, and Enterprise audience sizes. The comparison must cover scalability, resilience, and the other system-design concerns that materially affect architecture without forcing enterprise complexity onto ordinary small work.

## Sizing model

The requested audience bands are retained:

| Scenario | Audience-size label |
|---|---:|
| Small | fewer than 1,000 users |
| Medium | 1,000 through 10,000 users |
| Enterprise | more than 10,000 users |

`users` is a comparison label, not a capacity model. Each plan must name the metric used, such as registered users, MAU, DAU, or another evidence-backed measure. If the request does not define it, Planning records an explicit assumption instead of silently choosing a meaning.

Architecture decisions must additionally use a workload envelope: concurrent users, request/transaction rate, peak-to-average ratio, payload size, read/write mix, data volume and growth, tenant skew, geographic distribution, availability and latency SLOs, durability, RTO/RPO, compliance, and cost constraints. A system with 500 highly concurrent financial users may require stronger architecture than one with 20,000 occasional readers.

The name `Enterprise` identifies the user-requested third scenario; it does not by itself prove enterprise organizational, regulatory, or traffic requirements.

## Conditional activation

The scenario matrix activates when the user explicitly asks for system architecture, scale, resilience, or audience-tier comparison. Without an explicit request, any one of these material concerns in current Discovery/equivalent evidence also activates it:

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
| Workload and SLOs | User metric, concurrency, throughput, burst, data growth, availability, latency percentiles, correctness, durability, freshness, and error budget. |
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
- User count alone never selects a topology. The workload envelope and risk constraints choose the recommendation.
- Small may use a modular monolith and managed services when that is the simplest evidence-backed design.
- Medium introduces only the bottleneck-driven deltas justified by measured limits, such as horizontal stateless scaling, caching, queues, read replicas, or stronger operational controls.
- Enterprise does not automatically mean microservices, Kubernetes, sharding, or multi-region. Those appear only when failure isolation, independent scaling, organizational boundaries, SLOs, data locality, or measured capacity require them.
- Each transition names measurable upgrade triggers, compatibility needs, migration/backfill steps, rollback/recovery, and the decisions that should remain reversible.
- Implementation Task Contracts cover only the approved current scenario unless the execution request explicitly authorizes future-tier work.

## Review and validation

The fresh final Planning reviewer must verify:

1. conditional activation is justified and does not over-design an ordinary small task;
2. all three audience bands are present with an exact `users` metric or explicit assumption;
3. workload/SLO evidence, rather than user count alone, drives the recommendation;
4. every applicable domain is `required`, evidenced `not_applicable`, or owned/triggered `deferred`;
5. scenario deltas, upgrade triggers, migration, resilience, recovery, operations, security, and cost trade-offs are internally consistent;
6. Task Contracts implement only the authorized current scenario.

Validation will add an executable contract test for the activation, audience bands, workload envelope, disposition semantics, no-invented-numbers rule, and reviewer checks. A behavior-eval assertion will require a qualifying architecture case to emit the matrix while a narrow small-task activation case continues to skip the full pipeline.

## Rejected alternatives

- Always-on enterprise checklist: rejected because it adds noise and premature infrastructure to small, well-understood changes.
- Three complete independent plans: rejected because duplicated requirements drift; one baseline plus explicit deltas makes comparison and migration clearer.
- User-count-only architecture selection: rejected because concurrency, workload shape, data, SLOs, recovery, compliance, and cost can dominate audience size.
- Mandatory microservices or multi-region at the Enterprise label: rejected because these are costly mechanisms, not scale guarantees.
