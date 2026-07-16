# Autonomous Orchestration Validation

Date: 2026-07-17 (Asia/Tokyo)
Branch: `codex/autonomous-orchestration-skills`
Pinned source: `HEAD == origin/main == 630c2cef90cdbec14ef3c2cab688f4587a29aeb4`
Verdict: `PASS_WITH_DOCUMENTED_EVAL_LIMITATIONS`

## Scope and final responsibility verdict

The three packages remain independently installable and use one shared `autonomous-artifacts-v2` protocol. Ownership is coherent:

| Concern | Owner | Consumer / route | Verdict |
|---|---|---|---|
| Users, outcomes, scope, non-goals, journeys, acceptance intent | Discovery | Planning and Implementation consume; framing contradictions route backward | clear |
| Architecture, interfaces, data/workflows, migration/deployment, verification design | Planning | Implementation consumes exact current Task Contracts | clear |
| Product/test/docs/migration writes inside approved contracts | Implementation | Discovery/Planning forbid product writes | clear |
| Exact Task Contracts and side-effect authority | Planning emits | Implementation verifies and enforces | clear |
| Repository/dirty evidence | each stage at its boundary | repeated checks are safety gates, not ownership duplication | clear |
| UI automatic proof and exact-build human UAT | Implementation | Planning schedules timing/criteria/boundary | clear |
| Backward routing | current owner | Implementation routes framing to Discovery and contract/design to Planning | clear |

The independent static rereview in `.superpowers/sdd/task-8-integration-fix-rereview.md` is `PASS_STATIC` with Critical 0 / Important 0 / Minor 0. It verified closure of the Planning approval producer/Implementation consumer contract, the missing-plan negative activation boundary, and atomic Discovery offline routing.

The final independent review initially found one Important citation defect and one Minor selected-grade metadata omission. After two citation-correction cycles, fresh closure session `189fcf41-9a0c-4ee2-84fe-fb713411bcc4` verified exact Planning citations `:55`, `:121`, `:147-154`, and `:158-166`; final verdict is PASS with Critical 0 / Important 0 / Minor 0. The eval-2 selected grading copy now self-identifies its source eval/run without changing score or evidence.

## Executed validation

All commands below were rerun from the mapped `S:` worktree; exit code was 0 unless stated otherwise.

| Check | Representative signal | Result |
|---|---|---|
| `pnpm dlx skills-ref validate` for Discovery, Planning, Implementation | `Valid skill` for all three | PASS 3/3 |
| Garen `quick_validate.py` for all three packages | `Skill is valid!` for all three | PASS 3/3 |
| `python skills/<package>/evals/test_append_event.py` | `append event tests: PASS` for all three | PASS 3/3 |
| Production JSON parsing | behavior eval counts Discovery 8 / Planning 3 / Implementation 3; activation counts 10 / 13 / 11 | PASS |
| Selected benchmark and Task 8 JSON parsing | 16 files parsed after final selection | PASS |
| Planning fixture manifest | 28 entries, 0 mismatches; manifest SHA-256 `0c9183e427e42cdb5533c7c095e8000b66137e7823333cc494f92b75434cc567` | PASS |
| Implementation fixture manifest | 41 entries, 0 mismatches; manifest SHA-256 `2cbac7ee34c266dd43b5afb45c198b55dc3d94d8b40ccedbf3bbddb5d8dd7a42` | PASS |
| Shared `artifact-protocol.md` | identical SHA-256 `001a7c16f684e076fb0263314e8711dd49b0f711ace9990d17b94531c8c9c8c6` | PASS |
| Shared `append_event.py` | identical SHA-256 `5f43334acd31624b3dff817876ea55db1403097bd7d1b21c924c45fe5e6cdbf7` | PASS |
| Shared `test_append_event.py` | identical SHA-256 `516a7d220fb0e1741f8615cbeef56071d0fdf5042231034869953a8c355e0aa4` | PASS |
| `git diff --check` | no output | PASS |
| Tracked source containment | `git diff --name-status` empty before final report creation | PASS |

Generated `__pycache__` residue from the append suites was removed by exact path after the test run; no lockfile, `.env`, secret, fixture source, Git index/remote, deployment, or external system was modified.

## Dynamic activation matrix

Fresh session `f2b6da22-dbec-40ce-b47e-8c2103e758d0` read only the approved design rows and six activation/skill sources. Root rehashed all seven sources and parsed the result. The evaluator initially invented a UUID because the CLI-assigned value was not visible inside its prompt; root corrected only that provenance field from the actual `claude --session-id` invocation and recorded the correction in both outputs.

| Case | Winning owner | Result |
|---|---|---|
| 1 new AI agent platform | `autonomous-project-discovery` | PASS |
| 2 explore personal OS | `autonomous-project-discovery` | PASS |
| 3 plan from current Discovery artifact | `autonomous-planning` | PASS |
| 4 implement approved plan | `autonomous-implementation` | PASS |
| 5 routine loading-state fix | `ordinary_scoped_workflow` | PASS |
| 6 materially ambiguous billing subsystem | `autonomous-project-discovery` | PASS |
| 7 resume yesterday's implementation | `autonomous-implementation` | PASS |
| 8a offline architecture-only contradiction, framing unchanged | `autonomous-planning` | PASS |
| 8b offline users/outcomes/scope/journeys/acceptance change | `autonomous-project-discovery` | PASS |

Result: 8 design prompt groups, 9 atomic verdicts, 9/9 PASS, exactly one `winning_owner` per row. The routine case correctly has all three skill triggers false while `ordinary_scoped_workflow` wins. Cases without text-identical negative eval rows use bounded SKILL.md activation-boundary evidence and are reported as an inference, not a contradiction.

## Cold evaluation evidence

No reused agent, copied predecessor worker, controller, pre-identity rejected spawn, or invalid reservation candidate counts as cold evidence.

| Package / eval | Selected cold result | Representative real output | Limitation |
|---|---:|---|---|
| Planning eval 1 run-7 | 6/11 | 24-row System design matrix passes | honest weighted cutover; final review/contracts incomplete; stale mutable gate references |
| Implementation eval 1 run-3 | 6/7 | 5/5 tests; exact `MATCH_IDS=2` | controller acceptance evidence time is later than verified event |
| Implementation eval 2 run-3 | 5/7 | 7/7 tests; exact `UNREAD_IDS=evt-3,evt-1`; populated/empty screenshots inspected | dispatch events written after worker returns; handoff not self-contained |
| Implementation eval 3 run-3 | 6/7 | 3/3 tests; exact `NOTIFY_FALSE=false`; direct boolean `false`; dirty draft hash preserved | two fresh WSL reviews returned BLOCKED and Windows reservation failed pre-dispatch, so integration acceptance is honestly blocked |

Implementation final-selected aggregate is 81% versus a 0% reused warm comparison baseline. The baseline is not cold evidence. Duration/token telemetry was unavailable; legacy nonzero `tokens` values in benchmark tooling are output-size proxies.

Representative artifacts inspected include the eval-2 populated and empty UI PNG evidence, eval-3 immutable receipts and terminal 93-event chain, Task 8 routing JSON, both final-selected benchmark JSON files, the static responsibility rereview, and current manifest entries rather than only command exit codes.

## WSL / Codex execution finding

Codex in WSL is viable when the repository or worktree is WSL-native under the Linux filesystem. The attempted WSL cold reviewers could read `/mnt/s` and run `/home/garen/.local/bin/node`, but their Codex `workspace-write` sandbox denied canonical writes on the Windows-mounted worktree. Windows Git also cannot resolve this linked worktree from WSL because its `.git` pointer targets a Windows/UNC worktree gitdir.

Recommended setup: clone or create the worktree inside WSL (for example under `~/git/...`) and run `codex exec` there. Do not migrate an active artifact run midway, and do not treat a read-only WSL observation as accepted work when assigned canonical outputs could not be written.

## Known assumptions and residual risks

- Host context telemetry and some exact model selectors are unavailable; packages record `unavailable` / `host_default` instead of inventing values.
- Git status and linked-worktree operations on the network-backed `S:` mapping are slower than local filesystem operations but completed successfully.
- Historical immutable events may reference later-mutated state/gate/handoff files. The event chains remain valid, but current reference revalidation can be stale; future runs should reference immutable versioned snapshots.
- Validator PASS proves package/schema integrity, not perfect autonomous execution. The cold-score failures above remain real gaps and are preserved in Planning/Implementation `gaps.md`.

## Rollback points

- Discovery handoff/audit hardening: `d572275`
- Autonomous Planning package: `71f1a73`
- Autonomous Implementation package: `f2c52cb`
- Pinned integrated source and rollback baseline: `630c2cef90cdbec14ef3c2cab688f4587a29aeb4`

Rollback must be commit- or exact-path-scoped. Do not use destructive reset/clean operations in a dirty or network-backed worktree.
