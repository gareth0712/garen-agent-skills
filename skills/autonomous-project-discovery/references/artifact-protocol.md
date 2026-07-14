# Autonomous Artifacts Protocol

## Identifier and scope

Use `protocol_version: autonomous-artifacts-v2` for Discovery, Planning, and Implementation runs. Each skill vendors this protocol so it remains usable alone. Durable artifacts are the source of truth; conversation summaries and worker completion messages are claims until reconciled with files and repository evidence.

## Canonical run root

Use the project's established planning location. When none exists, create:

```text
docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/
├── AGENT-STATE.md
├── EVENTS.jsonl
├── SCOPE.md
├── DISCOVERY.md
├── MASTER-PLAN.md
├── IMPLEMENTATION-NOTES.md
├── gates/
│   └── G-###.md
├── packets/
│   └── D-001.md, P-001.md, or I-001.md
├── reports/
│   └── D-001-report.md, P-001-report.md, or I-001-report.md
├── evidence/
└── SESSION-HANDOFF.md
```

Append `-2`, `-3`, and so on if the computed run root already exists. Artifacts use portable forward-slash paths even when the active shell needs different quoting.

## Single-writer control plane

`AGENT-STATE.md` is the sole authoritative control-plane index, and only the top-level orchestrator writes it. `EVENTS.jsonl` is bounded audit evidence, not a second state index; only the top-level orchestrator appends it. Workers write only their assigned packet output, report, and evidence paths. A worker must never set its own packet status, append events, or edit another worker's artifact.

The state records at minimum:

- protocol version, workflow type, active pipeline stage, run ID, absolute repository/worktree roots, and the portable run-root path;
- harness, discovered capabilities, unavailable capabilities, and fallback behavior;
- requested/effective orchestrator and worker models plus fallback reasons;
- baseline Git SHA and pre-existing dirty paths when Git exists;
- `SCOPE.md`, stop-boundary, and stage-artifact paths;
- Discovery, Planning, and Implementation readiness values;
- artifact revisions, source revisions, freshness evidence, `derived_from`, and `supersedes` links;
- packet table, dependency, status, report, evidence, requested/effective model, and fallback reason;
- `session_budget`, `completed_weight`, retry counters, risk mode, context telemetry, and UAT state;
- next stage, next action, `continuation_kind`, `continuation_verification`, exact `continuation_command` value, and whether restart is manual.

Packet statuses are exactly `pending`, `in_progress`, `verified`, `blocked`, or `superseded`.

## Readiness semantics

`discovery_readiness` is the current Discovery artifact's handoff/entry readiness for Planning. Derive the exact `DISCOVERY.md` summary line from it: `ready` maps to `Planning readiness: READY`; `not_ready` and `stale` map to `Planning readiness: NOT_READY`.

`planning_readiness` is different: it describes an actual Planning artifact's readiness for its downstream stage. Keep it `not_assessed` until a Planning artifact exists. Protocol v2 retains both shared field names; do not use `planning_readiness` as a synonym for Discovery handoff readiness.

## Artifact lineage and freshness

Every stage artifact declares a stable revision identifier, the repository/reference revisions it inspected, its upstream `derived_from` revision, freshness evidence, creation/update time, and any revision it supersedes. A content digest, Git SHA, or explicit revision string is acceptable when reproducible.

Before consuming an upstream artifact:

1. Confirm the path exists and the artifact has the required decisions, not merely the expected filename.
2. Compare recorded repository/reference revisions with current evidence.
3. Inspect known contradiction paths and pre-existing dirty changes.
4. Mark the artifact stale when current evidence changes a decision owned by that stage.
5. Preserve the contradiction and supersession link; route to the owning stage.

A framing contradiction routes to Discovery. An architecture, interface, data, sequencing, migration, or verification contradiction routes to Planning. A local reversible choice inside a current contract remains with Implementation.

Equivalent non-canonical artifacts may be consumed only when their content satisfies the required fields and freshness checks. Record the equivalent source path and mapped revision.

## Absolute worker dispatch anchors

Portable forward-slash paths remain canonical references inside state, packet, report, and gate artifacts. Before dispatch, resolve the filesystem targets and include these absolute anchors in the worker contract:

- `repository_root`
- `worktree_root`
- `run_root`
- `working_directory`
- `input_paths`
- `output_paths`
- `report_path`
- `evidence_paths`

Never rely on a relative path when a worktree, nested worker, or patch/shell tool may use a different base. Before its first write, the worker normalizes every anchor, resolves every assigned write parent, and proves each parent is the absolute `run_root` or a descendant. A mismatch blocks the packet before any write. After work, the worker inventories its assigned root and checks the scoped repository/worktree surfaces for out-of-root changes; any contradiction is evidence for `blocked`, not a path to normalize after the fact.

## Pre-dispatch blocking

Preflight required inputs, capabilities, authority, dependencies, and all absolute path anchors before invoking `spawn_worker`. When a required item is missing:

1. Do not dispatch a worker.
2. Set the packet to `blocked`; leave `completed_weight` unchanged.
3. Set `effective_model: not_executed` and a non-empty block/fallback reason. `not_executed` is valid only when no worker ran.
4. Set the report field to `none_not_dispatched`; do not create a worker report.
5. Write bounded orchestrator-owned preflight evidence under the packet evidence root and open canonical `gates/G-###.md`.
6. Append packet-status, `preflight_blocked`, and `gate_opened` events.

A worker report is valid only after a worker actually ran. Orchestrator preflight evidence must not imitate the reusable worker-report schema.

## Durable lifecycle audit

`EVENTS.jsonl` is a bounded append-only audit artifact. Each line is one JSON object with a monotonically increasing `event_seq`, ISO-8601 `timestamp`, `event_type`, `stage`, optional `packet_id`, `from_status`, `to_status`, `actor`, referenced paths with available hashes/revisions, and a bounded `evidence_summary`. The top-level orchestrator is the only writer. Never include secrets, chain-of-thought, transcripts, or raw/unbounded logs.

Append events for: `run_initialized`; `packet_created`; every `packet_status_transition`; `preflight_blocked`; `worker_dispatched`; `report_observed`; `evidence_observed`; `artifact_sampled`; `packet_verified`; `gate_opened`; `gate_resolved`; `handoff_written`; `stage_routed`; and `reconciliation_contradiction`.

A transition to `verified` is invalid unless earlier events for that packet record an existing report, existing evidence, and orchestrator artifact sampling. During recovery, reconcile state, files, and events. Downgrade unsupported `verified` status in `AGENT-STATE.md` and append `reconciliation_contradiction` with bounded references; never rewrite earlier event lines. This production log strengthens resumable handoff, but it does not replace runner-owned audit evidence required by evaluations.

## Report-before-state acceptance ordering

Use this order for every packet or stage:

1. After preflight passes, the orchestrator writes the packet, appends creation/status events, and sets status to `in_progress`.
2. The worker performs only authorized work and writes its reusable report.
3. The worker writes or cites bounded evidence under the assigned evidence path.
4. The worker returns at most ten lines pointing to the report and evidence.
5. The orchestrator opens the report and representative artifacts, checks cited paths, and reruns a relevant verification when possible.
6. The orchestrator appends report-observation, evidence-observation, and artifact-sampling events.
7. Only after successful inspection may the orchestrator set status to `verified`, append the verified transition, and update derived artifacts.

If the report is absent, required evidence is absent, an evidence path does not exist, or inspection contradicts the report, status cannot be `verified`. Use `blocked` or keep `in_progress` while bounded remediation remains.

## Reusable report content

Each worker report preserves:

- verdict and primary outcome;
- conclusions and decisions unlocked;
- assumptions and unresolved questions with owners;
- source paths, source revisions, and relevant excerpts;
- commands and bounded relevant output excerpts;
- created/changed files and intentionally untouched paths;
- failures, retry count, and fallback used;
- verification evidence paths and observed signals;
- recommended next action and route.

Reports store work products and evidence, not private reasoning. Never request or persist chain-of-thought, secrets, credentials, tokens, full transcripts, or unbounded raw logs. Redact sensitive values. Keep large raw output outside Git when possible; cite a reproducible command, bounded redacted excerpt, and storage/disposal location.

## Worker return contract

The worker's chat return is at most ten lines and contains only:

1. verdict: `PASS`, `FAIL`, `BLOCKED`, or the packet-specific readiness value;
2. report path;
3. evidence paths;
4. created/changed paths;
5. one-line verification summary;
6. one-line blocker or next-action summary when applicable.

The return never substitutes for the report and never contains chain-of-thought or a full log.

## Compaction, resumption, and handoff

After compaction, interruption, or handoff, treat conversation summaries as unverified. Before dispatching another worker:

1. Read `AGENT-STATE.md`, `SCOPE.md`, the current stage artifact, active packet, packet report, and `SESSION-HANDOFF.md` when present.
2. Reconcile packet statuses with actual report/evidence files.
3. Recheck Git/filesystem state, artifact lineage, and freshness evidence.
4. Downgrade any unsupported `verified` claim and append a `reconciliation_contradiction` event.
5. Recompute remaining session budget from verified packet weights.
6. Choose the next action from evidence and rewrite state only as the orchestrator.

Persist `continuation_kind: verified_command | manual_host_action`, `continuation_verification`, and the exact continuation value in the existing `continuation_command` field. Use `verified_command` only after a harmless capability check proves both the executable and invocation form; cite the check and observed signal in `continuation_verification`. Otherwise use `manual_host_action` and write precise natural language naming the skill, absolute run root, files to read first, required gate input, and next action. Set `restart_mode: manual` when the host cannot create a new top-level session. Never invent CLI syntax or claim unattended continuation when a person must restart or answer a preference/UAT gate.
