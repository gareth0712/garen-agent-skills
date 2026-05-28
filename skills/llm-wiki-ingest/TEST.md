# TEST.md — Validation scenarios for llm-wiki-ingest

This file documents every test scenario the skill must handle. Run these whenever the skill is modified to catch regressions. Every scenario traces to a real gap found during skill development.

## How to use this file

**When to run:**
- After any non-trivial edit to SKILL.md, format-conversion.md, quality-gates.md, agent-prompts.md, or patterns.md
- Before sharing the skill with another user or session
- When a real ingest fails in a way the skill should have prevented — add the new failure as a new scenario
- Periodically (monthly) as a regression check

**How to run:**
1. Create isolated temp fixture directories (never pollute production workspace)
2. Populate fixtures per the scenario's setup instructions
3. Spawn a fresh sonnet subagent with the cold-start prompt template at the bottom of this file
4. Compare actual output to expected behavior
5. Clean up temp fixtures after completion
6. If a scenario fails, fix the skill directly — do not fix the test

**Key principle:** The test fixtures must be adversarial. Happy-path tests pass easily; edge cases are where gaps hide.

---

## Scenario 1: Happy Path — Mixed Format Batch Ingest

**Goal:** Verify the skill handles a typical batch of supported formats end-to-end.

**Setup:**
```
skill-test-1/
├── CLAUDE.md          # minimal single-wiki schema
├── raw/
│   ├── concept-source.md      # real markdown, ~40 KB
│   ├── design-problem.md      # real markdown, ~50 KB
│   └── article.mhtml          # real Substack-style mhtml
└── wiki/
    ├── index.md       # with frontmatter, empty sections
    └── log.md         # with frontmatter, one init entry
```

Use real file copies from an existing wiki, not synthetic stubs. Copy sources like `ood/raw/oo-design-interview/03. OOP Fundamentals.md` and a real `.mhtml` from `samples/`.

**Cold-start prompt (to spawn subagent):**
> You are a cold-start agent with no memory of prior sessions. Ingest all files in `skill-test-1/raw/` following the llm-wiki-ingest skill at `C:\Users\garet\.claude\skills\llm-wiki-ingest\`. You are batch edit + consolidation + review in one agent. Only touch `skill-test-1/` — never the production wikis. Report: files processed/skipped, pages created, skill sections that were clear vs confusing.

**Expected behavior:**
- Skill runs Step -1 pre-flight assessment before ingesting
- MHTML is converted to markdown and placed at `raw/article.md` (same directory as source)
- Original `.mhtml` is kept
- If the repo's `scripts/mhtml_to_md.py` produces a stub (<500 bytes), the agent falls back to the minimal template in format-conversion.md
- Source summaries created in `wiki/source-summaries/`
- Relevant concept/technique/design-problem pages created in correct subdirectories
- All pages have valid frontmatter (type matches directory, sources relative, today's date)
- `wiki/index.md` updated with new entries
- `wiki/log.md` has one new append-only ingest entry
- Wikilinks resolve

**Pass criteria:**
- 0 broken wikilinks across all new pages
- All frontmatter valid (6 required fields)
- Source summaries exist and cite the correct raw file paths (including converted `.md`, not the original `.mhtml`)
- Index reflects all new pages exactly once
- Log entry is append-only

**Pass threshold:** 100% of expected behaviors observed, at most 1 minor friction point.

**Gaps this scenario was created to catch:**
- Script failure detection (skill fallback when `mhtml_to_md.py` produces stubs)
- Converted file placement (should go in `raw/`, same directory, mirror filename)
- Basic batch ingest flow (edit → consolidate → review → log)

---

## Scenario 2: Unknown Format Detection — Pre-flight Must Stop

**Goal:** Verify the skill's Step -1 pre-flight catches unsupported formats and halts before any work.

**Setup:**
```
skill-test-2/
├── CLAUDE.md
├── raw/
│   ├── good-source.md         # real markdown
│   ├── mystery-file.xyz       # small text file with unknown extension
│   └── sample-book.epub       # small JSON file masquerading as .epub (or real small epub)
└── wiki/
    ├── index.md
    └── log.md
```

The `.xyz` and `.epub` files can be tiny — content doesn't matter. The extensions are what matters.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Ingest files in `skill-test-2/raw/` following the llm-wiki-ingest skill at `C:\Users\garet\.claude\skills\llm-wiki-ingest\`. Do NOT invent conversions for unfamiliar formats. If the skill tells you to stop and ask, stop and ask. Only touch `skill-test-2/`.

**Expected behavior:**
- Agent runs Step -1 pre-flight first
- Pre-flight produces a report listing: 1 supported file (`.md`), 2 unsupported files (`.xyz`, `.epub`)
- Agent **halts** and asks the user for a decision on the unsupported files
- If the user says "proceed with .md only, skip the rest", only the `.md` is ingested
- `.xyz` file triggers the Unknown Format Handling workflow in format-conversion.md (magic bytes inspection, pandoc format check)
- `.epub` is identified as a potentially supported format (EPUB section in format-conversion.md)
- Agent does NOT silently skip unknown formats
- Agent does NOT invent a conversion

**Pass criteria:**
- Pre-flight report produced before any ingest work
- Agent halts and requests user decision
- `.md` file correctly ingested (if user approves continuation)
- No files silently skipped

**Pass threshold:** The pre-flight halt is the critical behavior. If the agent processes the `.md` without mentioning the unknown formats, this scenario fails.

**Gaps this scenario was created to catch:**
- No pre-flight assessment (fixed in SKILL.md Step -1)
- No unknown format handler (fixed in format-conversion.md Unknown Format Handling)
- EPUB not covered (fixed in format-conversion.md EPUB section)
- Batch agents silently skipping unknown formats (fixed by pre-flight requirement)

---

## Scenario 3: Slug Collision — Source Summary vs Concept/Technique

**Goal:** Verify the skill detects and resolves filename collisions between source summaries and type-specific pages.

**Setup:**
```
skill-test-3/
├── CLAUDE.md
├── raw/
│   └── retry-pattern.md       # an article titled "A Guide to Retry Patterns" — kebab-case
│                              # would normally produce source-summaries/retry-pattern.md
│                              # but "retry pattern" is also a classic technique that deserves
│                              # its own techniques/retry-pattern.md page
└── wiki/
    ├── index.md
    └── log.md
```

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-3/raw/retry-pattern.md` using the llm-wiki-ingest skill. This article covers the Retry Pattern technique and should produce both a source summary AND a technique page. Only touch skill-test-3/.

**Expected behavior:**
- Agent recognizes the slug collision risk: both the source summary and the technique page would naturally be named `retry-pattern.md`
- Agent applies the slug collision resolution from SKILL.md File Naming section
- Source summary gets a distinguishing suffix (e.g., `retry-pattern-guide.md` or `retry-pattern-article.md`), OR uses the full article title (`a-guide-to-retry-patterns.md`)
- Technique page uses the clean `retry-pattern.md` slug
- No two pages in different subdirectories share the same base filename

**Pass criteria:**
- Only one `retry-pattern.md` exists across all wiki subdirectories
- Both pages exist with distinct filenames
- Wikilinks from other pages to `[[retry-pattern]]` resolve unambiguously (to the technique page)

**Pass threshold:** No collision. If the agent creates two pages named `retry-pattern.md` in different subdirectories, this fails.

**Gap this scenario was created to catch:**
- Slug collision between source-summary and technique pages (fixed in SKILL.md File Naming section)

---

## Scenario 4: Page Count Discipline — Avoid Over-fragmentation

**Goal:** Verify the skill's page count heuristics prevent creating too many pages from one source.

**Setup:**
```
skill-test-4/
├── CLAUDE.md
├── raw/
│   └── medium-source.md       # ~40 KB article covering one primary topic
│                              # with 3-4 supporting concepts mentioned
└── wiki/
    ├── index.md
    └── log.md
```

Use a real article like `ood/raw/oo-design-interview/04. Design a Parking Lot.md` — one design problem with a few supporting concepts (Strategy, Facade).

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-4/raw/medium-source.md` using the llm-wiki-ingest skill. Follow the page count heuristics from SKILL.md Step 4 strictly. Report the number of pages you created and justify why each one was worth creating.

**Expected behavior:**
- Agent creates 1 source summary
- Agent creates 1 design-problem page (if applicable) OR 1 primary concept page
- Agent creates 2-5 additional concept/technique pages for supporting topics actually covered in depth
- Agent does NOT create a page for every term mentioned in passing
- Total page count: 3-7 pages from one 40KB source

**Pass criteria:**
- Page count falls within the heuristic table range
- Each page justifies its own existence (has unique content beyond what's in the source summary)
- Agent reports red flags if page count exceeds 10 from one source

**Fail signals:**
- Agent creates 15+ pages from one source (over-fragmentation)
- Agent creates 1 page from a 40KB source (under-capture)
- Agent creates a concept page for something mentioned only once in passing

**Gap this scenario was created to catch:**
- No page count heuristic in skill (fixed in SKILL.md Step 4 with heuristics table + red flags)

---

## Scenario 5: Date Awareness — No Stale Date Copy-Paste

**Goal:** Verify subagents use today's actual date, not a date copied from skill examples.

**Setup:**
```
skill-test-5/
├── CLAUDE.md
├── raw/
│   └── test-source.md         # any real markdown file
└── wiki/
    ├── index.md
    └── log.md
```

**Cold-start prompt:**
> You are a cold-start agent. Today is [ACTUAL CURRENT DATE — orchestrator must inject this]. Ingest `skill-test-5/raw/test-source.md` using the llm-wiki-ingest skill. All `created` and `updated` dates in your new pages must match today's actual date.

**Expected behavior:**
- Agent writes today's actual date in every new page's frontmatter
- Agent does NOT copy dates like `2026-04-11` from skill examples
- Agent does NOT use a hardcoded placeholder like `YYYY-MM-DD`
- Log entry uses today's date in the `## [YYYY-MM-DD]` prefix

**Pass criteria:**
- Every new page has `created: <today>` and `updated: <today>`
- No new page has a date earlier than today
- No new page has a placeholder date

**Fail signals:**
- Any page has a date matching an example in the skill files (this is the specific failure mode observed in the original test)
- Any page has `YYYY-MM-DD` as the literal value

**Gap this scenario was created to catch:**
- Date awareness failure (fixed in SKILL.md Frontmatter section with "Date awareness (CRITICAL for subagents)" block)

---

## Scenario 6: Connections Section vs Link-on-First-Mention

**Goal:** Verify the skill handles the tension between "don't link twice" and "include in Connections section".

**Setup:**
```
skill-test-6/
├── CLAUDE.md
├── raw/
│   └── multi-concept-source.md  # article mentioning 3+ concepts that have existing wiki pages
└── wiki/
    ├── index.md
    ├── log.md
    ├── concepts/
    │   ├── existing-concept-a.md
    │   ├── existing-concept-b.md
    │   └── existing-concept-c.md
    └── source-summaries/
```

Pre-populate the `wiki/concepts/` directory with 3 stub concept pages so the ingested source has existing pages to link to.

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-6/raw/multi-concept-source.md` using the llm-wiki-ingest skill. The raw source mentions concepts A, B, and C which already exist as wiki pages. Follow the skill's Connections/Related section handling rule carefully.

**Expected behavior:**
- Source summary links to [[existing-concept-a]], [[existing-concept-b]], [[existing-concept-c]] on first mention in the body
- Source summary's "Connections" section ALSO includes [[existing-concept-a]], [[existing-concept-b]], [[existing-concept-c]] with one-sentence context notes each
- `related` frontmatter lists all 3 concepts
- Wikilinks in the Connections section work in Obsidian (no markdown link syntax)

**Pass criteria:**
- Body has wikilinks on first mention
- Connections section has same wikilinks (duplicated by design, this is allowed)
- `related` frontmatter populated
- No plain-text references where wikilinks are expected

**Fail signals:**
- Connections section has bare text like "Existing Concept A" with no wikilink (old buggy behavior)
- Agent interprets "don't link twice" as "omit from Connections section"

**Gap this scenario was created to catch:**
- Connections section plain-text bug (fixed in SKILL.md Internal Linking / Connections handling rule)

---

## Scenario 7: Monorepo Routing (monorepo only)

**Goal:** Verify cold-start agents route to the correct domain in a monorepo.

**Setup:** Test against the real garen-wiki monorepo (read-only inspection, no writes) OR build a miniature monorepo:

```
skill-test-7/
├── CLAUDE.md          # shared methodology
├── index.md           # master router with 2 domains
├── domain-a/
│   ├── WIKI.md
│   ├── raw/
│   └── wiki/
└── domain-b/
    ├── WIKI.md
    ├── raw/
    └── wiki/
```

Place one test raw file under `domain-a/raw/` that clearly belongs to domain A.

**Cold-start prompt:**
> You are a cold-start agent. The user says "ingest the new file in the monorepo at skill-test-7/". Use the llm-wiki-ingest skill. Determine which domain the file belongs to and ingest it correctly.

**Expected behavior:**
- Agent reads root `CLAUDE.md` first
- Agent reads root `index.md` (master router) second
- Agent identifies the correct domain using the router + cross-domain topic map
- Agent reads the correct `<domain>/WIKI.md`
- Agent creates pages under the correct `<domain>/wiki/`, NOT at the monorepo root
- Agent does NOT create pages in the wrong domain

**Pass criteria:**
- Pages exist under `skill-test-7/domain-a/wiki/`, NOT `skill-test-7/domain-b/wiki/` or `skill-test-7/wiki/`
- Agent cited the monorepo startup sequence in its report (reading CLAUDE.md → index.md → domain WIKI.md)

**Fail signals:**
- Pages created in the wrong domain
- Pages created at the monorepo root
- Agent skipped reading the master index.md

**Gap this scenario was created to catch:**
- Cold-start agents with no routing mechanism (fixed by adding master index.md + session startup sequence to SKILL.md)

---

## Scenario 8: Content Traceability — No Invented Claims

**Goal:** Verify the skill enforces the "every claim traces to a raw source" rule.

**Setup:**
```
skill-test-8/
├── CLAUDE.md
├── raw/
│   └── narrow-source.md       # a short focused article, ~5 KB, covering ONE specific topic
└── wiki/
    ├── index.md
    └── log.md
```

The raw source should be narrow enough that it's obvious when the agent adds general knowledge.

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-8/raw/narrow-source.md` using the llm-wiki-ingest skill. Every claim in your wiki pages must be traceable to the raw source. Do NOT add information from general knowledge — mark uncertain claims `[UNVERIFIED]` or omit them.

**Expected behavior:**
- Agent reads the raw source in full
- Agent creates wiki pages that only contain claims present in the raw source
- Any inferred claims are marked `[UNVERIFIED]`
- Any contradictions with existing pages are flagged in a Contradictions section

**Pass criteria:**
- Manual spot-check of the output: every factual claim in the wiki pages can be found in the raw source
- Uncertain claims are marked
- No invented claims

**Fail signals:**
- Wiki page contains benchmarks, version numbers, or facts not in the raw source
- Wiki page confidently states things that require general knowledge beyond the source
- No `[UNVERIFIED]` markers on inferred content

**Gap this scenario was created to catch:**
- General knowledge leakage (an ongoing risk, not from a specific fix — but must be tested)

---

## Scenario 9: Newsletter Consolidation — Prevent Over-fragmentation

**Goal:** Verify the skill consolidates related articles into thematic summaries instead of creating one page per source.

**Setup:**
```
skill-test-9/
├── CLAUDE.md
├── raw/
│   ├── caching-part-1.md        # "A Crash Course in Caching - Part 1"
│   ├── caching-part-2.md        # "A Crash Course in Caching - Part 2"
│   ├── caching-final.md         # "A Crash Course in Caching - Final Part"
│   ├── distributed-caching.md   # standalone article on distributed cache patterns
│   └── redis-production.md      # standalone article on Redis usage
└── wiki/
    ├── index.md
    └── log.md
```

Use real newsletter-style articles (copies from `system-design/raw/2024PaidNewsletter/` work well).

**Cold-start prompt:**
> You are a cold-start agent. Ingest the 5 files in `skill-test-9/raw/` using the llm-wiki-ingest skill. These are all related articles on caching. Apply the newsletter consolidation pattern from patterns.md.

**Expected behavior:**
- Agent recognizes the 3-part series (Part 1 / Part 2 / Final) and consolidates into ONE source summary (e.g., `caching-deep-dive.md`)
- Agent groups the 2 standalone articles into thematic summaries (or updates existing pages if they exist)
- Total new wiki pages: roughly 2-4, NOT 5
- Source summaries reference multiple raw files in their `sources` frontmatter

**Pass criteria:**
- Wiki page count < raw file count (consolidation happened)
- The 3-part series produces exactly 1 source summary
- Source summaries list all consolidated raw files in frontmatter

**Fail signals:**
- 5 source summaries created (one per raw file — no consolidation)
- Part 1/2/Final each get their own pages with duplicate content
- Agent creates a concept page for every minor term mentioned

**Gap this scenario was created to catch:**
- Newsletter consolidation pattern (documented in patterns.md Pattern 1)
- Page count red flag ("96 articles do not become 96 pages")

---

## Scenario 10: Notion Export Handling — UUID Stripping and Triage

**Goal:** Verify the skill handles Notion export artifacts (UUIDs, nested dirs, co-located images, mixed content).

**Setup:**
```
skill-test-10/
├── CLAUDE.md
├── raw/
│   └── notion-export/
│       ├── Research 3f8a9b2c4d5e6f7890abcdef12345678.md      # UUID suffix
│       ├── Project Plan abc123def456abc123def456abc12345.md   # UUID, operational
│       ├── Contract Monitor 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d/
│       │   └── Todos 9876543210fedcba9876543210fedcba.md      # nested, UUID
│       └── API Deep Dive 5f4e3d2c1b0a9876543210fedcba9876.md  # knowledge
└── wiki/
    ├── index.md
    └── log.md
```

The file contents can be short stubs — the point is the naming pattern and triage behavior.

**Cold-start prompt:**
> You are a cold-start agent. Files in `skill-test-10/raw/notion-export/` are a Notion export dump. Follow the Notion export handling pattern in patterns.md Pattern 2 before ingesting anything.

**Expected behavior:**
- Agent identifies Notion UUID suffixes via the regex `[0-9a-f]{32}$` on filenames (pre-ingest)
- Agent proposes stripping UUIDs — stops for user confirmation before modifying `raw/`
- After approval, files are renamed: `Research.md`, `Project Plan.md`, `Contract Monitor/Todos.md`, `API Deep Dive.md`
- Agent classifies each file: Knowledge (API Deep Dive), Operational (Project Plan, Contract Monitor/Todos), Knowledge-borderline (Research)
- Agent proposes moving operational files to a reference directory (e.g., `raw/non-domain-reference/`)
- Only approved Knowledge files are ingested

**Pass criteria:**
- UUIDs stripped from filenames (or proposed for stripping)
- Operational files correctly identified and separated
- Agent pauses for user decisions on borderline files
- No operational files ingested as wiki pages

**Fail signals:**
- Agent ingests files with UUIDs in the `sources` frontmatter (ugly paths)
- Agent silently strips UUIDs without asking
- Operational files (Todos, Project Plan) get ingested as wiki pages

**Gap this scenario was created to catch:**
- Notion export handling pattern (documented in patterns.md Pattern 2)
- Destructive rename operations require user approval
- Triage classification for mixed Notion content

---

## Scenario 11: Cross-Domain Meta-Wiki Page Creation

**Goal:** Verify the skill creates cross-domain comparison pages using the `wiki:` prefix source convention.

**Setup:** Miniature monorepo with 2 domains and existing wiki pages in both.

```
skill-test-11/
├── CLAUDE.md            # shared methodology
├── index.md             # master router
├── cross-domain/
│   ├── WIKI.md          # meta-wiki schema
│   └── wiki/
│       ├── index.md
│       ├── log.md
│       └── comparisons/
├── domain-a/
│   ├── WIKI.md
│   ├── raw/
│   └── wiki/
│       └── concepts/
│           └── caching-distributed.md   # pre-populated
└── domain-b/
    ├── WIKI.md
    ├── raw/
    └── wiki/
        └── concepts/
            └── caching-local.md         # pre-populated
```

**Cold-start prompt:**
> You are a cold-start agent. The user asks: "Create a cross-domain comparison page for caching across domain-a and domain-b." Use the llm-wiki-ingest skill's cross-domain comparison agent workflow (see agent-prompts.md and patterns.md Pattern 3).

**Expected behavior:**
- Agent identifies relevant wiki pages in both domains
- Reads both pages in full
- Creates `cross-domain/wiki/comparisons/caching-domain-a-vs-domain-b.md`
- Frontmatter `sources` uses `wiki:` prefix: `wiki:domain-a/wiki/concepts/caching-distributed.md`
- Comparison table cites specific wiki pages per cell
- Updates `cross-domain/wiki/index.md` and `log.md`
- Does NOT touch raw files (meta-wiki has no raw/)

**Pass criteria:**
- Comparison page exists in correct location
- Sources use `wiki:` prefix, not `raw:` prefix
- At least 5 comparison dimensions in the table
- Each dimension cites a specific wiki page

**Fail signals:**
- Page created in `domain-a/wiki/` or `domain-b/wiki/` instead of `cross-domain/wiki/comparisons/`
- Sources list raw files instead of wiki pages
- Agent invents comparison claims not present in the source wiki pages

**Gap this scenario was created to catch:**
- Cross-domain meta-wiki pattern (documented in patterns.md Pattern 3)
- The `wiki:` prefix source citation convention
- Cross-domain comparison agent template (agent-prompts.md)

---

## Scenario 12: Monorepo Restructuring — Propose, Don't Execute

**Goal:** Verify the skill proposes a restructure plan for an overgrown single-wiki but does not silently execute it.

**Setup:**
```
skill-test-12/
├── CLAUDE.md            # single-wiki schema with 3+ unrelated topics listed
└── wiki/
    ├── index.md
    ├── log.md
    ├── concepts/
    │   ├── ood-encapsulation.md
    │   ├── web3-erc20.md
    │   └── ml-embeddings.md    # three wildly different domains in one wiki
    └── source-summaries/
```

**Cold-start prompt:**
> You are a cold-start agent. Review the structure of `skill-test-12/`. Does it need monorepo restructuring? If yes, propose a plan — do NOT execute it without explicit user approval. Reference patterns.md Pattern 4.

**Expected behavior:**
- Agent identifies restructure trigger signs (3+ unrelated topics in CLAUDE.md, mixed concept pages)
- Agent produces a proposal: which domains to split into, which files go where
- Agent does NOT execute file moves without user approval
- Agent references patterns.md Pattern 4 steps in the proposal

**Pass criteria:**
- Written proposal with domain names, directory structure, and migration plan
- No files actually moved
- User decision point clearly marked

**Fail signals:**
- Agent silently restructures the wiki
- Agent declares "no restructure needed" despite obvious domain divergence
- Agent refuses to consider restructuring at all

**Gap this scenario was created to catch:**
- Monorepo restructuring pattern (documented in patterns.md Pattern 4)
- Destructive operations require explicit approval (operational discipline)

---

## Scenario 13: Proprietary Content Generalization

**Goal:** Verify the skill generalizes company-specific names in concept/technique pages but preserves them in source summaries.

**Setup:**
```
skill-test-13/
├── CLAUDE.md
├── raw/
│   └── internal-audit.md        # content mentions "AcmeCorp", "ProjectPhoenix", "InternalAPI v3"
└── wiki/
    ├── index.md
    └── log.md
```

The raw file should discuss a technical topic (e.g., security audit findings) while liberally mentioning internal project/company names. Example: "The AcmeCorp ProjectPhoenix audit identified a reentrancy vulnerability in the InternalAPI v3 payment flow."

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-13/raw/internal-audit.md`. The source contains company-specific names (AcmeCorp, ProjectPhoenix, InternalAPI v3). Follow the proprietary content generalization rule in SKILL.md.

**Expected behavior:**
- Source summary page MAY retain the proprietary names (it describes a specific source)
- Concept pages (e.g., `reentrancy-vulnerability.md`) generalize: "a production audit identified..." instead of "the AcmeCorp audit identified..."
- Technique pages (e.g., `payment-flow-security.md`) generalize similarly
- No mention of "AcmeCorp", "ProjectPhoenix", or "InternalAPI v3" in concept/technique pages

**Pass criteria:**
- Grep concept/technique pages for the proprietary names — zero matches
- Grep source summary for proprietary names — matches allowed
- Generic replacements ("the project", "a production audit", "the payment flow") used in generalized content

**Fail signals:**
- Concept pages contain proprietary names
- Source summary is overly scrubbed (losing useful context)
- Agent generalizes to the point of uselessness ("something happened somewhere")

**Gap this scenario was created to catch:**
- Proprietary content leakage (SKILL.md Critical Non-Negotiables rule #7)
- Real-world risk observed during Memeland/Memeverse ingests

---

## Scenario 14: Contradiction Flagging — No Silent Overwrites

**Goal:** Verify the skill flags contradictions between new sources and existing wiki pages instead of silently updating.

**Setup:**
```
skill-test-14/
├── CLAUDE.md
├── raw/
│   └── new-claim.md             # states "Lido fee is 5% of rewards"
└── wiki/
    ├── index.md
    ├── log.md
    ├── source-summaries/
    │   └── old-source.md        # existing summary states "Lido fee is 10%"
    └── protocols/
        └── lido-protocol.md     # existing page says "10% protocol fee (5% to node operators, 5% to DAO treasury)"
```

Pre-populate the wiki with an existing page that has a specific factual claim. The new raw source should contradict that claim.

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-14/raw/new-claim.md`. Before silently updating `lido-protocol.md`, check for contradictions with existing content and flag them explicitly.

**Expected behavior:**
- Agent reads the raw source and notices the 5% claim
- Agent reads `lido-protocol.md` and notices the 10% claim
- Agent does NOT silently overwrite the old claim
- Agent adds a Contradictions section to `lido-protocol.md` listing both claims with their sources
- Agent flags the contradiction in the log entry and asks the user how to resolve

**Pass criteria:**
- `lido-protocol.md` has a new Contradictions section
- Both claims preserved with their source citations
- Log entry notes the contradiction
- Agent requests user decision

**Fail signals:**
- Old claim silently overwritten
- New claim silently ignored
- Contradictions section missing

**Gap this scenario was created to catch:**
- Contradiction handling rule (SKILL.md Critical Non-Negotiables rule #3)
- Real-world pattern observed with Lido fee 5% vs 10% during session 2026-04-09

---

## Scenario 15: Append-Only Log with Correction Notes

**Goal:** Verify the skill appends correction notes to the log instead of editing past entries.

**Setup:**
```
skill-test-15/
├── CLAUDE.md
├── raw/
│   └── test-source.md
└── wiki/
    ├── index.md
    └── log.md                   # has an existing entry with an incorrect detail
```

Pre-populate `log.md` with an entry that has an obvious error:
```markdown
## [2026-04-10] ingest | Previous batch
Pages created: [[nonexistent-page-a]], [[nonexistent-page-b]]
Notes: This claim is wrong — no such pages exist.
```

**Cold-start prompt:**
> You are a cold-start agent. First, audit `wiki/log.md`. The previous entry references pages that do not exist. Correct this WITHOUT editing the original entry. Then ingest `raw/test-source.md`.

**Expected behavior:**
- Agent identifies the error in the previous log entry
- Agent APPENDS a correction note at the bottom: `## [2026-04-11] note | Log correction`
- Original incorrect entry remains byte-for-byte unchanged
- Correction note explains what was wrong and what the correct state is

**Pass criteria:**
- `git diff` (or file comparison) shows NO changes to lines containing the old entry
- New correction note appended at the bottom
- Correction note dated today, not the original date

**Fail signals:**
- Original log entry modified
- Old entry silently deleted
- No correction note added

**Gap this scenario was created to catch:**
- Append-only log rule (SKILL.md Critical Non-Negotiables rule #4)
- Real pattern used during Morpho ingest count correction in session 2026-04-09

---

## Scenario 16: Script Failure Fallback

**Goal:** Verify the skill detects broken conversion scripts and falls back to the minimal template.

**Setup:**
```
skill-test-16/
├── CLAUDE.md
├── scripts/
│   └── mhtml_to_md.py           # deliberately broken — produces 32-byte stub output
├── raw/
│   └── article.mhtml            # valid Substack-style mhtml
└── wiki/
    ├── index.md
    └── log.md
```

The `mhtml_to_md.py` should be a 3-line Python script that writes a constant short string like `"# AUTH_WALL_STUB"` to the output. This simulates the real failure mode observed with the garen-wiki script.

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-16/raw/article.mhtml` using the llm-wiki-ingest skill. A conversion script exists at `scripts/mhtml_to_md.py` — use it first, but verify the output.

**Expected behavior:**
- Agent tries `scripts/mhtml_to_md.py` first (preferred per format-conversion.md)
- Agent runs the script and checks output size
- Agent detects the stub output (< 500 bytes, contains only boilerplate)
- Agent falls back to the minimal BeautifulSoup + html2text template in format-conversion.md
- Agent produces a valid `.md` file via fallback
- Agent notes the script failure in the log

**Pass criteria:**
- Final `.md` file is substantial (not 32 bytes)
- Fallback was used
- Script failure logged

**Fail signals:**
- Agent ingests the broken 32-byte output as if it were valid
- Agent gives up entirely instead of falling back
- Agent silently replaces the broken script without user permission

**Gap this scenario was created to catch:**
- Conversion script failure detection (format-conversion.md Conversion Script Failure Detection section)
- Real pattern from Substack mhtml conversion failure in original Test 1

---

## Scenario 17: Backtick Wrapping for Generics

**Goal:** Verify the skill wraps generic types in backticks to prevent markdown rendering bugs.

**Setup:**
```
skill-test-17/
├── CLAUDE.md
├── raw/
│   └── java-design-problem.md   # contains Java code with Map<String, List<Integer>>,
│                                # SortedSet<Long>, HashMap<K, V>, Optional<T>
└── wiki/
    ├── index.md
    └── log.md
```

The raw file should mention generic types both in code blocks AND in prose. For example: "The `Map<String, Integer>` stores..." vs "Map<String, Integer> is used for..."

**Cold-start prompt:**
> You are a cold-start agent. Ingest `skill-test-17/raw/java-design-problem.md`. Pay attention to generic types in prose (e.g., `Map<K, V>`). Follow the backtick wrapping rule in SKILL.md.

**Expected behavior:**
- In code blocks (fenced with ```), generics appear as-is (no extra backticks needed)
- In prose, every bare generic type (`<T>`, `Map<K, V>`, `List<Integer>`, etc.) is wrapped in single backticks
- Wiki pages render correctly in Obsidian (no hidden `<Integer>` interpreted as HTML)

**Pass criteria:**
- Grep wiki pages for unwrapped `<[A-Z]` patterns outside of code blocks — zero matches
- All prose-level generics have backticks: `` `Map<String, Integer>` ``

**Fail signals:**
- Bare `<T>` or `<Integer>` in prose (would break rendering)
- Double-backticked generics in code blocks (over-correction)
- Inconsistent wrapping across pages

**Gap this scenario was created to catch:**
- Backtick wrapping rule (SKILL.md File Naming / Backtick generic types)
- Real bug fixed across 11 files (~32 occurrences) in session 2026-04-11

---

## Scenario 18: Verification Script Run

**Goal:** Verify the skill can run the wiki verification script and interpret its output.

**Setup:**
```
skill-test-18/
├── CLAUDE.md
├── scripts/
│   └── verify-wiki.sh           # the template from patterns.md Pattern 5
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── source-summaries/
│   │   └── clean-page.md        # valid frontmatter, valid wikilinks, sources section
│   └── concepts/
│       └── broken-page.md       # deliberately broken — missing frontmatter, broken link
```

Pre-populate with one clean page and one deliberately broken page.

**Cold-start prompt:**
> You are a cold-start agent. Run `scripts/verify-wiki.sh` against `skill-test-18/wiki/` and report the findings. Do not fix anything — just report what the script found.

**Expected behavior:**
- Agent locates `scripts/verify-wiki.sh`
- Agent runs it with appropriate arguments
- Agent parses the output and reports: X files checked, N failures
- Agent correctly identifies `broken-page.md` as the failing file
- Agent does NOT auto-fix the issues without permission

**Pass criteria:**
- Script executed
- Exit code and failure count reported accurately
- Specific broken checks identified (missing frontmatter, broken wikilink)

**Fail signals:**
- Agent can't find the script
- Agent tries to implement verification manually instead of running the script
- Agent auto-fixes the broken page without approval

**Gap this scenario was created to catch:**
- Verification script pattern (documented in patterns.md Pattern 5)
- Tool usage vs reimplementation discipline

---

## Scenario 19: Cold-Start Readiness Audit

**Goal:** Verify the skill can audit an unfamiliar wiki for cold-start readiness issues.

**Setup:**
```
skill-test-19/
├── CLAUDE.md                    # exists but no First Read sequence
└── wiki/
    ├── index.md                 # missing YAML frontmatter (broken)
    ├── log.md                   # ok
    ├── source-summaries/
    │   └── orphan-page.md       # exists but not in index — orphan
    └── concepts/
        └── referenced-but-missing.md content: [[nonexistent-target]]  # broken wikilink
```

Deliberately introduce multiple cold-start gaps: missing frontmatter, missing index entries, broken wikilinks, no startup sequence in CLAUDE.md.

**Cold-start prompt:**
> You are a cold-start agent. You were handed a wiki at `skill-test-19/` that may have cold-start readiness issues. Audit it against the llm-wiki.md pattern and your own skill's requirements. Produce a report listing every gap. Do NOT fix anything.

**Expected behavior:**
- Agent reads CLAUDE.md and notes missing startup sequence
- Agent reads wiki/index.md and notes missing frontmatter
- Agent glob-scans all wiki pages for orphans (pages not in index)
- Agent scans wikilinks and identifies broken references
- Agent produces a structured audit report with severity levels (CRITICAL / WARN / INFO)
- Agent does NOT auto-fix — the audit is read-only

**Pass criteria:**
- Audit report covers all 4 deliberately-introduced gaps
- Report distinguishes CRITICAL (broken links, missing frontmatter) from WARN (orphans) from INFO (suggestions)
- No files modified

**Fail signals:**
- Agent fixes issues without being asked
- Audit misses obvious gaps
- Audit mixes up severity (broken link reported as INFO)

**Gap this scenario was created to catch:**
- Cold-start readiness audit pattern (used during session 2026-04-11 to produce master index.md)
- Read-only audit discipline (audits do not mutate state)

---

## Cold-Start Subagent Prompt Template

Use this template when spawning test subagents for any scenario above. Replace placeholders.

```
You are a cold-start agent with ZERO memory of prior sessions. You are running a test of the llm-wiki-ingest skill.

TODAY'S DATE: {{today}}

TASK: {{scenario_task_description}}

SKILL TO USE: C:\Users\garet\.claude\skills\llm-wiki-ingest\
  - Read SKILL.md first
  - Branch to format-conversion.md, patterns.md, quality-gates.md, agent-prompts.md as the skill directs

TEST FIXTURE: {{fixture_path}}
  - You may read/write only within this fixture
  - NEVER touch production wikis (garen-wiki, web3-wiki, etc.)

INSTRUCTIONS:
1. Read the skill files as SKILL.md directs
2. Read the fixture's CLAUDE.md to understand the test wiki's schema
3. List raw files in the fixture
4. Execute the full ingest workflow (triage, convert if needed, read, write, update index/log)
5. You are edit + consolidation + review in one agent — do not spawn further subagents

REPORT WHEN DONE:
- Files processed
- Files skipped (with reason)
- Wiki pages created (full paths)
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
cd <workspace-root>
find skill-test-* -type f -delete
find skill-test-* -type d -empty -delete
```

Verify no `skill-test-*` directories remain in the workspace before declaring the test session complete.

---

## When a Scenario Fails

1. Do NOT fix the test to make it pass
2. Diagnose: which part of the skill was missing, unclear, or wrong?
3. Edit the relevant skill file (SKILL.md, format-conversion.md, etc.)
4. Re-run the specific failed scenario to confirm the fix
5. Run Scenario 1 (happy path) as a smoke test to ensure the fix didn't break anything else
6. Update TEST.md if the failure revealed a new scenario worth capturing

---

## Scenario Coverage Summary

| # | Scenario | Gap origin |
|---|---|---|
| 1 | Happy path (md + mhtml batch) | Baseline — must work |
| 2 | Unknown format detection | Found in original Test 2 — led to Step -1 pre-flight + Unknown Format Handling |
| 3 | Slug collision | Found in original Test 1 — led to File Naming collision warning |
| 4 | Page count discipline | Found in original Test 1 — led to Step 4 heuristics table |
| 5 | Date awareness | Found in original Test 1 (subagents used stale dates) — led to Frontmatter date awareness block |
| 6 | Connections section vs link-once | Found in original Test 1 — led to Internal Linking Connections rule |
| 7 | Monorepo routing | Found in cold-start audit — led to master index.md + startup sequence |
| 8 | Content traceability | Core rule from llm-wiki.md — ongoing validation |
| 9 | Newsletter consolidation | Real pattern from 96-article ingest; documented in patterns.md Pattern 1 |
| 10 | Notion export handling | Real pattern from 151-file web3-wiki ingest; documented in patterns.md Pattern 2 |
| 11 | Cross-domain meta-wiki creation | Designed and built in session 2026-04-11; documented in patterns.md Pattern 3 |
| 12 | Monorepo restructuring (proposal) | Done for garen-wiki during session; documented in patterns.md Pattern 4 |
| 13 | Proprietary content generalization | Real issue during Memeland/Memeverse ingests (audit findings leaked company names into concept pages) |
| 14 | Contradiction flagging | Real case during Lido ingest — fee rate 5% vs 10% contradiction across raw sources |
| 15 | Append-only log correction | Used during Morpho ingest count correction in session 2026-04-09 |
| 16 | Script failure fallback | Real failure in original Test 1 — garen-wiki mhtml_to_md.py produced 32-byte stub |
| 17 | Backtick wrapping for generics | Real bug fixed across 11 files (~32 occurrences) in session 2026-04-11 |
| 18 | Verification script run | verify-wiki.sh built in patterns.md Pattern 5; not previously tested via a scenario |
| 19 | Cold-start readiness audit | Audit pattern used to produce master index.md in session 2026-04-11 |

Every scenario in this file exists because a specific failure was observed in testing, a specific pattern emerged from real session work, or a specific rule in llm-wiki.md needs ongoing validation. No speculative scenarios — every one traces to something that actually happened.
