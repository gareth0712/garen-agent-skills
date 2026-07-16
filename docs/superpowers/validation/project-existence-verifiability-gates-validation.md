# Project Existence and Verifiability Gates — Final Validation

## Verdict

**PASS with explicit observer-assurance limitations.** The evaluated Project Discovery skill implements the approved two-stage product-existence and outcome-verifiability gates at remote `main` revision `13f8fe65c9ed1ab0d00c12ff794e240eefbc8c1a`. All five qualifying runs reached the required truth-preserving state, every gate-specific expectation passed, the routine-fix dynamic negative stayed outside these gates, and the focused/static/protocol validators passed from the evaluated revision.

This verdict does **not** claim independently authenticated runner lifecycle ordering or prove the absence of network/process effects outside the runner's audited channels. Original grader files and failed attempts remain unchanged.

## Scope and source binding

- Initial pushed feature SHA: `09d57bad97bd2c40bf6750a5cb76ccd2729d770f`
- Post-review repair/evaluated SHA: `13f8fe65c9ed1ab0d00c12ff794e240eefbc8c1a`
- Evaluated remote: `origin/main`
- Source observation: `2026-07-16T08:58:59.076Z`
- Report date: `2026-07-16`
- Production commits:
  - `47c4255` — `feat(discovery): add product justification gates`
  - `09d57ba` — `test(discovery): cover product justification states`
  - `13f8fe6` — `fix(discovery): enforce learning bypass expiry`
- Rollback: none

The full source hashes are recorded in [source-revision-after-repair.md](../../../skills/autonomous-project-discovery-workspace/iteration-3/source-revision-after-repair.md). Representative bindings:

| Input | SHA-256 |
| --- | --- |
| `SKILL.md` | `807644ae9e68981ceaf14edd444a7701cfbe83f03dee788cb08d173067f1c271` |
| `references/discovery-method.md` | `18422e9254f0be1f8485d321e409fd45cdaf4cfa154ba35e2d04913d5c7a746d` |
| `references/state-templates.md` | `8df39217295f2afd7da96fad3c49060db0e0f54054f95d30e9cda8fc58e3ef56` |
| `evals/evals.json` | `4c976603e56ffba6186b5625b5663145712da36430cfb6270a2ec63f439847fb` |
| `evals/viability-evals.json` | `fc9820244d8fe88a403db2acf63496aae4333c7568c520a07df40f4cae050d36` |
| Contract test | `8e6bf3b037531dc0a378fbbe528b914d907fd57c255ea64de1e9e15b9c16102b` |

Before the artifact-producing evaluations, a fresh read-only review found two IMPORTANT issues: bypass expiry had no deterministic transition, and the static contract under-specified routing/expiry/event-anchor behavior. Both were fixed by `13f8fe6`; no CRITICAL or unresolved IMPORTANT finding remains. See [postpush-review-1.md](../../../skills/autonomous-project-discovery-workspace/iteration-3/review/postpush-review-1.md).

## Evidence classification

- **Pre-change RED only:** three fresh read-only identities showed that the prior skill lacked binding baseline, exact unapproved-override, and learning-bypass/verifiability contracts. This is not post-push cold evidence. See [pre-change-pressure-baseline.md](../../../skills/autonomous-project-discovery-workspace/iteration-3/baseline/pre-change-pressure-baseline.md).
- **Qualifying evaluation evidence:** each accepted run used an isolated run root bound to evaluated SHA `13f8fe6`; state-changing runs were sequential. Eval 6 run 2 resumed the same top-level evaluator after a host slot limit and used a newly spawned `fork_turns=none` worker. The resumed identity is not counted as a second cold identity.
- **Independent grading:** one new read-only grader identity graded each qualifying run from its exact expectations and run artifacts. No grader result was inferred from an evaluator self-report.
- **Methodology adjudication:** a separate fresh read-only adjudicator examined only the protocol, the disputed exact expectations, and Eval 4/7 artifacts. It did not rewrite their original grading files.
- **Reused identity rule:** an interrupted/resumed reviewer or evaluator is one continued identity and is never described as new cold evidence.

## Qualifying evaluation results

| Eval | Accepted run | Required canonical truth | Original independent grade | Acceptance interpretation |
| --- | --- | --- | --- | --- |
| 4 — insufficient wrapper | [run-2](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-4-blocked/with_skill/run-2/) | `production_commercial / insufficient / approved / blocked / not_ready / DISCOVERY` | `7/8`, `0.875`, `gate_specific_pass=true`, original verdict `fail` | The only failed expectation was adjudicated PASS: event references are append-time snapshots, while the accepted event anchor and all four receipted subjects recompute. Runner-authenticated lifecycle remains a limitation. |
| 5 — external baseline owner | [run-1](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-5-external-evidence/with_skill/run-1/) | `production_commercial / external_evidence / approved / blocked / not_ready / DISCOVERY` | `7/7`, `1.0`, `pass` | Exact external owner, prohibited unauthorized execution, and falsifiable recovery check are durable. |
| 6 — explicit unapproved override | [run-2](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-6-user-directed-unapproved/with_skill/run-2/) | `production_commercial / insufficient / approved / user_directed_unapproved / ready / PLANNING` | `8/8`, `1.0`, `pass` | Exact scope/authority is durable; failed claims, non-endorsement, and prohibited effects remain in Discovery and handoff. |
| 7 — bounded learning bypass | [run-2](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-7-learning-bypass/with_skill/run-2/) | `learning_prototype / bypassed_learning / approved / bypassed_learning / not_reached / ready / PLANNING` | `8/9`, `0.8888888889`, `gate_specific_pass=true`, original verdict `FAIL` | The only failed expectation was adjudicated PASS under append-time reference semantics. Fired/unverifiable triggers deterministically block and return to Discovery. Runner lifecycle remains unauthenticated. |
| 8 — approved regulated workflow | [run-1](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-8-approved-workflow/with_skill/run-1/) | `production_commercial / approved / approved / approved / ready / PLANNING` | `9/9`, `1.0`, `pass` | Durable workflow value is distinct from drafting; automatic outcomes and the blinded human-only rubric remain separate. |

Every accepted `DISCOVERY.md` contains the five canonical product-justification sections and every material outcome row has all twelve required fields. Discovery did not select Planning-owned architecture, API/data contracts, deployment, or implementation stages.

### Event anchors and receipt checks

| Eval | Events | Tip | Full `EVENTS.jsonl` SHA-256 | Receipt/subject result |
| --- | ---: | --- | --- | --- |
| 4 | 13 | `b50aaf655747c1495953704256ad6468f5e08354be514d0c01d9625875c68f62` | `845fdcd5d89a265ae8eb9f9531c090169c076a1b846417e5b7c978db7f4a7d48` | 2 ReadOnly receipts; 4/4 report/evidence subjects match exact size and SHA-256. |
| 5 | 13 | `dab1a6a632272e57e425139d87dd58ccf274ccaa51135c74b4f1271a41645154` | `49a2187c01d600df5037fa99bf18bb960523f18b2ee4592380140aae05746607` | 2 ReadOnly receipts; 2/2 accepted subjects match, with sampling evidence. |
| 6 | 13 | `1827111107176f6c1bd3b7158dd6f6f41f60888aee2e9733113b7fb69e19fd38` | `620e927ee78228e192aa19f93c5c8bd673357ba3b885be60432df57a9bac3882` | 1 content-addressed JSON receipt binds 3/3 worker progress/analysis/report subjects; all hashes and sampling references match. |
| 7 | 13 | `e0a6c7470e93d5a3ab5c0624be99e74819e3eacf02886f05bdfa35114a73ba79` | `afe21ae3031956bf6e4e135204a7b5705179af626b99cd62a07d00e51081577f` | 4 ReadOnly receipts; 4/4 subjects match exact size and SHA-256. |
| 8 | 12 | `d406edaa2c38b2553b4ab5ba4ae881cf1e911837d64277d6bc380ab045005223` | `a22a409dc49bdabaf09e591547b8c20c30883e1325855549f84d099f2dec2dd6` | 2 ReadOnly receipts; 2/2 subjects and orchestrator sampling match. |

The accepted event count, chain tip, and full-file digest above were recomputed and agree with each terminal `AGENT-STATE.md`. Original grading is available beside each run as `grading.json`; the separate interpretation record is [grading-adjudication.json](../../../skills/autonomous-project-discovery-workspace/iteration-3/grading-adjudication.json).

## Truthful override and bypass samples

Eval 6 records user/product authority and the exact continued scope as local image selection, upload, and recommendation display only. The durable override explicitly says it is `user_directed_unapproved`, not product approval or Discovery endorsement, and does not authorize implementation, deployment/public effects, credentials, expanded scope, fixture creation, external model/API execution, or architecture selection. See [user-override.md](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-6-user-directed-unapproved/with_skill/run-2/outputs/evidence/authority/user-override.md).

Eval 7 records a local-only, non-commercial, synthetic non-PII, 14-day learning boundary. `revisit_trigger_state` was rechecked immediately before READY. A fired trigger deterministically becomes `production_commercial / insufficient / blocked / not_ready / DISCOVERY`; an unverifiable trigger becomes `external_evidence / blocked / not_ready / DISCOVERY`. Verifiability is never bypassed. See [product-justification.md](../../../skills/autonomous-project-discovery-workspace/iteration-3/eval-7-learning-bypass/with_skill/run-2/outputs/evidence/product-justification.md).

## No invented model or external evidence

Across the five accepted runs, supplied baselines are labeled supplied and bounded; unavailable baselines remain `unknown`/`not_executed`; product advantages and outcome metrics are not promoted to observed results; and no fixed prompt-count threshold is introduced. Eval 5 creates an `external_evidence` gate instead of fabricating a comparison. Run metadata and canonical artifacts state that no model/API/network execution or fixtures were used.

This is evidence that the artifacts make no invented claim. It is **not** independent proof that every external channel remained idle: runner summaries explicitly exclude network/remote services, external process state, writes outside audited roots, credentials, and host-private tool transcripts.

## Dynamic routine-work boundary

The fresh read-only classifier bound viability case 7 and activation case 5 to evaluated SHA `13f8fe6` and returned:

```text
should_activate_gates=false
first_stage=Ordinary scoped implementation
competing_owner=ordinary scoped workflow
```

The exact prompt/scenario digests and reasoning are in [activation-negative-cold-test.json](../../../skills/autonomous-project-discovery-workspace/iteration-3/activation-negative-cold-test.json). This dynamic result is separate from the already completed static stage-integration evidence.

## Failed attempts and preserved contradictions

- Eval 4 run 1 was incomplete and is not qualifying evidence; run 2 is the accepted retry.
- Eval 6 run 1 scored `7/8` with `gate_specific_pass=false` because production references were invalid; it remains preserved and is superseded only by fresh run 2 plus a new grader.
- Eval 7 run 1 had an observer setup failure and is not qualifying evidence; run 2 is the accepted retry.
- Eval 4 and Eval 7 original graders failed one artifact expectation each by comparing historical mutable references to terminal-current bytes and by demanding authenticated runner lifecycle evidence not stated in those exact expectations. Their scores/verdicts remain unchanged. The adjudicator found no material failure under the committed append-time protocol.
- Eval 6 run 2 runner audit reports historical `path_missing`/`references_valid=false`, although terminal grading found all 33 paths present and 32/33 hashes matching; the only mismatch is a later-updated `SESSION-HANDOFF.md`. This observer contradiction is preserved, not normalized away.
- Eval 5 reports a worker inventory claim whose file is absent; it was explicitly excluded from acceptance rather than fabricated.

## Limitations

1. All qualifying runner summaries report `lifecycle.D-001.strictly_ordered=false` and `runner_control_integrity.accepted_control_count=0`. Production event/sample claims cross-check, but the runner did not independently authenticate sample/verify ordering.
2. `AGENT-STATE.md` and `SESSION-HANDOFF.md` are mutable indexes. Historical event references hash their append-time bytes, so later terminal-anchor updates cause expected terminal-current mismatches. The current protocol validates append-time references and the accepted event-stream anchor; it does not provide immutable historical copies of every mutable index.
3. Windows ReadOnly attributes are reversible by a writer with authority. Content hashes and event anchors detect changes only while the trusted anchors remain trustworthy; this is not an adversarial external transparency log.
4. Eval 6's single JSON receipt is content-addressed and event-bound but not filesystem ReadOnly; its integrity assurance is therefore hash/anchor based.
5. Observation scope does not prove absence of network, process, credential, deployment, publication, or out-of-root effects.

## Fresh final verification

The first attempted PowerShell wrapper was discarded because it accidentally invoked Python with no arguments; visible `>>>` prompts proved those exit codes invalid. The following commands were then executed literally from evaluated SHA `13f8fe65c9ed1ab0d00c12ff794e240eefbc8c1a`:

| Command | Observed signal |
| --- | --- |
| `python skills/autonomous-project-discovery/evals/test_product_existence_verifiability_contract.py` | exit `0`; `product existence and verifiability contract tests: PASS` |
| `python skills/autonomous-project-discovery/evals/test_append_event.py` | exit `0`; `append event tests: PASS` |
| `python skills/autonomous-project-discovery/evals/test_run_audit.py` | exit `0`; `runner audit smoke test: PASS` |
| `python skills/garen-skill-creator/scripts/quick_validate.py skills/autonomous-project-discovery` | exit `0`; `Skill is valid!` |
| `python -m json.tool skills/autonomous-project-discovery/evals/evals.json` | exit `0` |
| `python -m json.tool skills/autonomous-project-discovery/evals/activation-evals.json` | exit `0` |
| `python -m json.tool skills/autonomous-project-discovery/evals/viability-evals.json` | exit `0` |
| `git diff --check` | exit `0` |

At verification time, local `HEAD` and `origin/main` both equaled the evaluated SHA. Only pre-existing untracked evaluation/workspace/cache artifacts were present; there were no tracked production edits. The report itself must be whitespace-checked, staged alone, committed, pushed, and remote-verified before this validation task is closed.
