# Audit Checklist

Structured criteria from "The CLAUDE.md File That 10x'd My Output" and production CLAUDE.md best practices.

## Check 1: Line Count Budget

| Scope | Recommended | Max |
|-------|-------------|-----|
| Global | ≤80 | ≤150 |
| Project | ≤60 | ≤100 |
| Local | ≤30 | ≤50 |

Verdicts: ✅ within recommended | ⚠️ over recommended, under max | ❌ over max

## Check 2: Critical Sections (the 5 that matter)

### Project-scope CLAUDE.md (all 5 expected):
1. **Commands** — build, dev, test, lint, type check
2. **Architecture** — folder → purpose mapping
3. **Rules/NEVER** — hard constraints preventing specific mistakes
4. **Workflow** — how Claude should approach tasks
5. **Out of scope** — files/areas Claude should not touch

### Global-scope CLAUDE.md:
Sections 1-2 (Commands, Architecture) are usually CORRECTLY ABSENT — they're project-specific.
Sections 3-5 should be present (including Out of scope — it prevents Claude from touching files managed by other tools).

### Detection heuristics:
- Commands: grep for `## Command` / `build:` / `dev:` / `test:` / `lint:`
- Architecture: grep for `## Arch` / `→` / `folder` / `directory`
- Rules: grep for `## Rule` / `## NEVER` / `IMPORTANT`
- Workflow: grep for `## Workflow` / `## Role` / `## Process`
- Out of scope: grep for `## Out of` / `## Don't` / `## Scope`

## Check 3: Hard Rules Quality — The Removal Test

For each rule in NEVER/Rules section:
> "Would removing this line cause Claude to make a specific mistake?"

**Flag as vague** (fails removal test):
- "Write clean code" / "Follow best practices" / "Be thorough"
- "Think before acting" / "Write maintainable code"
- Anything a linter/formatter already enforces

**Keep** (passes removal test):
- "NEVER commit .env files" — prevents secret leaks
- "pnpm only, no npm/yarn" — prevents toolchain mismatch
- "Static export only, no SSR" — prevents wrong deployment mode
- "Run type check after every code change" — prevents broken types

## Check 4: Personality Instructions

Detect lines describing WHO Claude should be rather than WHAT to do:

Patterns to flag:
- "You are a senior engineer"
- "Act as an expert in..."
- "Think step by step"
- "Be a careful programmer"
- "Think outside the box"
- "Always reason thoroughly before answering"

**Exception**: Role instructions that change output level are valid:
- "I am a junior developer — explain with examples" ✅ (changes explanation depth)
- "Be brutally honest, challenge flawed thinking" ✅ (prevents default over-politeness)

Test: does the line change Claude's observable output? If only its "mindset," flag it.

## Check 5: Auto-Memory-Learnable Content

Content Claude's auto-memory picks up after 1 session:

- Format preferences ("use tables", "use bullet points", "prefer lists")
- Output style ("be concise", "no emojis", "show code only")
- Personal details already stored in `~/.claude/projects/*/memory/`
- Project facts discoverable from reading code or git history

If `/memory` shows Claude already knows something, that line in CLAUDE.md is wasted instruction budget.

## Check 6: IMPORTANT Marker Usage

Anthropic docs confirm IMPORTANT / YOU MUST improves adherence.

| Check | Good | Bad |
|-------|------|-----|
| Most-violated rules marked? | ✅ | ❌ Unmarked critical rules |
| Total IMPORTANT count | 2-4 | >4 (dilutes impact) |
| On genuinely critical rules? | ✅ Security, verification | ❌ Style preferences |

## Check 7: NEVER Section Size

**Target**: ≤15 rules.

Over 15 → Claude starts dropping rules. Triage by impact:
1. Security (env, secrets, auth) — keep
2. Tool/framework constraints (pnpm, viem) — keep
3. Workflow (verify before claim) — keep
4. Style preferences — move to `rules/` or auto-memory

## Check 8: Cross-Scope Duplication Detection

For each rule, check if it appears in multiple places:

| Duplication Type | Resolution |
|---|---|
| Same rule in Global AND Project | Keep in Global, remove from Project |
| Same rule in CLAUDE.md AND rules/*.md | Keep in rules/ (purpose-built), remove from CLAUDE.md |
| Same rule in CLAUDE.md AND auto-memory | Remove from CLAUDE.md |
| Project overrides Global intentionally | Keep both, add comment explaining override |

Article principle: "if global says 'run tests,' project doesn't repeat it."
When content exists in both CLAUDE.md and rules/, prefer rules/ — it's auto-loaded and purpose-built.
