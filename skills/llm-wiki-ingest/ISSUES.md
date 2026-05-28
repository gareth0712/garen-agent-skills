# ISSUES.md — Known limitations and open risks

This file tracks known limitations, untested assumptions, and open risks for the llm-wiki-ingest skill. It exists because some problems cannot be fixed today but must not be forgotten.

**Distinction from TEST.md:** TEST.md validates what the skill DOES handle. ISSUES.md documents what the skill MIGHT NOT handle, or handles in ways that haven't been proven in production.

**Distinction from patterns.md:** patterns.md documents workflows that work. ISSUES.md documents workflows that are untested, partially working, or known to have edge cases.

---

## Active Issues

### Issue #1: Skill is untested in production by anyone except the author

**Severity:** HIGH — the skill's reliability is theoretical until validated by independent use

**Description:**
The skill was authored in session 2026-04-11 by a single agent (Claude Opus) based on that session's experience with real ingests. It was validated by 2 cold-start subagent tests in isolated fixtures, and all 19 TEST.md scenarios were written based on failures observed during that session.

However, the skill has NOT been used for a real ingest by:
- A fresh Claude session (without session 2026-04-11 context)
- A human user following the skill manually
- Any session other than the one that wrote it

**Why this matters:**
A closed loop of "author tests own work" catches obvious bugs but misses assumptions the author took for granted. Real validation requires independent use.

**How to resolve:**
On the next new raw file ingest, start a fresh Claude session. Don't reference this session's memory. Let the fresh session discover and invoke the skill. Observe where it struggles or makes wrong assumptions. Those observations become new TEST.md scenarios (or ISSUES.md entries).

**Workaround until resolved:**
Treat the skill as a hypothesis, not a validated tool. When it fails in a new way, update the skill rather than forcing the ingest through manually.

---

### Issue #2: 19 scenarios may be too many to run regularly

**Severity:** MEDIUM — if TEST.md is never run, its value is zero

**Description:**
TEST.md has 19 scenarios. Running all of them against isolated fixtures takes significant time and token budget. If the user never runs TEST.md because it's too long, the tests provide no regression protection.

**Why this matters:**
Tests only catch regressions if they run. A test suite that's too large to run is functionally equivalent to no tests at all.

**How to resolve:**
Add a "Test tier" system to TEST.md:
- **Smoke tests (2 scenarios):** Scenarios 1 + 2 — run after every skill change
- **Core tests (8 scenarios):** Scenarios 1-8 — run weekly or before sharing
- **Full suite (19 scenarios):** All scenarios — run monthly or before major version bumps

Alternatively, tag each scenario with which skill files trigger its re-run. E.g., "if you edited format-conversion.md, run Scenarios 1, 2, 9, 16, 17."

**Workaround until resolved:**
Default to running Scenarios 1 and 2 only after changes. Run the full suite only when the user explicitly asks or at scheduled intervals.

---

### Issue #3: Skill is large (~3,300 lines) — subagents may skim and miss details

**Severity:** MEDIUM — comprehensive skill may not improve behavior if not fully read

**Description:**
The skill spans 6 files totaling ~3,300 lines. Cold-start subagents have limited attention and may skim the files rather than read them in full, particularly the supporting files (patterns.md, quality-gates.md).

**Why this matters:**
The skill's reliability depends on subagents internalizing ALL relevant sections before executing. If a subagent reads SKILL.md but skims format-conversion.md, a pattern like Unknown Format Handling may be missed.

**Symptoms to watch for:**
- Subagent makes a decision that contradicts a rule documented in a supporting file
- Subagent cites SKILL.md but not patterns.md in its reasoning
- Subagent's output shows a gap that IS covered in the skill but wasn't applied

**How to resolve:**
1. Keep SKILL.md as the "required reading" entry point — it should be self-contained enough that an agent can start from it alone
2. Treat supporting files as "branch when needed" references, not mandatory reading
3. Add explicit "STOP and read X.md before proceeding" callouts in SKILL.md at the exact points where branching is required
4. Consider extracting a "SKILL-QUICKSTART.md" (~100 lines) that covers the 80% case, with pointers to the full SKILL.md for edge cases

**Workaround until resolved:**
When spawning subagents, explicitly list which skill files they must read in full versus which they should reference as needed. Don't assume the subagent will branch correctly on its own.

---

### Issue #4: Some TEST.md scenarios may be wrong or incomplete

**Severity:** MEDIUM — if tests encode wrong assumptions, fixing code to match breaks real use

**Description:**
TEST.md scenarios 9-19 (the ones added in the final push before compaction) were written based on patterns.md content, not based on actual test runs. Scenarios 1-8 were written from real test observations.

**Why this matters:**
A scenario written from memory may encode the WRONG expected behavior. If a future session runs such a scenario and the skill "fails" it, they might "fix" the skill to match the wrong expectation, breaking real-world use.

**Scenarios at risk (not validated by actual runs):**
- Scenario 9 (Newsletter consolidation) — based on recollection of 96-article ingest
- Scenario 10 (Notion export handling) — based on recollection of 151-file web3-wiki ingest
- Scenario 11 (Cross-domain meta-wiki) — based on the session's build of cross-domain/
- Scenario 12 (Monorepo restructuring) — based on session's garen-wiki split
- Scenario 13 (Proprietary content) — based on Memeland/Memeverse patterns
- Scenario 14 (Contradiction flagging) — based on Lido 5% vs 10% real case
- Scenario 15 (Append-only log) — based on Morpho correction pattern
- Scenario 16 (Script failure) — based on Substack mhtml_to_md observation
- Scenario 17 (Backtick generics) — based on 32 fixes across 11 files
- Scenario 18 (Verification script) — based on verify-wiki.sh design, never run
- Scenario 19 (Cold-start audit) — based on master index creation

**How to resolve:**
Run each scenario at least once against a real fixture. Mark scenarios as "validated" (v) or "unvalidated" (u) in TEST.md. Unvalidated scenarios should be treated as hypothesis tests — a failure there means "investigate", not "fix the skill".

**Workaround until resolved:**
When a scenario fails, before fixing the skill, verify the scenario's expected behavior is actually correct. If it's not, fix the scenario first.

---

### Issue #5: Skill was written with heavy reliance on session context

**Severity:** LOW — content is sound but provenance matters for future updates

**Description:**
Many skill decisions (page count heuristics, thematic grouping patterns, slug collision rules) were extrapolated from a single session's experience. A larger sample size might reveal that some of these patterns don't generalize.

**Why this matters:**
The page count heuristic table in SKILL.md Step 4 says "1 source summary + 2-5 concept/technique pages" for a typical chapter. This was based on observations in ood/wiki and system-design/wiki. A different domain (e.g., legal research, medical literature) might produce very different ratios.

**How to resolve:**
Over time, as the skill is used in diverse domains, update the heuristics with real observed ranges. Add domain-specific notes if patterns diverge.

**Workaround until resolved:**
Treat numerical heuristics as guidelines, not hard rules. If a real ingest consistently produces counts outside the heuristic range without obvious over/under-fragmentation, update the heuristic.

---

### Issue #6: No versioning or changelog for the skill

**Severity:** LOW — hard to trace which version of the skill produced which wiki state

**Description:**
The skill has no version number or changelog. If the skill is updated and a future session needs to know "which version of the skill did we use for the Lido ingest?", there's no way to tell.

**Why this matters:**
When the skill evolves, existing wiki pages will have been produced by older versions. Debugging "why does this page look different?" requires knowing the skill version at production time.

**How to resolve:**
Add a `version:` field to SKILL.md frontmatter. Increment on any substantive change. Keep a `CHANGELOG.md` in the skill directory with entries per version.

**Workaround until resolved:**
Use git log on the skill directory to see what changed when. The `logs-subagents/` action logs in the wiki repo also capture some of this history.

---

### Issue #7: No direct validation that format-conversion.md scripts actually work

**Severity:** LOW — templates may have bugs that won't surface until used

**Description:**
The Python templates in format-conversion.md (minimal mhtml_to_md, minimal html_to_md, SRT strip function) are included verbatim from similar working scripts but have not been run in isolation as part of this skill's development.

**Why this matters:**
A cold-start agent may copy-paste the minimal template and find it doesn't work. This would erode trust in the skill.

**How to resolve:**
Test each template script against a real source file in an isolated environment. Fix any bugs. Mark tested templates with a comment like `# Validated against <fixture> on <date>`.

**Workaround until resolved:**
Treat the templates as starting points, not guaranteed-working code. If a template fails, inspect the error and adapt.

---

## Resolved Issues

(Move issues here when they are validated or fixed. Keep the record for history.)

None yet.

---

## How to Use This File

**When encountering a new problem:**
1. Check if it matches an existing issue here — if yes, apply the workaround
2. If not, add a new entry with severity, description, and how to resolve

**When fixing an issue:**
1. Implement the fix in the skill
2. Run the relevant TEST.md scenarios to verify
3. Move the issue to "Resolved Issues" with the fix date and what was done

**When compacting:**
This file is institutional memory. It should survive compaction. A fresh session reading the skill should read ISSUES.md before trusting anything.

---

## Principle

Every issue here exists because a REAL risk was identified, not a speculative "what if". If a risk isn't real or actionable, it doesn't belong here. If a risk IS real but we can't fix it today, it MUST belong here.

The goal is to prevent the next session from rediscovering problems we already know about.
