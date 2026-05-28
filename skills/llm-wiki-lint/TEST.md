# TEST.md — Validation scenarios for llm-wiki-lint

This file documents every test scenario the skill must handle. Run these whenever the skill is modified to catch regressions.

## How to Use This File

**When to run:**
- After any non-trivial edit to SKILL.md or agent-prompts.md
- Before sharing the skill with another user or session
- When a real lint pass fails in a way the skill should have prevented — add the new failure as a new scenario
- Periodically (monthly) as a regression check

**How to run:**
1. Create isolated temp fixture directories (never pollute production workspace)
2. Populate fixtures per the scenario's setup instructions
3. Spawn a fresh Sonnet subagent with the cold-start prompt template at the bottom of this file
4. Compare actual output to expected behavior
5. Clean up temp fixtures after completion
6. If a scenario fails, fix the skill directly — do not fix the test

**Key principle:** Use adversarial fixtures. Happy-path tests pass easily; edge cases are where gaps hide.

---

## Scenario 1: Healthy Wiki — Full Pass, Verdict PASS

**Goal:** Verify all 5 phases run cleanly on a structurally sound wiki and produce a PASS verdict with curiosity seeds generated.

**Setup:**
```
lint-test-1/
├── CLAUDE.md                    # minimal schema with page types
├── wiki/
│   ├── index.md                 # valid frontmatter, all pages listed
│   ├── log.md                   # valid frontmatter, 2 prior ingest entries
│   ├── overview.md              # valid
│   ├── concepts/
│   │   ├── consistent-hashing.md     # valid: frontmatter, Connections section, sources, wikilinks
│   │   ├── bloom-filter.md           # valid
│   │   └── rate-limiting.md          # valid, linked to from consistent-hashing
│   ├── techniques/
│   │   └── circuit-breaker.md        # valid
│   ├── source-summaries/
│   │   └── system-design-primer.md   # valid, references multiple concepts in related
│   └── protocols/
│       └── consistent-hashing-protocol.md  # valid
```

Use real wiki page content (copies from garen-wiki or web3-wiki). All pages must:
- Have valid frontmatter (all 6 fields)
- Have Connections sections
- Have Sources sections
- Have no broken wikilinks
- All be listed in index.md
- Have no conflicts in factual claims

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Run a full wiki lint pass on the wiki at `lint-test-1/` using the llm-wiki-lint skill at `~/.claude/skills/llm-wiki-lint/`. TODAY'S DATE: [inject actual date]. You are running phases 1-5 as a single agent (no parallel subagents). Write the lint report to `lint-test-1/wiki/lint-reports/[TODAY]-lint.md`. Append curiosity seeds to `lint-test-1/wiki/questions.md`. Report: which skill sections were clear, which were unclear, and your honest assessment of whether the skill gave you everything you needed.

**Expected behavior:**
- Agent reads SKILL.md fully before starting
- Agent runs Session Startup (reads CLAUDE.md and wiki/index.md)
- Phase 1: zero orphans, zero broken links, zero missing frontmatter, zero duplicate slugs
- Phase 2: zero contradictions, zero stale claims, zero fragmentation candidates
- Phase 3: zero entity gaps (no entity pages in this wiki), zero missing Connections (all concepts have them), possibly 1-2 INFO items
- Phase 4: 5-10 curiosity seeds appended to `wiki/questions.md` (file created if not present)
- Phase 5: verdict = PASS, lint report written, log entry appended
- Auto-fixes: 0

**Pass criteria:**
- Lint report exists at correct path
- Verdict = PASS
- questions.md created/updated with at least 5 new seed entries
- Log entry appended to wiki/log.md
- No wiki pages modified (except questions.md)
- No raw/ modified

**Fail signals:**
- Verdict is WARN or FAIL (false positives from healthy wiki)
- Agent skipped any phase
- No curiosity seeds generated
- Agent modified a content page without authorization
- questions.md not created

**Gap this scenario was created to catch:**
- Baseline: skill must not over-report on a clean wiki (false positive noise erodes trust)
- questions.md creation logic (file may not exist on first lint pass)

---

## Scenario 2: Wiki With 3 Orphans + 2 Broken Links — Structural Issues, Verdict WARN

**Goal:** Verify Phase 1 detects orphans and broken links correctly; auto-fixes the obvious broken link; flags the ambiguous one; verdict = WARN.

**Setup:**
```
lint-test-2/
├── CLAUDE.md
├── wiki/
│   ├── index.md           # lists all pages including the orphans
│   ├── log.md
│   ├── concepts/
│   │   ├── bloom-filter.md             # healthy — linked from source-summaries/primer.md
│   │   ├── gossip-protocol.md          # ORPHAN — no other page links to it
│   │   ├── merkle-tree.md              # ORPHAN — no other page links to it
│   │   └── consistent-hashing.md      # has [[bloom-filter]] (valid) + [[rate-limiter]] (BROKEN — no such file)
│   ├── techniques/
│   │   └── rate-limiting.md           # ORPHAN — no other page links to it
│   │                                  # Note: consistent-hashing.md links to [[rate-limiter]], not [[rate-limiting]]
│   └── source-summaries/
│       └── primer.md                  # links to [[bloom-filter]] (valid)
│                                      # links to [[gossip]] (BROKEN — no 'gossip.md', only 'gossip-protocol.md')
```

Key detail: `[[rate-limiter]]` is broken and has zero candidates (no `rate-limiter.md` anywhere) — FLAG only, do not auto-fix. `[[gossip]]` is broken and `gossip-protocol.md` is the only candidate — auto-fix to `[[gossip-protocol]]`.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Run a lint pass on `lint-test-2/wiki/` using the llm-wiki-lint skill. TODAY'S DATE: [inject actual date]. Phase 1 only (structural checks). AUTO-FIX AUTHORIZED for broken wikilinks with exactly one slug-match candidate. Report Phase 1 findings, auto-fixes applied, and action items for user.

**Expected behavior:**
- Phase 1 finds exactly 3 orphans: gossip-protocol.md, merkle-tree.md, rate-limiting.md
- Phase 1 finds exactly 2 broken links: `[[rate-limiter]]` in consistent-hashing.md (no candidate → FLAG), `[[gossip]]` in primer.md (1 candidate: gossip-protocol.md → AUTO-FIX)
- Auto-fix applied: primer.md `[[gossip]]` → `[[gossip-protocol]]`
- Orphans flagged in Action Items (NOT auto-fixed)
- `[[rate-limiter]]` flagged in Action Items (NOT auto-fixed)
- Verdict = WARN

**Pass criteria:**
- Exactly 3 orphans reported
- Exactly 1 auto-fix applied (the gossip link)
- Exactly 1 broken link flagged as action item (rate-limiter)
- primer.md on disk has `[[gossip-protocol]]` (the auto-fixed version)
- gossip-protocol.md, merkle-tree.md, rate-limiting.md NOT deleted or modified by the agent
- Lint report written with WARN verdict
- Log entry appended

**Fail signals:**
- Agent auto-fixes `[[rate-limiter]]` (no candidate exists — this would be an invented fix)
- Agent reports 0 orphans (missed detection)
- Agent deletes orphan pages without permission
- Verdict is FAIL instead of WARN (over-reporting severity)

**Gap this scenario was created to catch:**
- Orphan detection correctness (pages with 0 incoming body/related references)
- Broken link auto-fix vs flag discrimination (exact single-candidate match = auto-fix; zero candidates = flag)
- Severity calibration (orphans + 1 flagged broken link = WARN, not FAIL)

---

## Scenario 3: Wiki With Contradiction — Phase 2 Flags, Not Fixed, Verdict WARN

**Goal:** Verify Phase 2 detects a semantic contradiction between two pages, produces a FLAG entry, and does NOT auto-fix anything. Verdict = WARN.

**Setup:**
```
lint-test-3/
├── CLAUDE.md
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── protocols/
│   │   └── lido-protocol.md
│   │       # Frontmatter: type: protocol, sources: [raw/lido-source-a.md]
│   │       # Body contains: "Lido charges a 10% fee on staking rewards,
│   │       #   split equally between node operators and the DAO treasury."
│   ├── source-summaries/
│   │   └── lido-q1-report.md
│   │       # Frontmatter: type: source-summary, sources: [raw/lido-source-b.md]
│   │       # Body contains: "According to Lido's Q1 2026 report, the protocol fee
│   │       #   is 5% of staking rewards."
│   └── concepts/
│       └── liquid-staking.md
│           # healthy concept page, links to [[lido-protocol]]
```

The contradiction is explicit: `lido-protocol.md` says 10% fee; `lido-q1-report.md` says 5% fee. Both have source citations in their frontmatter pointing to different raw files.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Run a full lint pass (all 5 phases) on `lint-test-3/wiki/` using the llm-wiki-lint skill. TODAY'S DATE: [inject actual date]. IMPORTANT: Do NOT resolve any contradiction you find. Flag it and add it to the Action Items. AUTO-FIX AUTHORIZED: NO. Write the lint report to `lint-test-3/wiki/lint-reports/[TODAY]-lint.md`.

**Expected behavior:**
- Phase 1: clean (no structural issues)
- Phase 2: contradiction detected between lido-protocol.md and lido-q1-report.md
  - Specific finding: fee rate "10%" vs "5%"
  - Both source citations listed in the finding
  - NOT resolved — only flagged
- Phase 3: possibly minor coverage gaps (INFO level)
- Phase 4: at least one curiosity seed generated referencing the contradiction ("What is Lido's current protocol fee?")
- Phase 5: verdict = WARN (contradiction flagged)
- Action Items include the contradiction with both page paths and both claim texts
- lido-protocol.md NOT modified
- lido-q1-report.md NOT modified

**Pass criteria:**
- Contradiction finding in lint report: page paths correct, both fee values cited, source citations included
- Neither lido-protocol.md nor lido-q1-report.md modified on disk
- Lint report verdict = WARN
- Action Items contain at least 1 item for user to resolve (the contradiction)
- questions.md has at least one seed about Lido fee (or equivalent contradiction-grounded question)
- Log entry appended

**Fail signals:**
- Agent modifies lido-protocol.md or lido-q1-report.md to "resolve" the contradiction
- Contradiction not detected (Phase 2 missed it)
- Verdict = PASS (under-reporting severity for a known contradiction)
- Verdict = FAIL (over-reporting severity — a single contradiction is WARN, not FAIL)
- Contradiction finding lacks source citations for both sides

**Gap this scenario was created to catch:**
- Phase 2 semantic detection (contradictions must be found by reasoning, not structural scan)
- Non-resolution discipline: lint identifies contradictions, it does NOT resolve them
- Severity calibration: 1 contradiction = WARN, not FAIL
- Action Items format: user needs clear next step (which pages to read, what the conflict is)

---

## Scenario 4: Adversarial — Restatement Not Flagged as Contradiction

**Goal:** Verify Phase 2 does NOT false-positive when two pages state the same fact in different words (Issue #2).

**Setup:**
```
lint-test-4/
├── CLAUDE.md
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── concepts/
│   │   ├── kafka-delivery.md
│   │   │   # Contains: "Kafka guarantees at-least-once delivery by default."
│   │   └── kafka-consumer-groups.md
│   │       # Contains: "By default, Kafka's delivery guarantee is at-least-once
│   │       #   (consumers may receive duplicate messages)."
│   └── source-summaries/
│       └── kafka-guide.md
│           # Contains: "Kafka does not guarantee exactly-once delivery in its default configuration."
```

All three pages are consistent — they describe the same guarantee from different angles. None contradicts the others.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Run Phase 2 (semantic) lint on `lint-test-4/wiki/` using the llm-wiki-lint skill. TODAY'S DATE: [inject actual date]. Focus specifically on contradiction detection. Report findings. Be conservative — only flag actual conflicting claims, not restatements of the same fact.

**Expected behavior:**
- Phase 2: zero contradictions detected
- Agent notes in its reasoning that kafka-delivery.md and kafka-consumer-groups.md are restatements, not contradictions
- No false-positive contradiction findings
- Verdict (if full lint run): PASS

**Pass criteria:**
- Zero contradictions in the lint report
- Agent's reasoning (if visible) correctly identifies the pages as non-conflicting
- No WARN or FAIL verdict caused by false-positive contradictions

**Fail signals:**
- Agent flags the kafka delivery guarantee as a contradiction
- Lint report shows a contradiction finding for these pages
- Verdict = WARN due to false-positive (no real issues exist)

**Gap this scenario was created to catch:**
- Issue #2: contradiction detection false-positives on restatements
- Calibrating the Phase 2 agent to distinguish "same fact, different words" from "genuinely conflicting claims"

---

## Scenario 5: questions.md Already Exists — Deduplication Works

**Goal:** Verify Phase 4 reads existing questions.md and does NOT append substantially duplicate questions.

**Setup:**
```
lint-test-5/
├── CLAUDE.md
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── concepts/
│   │   └── consistent-hashing.md   # healthy page, but no recent updates
│   ├── questions.md                # pre-populated with existing seeds (see below)
```

Pre-populate `wiki/questions.md` with:
```markdown
---
type: overview
sources: []
created: 2026-01-15
updated: 2026-01-15
tags:
  - questions
  - curiosity-seeds
related: []
---

## [2026-01-15] seed | What is the optimal number of virtual nodes for consistent hashing in a 10-node cluster?
Rationale: The wiki covers consistent hashing theory but lacks practical configuration guidance.

## [2026-01-15] seed | How does consistent hashing handle hotspots when keys are unevenly distributed?
Rationale: Current wiki page mentions hotspots but does not explain mitigation strategies.
```

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Run Phase 4 (curiosity seeds) of the lint pass on `lint-test-5/wiki/` using the llm-wiki-lint skill. TODAY'S DATE: [inject actual date]. The wiki currently has one concept page. Read wiki/questions.md first and do not append questions that are substantially similar to existing entries.

**Expected behavior:**
- Agent reads questions.md in full before generating seeds
- Agent generates new seeds that are meaningfully different from the two existing ones
- Agent does NOT append "What is the optimal virtual node count for consistent hashing?" (too similar to existing #1)
- Agent appends only genuinely new questions
- questions.md updated date in frontmatter updated to today

**Pass criteria:**
- questions.md has more entries than before (at least 1 new seed)
- No new seed is substantially similar to the two pre-existing ones
- Existing 2 entries are unmodified (append-only verified)
- `updated` frontmatter field in questions.md reflects today's date

**Fail signals:**
- Agent appends a near-duplicate of the existing virtual nodes question
- Agent deletes or rewrites existing entries
- Agent creates a new questions.md instead of appending to the existing one

**Gap this scenario was created to catch:**
- Issue #5: curiosity seeds repeating past lint passes
- questions.md append-only discipline
- questions.md `updated` frontmatter maintenance

---

## Cold-Start Subagent Prompt Template

Use this template when spawning test subagents for any scenario above. Replace placeholders.

```
You are a cold-start agent with ZERO memory of prior sessions. You are running a validation test of the llm-wiki-lint skill.

TODAY'S DATE: {{today}}

TASK: {{scenario_task_description}}

SKILL TO USE: ~/.claude/skills/llm-wiki-lint/
  - Read SKILL.md first (read it in full before starting)
  - Read agent-prompts.md for phase agent templates
  - Read ISSUES.md before trusting any automated finding

TEST FIXTURE: {{fixture_path}}
  - You may read/write ONLY within this fixture directory
  - NEVER touch production wikis (garen-wiki, web3-wiki, etc.)
  - NEVER touch raw/ directories

INSTRUCTIONS:
1. Read SKILL.md in full
2. Read the fixture's CLAUDE.md to understand the test wiki's schema
3. Run the Session Startup sequence as SKILL.md directs
4. Execute the specified lint phases (or all 5 if not specified)
5. Write the lint report to {{fixture_path}}/wiki/lint-reports/{{today}}-lint.md
6. Append to {{fixture_path}}/wiki/log.md

REPORT WHEN DONE:
- Lint verdict: PASS / WARN / FAIL
- Phase 1 findings: orphans N, broken links N (auto-fixed N, flagged N)
- Phase 2 findings: contradictions N, stale N
- Phase 3 findings: coverage gaps N
- Phase 4: seeds appended N
- Which skill sections were clear and helpful
- Which skill sections were confusing, ambiguous, or missing
- Any judgment calls you had to make that the skill did not cover
- Honest assessment: did the skill give you everything you needed?

Be critical. The point of this test is to find gaps in the skill, not to succeed at the task.
```

---

## Fixture Cleanup

After EVERY test run:

```bash
rm -rf lint-test-*/
```

Verify no `lint-test-*` directories remain before declaring the test session complete.

---

## When a Scenario Fails

1. Do NOT fix the test to make it pass
2. Diagnose: which part of the skill was missing, unclear, or wrong?
3. Edit the relevant skill file (SKILL.md, agent-prompts.md, etc.)
4. Re-run the specific failed scenario to confirm the fix
5. Run Scenario 1 (happy path) as a smoke test to ensure the fix didn't break anything else
6. If the failure reveals a new risk, add an entry to ISSUES.md

---

## Scenario Coverage Summary

| # | Scenario | Key behavior tested | Gap origin |
|---|----------|---------------------|------------|
| 1 | Healthy wiki — PASS | Full pipeline, questions.md creation, no false positives | Baseline smoke test |
| 2 | 3 orphans + 2 broken links — WARN | Phase 1 detection, auto-fix vs flag discrimination | Core structural lint |
| 3 | Contradiction — WARN, not auto-fixed | Phase 2 detection, non-resolution discipline | Karpathy: contradictions flagged not resolved |
| 4 | Restatement NOT flagged as contradiction | Phase 2 false-positive avoidance | Issue #2: fuzzy detection |
| 5 | questions.md deduplication | Phase 4 append-only + dedup | Issue #5: repeat questions |
