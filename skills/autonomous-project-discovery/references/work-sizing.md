# Work Sizing and Session Cutover

## Observable unit rubric

Every Discovery packet has one primary outcome, explicit inputs, a named `decision_unlocked`, an observable completion criterion, verification, fallback, owner, disposition, and no unresolved dependency on a later unit.

| size | weight | observable boundary |
|---|---:|---|
| `Small` | 1 | One behavior or decision, one subsystem or evidence surface, direct verification. |
| `Medium` | 2 | One outcome across at most two coupled subsystems or evidence surfaces, with integration verification. |
| `Large` | invalid | Multiple primary outcomes, three or more coupled subsystems, an unknown interface, or unbounded verification. Split before dispatch. |

Only `Small`/1 and `Medium`/2 are dispatchable. Do not relabel a Large unit Medium to fit a session.

## Dependency ordering

Build an explicit dependency graph, then order packets by:

1. instruction, territory, and freshness evidence needed by later packets;
2. framing decisions that can eliminate downstream work;
3. high-impact or irreversible uncertainties before preference polish;
4. cheap falsification/research before a prototype;
5. unknown-known examples/prototypes only after meaningful alternatives can be framed;
6. readiness synthesis after all `must_resolve_before_planning` dependencies are verified.

A packet is dispatchable only when every dependency is `verified` and its assigned inputs exist. Independent read-only scouts may run concurrently only with isolated output paths and one primary acceptance packet. Never parallelize writes to shared artifacts or `AGENT-STATE.md`.

## Session budget

Set `session_budget: 6` for a normal session. Set `session_budget: 4` when `risk_mode` is `high_risk` or `ui`, including security-sensitive behavior, data changes, external integrations, destructive/irreversible risk, or preference/UI prototype gates.

Before dispatch, calculate `completed_weight + next_packet_weight`. If the result exceeds `session_budget`, do not dispatch. Write `SESSION-HANDOFF.md`; persist `continuation_kind`, `continuation_verification`, and the exact `continuation_command` value; set manual restart when the host cannot create a top-level session; and end cleanly. A command requires a harmless successful capability check; otherwise use the protocol's precise `manual_host_action`.

The budget is a ceiling, not a target. Stop earlier after the current unit when:

- host-reported context usage reaches at least 50%;
- compaction occurred;
- two remediation cycles were needed in the session;
- the next action cannot be determined from `AGENT-STATE.md` plus the current report alone;
- a human preference/UAT or external-authority gate is pending.

When telemetry is absent, record `context_telemetry: unavailable`; never estimate a hidden percentage. Artifact, packet, and weight limits still apply.

## Retry and circuit breaker

For a failed or contradictory packet:

1. Inspect the real report, evidence, commands, and output.
2. Write an evidence-backed diagnosis and identify whether the contract, environment, or approach failed.
3. Preserve useful artifacts; change one bounded variable or repair the contract.
4. Retry only when the new attempt has a falsifiable reason to succeed.
5. Independently inspect the new output before acceptance.

Allow at most two evidence-driven remediation cycles for the same packet. If it remains unverified after the second cycle, set the packet to `blocked`, record the repeated condition and recovery options, write a handoff when needed, and route to the owner or human gate. Do not retry through alternate syntax to bypass a denied operation.

## No-rushing rule

Never compress packets, lower evidence quality, omit artifact sampling, skip a dependency, accept a worker self-report, or cross a gate to fit more work into the session. A session may finish early; verification and ownership boundaries remain fixed.
