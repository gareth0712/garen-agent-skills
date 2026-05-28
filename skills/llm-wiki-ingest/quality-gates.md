# Quality Gates

This document describes the multi-phase quality pipeline for batch ingests. Use it any time you run a batch of 3+ files or create 5+ new pages in one pass.

---

## The Pipeline

```
Phase 1: Parallel edit agents
Phase 2: Consolidation agent (sequential — waits for Phase 1)
Phase 3: Review agent
Phase 4: Fix agent (only if review found issues)
Phase 5: Final review (optional)
```

---

## Phase 1: Parallel Edit Agents

Run 2-5 agents in parallel. Each handles a subset of raw files.

**Each edit agent:**
- Processes its assigned raw files (triage, convert if needed, read, ingest)
- Creates source summary pages and type-specific pages (concept, technique, design-problem, protocol)
- Does NOT touch `wiki/index.md`, `wiki/overview.md`, or `wiki/log.md`
- Reports: files processed, files skipped (with reason), pages created (exact filenames)

**Why no shared files in Phase 1:** Race conditions. If two agents both write to `wiki/index.md`, the second write overwrites the first. Shared files are handled exclusively in Phase 2.

Split files evenly. For 20 newsletter articles, run 4 agents of 5 articles each. For 14 book chapters, run 3-4 agents of 4-5 chapters each.

---

## Phase 2: Consolidation Agent (Sequential)

One agent. Runs after all Phase 1 agents have completed.

**The consolidation agent:**
1. Reads the Phase 1 agents' reports to get the list of newly created files
2. Actually reads those files on disk (do NOT trust the report for filenames — verify)
3. Updates `wiki/index.md` with new entries, one per page
4. Updates `wiki/overview.md` with new topic sections or updated synthesis
5. Appends a single detailed entry to `wiki/log.md` covering the full batch

**CRITICAL: Read actual files, not just reports.** Phase 1 agents may have named files differently from what they reported, or may have skipped files without noting it clearly. The consolidation agent must discover the actual state of the wiki directory.

---

## Phase 3: Review Agent

Can run in parallel with Phase 2 IF scoped correctly (see race condition warning below).

**The review agent:**
1. Samples 3-5 newly created pages and checks each one
2. Checks all pages for wikilink integrity (do targets exist?)
3. Spot-checks content alignment against 3 raw source files
4. Does NOT re-read all pages — samples are sufficient for a quality gate
5. Produces a report with verdict: PASS / WARN / FAIL

### Race Condition Warning

If consolidation and review run in parallel:
- The review agent reads `wiki/index.md` BEFORE consolidation has updated it
- The review agent will flag missing index entries as errors — which are false positives
- This produces noise and may cause unnecessary fix work

**Recommended approach:** Run consolidation first, then review. The extra few minutes are worth the clean result.

If you must run them in parallel, tell the review agent explicitly: "Do NOT check `wiki/index.md` or `wiki/log.md` — they are being updated concurrently by another agent."

---

## Phase 4: Fix Agent (If Review Found Issues)

Only spawned if Phase 3 verdict is WARN or FAIL.

**The fix agent:**
- Reads the review report
- Applies targeted fixes to the specific pages flagged
- Does NOT re-run a full review pass
- Reports: issues fixed, issues that require user decision (e.g., contradictions)

Do not scope the fix agent too broadly. A WARN verdict means "fix the specific issues listed", not "re-ingest everything".

---

## Phase 5: Final Review (Optional)

Only needed after a FAIL verdict or a fix of multiple CRITICAL issues.

Scope: verify the specific fixes from Phase 4 were applied correctly. Do not re-review the entire wiki.

---

## Review Checklist

The review agent runs these checks. Reference this list when writing review agent prompts.

### Frontmatter (sample 3-5 pages)

- [ ] Every page has YAML frontmatter
- [ ] `type` field matches the subdirectory (concept in concepts/, technique in techniques/, etc.)
- [ ] `sources` field lists at least one source, using paths relative to repo root
- [ ] `created` and `updated` dates are populated and in ISO format (YYYY-MM-DD)
- [ ] `tags` are lowercase and hyphen-separated
- [ ] `related` lists wikilinks to other pages

### Wikilink Integrity (all pages)

- [ ] Every `[[wikilink]]` target exists as an actual file in the wiki
- [ ] No wikilinks point to non-existent pages (broken links)
- [ ] Common mistake: `[[lido]]` when the file is `lido-protocol.md`

### Index Completeness (after consolidation)

- [ ] Every newly created page appears in `wiki/index.md` exactly once
- [ ] No duplicate entries in the index
- [ ] Each index entry has a specific one-line description (not "concept page about X")

### Content Alignment (spot-check 3 pages)

- [ ] Claims in wiki pages trace to the referenced raw sources
- [ ] No claims appear that are not in the raw source (no inserted general knowledge)
- [ ] Uncertain claims are marked `[UNVERIFIED]`
- [ ] Contradictions are flagged, not silently overwritten

### Sources Section (sample 5 pages)

- [ ] Every page ends with `## Sources`
- [ ] Source paths are relative to repo root (e.g., `system-design/raw/book-chapters/...`), not absolute
- [ ] Source paths point to files that actually exist in raw/

### Proprietary Content (if applicable)

- [ ] Company-specific names are generalized in concept/technique/protocol pages
- [ ] Company names appear only in source-summary pages

### Dates

- [ ] `updated` date on modified pages reflects the current date, not the original creation date
- [ ] `created` date on new pages is set (not left as placeholder)

### Markdown Rendering

- [ ] Generic types like `List<Integer>` are wrapped in backticks
- [ ] No bare `<TypeName>` outside of code blocks
- [ ] No emoji in wiki pages

---

## Verdict Definitions

| Verdict | Meaning | Next action |
|---------|---------|-------------|
| PASS | No critical issues, warnings acceptable | Declare done |
| WARN | Minor issues (missing cross-references, stale dates, missing index entries) | Optional fix agent for cleanliness |
| FAIL | Critical issues (broken wikilinks, missing sources, false claims, proprietary leaks) | Required fix agent |

A WARN verdict means the wiki is usable but not clean. FAIL means the wiki has defects that could mislead users or break rendering.

---

## Common Pitfalls Checklist

Check this list after any batch ingest. These are the things that WILL go wrong if not watched for.

### Structural

1. **Broken wikilinks** — Links to pages that don't exist. Always verify targets exist before creating a link.
2. **Duplicate index entries** — Same page listed twice in different sections. Scan the full index before appending.
3. **Missing frontmatter on index.md / log.md** — These ARE wiki pages and need frontmatter too.
4. **Wrong `type` in frontmatter** — Must match directory. `concept` in `concepts/`, not `technique`.
5. **Absolute vs relative source paths** — Always use paths relative to domain root, never absolute filesystem paths.

### Race Conditions and Sequencing

6. **Parallel agents editing index.md** — The second write overwrites the first. Always use a dedicated consolidation agent for shared files.
7. **Review agent reads stale index.md** — When consolidation and review run in parallel. Tell the review agent to skip index.md explicitly.
8. **Consolidation agent guesses page names** — The agent should read actual files on disk, not trust what Phase 1 agents reported.
9. **Log entries with mismatched pages** — Log says "Pages created: A, B, C" but the files don't exist. Read actual files before logging.

### Content Quality

10. **Empty stubs passing triage** — Auth-wall MHTML, template placeholders. Read first 30 lines before ingesting.
11. **Creating too many pages from batch** — 96 newsletter articles do NOT become 96 concept pages. Consolidate by topic. Enrich existing pages.
12. **Unwrapped generics** — `<T>`, `List<Integer>` breaking Obsidian rendering. Wrap in backticks.
13. **Proprietary content leaks** — Internal project names bleeding into general concept pages. Generalize or keep in source summaries only.
14. **Invented claims** — Agent inserts general knowledge not in the raw source. Every claim needs a source.
15. **Silent contradiction overwrite** — New source contradicts existing page, agent silently updates without flagging. Must add Contradictions section.

### Index and Log

16. **Index entry too generic** — "Concept about caching" instead of "Three eviction strategies (LRU, LFU, TTL) and their trade-offs in distributed caches". Be specific.
17. **Log entry logged before pages exist** — Log first, then create pages — wrong order. Create pages first, then log.
18. **Editing existing log entries** — Log is append-only. Never edit. Only add at the bottom.

### Domain Routing (Monorepo Only)

19. **Pages created in wrong domain** — Checked the schema for `system-design/` but the source belongs in `ood/`. Always verify domain routing in `index.md` first.
20. **Cross-domain topic not flagged** — A concept appears in two domains but the agent did not update the Cross-Domain Topic Map in the root `index.md`.

### Multilingual

21. **Non-English content in English wiki** — For multilingual sources, triage by language if the wiki is English-only. Ask the user if unsure.

### Images

22. **Image files moved without updating references** — Do not move images out of `raw/assets/` without updating every markdown reference to them.
