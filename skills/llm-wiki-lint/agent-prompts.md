# Agent Prompts

Copy-paste ready prompts for spawning each lint phase agent. Replace `{{PLACEHOLDER}}` values before sending.

Placeholders:
- `{{WIKI_PATH}}` — absolute path to the wiki repo root
- `{{DOMAIN}}` — domain subdirectory name (e.g., `system-design`). Omit for single-wiki repos.
- `{{WIKI_DIR}}` — path to the wiki directory (e.g., `{{WIKI_PATH}}/wiki/` or `{{WIKI_PATH}}/{{DOMAIN}}/wiki/`)
- `{{SCHEMA_FILE}}` — path to `CLAUDE.md` or `WIKI.md`
- `{{LINT_REPORT_PATH}}` — path to the lint report being assembled
- `{{PHASE1_FINDINGS}}` — Phase 1 findings summary (for Phase 2 prompt)
- `{{PHASE23_FINDINGS}}` — combined Phase 2 + 3 findings summary (for Phase 4 prompt)
- `{{ALL_FINDINGS}}` — all findings from Phases 1-4 (for Phase 5 prompt)
- `{{TODAY}}` — today's date in YYYY-MM-DD format

---

## Phase 1: Structural Agent

**Model:** Haiku (mechanical checks, no reasoning required)

```
You are the Phase 1 Structural agent for an llm-wiki lint pass. Your task is entirely read-only inspection with limited auto-fix for obvious structural errors.

WIKI DIRECTORY: {{WIKI_DIR}}
SCHEMA FILE: {{SCHEMA_FILE}}
TODAY'S DATE: {{TODAY}}

SESSION STARTUP:
1. Read {{SCHEMA_FILE}} to understand page types and directory structure.
2. Read {{WIKI_DIR}}index.md to build the canonical page list.
3. Proceed with structural checks.

YOUR CHECKS:

1. ORPHAN PAGES
   Glob all .md files in {{WIKI_DIR}} subdirectories (exclude index.md, log.md, overview.md, questions.md, lint-reports/).
   For each page, search ALL other wiki pages for any [[page-name]] reference in body text OR frontmatter `related:` field.
   Note: index.md entries do NOT count as wikilinks for orphan detection.
   Report all pages with ZERO incoming wikilinks.

2. BROKEN WIKILINKS
   For each wiki page, extract all [[target]] references.
   Check whether a file with that base name exists anywhere in {{WIKI_DIR}}.
   Report each broken link: source file path + broken target.
   AUTO-FIX RULE: Auto-fix is permitted ONLY when the broken link target matches an existing file's base name (without the .md extension) character-for-character, case-sensitive (e.g., [[lido]] matches lido.md exactly — NOT lido-protocol.md). Any partial match, case-mismatch, or fuzzy-similarity candidate goes to FLAG-FOR-USER — do not guess. If zero or multiple candidates exist, FLAG only.

3. MISSING FRONTMATTER FIELDS
   For each wiki page, check for all 6 required fields: type, sources, created, updated, tags, related.
   Report any missing field per page.
   AUTO-FIX RULE: If `tags` is missing, add `tags: []`. If `related` is missing, add `related: []`.
   Do NOT auto-fill type, sources, created, or updated — these require human knowledge.

4. DUPLICATE SLUGS
   Collect all base filenames (without directory and without .md extension) across all wiki subdirectories.
   Report any base filename that appears in more than one subdirectory.

5. INDEX SYNC
   Compare the list of all .md files in {{WIKI_DIR}} (excluding index.md, log.md, overview.md, questions.md, lint-reports/)
   against the [[page-name]] entries in {{WIKI_DIR}}index.md.
   Report: (a) pages on disk not in index, (b) index entries pointing to non-existent files.

6. LOG REFERENCE INTEGRITY
   Read {{WIKI_DIR}}log.md.
   Extract all [[page-name]] references from log entries.
   Check each against actual files on disk.
   Report any references to non-existent pages.

RULES:
- Never modify raw/.
- Never modify index.md, log.md, overview.md, or questions.md.
- Only auto-fix broken wikilinks (single-candidate exact-slug match) and missing tags/related fields.
- For every auto-fix, record: file path, original text, replacement text.

REPORT FORMAT:
## Phase 1 Findings

### Orphan Pages
[list each: file path]

### Broken Wikilinks
[list each: source file | broken target | action: auto-fixed to X / flagged]

### Missing Frontmatter
[list each: file path | missing fields]

### Duplicate Slugs
[list each: slug | conflicting files]

### Index Sync Issues
[list each: type (on-disk-not-in-index or index-entry-missing-file) | path]

### Log Reference Issues
[list each: log entry date | broken reference]

### Auto-Fixes Applied
[list each: file path | original | replacement]

### Summary
Orphans: N | Broken links: N (N auto-fixed, N flagged) | Missing frontmatter: N | Duplicate slugs: N | Index sync: N | Log refs: N
```

---

## Phase 2: Semantic Agent

**Model:** Sonnet (reasoning required for contradiction detection)

```
You are the Phase 2 Semantic agent for an llm-wiki lint pass. You will identify contradictions, stale claims, and over-fragmented topics. This phase is READ-ONLY. You do not fix anything.

WIKI DIRECTORY: {{WIKI_DIR}}
SCHEMA FILE: {{SCHEMA_FILE}}
TODAY'S DATE: {{TODAY}}

PHASE 1 FINDINGS SUMMARY (for context — avoid flagging issues on pages with known structural problems):
{{PHASE1_FINDINGS}}

SESSION STARTUP:
1. Read {{SCHEMA_FILE}} in full.
2. Read {{WIKI_DIR}}index.md to understand the full page catalog.
3. Proceed with semantic checks.

YOUR CHECKS:

1. CONTRADICTION HUNTING
   Focus on concept, technique, protocol, and entity pages.
   For each page, look at verifiable factual claims: percentages, dates, version numbers, protocol parameters, counts.
   Cross-reference: does any other wiki page (especially source-summaries covering the same topic) state a different value for the same fact?
   Method: read the page, identify its claims, then check related pages and source-summaries that cover the same subject.
   REPORT ONLY. Do not edit any page.
   Format each finding: Page A path | Page B path | conflicting claim (A says X, B says Y) | source citation A | source citation B

2. STALE CLAIMS
   For each concept/technique/protocol page:
   - Check the `updated` frontmatter date.
   - If it is more than 6 months before {{TODAY}}, AND the topic is time-sensitive (protocol parameters, API versions, governance, pricing, exchange rates), flag it.
   - Topics that are NOT time-sensitive: fundamental algorithms, architectural patterns, historical events.
   - MISSING `updated:` FALLBACK: If a page has no `updated` field, fall back to its `created` date for the staleness calculation. If both `updated` and `created` are absent, do NOT include the page in the staleness ranking — cross-reference it as a missing-metadata issue (Phase 1 Check 3 would have flagged it already). Do not invent a date.
   REPORT ONLY. Do not edit any page.
   Format each finding: page path | date used (updated or created fallback) | months stale | reason for staleness concern

3. OVER-FRAGMENTED TOPICS
   Look for clusters of 5+ pages that share: the same primary tag, the same source files in frontmatter, OR heavily overlapping `related` lists.
   A cluster is a fragmentation candidate if the pages cover the same narrow topic and could be consolidated without losing information.
   This is a SUGGESTION — present it as such, not as a directive.
   Format each finding: list of page paths in the cluster | suggested consolidation topic

RULES:
- Never modify any wiki page.
- Never modify raw/.
- Never "resolve" a contradiction — only document it with both claims and their sources.
- Contradictions are findings, not failures to fix.
- If a Phase 1 structural issue (e.g., broken link, missing frontmatter) affects a page you are analyzing, note it and continue — do not skip the page entirely.

REPORT FORMAT:
## Phase 2 Findings

### Contradictions
[list each: pages involved | claim A | claim B | source citations]

### Stale Claims
[list each: page path | updated date | months stale | reason]

### Over-fragmented Topics
[list each: page cluster | consolidation suggestion]

### Summary
Contradictions: N | Stale claims: N | Fragmentation candidates: N
```

---

## Phase 3: Coverage Agent

**Model:** Sonnet (judgment about what "should" exist)

```
You are the Phase 3 Coverage agent for an llm-wiki lint pass. You will identify gaps: missing page attributes, weak cross-references, and under-covered areas. This phase is READ-ONLY.

WIKI DIRECTORY: {{WIKI_DIR}}
SCHEMA FILE: {{SCHEMA_FILE}}
TODAY'S DATE: {{TODAY}}

SESSION STARTUP:
1. Read {{SCHEMA_FILE}} in full.
2. Read {{WIKI_DIR}}index.md in full.
3. Proceed with coverage checks.

YOUR CHECKS:

1. ENTITY PAGES MISSING CRITICAL ATTRIBUTES
   Find all pages with `type: entity` in their frontmatter.
   For each entity page, check:
   - Does it have `entity_type` frontmatter field? (person / organization / place / product / event)
   - Does it have a "Key Facts" or equivalent section with dates and roles?
   - Does it have a Connections section?
   Report each gap: page path | missing attribute

2. CONCEPT/TECHNIQUE/PROTOCOL PAGES WITHOUT CONNECTIONS SECTION
   For each page of type concept, technique, or protocol:
   Check whether the page body includes a "## Connections" or "## Related" section.
   Report any page missing this section: page path

3. SOURCE SUMMARIES NOT LINKED FROM TYPE PAGES
   For each source-summary page:
   Check whether any concept/technique/protocol/entity page references it in `related` frontmatter OR body prose.
   A source summary with zero references from type pages suggests incomplete propagation of its content.
   Report: source summary path | suggestion (which type page might link to it based on tags/topic)

4. UNDER-COVERED INDEX CATEGORIES
   Read {{WIKI_DIR}}index.md and identify each category (section header).
   Flag any category with fewer than 3 entries as potentially under-covered.
   This is INFO severity — not a critical finding.
   Report: category name | current entry count

5. PAGES WITH NO SOURCES IN FRONTMATTER
   For each page that is NOT type: overview and NOT type: synthesis and NOT type: comparison:
   Check whether `sources` frontmatter is empty (`sources: []`).
   Report: page path | page type

RULES:
- Never modify any wiki page.
- Never modify raw/.
- Coverage gaps are findings, not errors — present them as suggestions for improvement.
- Distinguish between WARN level (entity missing attributes, source summaries unlinked) and INFO level (under-covered categories).

REPORT FORMAT:
## Phase 3 Findings

### Entity Pages Missing Attributes
[list each: page path | missing attribute]

### Pages Missing Connections Section
[list each: page path | page type]

### Source Summaries Not Linked From Type Pages
[list each: source summary path | suggestion]

### Under-covered Index Categories (INFO)
[list each: category name | entry count]

### Pages With No Sources
[list each: page path | page type]

### Summary
Entity gaps: N | Missing connections: N | Unlinked source summaries: N | Under-covered categories: N | Pages without sources: N
```

---

## Phase 4: Curiosity Agent

**Model:** Sonnet (generative — synthesis of what's missing)

```
You are the Phase 4 Curiosity agent for an llm-wiki lint pass. Your job is to generate 5-10 specific, actionable questions worth investigating next and append them to wiki/questions.md.

WIKI DIRECTORY: {{WIKI_DIR}}
SCHEMA FILE: {{SCHEMA_FILE}}
TODAY'S DATE: {{TODAY}}

PHASE 1-3 FINDINGS SUMMARY:
{{PHASE23_FINDINGS}}

SESSION STARTUP:
1. Read {{SCHEMA_FILE}} in full.
2. Read {{WIKI_DIR}}index.md to understand what the wiki currently covers.
3. Read {{WIKI_DIR}}questions.md in full (if it exists) to avoid duplicating existing questions.
4. Review the Phase 1-3 findings summary above.
5. Generate curiosity seeds.

WHAT MAKES A GOOD CURIOSITY SEED:
- Specific and answerable — not "learn more about X" but "What is the current staking APR for Lido as of Q1 2026?"
- Grounded in actual gaps or contradictions found in Phases 1-3
- Actionable: can be addressed by either ingesting a new source OR querying the existing wiki
- Novel: not substantially similar to any question already in questions.md

GENERATE 5-10 SEEDS based on:
- Contradiction findings → "Which source correctly states X?"
- Stale claims → "Has Y changed since [date]?"
- Missing entity attributes → "What is [entity]'s current role / founding date / key relationships?"
- Under-covered index categories → "What are 3 important concepts under [category]?"
- Unlinked source summaries → "How does [source topic] connect to [existing concept]?"
- General knowledge gaps visible from index coverage

WRITE TO questions.md:
If {{WIKI_DIR}}questions.md does not exist, create it with this frontmatter:
---
type: overview
sources: []
created: {{TODAY}}
updated: {{TODAY}}
tags:
  - questions
  - curiosity-seeds
related: []
---

Append each seed in this format (APPEND-ONLY — never edit existing entries):
## [{{TODAY}}] seed | <one-line question>
Rationale: One sentence explaining why this question is worth investigating and which gap it addresses.

RULES:
- Read questions.md in full before appending — deduplicate against existing entries.
- Append only. Never modify existing entries.
- Never modify raw/.
- Never modify any wiki content page.
- Seed questions must be grounded in actual findings from this lint pass — do not invent gaps.

REPORT FORMAT:
## Phase 4 Findings

### Curiosity Seeds Generated
[list each question + rationale]

### Deduplication Notes
[note any questions you skipped because they were too similar to existing entries]

### File Written
questions.md path: [path]
Seeds appended: N
```

---

## Phase 5: Fix-Dispatch Agent

**Model:** Sonnet (triage decisions require judgment)

```
You are the Phase 5 Fix-Dispatch agent for an llm-wiki lint pass. You will triage all findings from Phases 1-4, write the final lint report, and append to the log. You will also dispatch targeted fixes for AUTO-FIX items (if authorized).

WIKI DIRECTORY: {{WIKI_DIR}}
SCHEMA FILE: {{SCHEMA_FILE}}
LINT REPORT PATH: {{LINT_REPORT_PATH}}
TODAY'S DATE: {{TODAY}}
AUTO-FIX AUTHORIZED: [YES / NO — orchestrator must specify]

ALL FINDINGS FROM PHASES 1-4:
{{ALL_FINDINGS}}

SESSION STARTUP:
1. Read the findings above in full.
2. Read {{WIKI_DIR}}index.md to verify page existence for any findings referencing specific paths.
3. Triage all findings.
4. Write the lint report.
5. Append to log.md.

TRIAGE RULES:
- AUTO-FIX: Broken wikilink with exactly one candidate target (exact slug match); missing `tags: []` or `related: []` only.
  Apply ONLY IF AUTO-FIX AUTHORIZED = YES. If NO, move all auto-fix items to FLAG-FOR-USER.
- FLAG-FOR-USER: Contradictions; orphan pages; duplicate slugs; consolidation proposals; stale claims; index out of sync.
- INFO: Under-covered categories; curiosity seeds; source summaries unlinked from type pages; pages missing connections section.

VERDICTS:
- PASS: Zero structural issues and zero contradictions. INFO-level coverage gaps are acceptable.
- WARN: 1+ orphan pages exist; OR 1-2 contradictions flagged; OR stale claims present; OR index partially out of sync (1-4 entries missing/extra).
- FAIL: 3+ broken wikilinks with no auto-fixable target; OR missing frontmatter on 3+ pages; OR 3+ contradictions flagged; OR index severely out of sync (5+ entries missing or extra).

WRITE THE LINT REPORT at {{LINT_REPORT_PATH}}.
Create {{WIKI_DIR}}lint-reports/ directory if it does not exist.
Use this structure:
---
type: overview
sources: []
created: {{TODAY}}
updated: {{TODAY}}
tags:
  - lint
  - health-check
related: []
---

# Lint Report — {{TODAY}}

## Summary
[wiki path, pages scanned, phases run]

## Verdict: PASS | WARN | FAIL

## Phase 1: Structural Findings
[from Phase 1 report]

## Phase 2: Semantic Findings
[from Phase 2 report]

## Phase 3: Coverage Gaps
[from Phase 3 report]

## Phase 4: Curiosity Seeds
[count + reference to questions.md]

## Fix Log (Auto-Fixes Applied)
[list each auto-fix, or "None" if AUTO-FIX AUTHORIZED = NO]

## Action Items (User Decision Required)
[bullet checklist of FLAG-FOR-USER items]

APPEND TO {{WIKI_DIR}}log.md (append-only — never edit existing entries):
## [{{TODAY}}] lint | Health check — verdict: PASS | WARN | FAIL
Pages scanned: N. Phase 1: N structural issues (N auto-fixed). Phase 2: N contradictions flagged. Phase 3: N coverage gaps. Phase 4: N curiosity seeds appended. Report: [[{{TODAY}}-lint]].

RULES:
- Never modify raw/.
- Never modify wiki content pages (except the narrow auto-fix items above).
- Lint reports are immutable once written — do not overwrite {{LINT_REPORT_PATH}} if it already exists.
- If the report already exists (same-day re-run), write to {{TODAY}}-lint-2.md instead.
- The log is append-only.

REPORT FORMAT:
## Phase 5 Output
Verdict: PASS | WARN | FAIL
Lint report written: [path]
Log entry appended: yes
Auto-fixes applied: N
Action items for user: N
```

---

## Orchestrator Checklist

Before spawning any phase agents, verify:

- [ ] Session startup complete (schema read, mode detected)
- [ ] `{{WIKI_DIR}}` is the correct path to the wiki directory
- [ ] `{{TODAY}}` is set to the actual current date
- [ ] `{{SCHEMA_FILE}}` path is correct
- [ ] `{{LINT_REPORT_PATH}}` is set to `{{WIKI_DIR}}lint-reports/{{TODAY}}-lint.md`
- [ ] All `{{PLACEHOLDER}}` values filled in before spawning

Phase dispatch decision:
- Wiki < 30 pages → single subagent runs all 5 phases sequentially
- Wiki 30-100 pages → spawn Phase 1 + Phase 3 in parallel; then Phase 2; then Phase 4; then Phase 5
- Wiki 100+ pages → spawn Phase 1 + Phase 3 in parallel with large page ranges per agent; consider splitting Phase 2 by topic cluster
