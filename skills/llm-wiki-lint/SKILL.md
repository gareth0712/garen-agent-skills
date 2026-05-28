---
name: llm-wiki-lint
description: Periodic health check for an llm-wiki (single-wiki or monorepo). Use when the user says "lint the wiki", "wiki health check", "find contradictions", "check orphans", "find stale pages", "suggest gaps", "what should I ingest next", or asks for a structural/semantic audit. Produces a lint-report with verdict (PASS/WARN/FAIL), auto-fixes structural issues, flags semantic issues for user review, and appends curiosity seeds to questions.md.
---

# llm-wiki-lint

A cold-start playbook for running periodic health checks on an llm-wiki. This skill covers the full 5-phase lint pipeline: structural inspection, semantic analysis, coverage gap detection, curiosity seed generation, and fix dispatch. Read it in full before taking any action. Lint is a health-check pass — it hunts for contradictions, stale claims, orphan pages, broken links, missing cross-references, and data gaps, then suggests new questions to investigate. It is NOT a batch editor. Structural issues may be auto-fixed (broken links with obvious targets, missing frontmatter fields). Semantic issues are FLAGGED ONLY and require user confirmation before any changes.

---

## When to Use This Skill

- User says "lint the wiki", "run a health check", "audit the wiki"
- User asks "find contradictions", "check orphans", "are there stale pages?"
- User asks "suggest gaps", "what should I ingest next?", "what questions should I investigate?"
- After a large batch ingest of 10+ files (catch structural issues before they compound)
- On a scheduled cadence (monthly) to keep the wiki from rotting
- Before sharing the wiki with others or presenting it as a reference
- When the wiki hasn't been touched in 3+ months and staleness is a concern

---

## When NOT to Use

- Fresh wiki with fewer than 10 pages — structural and semantic issues are trivial at this scale; just fix manually
- During an active ingest session — lint and ingest simultaneously will produce race conditions on shared files
- When the user wants to fix a specific known issue — spawn a targeted fix agent directly instead of running the full pipeline
- When the user has not yet established a `wiki/index.md` — lint depends on the index as its primary page catalog

---

## Prerequisites

Before running lint, the following must exist:

- A wiki repo with a `CLAUDE.md` (or `WIKI.md`) schema file
- A `wiki/` directory with `index.md` and `log.md`
- At least 10 wiki pages (fewer pages make lint noise-to-signal ratio too high)
- The user's intent is health-check, not active content creation

If `wiki/lint-reports/` does not exist, create it before writing the report. If `wiki/questions.md` does not exist, create it with the correct frontmatter before appending curiosity seeds (see format below).

---

## Mode Detection: Single-Wiki vs Monorepo

Before doing anything else, determine which mode you are in. Use the same detection logic as `llm-wiki-ingest`.

**Check for monorepo:** Does a file called `index.md` exist at the repo root (not inside `wiki/`)? AND do multiple subdirectories each contain their own `WIKI.md`? If both are true, you are in a monorepo.

| Indicator | Monorepo | Single-wiki |
|-----------|----------|-------------|
| Root-level `index.md` exists | Yes | No |
| Multiple subdirs each have `WIKI.md` | Yes | No |
| Single `CLAUDE.md` at root | Shared methodology file | Entire schema |
| `wiki/` location | Inside each domain subdir | At repo root |

**Monorepo lint scope:** Lint one domain at a time. If the user says "lint the wiki" in a monorepo, ask which domain (or lint all sequentially). Cross-domain orphan detection requires reading the root `index.md`.

---

## Session Startup Sequence

**CRITICAL: Do not skip this.** Every session starts cold. Read the schema before linting anything.

### Monorepo startup

1. Read `CLAUDE.md` (shared methodology — conventions, rules, page types)
2. Read root `index.md` (master domain router — which domain owns which topic)
3. Identify the target domain(s) for this lint pass
4. Read `<domain>/WIKI.md` (domain-specific page types, directory structure)
5. Now run the lint pipeline

### Single-wiki startup

**Step 0 — Pre-flight (abort if any check fails):**
- Does `wiki/` directory exist and contain at least 10 `.md` files? If not, stop and tell the user: "Wiki has fewer than 10 pages — lint is not useful at this scale. Fix manually."
- Does `wiki/index.md` exist? If not, stop: "wiki/index.md is required for lint. Create it first."
- Does `wiki/log.md` exist? If not, stop: "wiki/log.md is required for lint. Create it first."
- Is an active ingest session in progress (concurrent writes to wiki/)? If yes, stop: "Do not run lint during an active ingest session."

1. Read `CLAUDE.md` (the full schema: page types, directory structure, operations, rules)
2. Read `wiki/index.md` to build the canonical page list
3. Now run the lint pipeline

**Sequential phase order for single-agent runs (<30 pages):** 1 → 2 → 3 → 4 → 5. Run phases strictly in this order. (Phases 1 and 3 may run in parallel only when spawning separate subagents for each.)

---

## Lint Pipeline (5 Phases)

The pipeline produces findings, not edits. Phases 1 and 3 can run in parallel. Phase 2 must follow Phase 1 (it needs clean structural data). Phase 4 follows Phases 2 and 3. Phase 5 is always last and sequential.

```
Phase 1 (Structural)  ─┐
                        ├── can run in parallel
Phase 3 (Coverage)    ─┘
        │
        ▼
Phase 2 (Semantic)    ← must follow Phase 1
        │
        ▼
Phase 4 (Curiosity Seeds) ← follows Phases 2 + 3
        │
        ▼
Phase 5 (Fix Dispatch)  ← always last, sequential
```

---

### Phase 1: Structural

**Model:** Haiku (mechanical checks — no reasoning required)

**What to check:**

1. **Orphan pages** — pages that exist on disk but have zero incoming wikilinks from any other page. A page is an orphan if no other wiki page's body or `related` frontmatter references it as `[[page-name]]`. Note: `index.md` entries do NOT count as wikilinks for orphan detection purposes; an orphan is a page that other CONTENT pages do not link to.

2. **Broken wikilinks** — every `[[target]]` reference in every page must resolve to an actual file in the wiki directories. If `[[lido-protocol]]` is referenced but `wiki/protocols/lido-protocol.md` does not exist, it is broken. **Scan includes `index.md` and `log.md`** — wikilinks in those files are checked here under Check 2, not only under Check 5 (Index Sync) or Check 6 (Log Reference Integrity). A single broken link in `index.md` will appear in both Check 2 (broken wikilink) and Check 5 (index entry with no matching file); that is correct behavior, not double-counting — each check serves a distinct diagnostic purpose.

3. **Missing frontmatter fields** — every page must have all 6 required fields: `type`, `sources`, `created`, `updated`, `tags`, `related`. Flag any page missing one or more fields.

4. **Duplicate slugs** — two pages must not share the same base filename (regardless of subdirectory). `wiki/concepts/retry-pattern.md` and `wiki/source-summaries/retry-pattern.md` is a collision. Flag all collisions.

5. **index.md sync** — every file in the wiki directories must appear in `wiki/index.md` exactly once. Exclude from this scan: `index.md`, `log.md`, `overview.md`, `questions.md`, and anything inside `lint-reports/`. Flag: (a) pages on disk not in the index, (b) index entries pointing to non-existent files.

6. **log.md reference integrity** — scan `wiki/log.md` entries for `[[page-name]]` references. Flag any that point to pages that do not exist on disk.

**Auto-fixable in Phase 1:**
- Broken wikilink where auto-fix is permitted ONLY when the broken link target matches an existing file's base name (without the .md extension) **character-for-character, case-sensitive**. Any partial match, case-mismatch, or fuzzy-similarity candidate goes to FLAG-FOR-USER — do not guess. (e.g., `[[lido]]` → `lido.md` exists and there is no other candidate — update the link. If more than one candidate, or the match is not exact, FLAG rather than fix.)
- Missing frontmatter field with a safe default: `tags: []`, `related: []`. Do NOT invent `type`, `sources`, `created`, or `updated` — these require human knowledge.

  **Important:** Even when `tags` or `related` are auto-fixed, they MUST still appear in two places: (1) the Fix Log in the lint report (recording original→replacement), AND (2) the Missing Frontmatter section (noting the field was absent but has been auto-filled with a safe default). Auto-fixing a field does not mean silently suppressing it from the Missing Frontmatter findings.

**NOT auto-fixable (FLAG for user):**
- Orphan pages — the user must decide whether to link them or delete them
- Duplicate slugs — the user must decide which page gets the canonical name
- Index out of sync — the user must review before the index is modified

---

### Phase 2: Semantic

**Model:** Sonnet (requires reasoning to detect contradictions and assess fragmentation)

**What to check:**

1. **Contradiction hunting** — identify pairs of pages covering the same topic that make inconsistent factual claims. Focus on verifiable facts: percentages, dates, version numbers, protocol parameters. Method: for each concept/protocol page, compare claims against any source-summary pages that reference the same topic. If two pages state different values for the same fact, flag as a contradiction.

   **FLAG ONLY. Never resolve a contradiction automatically.** Add to the lint report with: page A path, page B path, the conflicting claim, and both source citations.

2. **Stale claims** — a page is potentially stale if its `updated` date is more than 6 months ago AND the source is known to change over time (protocols, API endpoints, governance parameters, pricing). Flag with: page path, `updated` date, reason for staleness concern.

   **Missing `updated:` fallback:** If a page has no `updated` field, fall back to its `created` date for the staleness calculation. If both `updated` and `created` are absent, do NOT include the page in the staleness ranking — instead, cross-reference it as a missing-metadata finding in Phase 1 (Check 3). Do not invent a date.

   **FLAG ONLY. Do not modify the page.**

3. **Over-fragmented topics** — if 5 or more pages exist that cover the same narrow topic (detected by shared tags, shared source files, or highly overlapping `related` lists), suggest consolidation. This is a SUGGESTION, not an auto-fix.

   **SUGGEST ONLY. Require user confirmation before any consolidation.**

---

### Phase 3: Coverage Gaps

**Model:** Sonnet (requires judgment about what "should" exist)

**What to check:**

1. **Entity pages missing critical attributes** — for pages with `type: entity`, check for: missing `entity_type` frontmatter, missing a "Key Facts" or equivalent section with dates and roles, missing Connections section. Flag each gap.

2. **Concept pages without Connections section** — every concept/technique/protocol page should have a Connections section. Flag pages that are missing it.

3. **Source summaries not linked from any type page** — if a source summary exists but no concept/technique/protocol page references it in `related` or body prose, the ingest may be incomplete. Flag with: source summary path, suggestion to create or update a type page.

4. **index.md categories with fewer than 3 entries** — a category with 1–2 entries may indicate an under-covered area worth ingesting into. Flag as INFO (not WARN or FAIL).

5. **Pages with no sources in frontmatter** — non-synthesis, non-overview pages with empty `sources: []` may have been created without proper attribution. Flag for user review.

---

### Phase 4: Curiosity Seeds

**Model:** Sonnet (generative — requires synthesis of what's missing)

**What to generate:**

Based on the findings from Phases 1–3 and the current coverage of the wiki, generate 5–10 questions worth investigating next. Good curiosity seeds are:
- Specific and answerable (not "learn more about X")
- Grounded in actual gaps found in the wiki
- Actionable via either ingest (new source exists) or query (wiki already has fragments)

**Where to write:**

Append to `wiki/questions.md`. If the file does not exist, create it with this frontmatter:

```yaml
---
type: overview
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - questions
  - curiosity-seeds
related: []
---
```

Format for each entry (append-only, same log format):
```markdown
## [YYYY-MM-DD] seed | <one-line question>
Rationale: One sentence explaining why this question is worth investigating and what gap it addresses.
```

**Deduplication:** Before appending, read the existing `wiki/questions.md` in full. Do not add a question that is substantially similar to one already present (same topic, same angle). Rephrase or skip.

**`questions.md` is append-only.** Never edit or delete existing entries.

---

### Phase 5: Fix Dispatch

**Model:** Sonnet (triage decisions require judgment)

Triage all findings from Phases 1–4 by severity and action type:

| Action type | Criteria | Who acts |
|-------------|----------|----------|
| AUTO-FIX | Broken wikilink where target matches an existing file's base name character-for-character, case-sensitive (single exact match only); missing `tags: []` or `related: []` frontmatter fields | Fix agent (spawned by orchestrator) |
| FLAG-FOR-USER | Contradiction between two pages; consolidation proposal; orphan page; duplicate slug; index out of sync | Add to Action Items in the lint report; user decides |
| INFO | Under-covered index category; source summary unlinked from type pages; curiosity seeds | Logged in report only |

**Do not spawn the fix agent without user approval** unless the task description explicitly authorized auto-fix. Auto-fix scope is always narrow: only the specific items classified as AUTO-FIX above.

After Phase 5, write the lint report and append to `wiki/log.md`.

---

## Lint Report Format

**Path:** `wiki/lint-reports/YYYY-MM-DD-lint.md`

Create the `wiki/lint-reports/` directory if it does not exist.

**Lint reports are immutable once written.** Do not edit a lint report after the session ends. If a later session finds the report was wrong, append a correction entry to `wiki/log.md` referencing the original report.

```markdown
---
type: overview
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - lint
  - health-check
related: []
---

# Lint Report — YYYY-MM-DD

## Summary

Wiki: [path or name]
Pages scanned: N
Phases run: 1, 2, 3, 4, 5
Lint duration: [approximate]

## Verdict: PASS | WARN | FAIL

**PASS:** No structural issues. Semantic findings are informational only.
**WARN:** 1+ orphan pages exist; OR 1-2 contradictions flagged; OR stale claims present; OR index partially out of sync (1-4 entries missing/extra).
**FAIL:** 3+ broken wikilinks with no auto-fixable target; OR missing frontmatter on 3+ pages; OR 3+ contradictions flagged; OR index severely out of sync (5+ entries missing or extra).

## Phase 1: Structural Findings

### Orphan Pages (N found)
- `wiki/path/to/page.md` — no incoming wikilinks from any content page

### Broken Wikilinks (N found)
- `wiki/concepts/page.md` → `[[missing-target]]` — no file found

### Missing Frontmatter (N found)
- `wiki/path/to/page.md` — missing fields: [list]

### Duplicate Slugs (N found)
- `wiki/concepts/retry-pattern.md` ↔ `wiki/source-summaries/retry-pattern.md` — collision

### Index Sync Issues (N found)
- Pages on disk not in index: [list]
- Index entries with no matching file: [list]

## Phase 2: Semantic Findings

### Contradictions (N found)
- **[page-a.md] vs [page-b.md]:** Conflicting claim: "X" vs "Y". Sources: [citations].

### Stale Claims (N found)
- `wiki/protocols/lido-protocol.md` — updated 2025-06-01 (10 months ago); protocol parameters may have changed.

### Over-fragmented Topics (N suggested)
- 6 pages tagged `caching` with overlapping `related` lists — consider consolidation.

## Phase 3: Coverage Gaps (N found)

- `wiki/entities/vitalik-buterin.md` — missing `entity_type` frontmatter
- `wiki/concepts/merkle-tree.md` — missing Connections section
- `wiki/source-summaries/kafka-guide.md` — not referenced by any concept/technique page

## Phase 4: Curiosity Seeds

5 questions appended to `wiki/questions.md`. See that file for details.

## Fix Log (Auto-Fixes Applied)

- `wiki/concepts/page.md`: `[[lido]]` → `[[lido-protocol]]` (exact match found)
- `wiki/concepts/other.md`: added `tags: []` to frontmatter (was missing)

## Action Items (User Decision Required)

- [ ] Review orphan page `wiki/source-summaries/orphan.md` — link from relevant pages or delete
- [ ] Resolve contradiction between `concepts/fee-model.md` and `source-summaries/lido-report.md`
- [ ] Review proposed consolidation of 6 caching-related pages
```

---

## Log Entry Format

Append to `wiki/log.md` after the lint report is written. The log is append-only.

```markdown
## [YYYY-MM-DD] lint | Health check — verdict: PASS | WARN | FAIL
Pages scanned: N. Phase 1: N structural issues (N auto-fixed). Phase 2: N contradictions flagged. Phase 3: N coverage gaps. Phase 4: N curiosity seeds appended. Report: [[YYYY-MM-DD-lint]].
```

**Counting "N structural issues":** Count every individual finding across all 6 Phase 1 sub-checks — each orphan page, each broken wikilink, each missing-frontmatter page, each duplicate slug, each index-sync mismatch, and each broken log reference counts as one issue. Do NOT count by category; count by instance.

---

## Parallelization Strategy

Phases 1 and 3 can run in parallel because:
- Phase 1 is read-only structural inspection
- Phase 3 is read-only coverage analysis
- They do not write to any shared file during execution

Phase 2 must follow Phase 1 because:
- Contradiction detection is more accurate when broken links and missing pages are already known
- Flagging a contradiction on a broken-link page wastes effort

Phase 4 follows Phases 2 and 3 because:
- Curiosity seeds should be informed by both semantic findings AND coverage gaps

Phase 5 is always sequential and last because:
- Fix dispatch must triage the complete set of findings from all prior phases
- The lint report is written once, at the end

**When to spawn parallel subagents:**

For a large wiki (50+ pages), spawn Phase 1 and Phase 3 as parallel subagents. For a small wiki (<30 pages), a single subagent can run all 5 phases sequentially.

---

## Critical Non-Negotiables

1. **Never modify `raw/`.** Lint is a wiki-layer operation. Raw source files are immutable.
2. **Never silently overwrite any wiki page.** Lint reports findings. If a page needs to change, the user must approve.
3. **Contradictions are FLAGGED, not resolved.** Lint identifies the disagreement and presents both claims with sources. Resolution is the user's decision.
4. **Auto-fix only with high confidence.** Auto-fix is permitted ONLY when the broken link target matches an existing file's base name (without the .md extension) character-for-character, case-sensitive. Any partial match, case-mismatch, or fuzzy-similarity candidate goes to FLAG-FOR-USER — do not guess.
5. **`questions.md` is append-only.** Never edit or delete existing curiosity seed entries. Only append new ones, and only after deduplicating against existing entries.
6. **Lint reports are immutable once written.** A lint report is a historical record. If it contains errors, note them in `wiki/log.md` — do not rewrite the report.
7. **Semantic findings require user confirmation before any action.** No contradiction, consolidation, or staleness finding justifies an autonomous edit to wiki pages.
8. **Do not ingest during a lint session.** If Phase 3 reveals a gap that could be filled by ingesting a specific source, flag it as a curiosity seed — do not start an ingest inline. Keep the operations separate.

---

## Orchestrator vs Subagent Roles

**Orchestrator (main agent, with user context):**
- Runs Session Startup (reads schema, determines mode)
- Decides whether to spawn parallel Phase 1 + Phase 3 subagents or run sequentially
- Receives subagent reports and compiles the final lint report
- Presents Action Items to the user and awaits decisions
- Dispatches the fix agent (if any) only after user approves

**Subagents (spawned via Agent tool):**
- Execute their assigned phase (one phase per subagent)
- Return a structured findings report with exact page paths and issue descriptions
- Do NOT modify wiki pages (except Phase 1 auto-fixes for broken wikilinks/missing `tags`/`related`)
- Do NOT modify `raw/`

See [agent-prompts.md](agent-prompts.md) for ready-to-use agent templates for each phase.

---

## Reference: When to Branch

| If you need to... | Go to |
|-------------------|-------|
| Spawn a phase subagent | [agent-prompts.md](agent-prompts.md) |
| Understand the verdict scale | Phase 5 triage table above |
| Understand the fix agent scope | [agent-prompts.md](agent-prompts.md) — Phase 5 Fix-Dispatch Agent |
| Understand known limitations | [ISSUES.md](ISSUES.md) |
| Run cold-start test scenarios | [TEST.md](TEST.md) |

---

## Example Lint Report (Illustrative)

The following is a short example from a real-world-sized wiki (42 pages, system-design domain).

```
# Lint Report — 2026-04-16

## Summary
Wiki: system-design/wiki/
Pages scanned: 42
Phases run: 1, 2, 3, 4, 5

## Verdict: WARN

## Phase 1: Structural Findings
Orphan Pages (2):
- wiki/source-summaries/early-draft-rate-limiter.md — no incoming wikilinks
- wiki/concepts/gossip-protocol.md — no incoming wikilinks

Broken Wikilinks (1):
- wiki/design-problems/url-shortener.md → [[bloom-filter]] — no file found
  (bloom-filter-concept.md exists — auto-fixed)

Missing Frontmatter (0): None.
Duplicate Slugs (0): None.
Index Sync (1): wiki/concepts/gossip-protocol.md missing from index.

## Phase 2: Semantic Findings
Contradictions (1):
- concepts/consistent-hashing.md vs source-summaries/system-design-primer.md:
  "virtual nodes per server: 150" vs "virtual nodes per server: 100-200 (configurable)".
  Sources: raw/book-chapters/ch5.md vs raw/primer/consistent-hashing.md.

Stale Claims (1):
- protocols/kafka-protocol.md — updated 2025-08-10 (8 months ago); Kafka versions evolve rapidly.

## Phase 3: Coverage Gaps
- concepts/consistent-hashing.md — missing Connections section
- index categories "Comparisons" has 1 entry (under-covered area)

## Phase 4: Curiosity Seeds
3 questions appended to wiki/questions.md.

## Fix Log
- url-shortener.md: [[bloom-filter]] → [[bloom-filter-concept]] (auto-fixed, exact match)

## Action Items (User Decision Required)
- [ ] Review orphan: early-draft-rate-limiter.md — link or delete?
- [ ] Review orphan: gossip-protocol.md — add to index + link from relevant pages?
- [ ] Resolve contradiction: virtual nodes count (150 vs 100-200). Consult raw sources to determine correct value.
- [ ] Review kafka-protocol.md for staleness — re-ingest against current Kafka docs?
```
