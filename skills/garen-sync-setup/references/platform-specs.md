# Per-platform output specs

Four preference files in `6-integrated/`. One master + three trims. Same facts, different shape and
length per platform's import mechanism.

## `personal-preferences.md` (master)

- English-primary (matches the now-English CLAUDE.md).
- Full sections: General Conversation Preference, Verification Philosophy, Language, Stack,
  Tooling & Hardware, NEVER.
- This is the canonical version; the trims are derived from it.

## `personal-preferences-gemini.md` (Gemini "Saved info")

- Gemini stores preferences as discrete saved facts/bullets.
- Format: concise standalone bullets, each self-contained (Gemini may surface them individually).
- No long preamble. ~1–2 KB is fine.

## `personal-preferences-chatgpt.md` (ChatGPT custom instructions)

- **HARD LIMIT: < 1500 characters.** The custom-instructions box truncates beyond that.
- Include only the highest-value items: conversation style, reply language, the core verification
  rules, the NEVER list, and a one-line stack summary.
- Verify: `wc -c personal-preferences-chatgpt.md` must be < 1500.
- If it won't fit, cut domain reference (stack details) before cutting behavioral rules.

## `personal-preferences-claude-ai.md` (Claude.ai personal preferences)

- Claude already follows good defaults, so don't repeat generic "be helpful" content.
- Keep: verification philosophy, language preference (Traditional Chinese + Japanese correction),
  stack/domain reference, NEVER.
- Similar length to the master is fine.

## What never goes in any of these

CLI-only mechanics from CLAUDE.md: Phased Orchestration, Subagent Contract, Model Selection,
Dispatch, Agents table, Custom Skills location, Workspace dir map, Compact Instructions.
Web LLMs have no subagents — these are noise there.
