# Harness Adapters

## Rule

The workflow names semantic actions. Map each action only to a capability the active host actually exposes. Discover capabilities before dispatch, record unavailable capabilities and fallbacks in `AGENT-STATE.md`, and never claim a tool, model, telemetry signal, browser, or new session exists because another harness has one.

Claude Code and Codex are adapters to the same artifact workflow, not separate workflows.

## Semantic action map

| semantic action | Claude Code adapter | Codex adapter | generic fallback |
|---|---|---|---|
| `discover_capabilities` | Inspect the current tool/agent surface and read applicable `CLAUDE.md` and `AGENTS.md`. | Inspect the current collaboration/tool surface and read applicable `AGENTS.md` and `CLAUDE.md`. | Inventory exposed tools and every applicable instruction file; record unknown capability as unavailable. |
| `spawn_worker` | Use the exposed Agent/subagent mechanism with a fresh, self-contained contract. | Use the exposed collaboration/subagent mechanism with a fresh, self-contained contract. | A genuinely isolated worker mechanism is required; if absent, mark orchestration blocked and return to the top-level user/parent. |
| `wait_for_worker` | Use the host's foreground result or task-wait mechanism. | Use the host's agent wait/status mechanism. | Use only a supported wait/status operation; do not simulate completion or busy-loop with arbitrary sleep. |
| `inspect_artifact` | Open the assigned report, evidence, and representative outputs with available read tools. | Open the assigned report, evidence, and representative outputs with available read tools. | Read the actual filesystem or connected artifact store; a worker return alone is insufficient. |
| `verify_evidence` | Run project checks and use exposed browser/screenshot/computer observation when relevant. | Run project checks and use exposed browser/screenshot/computer observation when relevant. | Use observable commands/files; if required UI observation is unavailable, persist a human gate instead of substituting source inspection. |
| `checkpoint_state` | The top-level orchestrator updates `AGENT-STATE.md` after inspection. | The top-level orchestrator updates `AGENT-STATE.md` after inspection. | Preserve the same single-writer and report-before-state ordering with the host's safe file-edit mechanism. |
| `request_human_gate` | Ask one focused question and persist the paused state before yielding. | Ask one focused question and persist the paused state before yielding. | Surface one decision with evidence, alternatives, impact, and safe default if one exists; never claim an answer. |
| `route_stage` | Invoke or recommend the owning skill only after state/artifact readiness is current. | Invoke or recommend the owning skill only after state/artifact readiness is current. | Write the owning stage and reason into state; do not absorb another stage's responsibility. |
| `finish_or_handoff` | Continue in a new top-level session only if the host explicitly supports it; otherwise write a continuation command. | Continue in a new top-level task only if explicitly supported; otherwise write a continuation command. | Set `restart_mode: manual`, write the exact continuation action, and end cleanly. |

## Capability record

Record each capability as `available`, `unavailable`, or `unknown`, plus the observed host evidence and selected fallback.

| capability | Claude Code possibility | Codex possibility | recorded fallback |
|---|---|---|---|
| Fresh isolated worker | Agent/subagent mechanism may be exposed. | Collaboration/subagent mechanism may be exposed. | Hard blocker for this orchestration workflow if no isolated worker exists. |
| Model selection | Alias or exact model ID may be selectable. | A selector may or may not be exposed. | Set `effective_model: host_default` and record a non-empty `fallback_reason`; block only when the user required the exact model. |
| Context telemetry | Host-reported usage may be exposed. | Host-reported usage may be exposed. | Set `context_telemetry: unavailable`; enforce artifact and weight budgets without estimating hidden context. |
| Project instructions | `CLAUDE.md` and `AGENTS.md` may both apply. | `AGENTS.md` and `CLAUDE.md` may both apply. | Search the project hierarchy and read every applicable instruction file found. |
| UI observation | Browser, screenshot, or computer-use may be exposed. | Browser, screenshot, or computer-use may be exposed. | Mark required visual verification or preference/UAT as a human gate. |
| Git | Repository commands may be available. | Repository commands may be available. | Record filesystem revision evidence and pre-existing paths; never invent a Git SHA. |
| New top-level session | May exist only through an explicitly exposed host action. | May exist only through an explicitly exposed host action. | Exact `continuation_command` plus manual restart. |

## Model policy

Model names are preferences, not assumptions. Discovery may request a highest-reasoning/Fable-class orchestrator and workers, but it must record `requested_model`, `effective_model`, and `fallback_reason` for each. Use exact model IDs only after capability discovery confirms them. Unavailable selection is ordinarily non-blocking.

## Dispatch minimum

Every fresh worker receives the goal, one packet outcome, scope and stop boundary, required instruction paths, explicit inputs, assigned artifact/report/evidence paths, allowed side effects, requested model preference, verification and fallback, and the at-most-ten-line return contract. The worker does not receive hidden conversation context as a dependency.
