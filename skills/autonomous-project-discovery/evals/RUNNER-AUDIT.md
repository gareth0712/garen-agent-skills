# Runner-owned Discovery eval audit

`run_audit.py` is a reproducible eval-harness observer. It is not part of a Discovery run's production control plane and does not replace `AGENT-STATE.md` or production `EVENTS.jsonl`.

## Isolation contract

- Start the observer before the cold-start executor.
- Put `--output-root` inside the evaluated Git repository/worktree.
- Put `--audit-dir` inside that repository/worktree but outside `--output-root`; use a sibling such as `with_skill/run-1/runner-audit/`.
- Put `--stop-file` directly inside `--audit-dir`.
- Put `--control-file` directly inside `--audit-dir`, or omit it to use `runner-control.jsonl` there.
- Do not expose the audit directory, control file, or stop file to the executor as an input, output, report, or evidence path. The executor must neither read nor cite runner-owned artifacts. Only the parent eval runner writes control requests.
- Use a fresh audit directory for every run. The observer truncates `runner-audit.jsonl` at startup and is not a concurrent multi-run service.

## Invocation and finalization

From a clean checkout, use the active Python 3 interpreter:

```text
python skills/autonomous-project-discovery/evals/run_audit.py --repo <absolute-repository-or-worktree> --output-root <absolute-assigned-output-root> --audit-dir <absolute-sibling-runner-audit-dir> --stop-file <absolute-sibling-runner-audit-dir>/STOP --control-file <absolute-sibling-runner-audit-dir>/runner-control.jsonl --poll-ms 100
```

1. Launch the command as a separate process and wait until `runner-audit.jsonl` contains `runner_started`.
2. Run exactly one cold-start eval executor. Allow at least one polling interval between lifecycle writes when strict ordering is an assertion.
3. After the executor exits and its output writes are flushed, append runner-owned sample and verification requests to the control file as described below. Wait for each corresponding audit event; production `EVENTS.jsonl` cannot satisfy these requests.
4. Create the stop file only after the required runner verification requests were accepted (or after recording that they failed). Requests appended after the stop file are outside the contract.
5. Wait for the observer process to exit successfully. A run is finalized only when `summary.json` exists and the last JSONL event is `runner_finalized` with the summary hash.
6. Preserve the audit directory beside the eval outputs for grading. A missing/failed observer is an eval-harness failure, not evidence that the skill passed.

The observer refuses an output root outside the repository, an audit directory outside the repository or inside the output root, a stop/control file outside the audit directory, a control file that aliases the stop file, a stale non-empty control file, and polling intervals below 20 ms.

## Runner-owned control interface

`runner-control.jsonl` is an append-only request channel owned by the parent eval runner. Start with an absent or empty file. Append one complete newline-terminated JSON object at a time, then wait for the requested terminal event in `runner-audit.jsonl` before appending a dependent request.

To ask the observer itself to open and hash specific output artifacts:

```json
{"request_id":"sample-D-001","action":"sample","packet_id":"D-001","paths":["reports/D-001-report.md","evidence/D-001/result.txt"]}
```

Every path must be a relative, existing regular file physically contained by the assigned output root. The observer requires a matching, earlier filesystem write observation with the same SHA-256. Success emits one `runner_artifact_sampled` event per path followed by `runner_sample_completed` with a manifest hash. Invalid, missing, escaped, duplicated, or unobserved paths emit `runner_control_rejected` and no completed sample.

After a completed sample, request runner verification:

```json
{"request_id":"verify-D-001","action":"verify","packet_id":"D-001","sample_request_id":"sample-D-001"}
```

The observer accepts this request only when the referenced completed sample contains that packet's worker report and worker evidence, and the independently observed order is report write < evidence write < sample completion < verification request. Success emits `runner_verification_accepted`; a missing sample, packet mismatch, incomplete sample, or reversed order emits `runner_control_rejected`. Request IDs must be unique. The control file and resulting audit events are runner-owned evidence; they are not production artifacts and must remain undisclosed to the executor.

## Schema and evidence boundary

`runner-audit.jsonl` is append-only runner evidence. Each line has monotonically increasing `event_seq`, an ISO-8601 `timestamp`, `event_type`, and event-specific fields. File events include the output-relative path, absolute observed path, SHA-256, size, filesystem modification time, role, and inferred packet ID. Files under `gates/` use the neutral role `canonical_gate`; the audit does not relabel operational or external gates as human gates.

Production `EVENTS.jsonl` lines are copied only as hashed cross-check observations. For each source stream, the observer separately validates append-only history, strictly increasing positive integer `event_seq` values, present timezone-aware ISO-8601 timestamps in increasing order, and references. Every supplied reference must resolve to an existing regular file inside the assigned output root and carry either a matching SHA-256 or a Git revision whose referenced blob matches the observed file. Sampling/verified claims require at least one reference. Rewriting or truncating an observed prefix, or supplying an invalid sequence, timestamp, path, hash, revision, or empty required references, remains visible under `production_cross_checks`, but never creates runner sampling or verification events.

`summary.json` has `schema: runner-audit-v1` and records:

- initial/final Git HEAD, tracked status, and nonignored untracked paths;
- whether tracked HEAD/status remained unchanged;
- final files under the assigned output root and new nonignored paths outside it;
- production-code candidates under the assigned output root;
- per-packet lifecycle event sequence numbers, `strictly_ordered`, and whether post-write containment preceded sampling;
- per-file and per-claim production cross-check validity, resolved reference hashes, and validation errors;
- exact observed and `unaudited` channels plus the clean-claim boundary.

Strict lifecycle order means the runner independently observed and hashed worker report creation before worker evidence creation, then the parent runner requested an observer-owned sample and a dependent verification in that order. It is false when either runner request is missing, rejected, or out of order. Orchestrator-owned preflight and path-containment evidence have distinct roles and cannot masquerade as worker evidence. Production sampling/verification remain cross-checks only. Graders must not promote those cross-checks into stronger claims, and must keep network, remote services, out-of-repository writes, ignored paths outside assigned roots, credential stores, publishing, deployment, messaging, purchases, external processes, and host-private tool activity labeled `unaudited`.

## Automated smoke test

Run:

```text
python skills/autonomous-project-discovery/evals/test_run_audit.py
```

The behavioral test creates temporary real Git repositories and proves both failure and success paths. It checks that all nine canonical gate types receive the neutral role; valid or invalid production-only claims cannot pass; reversed source sequence, missing timestamp, empty references, and unhashed references are invalid cross-checks; a runner sample without runner verification remains false; premature verification is rejected; and valid runner sample/verification control produces `strictly_ordered: true`. It also preserves the original isolation, schema, hash, monotonic audit event, clean tracked state, unaudited-channel, and containment-before-sampling checks. Temporary repositories are removed automatically without writing Python bytecode into the skill package.
