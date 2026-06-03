## CLAUDE.md Audit Report

### Files Discovered

| Scope | Path | Exists | Lines | Budget | Status |
|-------|------|--------|-------|--------|--------|
| Global | `C:\Users\garet\.claude\CLAUDE.md` | ✅ | 108 | ≤80 rec / ≤150 max | ⚠️ over recommended |
| Project | `.claude/CLAUDE.md` (CWD: `C:\Users\garet`) | ✅ (same as global) | — | — | N/A (CWD is home dir, no separate project file) |
| Local | `CLAUDE.local.md` (CWD) | ❌ | — | — | Not found |
| Rules | `C:\Users\garet\.claude\rules\common\` | ✅ | 391 (9 files) | auto-loaded | ✅ |

> Note: The CWD when `/garen-memory-clean-up` was invoked is `C:\Users\garet`, which means `.claude/CLAUDE.md` resolves to the same file as the global. No standalone project-level CLAUDE.md was found in a code repository context. Audit treats only one file as in-scope: the global.

Rules files present: `agents.md`, `coding-style.md`, `git-workflow.md`, `hooks.md`, `patterns.md`, `performance.md`, `security.md`, `skill-development.md`, `testing.md`

---

### Section Coverage Scorecard

| Article Section | Global | Project | Local | Notes |
|---|---|---|---|---|
| 1. Critical commands | N/A | — | — | Correctly absent from global |
| 2. Architecture map | N/A | — | — | Correctly absent from global; workspace table at line 56 is a partial substitute |
| 3. Hard rules (NEVER) | ✅ | — | — | Lines 71–81, 9 rules |
| 4. Workflow preferences | ✅ | — | — | Role, Phased Orchestration, Task Contract, Dispatch all present |
| 5. Out of scope | ✅ | — | — | Lines 83–85 |

---

### Anti-Pattern Detection

| Anti-pattern | Found? | Lines | Verdict |
|---|---|---|---|
| Personality instructions | Borderline | 19–21 | "You should be 95% sure before you move on" / "Ask any hard questions" — these describe a mindset, not a concrete action. They don't clearly change observable output. Flag for removal test. |
| Auto-memory-learnable | Yes (partial) | 2–11 | Several conversation preferences (answer briefly, prefer tables, prefer action lists, no emojis) are format styles Claude learns after 1 session. Exception: "Be brutally honest / Challenge flawed thinking" (line 6) passes the output-change test and should stay. |
| Vague/non-actionable rules | Yes (minor) | 19–21 | "Be 95% sure before you move on" is not actionable — Claude cannot measure certainty. Similarly "Ask any hard questions" is vague. |
| >15 rules in NEVER | No | 71–81 | 9 rules — well under limit ✅ |
| Missing IMPORTANT markers | No | 76–80 | 3 IMPORTANT markers on the most-violated rules ✅ |
| Excessive IMPORTANT (>4) | No | 76–80 | 3 total — within 2–4 target ✅ |

---

### Cross-Scope Duplications

| Rule/Content | Scope A | Scope B | Keep in | Savings |
|---|---|---|---|---|
| Agent dispatch rules (Parallel/Sequential/Background) | Global CLAUDE.md line 54 (quick ref) | `rules/common/agents.md` lines 67–84 | `rules/common/agents.md` | Line 54 in CLAUDE.md can be deleted — agents.md is auto-loaded and is authoritative |
| Model selection (Haiku/Sonnet/Opus) | Global CLAUDE.md line 54 (quick ref) | `rules/common/performance.md` lines 1–18 | `rules/common/performance.md` | Same as above — the quick-ref summary on line 54 is redundant once rules/ is loaded |
| Subagent contract / quality requirements | Global CLAUDE.md lines 50, 52–54 | `rules/common/agents.md` lines 86–92 | `rules/common/agents.md` | CLAUDE.md line 50 ("Subagent dispatch: Task Contract goes into subagent prompt verbatim…") has overlap with agents.md subagent quality requirements |
| Read-before-claim discipline | Global CLAUDE.md lines 95–108 | Could live in `rules/common/` | Move to `rules/common/speculation.md` (new) or keep | These 14 lines are high-value but belong in rules/ — keep CLAUDE.md lean |
| Compact Instructions | Global CLAUDE.md lines 87–93 | Nowhere in rules/ | Keep in Global | Compaction behavior is runtime-specific, must stay in CLAUDE.md |
| "Prefer table format / action lists / documentation style" | Global CLAUDE.md lines 9–10 | Auto-memory | Remove from CLAUDE.md | Claude learns these preferences after first session |

---

### Action Items (Priority-Ordered)

| # | Action | Priority | File | Est. Savings |
|---|---|---|---|---|
| 1 | Remove conversation format preferences that auto-memory learns (lines 9–10: "Prefer table format", "Prefer action lists with priority ordering", "Documentation style…") | Medium | Global CLAUDE.md | ~3 lines |
| 2 | Remove line 54 quick-ref for agents/model/dispatch — it duplicates `rules/common/agents.md` + `rules/common/performance.md` which are auto-loaded | High | Global CLAUDE.md | ~1–2 lines |
| 3 | Move "Read-before-claim / No speculation" section (lines 95–108) to a new `~/.claude/rules/common/speculation.md` and replace with a 1-line pointer | Medium | Global CLAUDE.md | ~12 lines saved |
| 4 | Tighten lines 19–21 ("95% sure", "Ask any hard questions") — either convert to concrete NEVER rules or delete as unmeasurable personality instructions | Low | Global CLAUDE.md | ~2 lines |
| 5 | Consider splitting "Task Contract" detail (lines 34–50) into a rules/ file — it's 17 lines of process documentation that only needs a 1-line trigger in CLAUDE.md | Low | Global CLAUDE.md | ~12 lines (if moved) |

---

## Suggested Edits

### 1. Remove auto-memory-learnable format preferences (High impact, safe)

**File**: `C:\Users\garet\.claude\CLAUDE.md`
**Lines**: 9–10

```
- Documentation style: extremely concise, front-load critical info, prefer examples over prose, delete verbose explanations. Engineers scan, not read.
- When I request a prompt or any copyable text, ALWAYS wrap the entire copyable content in a single markdown code snippet (```markdown ... ```) so I can select-all in one go
```

Lines 9–10 are format preferences. The "ALWAYS wrap in code snippet" on line 11 does pass the removal test (prevents a specific formatting failure). Keep line 11. Delete line 10 ("Documentation style...") — Claude learns this from auto-memory.

**Why**: Saves ~1 line, reduces instruction budget, no behavior loss after first session.

---

### 2. Remove duplicate agent/dispatch quick-ref on line 54

**File**: `C:\Users\garet\.claude\CLAUDE.md`
**Line 54**: `Quick ref: Haiku = read-only/mechanical | Sonnet = reasoning | Parallel = independent tasks | Sequential = dependencies`

**Delete** this line entirely. The authoritative definitions live in `rules/common/agents.md` and `rules/common/performance.md` which are auto-loaded every session.

**Why**: Pure duplication. If these rules ever update in `rules/`, the CLAUDE.md quick-ref will drift and become misleading.

---

### 3. Move "Read-before-claim / No speculation" to rules/ (Medium impact)

**File**: `C:\Users\garet\.claude\CLAUDE.md`
**Lines 95–108**: Entire "Read-before-claim / No speculation" section

**Action**: 
1. Create `~/.claude/rules/common/speculation.md` with the full content from lines 95–108
2. Replace lines 95–108 in CLAUDE.md with a single pointer:
   ```
   ## Read-before-claim ✅
   → Defined in `~/.claude/rules/common/speculation.md` (auto-loaded every session).
   ```

**Why**: The content is high-value and should be preserved, but keeping 14 lines of it in CLAUDE.md when rules/ is auto-loaded wastes the global instruction budget. The pointer pattern is already used for agents at line 53.

---

### 4. Tighten lines 19–21 personality/vague instructions

**File**: `C:\Users\garet\.claude\CLAUDE.md`
**Lines 19–21**:
```
- If scope unclear, ask before spawning.
- You should be 95% sure before you move on
- Ask any hard questions to make sure you 100% understand the requirements
```

Line 19 passes the removal test (prevents premature spawning). Keep.
Lines 20–21: "95% sure" is unmeasurable. "Ask any hard questions" is vague.

**Replace** lines 20–21 with:
```
- If requirements are ambiguous, list your assumptions and ask for confirmation before spawning
```

**Why**: Converts vague mindset instruction into a concrete, observable action (list + ask). One line instead of two.

---

## Cold-Start Test Report

### Steps that were clear and actionable

1. **Step 0 (Discovery)** — The 3-level hierarchy table (Global / Project / Local / Rules) was clear. Paths were explicit. "Check existence → read content → record line count" was unambiguous.
2. **Step 1 (Per-File Audit)** — The numbered check list was actionable. Linking to `references/audit-checklist.md` for detection heuristics was the right pattern.
3. **Step 3 (Report template)** — The exact template was provided with column definitions. Status column legend (✅/⚠️/❌) was defined at the bottom.
4. **Line Count Budgets table** — Explicit numbers made the budget check mechanical.
5. **Step 5 (Wait for user decision)** — Clear constraint: do NOT make edits without approval.
6. **What Belongs Where table** — Useful for the cross-scope analysis, especially the `rules/` row.

### Steps that were vague or missing

1. **Step 0 — "Project" scope ambiguity**: The skill says "Project: `.claude/CLAUDE.md` (repo root)" but when the CWD is the user's home directory, `.claude/CLAUDE.md` resolves to the same file as the global. The skill has no instruction for this edge case. I had to decide on my own to note it as N/A.

2. **Step 1 — Which checks apply to Global vs Project**: The checklist (Check 2) explicitly says "Sections 1-2 (Commands, Architecture) are usually CORRECTLY ABSENT" from global scope — but the Step 1 instructions just say "run ALL checks." There's a contradiction. The checklist resolves it, but only if you read it carefully.

3. **Step 2 — "Auto memory" check**: The skill says check "Any scope ↔ Auto memory — content Claude learns automatically." But there's no instruction on HOW to determine what's in auto-memory (no path to the memory files, no command to inspect them). I had to reason from the checklist's description alone.

4. **Step 4 — "High/Medium priority" not defined before Step 3**: Step 4 says "For each High/Medium priority action item" — but priority levels aren't defined until the agent fills in the Action Items table in Step 3. This is fine but the skill doesn't note that Step 3 must be completed before Step 4.

5. **"Out of scope" section check**: The checklist (Check 2) lists "Out of scope" as section 5 expected in project-scope CLAUDE.md, but doesn't clearly state whether it's expected in the global scope. The skill's "What Belongs Where" table doesn't cover this either. I inferred it should be present globally from the example file having one.

### Decisions that required guessing

1. **Whether the home-dir `.claude/CLAUDE.md` counts as both global AND project**: The skill doesn't handle the case where CWD is `~` and `.claude/CLAUDE.md` is the same file as global. I guessed: treat as global only, mark project as N/A.

2. **Auto-memory content detection without access to `~/.claude/projects/*/memory/`**: The checklist references auto-memory files but the skill doesn't instruct the agent to read them. I guessed: apply heuristics from Check 5's description (format preferences, output style) without actually inspecting the memory files.

3. **Whether "Compact Instructions" section is auto-memory-learnable**: This section is about compaction behavior specific to Claude's session management. I guessed it must stay in CLAUDE.md (it's not something auto-memory learns), but the skill gives no guidance on this.

4. **Severity of "Prefer table format" being auto-memory-learnable**: The checklist says "Format preferences ('use tables', 'use bullet points'…)" are auto-memory-learnable, but the CLAUDE.md uses a "Prefer" qualifier. I guessed this still counts as a format preference and flagged it.

### Missing information

1. **How to handle CWD = home directory**: The skill assumes a code repository context. It needs a pre-flight check: "If CWD is not a git repo, skip project-level check and note it."

2. **How to inspect auto-memory**: The skill should either (a) instruct the agent to read `~/.claude/projects/*/memory/` files and compare, or (b) explicitly say "apply heuristic from Check 5 without inspecting memory files." The current silence forces guessing.

3. **Combined line budget check**: The skill's Line Count Budgets table includes a "Combined" row (≤120 rec / ≤200 max) but Step 1 only says to check per-file. The report template has no row for combined total. Either add it to Step 1 or add a row to the template.

4. **What to do when Rules/ content is present**: The skill says rules/ files are a "common duplication source" but Step 2 doesn't give specific detection heuristics for CLAUDE.md ↔ Rules/ duplication. The checklist (Check 8) has the resolution table but no detection method.

5. **Whether "pointer lines" (e.g., `→ Defined in agents.md`) count as duplication or good practice**: The skill's cross-scope section doesn't distinguish between "duplicate rule" and "pointer to rule file." This required a judgment call.

### Edge cases encountered

1. **CWD = home directory**: `.claude/CLAUDE.md` resolves to the global file. Skill assumes a repo context.
2. **The global CLAUDE.md already uses the pointer pattern** (line 53 points to agents.md) — this is actually the ideal pattern the skill recommends, but the skill doesn't acknowledge it as a positive finding. The audit framework only catches problems, not confirm best practices.
3. **Rules/ directory has 391 lines across 9 files** — this is a significant instruction load. The skill doesn't evaluate whether rules/ files themselves are over-budget or duplicative. It only checks CLAUDE.md ↔ Rules/ duplication.

### Overall verdict

**MOSTLY** — A fresh agent with zero context can produce a useful audit from this skill alone, but with the following caveats:
- The happy path (CWD = a real project repo with a distinct project CLAUDE.md) works well
- The adversarial path (CWD = home dir, no separate project file) requires guessing
- Auto-memory detection is not actionable without explicit inspection instructions
- The combined line budget is defined in the skill but not surfaced in the report template
- The skill correctly separates detection (checklist) from template (report) — this structure is sound
