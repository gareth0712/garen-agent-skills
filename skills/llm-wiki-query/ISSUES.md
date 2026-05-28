# ISSUES.md — Known limitations and open risks

This file tracks known limitations, untested assumptions, and open risks for the llm-wiki-query skill. It exists because some problems cannot be fixed today but must not be forgotten.

**Distinction from TEST.md:** TEST.md validates what the skill DOES handle. ISSUES.md documents what the skill MIGHT NOT handle, or handles in ways that haven't been proven in production.

---

## Active Issues

### Issue #1: Skill is untested in production

**Severity:** HIGH — the skill's reliability is theoretical until validated by independent use

**Description:**
The skill was authored in session 2026-04-16. It has not been used for a real query by:
- A fresh Claude session (without this session's context)
- A human user following the skill manually
- Any session other than the one that wrote it

The TEST.md scenarios cover three important cases (factual lookup, multi-page synthesis, gap detection), but none of these have been run against real fixtures. All expected behaviors are based on design intent, not observed outcomes.

**Why this matters:**
A closed loop of "author tests own work" catches obvious bugs but misses assumptions the author took for granted. Real validation requires independent use.

**How to resolve:**
On the next query task, start a fresh Claude session. Let it discover and invoke the skill. Observe where it struggles or makes wrong assumptions. Those observations become new TEST.md scenarios (or ISSUES.md entries).

**Workaround until resolved:**
Treat the skill as a hypothesis, not a validated tool. When it fails in a new way, update the skill rather than forcing the query through manually.

---

### Issue #2: Index-first search degrades past ~500 pages

**Severity:** MEDIUM — current wikis are unlikely to hit this limit, but planning for growth matters

**Description:**
The skill's primary search mechanism is scanning `wiki/index.md` one-line descriptions. This works well when the index has ~50-300 entries — an agent can read the entire index in one context window and identify relevant pages.

As the wiki grows past ~500 pages, two problems emerge:
1. The index file itself becomes too large to read efficiently in a single pass
2. One-line descriptions may become too generic to distinguish relevant from irrelevant pages

**Why this matters:**
A degraded index search means the agent misses relevant pages and produces incomplete answers. The user may not realize the incompleteness if no gap is flagged.

**How to resolve:**
Two mitigations when approaching the 500-page limit:
1. Improve index descriptions: if one-line entries are generic ("concept about caching"), upgrade them to specific ("LRU vs LFU eviction trade-offs under different workload patterns"). Good descriptions push the useful range higher.
2. Add an embedding-based or keyword search layer: store a search index separately, run keyword matching against it, then read the top N pages. This is the approach Karpathy anticipates for larger wikis.

**Workaround until resolved:**
For wikis approaching 500 pages, scan the index by section (Concepts, Techniques, Protocols separately) rather than reading the full index at once. This improves recall without requiring a new search mechanism.

---

### Issue #3: No dedup check on file-back — near-duplicate synthesis pages may accumulate

**Severity:** MEDIUM — creates wiki clutter and misleads future queries

**Description:**
The file-back workflow checks for exact filename collisions (slug collision check) but does not detect near-duplicate synthesis pages with different names.

Example: A user queries "how does LRU compare to LFU?" and files back `lru-vs-lfu-comparison.md`. Three sessions later, a user queries "what are the trade-offs between LRU and LFU cache eviction?" and the file-back agent creates `lru-lfu-tradeoffs.md` — a near-duplicate with different framing.

**Why this matters:**
Near-duplicate pages fragment the wiki's synthesis layer, make future index scans noisy, and may cause future queries to produce inconsistent answers depending on which synthesis page they happen to find first.

**How to resolve:**
Before any file-back, the file-back agent should:
1. Read the index section for `wiki/syntheses/` and `wiki/comparisons/`
2. Check for any page whose one-line description substantially overlaps with the new synthesis
3. If overlap is found, present both to the user and ask: "Update existing page `[[near-duplicate]]` or create a distinct new page?"

This requires the orchestrator to pass this "near-duplicate check" instruction to the file-back agent explicitly.

**Workaround until resolved:**
Before instructing file-back, manually scan the syntheses and comparisons sections of `wiki/index.md` for existing coverage of the same synthesis theme.

---

### Issue #4: Citation accuracy depends entirely on reader discipline — no automatic verification

**Severity:** MEDIUM — fabricated or misattributed citations are the most trust-damaging failure mode

**Description:**
The skill instructs agents to "only cite pages you actually read" and "never invent page names." But there is no automatic check that the pages cited in an answer actually contain the claimed information.

An agent under pressure to produce a complete answer may cite a page it read superficially, or may slightly paraphrase a claim in a way that isn't traceable to the source without careful re-reading.

**Why this matters:**
The entire value of a citation-backed wiki synthesis is that users can verify claims. A citation that points to a page that doesn't say what the answer claims destroys that value — and is harder to detect than a missing citation.

**How to resolve:**
Add a post-synthesis verification step: after producing the answer draft, for each cited claim, re-read the specific sentence or paragraph in the cited page that supports it. If no such sentence exists, mark the claim `[UNVERIFIED]` or remove it.

This step is already implicit in the skill ("every claim must trace to a specific page") but is not explicitly required as a verification pass.

**Workaround until resolved:**
When spawning a search-synthesis agent, explicitly instruct it to do one verification pass after drafting: "For each `[[page-name]]` citation in your answer, re-read that page and confirm the cited passage supports the claim."

---

### ~~Issue #5: File-back in monorepo requires domain routing — cross-domain syntheses have no home~~

**Severity:** ~~MEDIUM~~ — RESOLVED 2026-04-17

**Resolution:** Added monorepo cross-domain routing table to the "Where to file" section of SKILL.md (File-Back Rules). Single-domain syntheses go to `<domain>/wiki/syntheses/` or `<domain>/wiki/comparisons/`; cross-domain syntheses (source pages from ≥2 domains) go to `cross-domain/wiki/syntheses/` or `cross-domain/wiki/comparisons/` (create if absent), with source citations using `wiki:<domain>/<slug>` prefix. See SKILL.md File-Back Rules for full routing table.

---

### Issue #6: Orphan page detection not surfaced during queries

**Severity:** LOW — query task output is unaffected; relevant only if skill is extended to wiki health reporting

**Description:**
The skill has no mention of detecting or flagging pages with `related: []` (no outgoing links). A query agent scanning the wiki has no guidance on whether it should surface orphan awareness as part of its answer or gap report.

**Why this matters:**
Low impact for pure query tasks. If the skill is ever extended to include wiki health reporting (similar to `llm-wiki-lint`), orphan detection guidance will be needed here.

**How to resolve:**
If wiki health reporting is added to this skill, add an orphan detection pass after the index scan: flag any candidate pages that have `related: []` and appear not to be linked from any other page in the index.

**Workaround until resolved:**
Use `llm-wiki-lint` for wiki health checks including orphan detection. The query skill's scope is answering questions, not auditing the wiki graph.

---

### Issue #7: "Connections" section naming inconsistency between inline answer and filed-back page

**Severity:** LOW — functionally correct either way; creates minor cold-start confusion

**Description:**
In the answer structure for inline responses (Step 4, Synthesis Answer), item 3 is called "Connections noticed" with the description "wikilinks to related pages the user may want to read next." In the filed-back page structure (Page Conventions), item 4 is called "Connections" with the description "wikilinks to source pages with one-sentence context notes." The descriptions differ slightly, and it is unclear whether the same content should appear in both.

**Why this matters:**
Cold-start agents may wonder whether to include source-page context notes in the inline answer, or just navigation suggestions. The distinction is cosmetic but generates uncertainty.

**How to resolve:**
Unify the description: both contexts should say "wikilinks to related/source pages with one-sentence context notes." The inline answer can be slightly abbreviated, but the framing should match. Requires careful editing to avoid changing the meaning of the inline answer structure.

**Workaround until resolved:**
In both contexts, write wikilinks with one-sentence context notes. This is the more informative option and works correctly in both uses.

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
