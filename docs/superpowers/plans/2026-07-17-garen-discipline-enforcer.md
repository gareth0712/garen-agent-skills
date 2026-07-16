# Garen Discipline Enforcer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Use `superpowers:test-driven-development` for every hook state transition and `superpowers:verification-before-completion` before installation claims.

**Goal:** Turn Gareth’s key execution rules into observable Claude Code guardrails, with shared deterministic scripts that can later receive a Codex adapter without pretending the current Codex plugin runtime supports Claude hooks.

**Architecture:** Build a repository-owned Claude Code marketplace plugin first. One Node hook runner parses stdin JSON and updates per-session state outside the repository. Small policy modules enforce edit authorization, affected checks, sensitive-path review, abnormal Git changes, completion review, and session/repeated-error reminders. Bootstrap owns installation; the plugin repo owns source.

**Tech Stack:** Claude Code plugin marketplace, Node.js 18+ ESM, built-in `node:test`, Git, pnpm-aware command discovery.

**Provider boundary:** The first accepted artifact is a Claude Code plugin under `.claude-plugin`, because `claude plugin validate/install` is executable and the approved inventory manages Claude enabled plugins. Do not add `hooks` to a native `.codex-plugin/plugin.json`: the installed Codex validator guidance conflicts on that field and `codex.exe` is currently not executable from this shell. Codex support requires a separate acceptance spike; if native hooks are unavailable, Git gates remain mechanical while edit/delegation guidance is advisory because Codex currently exposes no interception point for built-in file-write tools.

---

## Task 1: Prove the Claude plugin contract with the smallest hook

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\.claude-plugin\marketplace.json`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\.claude-plugin\plugin.json`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\runner.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\plugin-smoke.test.mjs`

**Plugin identity:** `garen-discipline-enforcer`, version `0.1.0`, marketplace `garen-agent-skills`, category `development`, author `Gareth Lau`.

**Marketplace source:** `./plugins/garen-discipline-enforcer`.

- [ ] First create a failing test that pipes SessionStart JSON to `node hooks/runner.mjs session-start` and expects valid hook JSON with a visible version/context message.
- [ ] Create fully populated minimal manifests with command `node "${CLAUDE_PLUGIN_ROOT}/hooks/runner.mjs" session-start`.
- [ ] Run `claude plugin validate --strict <plugin-path>` and `claude plugin validate --strict <repo-root>`.
- [ ] Add the local marketplace with `claude plugin marketplace add --scope user <repo-root>`, install with `claude plugin install --scope user garen-discipline-enforcer@garen-agent-skills`, and verify it in `claude plugin list --json`.
- [ ] Start a fresh Claude task and inspect actual SessionStart output; uninstall on any schema/runtime mismatch before revising.
- [ ] Commit only plugin/marketplace smoke files: `feat(discipline): scaffold Claude hook plugin`.

## Task 2: Parse hook input and maintain bounded session state

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\input.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\state.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\output.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\input-state.test.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\fixtures\hook-inputs\`

**Accepted input fields:** `hook_event_name`, `session_id`, `cwd`, `transcript_path`, `tool_name`, `tool_input.file_path`, `tool_input.command`, `tool_response`, and optional agent identity fields when supplied by the runtime.

**State path:** `~/.claude/garen-discipline/sessions/<sha256(session_id)>.json`; never use the raw session ID as a filename.

- [ ] Test missing/extra fields, CRLF, malformed JSON, paths with spaces, and a 2 MB input cap.
- [ ] Store only hashes, normalized paths, timestamps, counters, and gate verdicts—never prompt/transcript contents or secrets.
- [ ] Use exclusive temp-write + rename and reject state paths outside the state root.
- [ ] Emit Claude-compatible JSON on stdout; diagnostics go to stderr and are capped at 20 lines.
- [ ] Malformed input is fail-closed only for destructive/security-sensitive PreToolUse gates; advisory hooks warn and exit `0`.
- [ ] Commit: `feat(discipline): add safe hook state machine`.

## Task 3: Enforce delegation or explicit hands-on declaration before production edits

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\edit-authorization.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\transcript.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\edit-authorization.test.mjs`

**PreToolUse matcher:** `Edit|Write|MultiEdit|NotebookEdit`.

**Authorization rules:**
- Allow edits from a runtime-confirmed subagent.
- Allow the main thread only when the most recent assistant text before the tool call contains `hands-on: <non-empty reason>`.
- Allow an edit whose target is documentation/plan/eval fixture only when the state records the current Task Contract; production code still needs delegation or hands-on.
- Block when identity/transcript evidence is unavailable; do not guess that the caller is a subagent.

- [ ] Build transcript fixtures for delegated, main-thread declared, declaration in old/stale message, user-only declaration, missing transcript, and spoofed file content.
- [ ] Parse JSONL structurally; never grep repository files for `hands-on:`.
- [ ] Block with exit `2` and structured `decision: "block"`, one concrete reason, and one allowed recovery path. Do not retry alternate edit syntax.
- [ ] Test Windows and macOS paths and ensure `.env`, lockfile, CI-secret rules still block independently.
- [ ] Commit: `feat(discipline): gate undeclared main-thread edits`.

## Task 4: Replace legacy PostToolUse scripts with pnpm-aware affected checks

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\affected-checks.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\process.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\affected-checks.test.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`

**Selection order:** nearest workspace/package `package.json` -> root `package.json`; package scripts first; otherwise local binaries through `pnpm exec`. Never invoke `npx`.

- [ ] Test JS/TS, test/non-test, no package, pnpm workspace, absent Biome/tsconfig, and command timeout fixtures.
- [ ] For edited JS/TS with Biome config, run `pnpm exec biome check --write <absolute-file>` using argument arrays.
- [ ] For TS/TSX with a typecheck script, run the nearest package’s `pnpm run typecheck`; otherwise `pnpm exec tsc --noEmit -p <nearest-tsconfig>`.
- [ ] For test files, run the exact test file through the detected Vitest/Jest package script; for production files, run related tests only when the package exposes a deterministic related-test command.
- [ ] Return failures as `hookSpecificOutput.additionalContext`; PostToolUse remains advisory exit `0` because the edit already occurred, but state records unresolved failures for the Stop gate.
- [ ] Limit output to the first/last relevant 20 lines and never modify a lockfile.
- [ ] Commit: `feat(discipline): run affected pnpm checks`.

## Task 5: Trigger security review on sensitive paths

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\config\policy.json`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\security-paths.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\security-paths.test.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`

**Sensitive patterns:** path segments `auth`, `payment`, `billing`, `admin`, `middleware`, `webhook`; filenames containing `debug`; and changes to permission/role/session/token handling detected in the affected diff.

- [ ] Test true positives, words embedded in unrelated names, case differences, generated/vendor paths, deletions, and rename diffs.
- [ ] Ignore `node_modules`, build output, generated files, and fixtures unless the user explicitly asked to review them.
- [ ] On a hit, record `securityReviewRequired` and add context directing use of the installed `security-guidance` plugin; do not duplicate its vulnerability scanner.
- [ ] Clear the requirement only when the transcript/state contains observable security-review completion after the latest sensitive edit hash.
- [ ] Stop must block with exit `2` if the latest sensitive diff lacks review evidence.
- [ ] Commit: `feat(discipline): require sensitive-path review`.

## Task 6: Gate abnormal Git commits with configurable evidence

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\git-diff-gate.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\git-diff-gate.test.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\config\policy.json`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`

**Default thresholds:** more than 30 staged files, more than 1500 staged added+deleted lines, any staged `.env`/lockfile/CI-secret file, or paths outside the current repository root.

- [ ] Match Bash commit commands structurally enough to include `git commit`, `git -C <path> commit`, and approved aliases; do not match harmless text containing those words.
- [ ] Gather evidence with `git diff --cached --numstat`, `--name-only`, and `--check`; use argument arrays and the hook `cwd`.
- [ ] Always block protected files. For size thresholds, block unless the current assistant transcript explicitly records `large-change: <reason>` after the latest staged-tree hash.
- [ ] Exit `2` on block, preserve the index, and never auto-reset/stage/commit.
- [ ] Test binary files, renames, submodules, empty index, dirty unstaged files, and malformed Git output.
- [ ] Commit: `feat(discipline): gate abnormal staged changes`.

## Task 7: Require post-edit code review before completion

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\completion-review.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\completion-review.test.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`

- [ ] Record production-edit hashes and successful affected-check hashes after every edit.
- [ ] Recognize review evidence only from a later observable reviewer/plugin/subagent event tied to the same Git diff hash; an assistant sentence “reviewed” is not evidence.
- [ ] Stop blocks when production edits have unresolved checks, missing security review, or missing code review. Documentation-only changes stay advisory.
- [ ] Prevent infinite Stop loops: include `stop_hook_active`/state guard, block at most twice for the same unchanged diff, then emit a visible unresolved warning and allow the session boundary.
- [ ] Test new edits after review invalidate old evidence, review of a different diff, no Git repo, docs-only edit, and two-block circuit breaker.
- [ ] Commit: `feat(discipline): enforce reviewed completion`.

## Task 8: Persist session-boundary and repeated-error reminders

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\policies\session-boundary.mjs`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\session-boundary.test.mjs`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\hooks\hooks.json`

- [ ] Count normalized command/error fingerprints without storing full command output.
- [ ] At three equivalent failures, add context requiring a circuit-breaker diagnosis or user decision; never retry a denied operation through alternate syntax.
- [ ] At Stop, report only unresolved work, rollback location, and a resume command/path; keep the existing `session-breadcrumb` purpose separate.
- [ ] Expire session state after 14 days and cap total state storage at 20 MB, deleting oldest closed sessions first.
- [ ] Test fingerprint stability, unrelated errors, compaction/re-entry, state corruption, expiry, and storage cap.
- [ ] Commit: `feat(discipline): persist circuit-breaker state`.

## Task 9: Full plugin validation and cold-start acceptance

**Files:**
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\fixtures\repositories\`
- Create: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\tests\acceptance.md`
- Modify: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\.claude-plugin\plugin.json`

- [ ] Run all Node tests on Windows and macOS path fixtures; run `claude plugin validate --strict` for plugin and marketplace.
- [ ] Reinstall the local plugin after version bump, start a fresh Claude task, and exercise: delegated edit allowed; hands-on edit allowed; undeclared edit blocked; sensitive path flagged; large commit blocked; reviewed completion allowed.
- [ ] Inspect state files, real hook output, Git index preservation, and representative edited/test artifacts; exit codes alone are insufficient.
- [ ] Spawn independent code review; rerun its evidence from the main orchestrator.
- [ ] Update `tests/acceptance.md` with date/platform/Claude version and exact pass/fail commands. Do not mark macOS accepted from Windows or WSL.
- [ ] Commit: `test(discipline): verify Claude enforcement workflow`.

## Task 10: Codex adapter spike and bootstrap integration

**Files:**
- Create only after a successful runtime spike: `S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer\.codex-plugin\plugin.json`
- Create only after a successful runtime spike: `S:\git\15-skills\garen-agent-skills\.agents\plugins\marketplace.json`
- Modify: `C:\Users\garet\sync-setup\bootstrap\capabilities.yaml`
- Modify: `C:\Users\garet\sync-setup\README.md`
- Create when native hooks are unavailable: `C:\Users\garet\sync-setup\.githooks\discipline-pre-commit.mjs`

- [ ] In a new Codex task where `codex plugin` is executable, scaffold/validate the smallest native plugin with the official `plugin-creator` scripts and confirm whether hook execution is actually supported.
- [ ] If native Codex hooks are unsupported, do not create the two Codex files above. Install a tracked Git adapter that invokes the shared plugin policy modules from the manifest-owned custom skills checkout for staged diff/protected-file/review-evidence gates; keep edit/delegation policy in Codex AGENTS/rules and label it advisory, not mechanically enforced.
- [ ] Add a provider-neutral `record-review` CLI that accepts the current diff hash and a real review artifact path, validates both, and stores only their hashes. The Git adapter rejects stale/missing review evidence after production edits; it never accepts a plain assistant claim.
- [ ] If supported, build a thin adapter that invokes the same deterministic policy modules; do not duplicate policies or put Claude hook fields into an invalid Codex manifest.
- [ ] Add the accepted plugin identity/version and adapter status to bootstrap, then verify install/check/rollback from a fresh task.
- [ ] Put the plugin source, install commands, provider support matrix, state/rollback paths, and limitations in the root recovery README.
- [ ] Commit in each repository separately: `feat(discipline): add accepted Codex adapter` only if proven; otherwise `docs(discipline): record Codex enforcement boundary`.

## Final Verification

```powershell
$pluginRoot = "S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer"
$tests = @(Get-ChildItem "$pluginRoot\tests" -Filter "*.test.mjs" -File)
if ($tests.Count -lt 8) { throw "Expected at least 8 discipline test files; found $($tests.Count)." }
node --test $tests.FullName
claude plugin validate --strict "S:\git\15-skills\garen-agent-skills\plugins\garen-discipline-enforcer"
claude plugin validate --strict "S:\git\15-skills\garen-agent-skills"
claude plugin list --json
git -C "S:\git\15-skills\garen-agent-skills" diff --check -- .claude-plugin plugins/garen-discipline-enforcer docs/superpowers/plans/2026-07-17-garen-discipline-enforcer.md
```

Expected: all deterministic tests pass; strict validation passes; Claude lists `garen-discipline-enforcer@garen-agent-skills` enabled at user scope; real acceptance evidence covers all six Claude gates; unrelated dirty files in the custom skills repo are not staged or modified. Codex support is labelled either native-hook accepted or fallback accepted; fallback acceptance must prove staged Git/review gates and explicitly mark built-in edit interception unavailable.

## Fallback

Run `claude plugin uninstall garen-discipline-enforcer@garen-agent-skills`, remove only the confirmed local marketplace registration if no other plugin uses it, and restore Claude settings/plugin inventory through the workstation bootstrap rollback manifest. Session state under `~/.claude/garen-discipline` can be archived; it is not required to restore source files. Revert plugin commits without touching existing custom skills or their uncommitted work.
