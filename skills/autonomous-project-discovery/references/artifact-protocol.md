# Autonomous Artifacts Protocol

## Identifier and scope

Use `protocol_version: autonomous-artifacts-v2` for Discovery, Planning, and Implementation runs. Each skill vendors this protocol so it remains usable alone. Durable artifacts are the source of truth; conversation summaries and worker completion messages are claims until reconciled with files and repository evidence.

## Canonical run root

Use the project's established planning location. When none exists, create:

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

Append `-2`, `-3`, and so on if the computed run root already exists. Artifacts use portable forward-slash paths even when the active shell needs different quoting.

## Single-writer control plane

`AGENT-STATE.md` is the only control-plane index, and only the top-level orchestrator writes it. Workers write only their assigned packet output, report, and evidence paths. A worker must never set its own packet status or edit another worker's artifact.

The state records at minimum:

- protocol version, workflow type, active pipeline stage, run ID, repository root, and run root;
- harness, discovered capabilities, unavailable capabilities, and fallback behavior;
- requested/effective orchestrator and worker models plus fallback reasons;
- baseline Git SHA and pre-existing dirty paths when Git exists;
- `SCOPE.md`, stop-boundary, and stage-artifact paths;
- Discovery, Planning, and Implementation readiness values;
- artifact revisions, source revisions, freshness evidence, `derived_from`, and `supersedes` links;
- packet table, dependency, status, report, evidence, requested/effective model, and fallback reason;
- `session_budget`, `completed_weight`, retry counters, risk mode, context telemetry, and UAT state;
- next stage, next action, exact `continuation_command`, and whether restart is manual.

Packet statuses are exactly `pending`, `in_progress`, `verified`, `blocked`, or `superseded`.

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

## Report-before-state acceptance ordering

Use this order for every packet or stage:

1. The orchestrator writes the packet and sets status to `in_progress`.
2. The worker performs only authorized work and writes its reusable report.
3. The worker writes or cites bounded evidence under the assigned evidence path.
4. The worker returns at most ten lines pointing to the report and evidence.
5. The orchestrator opens the report and representative artifacts, checks cited paths, and reruns a relevant verification when possible.
6. Only after successful inspection may the orchestrator set status to `verified` and update derived artifacts.

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
4. Downgrade any unsupported `verified` claim and record the contradiction.
5. Recompute remaining session budget from verified packet weights.
6. Choose the next action from evidence and rewrite state only as the orchestrator.

`continuation_command` is an exact, safely quoted command or host action that names the skill, run root, and next action. If the host cannot create a new top-level session, write the command, set `restart_mode: manual`, and end cleanly. Never claim unattended continuation when a person must start the next session or answer a preference/UAT gate.
