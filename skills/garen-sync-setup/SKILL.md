---
name: garen-sync-setup
description: >-
  Maintain Garen's `~/sync-setup/` config repo — the cross-device source of truth for
  Claude Code / Codex / web-LLM setup. Use this skill whenever the user wants to
  regenerate or update the integrated web-LLM personal preferences and memories,
  combine new raw exports from `5-sources/` into `6-integrated/`, produce per-platform
  preference files (Gemini / ChatGPT / Claude.ai), sanitize memories before sharing,
  sync `~/.codex/AGENTS.md` with `~/.claude/CLAUDE.md`, or refresh the plugin/mcp/skill/hook
  READMEs that keep all devices in sync. Trigger on `/garen-sync-setup`, and also on
  "integrate my memories", "update web preferences", "regenerate the integrated version",
  "combine 5-sources", "sync AGENTS.md with CLAUDE.md", "I dropped a new export", or any
  request touching `sync-setup/`. Prefer this skill over ad-hoc edits — the folder layout,
  sanitization rules, and per-platform char limits are easy to get wrong from memory.
---

# garen-sync-setup

Maintains `C:\Users\garet\sync-setup\` (`~/sync-setup/` on Mac) — Garen's config repo synced
across **4 devices**: H255 (Proxmox), Mac Mini M2, MacBook Pro M1, 5090 Windows PC.

This skill is the captured experience of building the integrated web-LLM preferences/memories.
The layout and rules below are non-obvious — follow them instead of guessing.

## Step -1: Pre-flight (always do this first)

1. Read `~/sync-setup/README.md` — the folder map. If it's missing, recreate it (template in `references/folder-map.md`... or reconstruct from the table below).
2. Read `~/.claude/CLAUDE.md` — the **source of truth** for preferences + the verification discipline that gets ported to web.
3. `ls ~/sync-setup/5-sources/` — anything outside `obsolete/` is a **new, unconsumed** input to integrate.
4. Confirm with the user which task they want (integration / AGENTS sync / README refresh) before editing.

## Folder map

| Dir | What | Action when triggered |
|-----|------|------------------------|
| `1-plugins/` | Installed Claude Code plugins | README = the install list; refresh from actually-installed plugins so all devices match |
| `2-mcps/` | Installed MCP servers | same — README mirrors installed MCPs |
| `3-skills/` | Installed skills | same — README mirrors installed skills |
| `4-hooks/` | Installed hooks | same — README mirrors installed hooks |
| `5-sources/` | Raw per-platform exports (inbox) | Consume → write to `6-integrated/`, then move sources to `5-sources/obsolete/` |
| `6-integrated/` | **Generated output** for web LLMs | `personal-preferences*.md` + `memories.md` live here |
| `7-stakeland/` | Stakeland project `claude.local.md` | Project-specific only — **leave alone** unless asked |

## Core task A: Integrate `5-sources/` → `6-integrated/`

Two outputs: **personal-preferences** (behavioral) and **memories** (facts). Keep them separate —
behavioral rules never go in memories; facts never go in preferences.

### A1. personal-preferences (master + per-platform trims)

Source of truth is `~/.claude/CLAUDE.md` plus any new raw prefs in `5-sources/`.

**Master** `6-integrated/personal-preferences.md` — English-primary (matches the now-English CLAUDE.md):
- **INCLUDE**: conversation style, language (reply in Traditional Chinese; Japanese N4-N5 correction), the **verification philosophy** ported from CLAUDE.md, stack/tooling/hardware as domain reference, NEVER (web-relevant subset).
- **PORT the verification philosophy, STRIP the orchestration mechanics.** Web LLMs have no subagents. Drop: Phased Orchestration, Subagent Contract, Model Selection (Haiku/Sonnet), Dispatch, Agents table, Custom Skills location, the Workspace dir map, Compact Instructions. Keep the *spirit*: state what "done" looks like, cite evidence not guesses, read before claiming, give a rollback path, say "I don't know" rather than fabricate.
- **Do not resurrect cut lines.** Lines deleted from CLAUDE.md (e.g. "Think outside the box", "Always reason thoroughly") must stay deleted.

**Per-platform trims** — see `references/platform-specs.md` for exact formats. Summary:
- `personal-preferences-gemini.md` — concise bullet facts for Gemini "Saved info".
- `personal-preferences-chatgpt.md` — **must be < 1500 chars** (ChatGPT custom-instructions box limit). Most essential only.
- `personal-preferences-claude-ai.md` — for Claude.ai personal preferences; skip what Claude already does well, keep verification + language + stack.

### A2. memories (consolidated facts)

`6-integrated/memories.md` — one deduplicated master of facts (identity, career, projects, hardware,
lifestyle, legal/compliance, dated events).

- **Deduplicate** across all raw sources — one authoritative line per fact.
- **Convert relative dates to absolute** (use today's date).
- **Facts only.** A raw line that's actually an instruction ("always use pnpm") → note it in the bottom
  "Notes for downstream review" section as "belongs in preferences", don't put it in the facts body.
- **SANITIZE before writing.** This is mandatory and security-critical — read `references/sanitization.md`.
- Optional richer infra: `S:/git/10-my-infrastructure/index.html` is the homelab single-source-of-truth.
  Pull the 4-host roles + locked architecture decisions from it, but apply the same sanitization.

### A3. Move consumed sources to obsolete

After integrating, `git mv` every consumed file in `5-sources/` into `5-sources/obsolete/`.
This keeps `5-sources/` root clear so the user knows anything there next time is new.

### A4. Coding skill (web mirror of `~/.claude/rules/`)

`6-integrated/skills/coding/SKILL.md` is the web-LLM equivalent of `~/.claude/rules/` — web LLMs have
no auto-loaded `rules/`, so coding standards ship as a skill the user adds manually (Claude.ai Skills /
ChatGPT Project / Gemini Gem). When `~/.claude/rules/` changes, regenerate this file to match. It is a
hand-added skill, NOT pasted like the preference files — see `6-integrated/README.md` for the per-platform
"how to add" table.

## Core task B: Sync AGENTS.md with CLAUDE.md

`~/.codex/AGENTS.md` must carry the same preferences as `~/.claude/CLAUDE.md`. Windows symlinks are
fragile across git + Mac, so we **copy** via a script (single home, DRY):

```bash
bash ~/sync-setup/6-integrated/scripts/1-sync-agents-md.sh    # Mac / Git Bash
# Windows: ~/sync-setup/6-integrated/scripts/1-sync-agents-md.bat (thin wrapper that calls the .sh)
```

It copies CLAUDE.md into AGENTS.md, mapping Claude model names to GPT (Opus→GPT-5.5, Sonnet→GPT-5.4,
since Codex runs GPT), plus a "do not edit directly" header. Paths use `~`/`$HOME` so they work from
any cwd on both OSes.
**Re-run this whenever CLAUDE.md changes.** Verify: `wc -l` of AGENTS.md = CLAUDE.md + 3 header lines.

## Core task C: Refresh device-sync READMEs (1-plugins … 4-hooks)

Each README is the install list that keeps all 4 devices' plugins/mcps/skills/hooks identical.
When asked to refresh, derive each from what is **actually installed** on the current machine
(don't hand-edit from memory), so a fresh device can reproduce the setup from the README.

## Verification (always run before reporting done)

Zero-trust: verify your own output, don't assume the edits landed.

```bash
cd ~/sync-setup/6-integrated
# 1. orchestration mechanics must NOT leak into web prefs
grep -inE "subagent|orchestrat|phased|haiku|sonnet|dispatch|spawn" personal-preferences.md || echo CLEAN
# 2. ChatGPT trim under limit
wc -c personal-preferences-chatgpt.md   # must be < 1500
# 3. sanitization (see references/sanitization.md for the full battery)
grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' memories.md | grep -vE '192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.' || echo "no public IPs"
grep -nE '([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}' memories.md || echo "no MACs"
# 4. sources cleared
ls ~/sync-setup/5-sources/   # should be just obsolete/
```

## Commit

This is a personal config repo — direct commits to `main` are the established pattern (attribution
disabled globally). Stage only the sync-setup files you changed; never stage `.claude/projects/`
(auto-managed memory). Don't push unless asked.

```
refactor(web): <what changed>
```

## Reference files

- `references/sanitization.md` — **mandatory** redaction rules + verification grep battery before sharing memories.
- `references/platform-specs.md` — exact per-platform output formats and the ChatGPT char limit.


## Relationship

```
~/.claude/CLAUDE.md  ──(去掉 orchestration 機制、抽哲學)──►  master personal-preferences.md
    (CLI 真相來源)                                              (web 母本)
                                                                    │ 衍生
                                                                    ▼ 3 平台裁剪版
```
- 所以是 CLAUDE.md ⊃ master：master 是 CLAUDE.md 的「web 可用子集」。/garen-sync-setup 重生時就是讀 CLAUDE.md→產 master→產 3 裁剪版。
- **`~/.codex/AGENTS.md` ≈ CLAUDE.md**（近乎逐字：3-line header + 全文，但 Claude model 名映射成 GPT — Opus→GPT-5.5、Sonnet→GPT-5.4，因為 Codex 跑 GPT）。是 **superset**（非 subset，與 master 相反）。**gitignored** — 被 `.gitignore` 預設 `*` 吃掉，與 `config.toml` 同理：每台機器由 `6-integrated/scripts/1-sync-agents-md.sh`（Windows: `.bat`）重生，不入版控（避免在 git 裡複製 CLAUDE.md 一份造成 drift）。

完整關係：

```
CLAUDE.md ──header + model名映射(Opus→GPT-5.5/Sonnet→GPT-5.4)──► AGENTS.md (Codex, gitignored, superset)
    └──去 orchestration──► personal-preferences.md (master)
                              └──► chatgpt / gemini / claude-ai 裁剪版
```

- **⚠ 沒有任何東西自動同步。** 改了 `CLAUDE.md` 後，**兩個都要重跑**，否則下游 stale：
  1. `/garen-sync-setup` → 重生 master + 3 trims
  2. `bash ~/sync-setup/6-integrated/scripts/1-sync-agents-md.sh`（Windows `.bat`）→ 重生 AGENTS.md
- 對應的 web 端說明同步寫在 `6-integrated/README.md`（paste 位置 + 此關係圖）。