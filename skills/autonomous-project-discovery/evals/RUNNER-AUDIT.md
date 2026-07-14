# Runner-owned Discovery eval audit

`run_audit.py` is a reproducible eval-harness observer. It is not part of a Discovery run's production control plane and does not replace `AGENT-STATE.md` or production `EVENTS.jsonl`.

## Isolation contract

- Start the observer before the cold-start executor.
- Put `--output-root` inside the evaluated Git repository/worktree.
- Put `--audit-dir` inside that repository/worktree but outside `--output-root`; use a sibling such as `with_skill/run-1/runner-audit/`.
- Put `--stop-file` directly inside `--audit-dir`.
- Do not expose the audit directory or stop file to the executor as an input, output, report, or evidence path. The executor must neither read nor cite runner-owned artifacts.
- Use a fresh audit directory for every run. The observer truncates `runner-audit.jsonl` at startup and is not a concurrent multi-run service.

## Invocation and finalization

From a clean checkout, use the active Python 3 interpreter:

```text
python skills/autonomous-project-discovery/evals/run_audit.py --repo <absolute-repository-or-worktree> --output-root <absolute-assigned-output-root> --audit-dir <absolute-sibling-runner-audit-dir> --stop-file <absolute-sibling-runner-audit-dir>/STOP --poll-ms 100
```

1. Launch the command as a separate process and wait until `runner-audit.jsonl` contains `runner_started`.
2. Run exactly one cold-start eval executor. Allow at least one polling interval between lifecycle writes when strict ordering is an assertion.
3. After the executor exits and its output writes are flushed, create the stop file.
4. Wait for the observer process to exit successfully. A run is finalized only when `summary.json` exists and the last JSONL event is `runner_finalized` with the summary hash.
5. Preserve the audit directory beside the eval outputs for grading. A missing/failed observer is an eval-harness failure, not evidence that the skill passed.

The observer refuses an output root outside the repository, an audit directory outside the repository or inside the output root, a stop file outside the audit directory, and polling intervals below 20 ms.

## Schema and evidence boundary

`runner-audit.jsonl` is append-only runner evidence. Each line has monotonically increasing `event_seq`, an ISO-8601 `timestamp`, `event_type`, and event-specific fields. File events include the output-relative path, absolute observed path, SHA-256, size, filesystem modification time, role, and inferred packet ID. Production `EVENTS.jsonl` lines are copied only as hashed cross-check observations; they are not treated as independent filesystem/read tracing.

`summary.json` has `schema: runner-audit-v1` and records:

- initial/final Git HEAD, tracked status, and nonignored untracked paths;
- whether tracked HEAD/status remained unchanged;
- final files under the assigned output root and new nonignored paths outside it;
- production-code candidates under the assigned output root;
- per-packet lifecycle event sequence numbers, `strictly_ordered`, and whether post-write containment preceded sampling;
- exact observed and `unaudited` channels plus the clean-claim boundary.

Strict lifecycle order means the runner independently observed and hashed worker report creation before worker evidence creation, then observed production sampling and verified events in that order. Orchestrator-owned preflight and path-containment evidence have distinct roles and cannot masquerade as worker evidence. Sampling/verification remain production-event cross-checks because this portable observer does not trace OS reads or private host actions. Graders must not promote those cross-checks into stronger claims, and must keep network, remote services, out-of-repository writes, ignored paths outside assigned roots, credential stores, publishing, deployment, messaging, purchases, external processes, and host-private tool activity labeled `unaudited`.

## Automated smoke test

Run:

```text
python skills/autonomous-project-discovery/evals/test_run_audit.py
```

The test creates a temporary real Git repository, starts the observer, verifies that an audit directory inside the assigned output is rejected, emits preflight/report/evidence/post-write-containment/sampling/verified lifecycle events, requests finalization, and validates role separation, schema, hashes, isolation, monotonic events, clean tracked state, explicit unaudited channels, containment-before-sampling, and `strictly_ordered: true`. The temporary repository is removed automatically.
