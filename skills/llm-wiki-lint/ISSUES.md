# ISSUES.md — Known limitations and open risks

This file tracks known limitations, untested assumptions, and open risks for the llm-wiki-lint skill.

**Distinction from TEST.md:** TEST.md validates what the skill DOES handle. ISSUES.md documents what the skill MIGHT NOT handle, or handles in ways that haven't been proven in production.

---

## Active Issues

### Issue #1: Skill is untested in production

**Severity:** HIGH — reliability is theoretical until independently validated

**Description:**
This skill was written in a single session based on the llm-wiki-ingest skill as a template. It has NOT been used for a real lint pass by:
- A fresh Claude session with no prior memory of this session
- A human user following the skill manually
- Any wiki other than the design-level fixture used for writing it

**Why this matters:**
Structural checks (orphan detection, broken wikilinks) are mechanically sound and likely to work. Semantic checks (Phase 2 contradiction detection) are the most uncertain — they depend on LLM reasoning quality and may behave differently on wikis with very different page types or writing styles.

**How to resolve:**
Run the TEST.md cold-start scenarios against a real wiki fixture. Start with Scenario 1 (healthy wiki). Observe where the subagent struggles or makes wrong assumptions. Each failure becomes a new TEST.md scenario or ISSUES.md entry.

**Workaround until resolved:**
Treat all Phase 2 findings as hypotheses to be verified by the user, not confirmed facts.

---

### Issue #2: Contradiction detection is fuzzy and may false-positive on restatements

**Severity:** MEDIUM — generates noise that erodes user trust in lint findings

**Description:**
Phase 2 relies on a Sonnet subagent reading pairs of pages and comparing claims. However, LLMs frequently flag restatements as contradictions:
- Page A: "Kafka guarantees at-least-once delivery by default"
- Page B: "Kafka's default delivery guarantee is at-least-once"

These are the same claim stated differently. A careless Phase 2 agent may flag them as a contradiction.

Additionally, context-dependent claims may appear contradictory out of context:
- Page A (discussing Kafka v2.x): "replication factor default is 1"
- Page B (discussing Kafka v3.x best practices): "replication factor should be 3"

These are NOT contradictions but may be flagged as such.

**Workaround:**
Phase 2 agent prompt instructs focusing on verifiable facts (percentages, dates, version numbers, protocol parameters). But this is a guideline, not a guarantee.

When reviewing a lint report, treat Phase 2 contradiction findings as "worth investigating" rather than "confirmed errors". The user should read both pages and their sources before concluding a real contradiction exists.

**How to resolve:**
Add adversarial fixture to TEST.md with pages that are restatements (should NOT be flagged) alongside true contradictions (should be flagged). Cold-start test the Phase 2 agent specifically against this fixture.

---

### Issue #3: Orphan detection misses pages referenced only from frontmatter `related`

**Severity:** MEDIUM — false positives inflate orphan counts

**Description:**
The current orphan detection logic checks for `[[page-name]]` wikilinks in page body AND in frontmatter `related:` lists. However, if a page is referenced exclusively from frontmatter `related:` fields (not in any body prose), it may or may not count as "linked in" depending on how the Phase 1 agent implements the search.

The Phase 1 agent prompt specifies checking both body text AND frontmatter `related:`. If an agent skims the prompt and only checks body wikilinks, it will over-report orphans.

**Workaround:**
The Phase 1 prompt explicitly states: "search ALL other wiki pages for any [[page-name]] reference in body text OR frontmatter `related:` field." Verify that the executing agent followed this instruction when reviewing orphan findings.

If orphan counts seem unreasonably high, manually check whether the reported orphans appear in any `related:` frontmatter field across the wiki.

**How to resolve:**
Add a TEST.md scenario where a page is referenced only via frontmatter `related:` and verify it is NOT flagged as an orphan.

---

### Issue #4: Auto-fix of broken wikilinks relies on fuzzy slug matching — could mis-link

**Severity:** HIGH — an incorrect auto-fix silently corrupts wiki content

**Description:**
The Phase 1 agent auto-fixes a broken `[[target]]` link only when "exactly one file exists with a matching base name." However, slug matching is case-sensitive in some environments and case-insensitive in others (macOS HFS+ is case-insensitive; Linux ext4 is case-sensitive). This could cause:

- `[[LidoProtocol]]` auto-fixed to `lido-protocol.md` on macOS (match found), but the link would be broken on a Linux system
- `[[rate-limiter]]` auto-fixed to `rate-limiter-pattern.md` if that is the only file containing "rate-limiter" in its name, even though `[[rate-limiter]]` was intended to link to a page that doesn't exist yet

The second case is particularly dangerous: the auto-fix creates a link to a semantically wrong page.

**Workaround:**
The Phase 1 prompt specifies "exact slug match" — `[[lido]]` matches `lido.md`, not `lido-protocol.md`. However, agents may interpret "exact match" loosely.

Until validated by a cold-start test, treat all auto-fixed broken links as candidates for manual review. The lint report's Fix Log section lists every auto-fix applied — review it before accepting the report.

**How to resolve:**
Tighten the Phase 1 prompt to require: the broken link target must match the base filename EXACTLY (character-for-character, case-sensitive, ignoring `.md` extension). Any partial match → FLAG only, never auto-fix.

---

### Issue #5: Curiosity seeds may repeat questions from past lint passes

**Severity:** LOW — cosmetic noise in questions.md, not a functional failure

**Description:**
Phase 4 generates curiosity seeds by reading the wiki's current coverage and the Phase 1-3 findings. If the same coverage gaps persist across multiple lint passes (e.g., an under-covered category that the user has not addressed), the Phase 4 agent will likely generate similar or identical questions.

The Phase 4 prompt instructs the agent to read `questions.md` in full and deduplicate. However, LLMs are imperfect at semantic deduplication — a question phrased differently may not be recognized as "substantially similar."

**Workaround:**
After appending curiosity seeds, scan `questions.md` visually for semantic duplicates. The deduplication is best-effort, not guaranteed.

**How to resolve:**
Add a TEST.md scenario where `questions.md` already contains 5 questions and verify the Phase 4 agent does not re-add substantially similar ones. Measure false-negative deduplication rate.

---

### Issue #6: Phase 2 staleness check uses a hard 6-month threshold

**Severity:** LOW — may generate noise for stable domains, miss urgency in fast-moving domains

**Description:**
The 6-month staleness threshold was chosen as a reasonable default. However:
- For protocol wikis (DeFi, chain upgrades), 3 months may already be too stale
- For architecture/algorithm wikis, 2 years may still be fine
- The threshold is hardcoded in the Phase 2 prompt, not configurable per wiki

**Workaround:**
The user can manually instruct the Phase 2 agent to use a different threshold when spawning it: "Use a 3-month staleness threshold for this pass."

**How to resolve:**
Add an optional `lint_staleness_months` setting to the wiki's `CLAUDE.md` or `WIKI.md` schema. The Phase 2 agent reads this value and uses it; falls back to 6 months if not set.

---

### Issue #7: Same missing file may appear in multiple Phase 1 checks — no deduplication rule

**Severity:** LOW — cosmetic over-counting in lint reports, not a functional failure

**Description:**
A single missing file can legitimately appear in more than one Phase 1 check. For example, `[[deprecated-pattern]]` referenced in `index.md` will be flagged by both Check 2 (Broken Wikilinks) and Check 5 (Index Sync). Similarly, a missing file referenced in `log.md` will appear in both Check 2 (Broken Wikilinks) and Check 6 (Log Reference Integrity).

SKILL.md intentionally preserves both findings (each check serves a distinct diagnostic purpose). However, this means "N structural issues" in the log entry counts the same underlying missing file multiple times, which can make reports feel noisier than the actual problem warrants.

**Workaround:**
When reviewing the lint report, look for the same missing slug appearing in multiple sections — this is expected. The log count (N structural issues) counts individual findings, not unique missing files.

**How to resolve:**
Add an optional "Deduplicated Root Causes" summary at the end of Phase 1 that groups findings by the missing file slug, showing which checks flagged it. This is a usability enhancement, not a correctness fix — do not implement until user feedback confirms it causes confusion.

---

## Resolved Issues

(Move issues here when fixed and validated. Keep for history.)

None yet.

---

## How to Use This File

**When encountering a new lint failure:**
1. Check for an existing issue entry that matches — apply the workaround
2. If none, add a new entry with: severity (HIGH/MEDIUM/LOW), description, why it matters, workaround, how to resolve

**When fixing an issue:**
1. Implement the fix in SKILL.md or agent-prompts.md
2. Run the relevant TEST.md scenario to verify
3. Move the issue to "Resolved Issues" with the fix date and what was changed

**When compacting:**
This file is institutional memory. A fresh session must read ISSUES.md before trusting Phase 2 contradiction findings or Phase 1 auto-fixes.
