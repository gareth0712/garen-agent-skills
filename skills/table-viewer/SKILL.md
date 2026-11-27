---
name: table-viewer
description: Build a row-table viewer page — interview first, spec, then build. Use when the user wants a table, list or viewer page for some data ("make a table / dashboard page for X", "let me browse, sort, filter X", "list everything in X so I can mark or review it"), or wants a table page added to an existing dashboard. Not for charts or KPI dashboards with no row table.
---

The owner has built this page type three times and is tired of re-stating what he wants. Everything below is the answer he has already given. A **viewer page** is one table of rows with search, sort, filters, marks and bulk actions. Never start from a blank page: read, ask, spec, then build.

Items marked _(agent default)_ are the agent's judgement, not the owner's words; the owner can cut them.

## Flow

1. **Read the repo.** Find the stack, the existing pages, the data source, the API conventions, the docs and tests layout. Reuse them; the skill fixes no framework. Open one existing page as the reference for look and structure. A fact the repo can answer is never asked. If the repo already has a table page or shared table component, build on it; if you would write the same plumbing (sortable header, filter module, editable cell, copy button) a second or third time, say so in the spec and propose extracting it. A fact you could not find goes into the interview as a numbered item marked "not verified", never silently assumed.
   Done when you can name: the data source, the serving process, how pages are registered, how tests run.
2. **Interview, one batched round.** Follow [references/interview.md](references/interview.md). _(agent default)_ One message, never one question per turn. Every numbered item has exactly this shape: the question with its proposed default on the first line; a line `Changes:` (what it is for, what it changes in the build); a line `If skipped:` (what you will do). Every group of the question bank appears, merged down to 8 to 12 items. Write the interview, spec and report in the language the owner writes in, or the one the repo or user instructions specify. Repeat the round only for items still open. Keep going until nothing is unclear. A question that appears after approval, while building: finish the layer you are on if the answer cannot change it, then ask in one batched message of the same shape; never guess and never ask one at a time.
   Done when every open item has an answer or an accepted default.
3. **Write the one-page spec** from [references/spec-template.md](references/spec-template.md) and wait for approval. _(agent default)_ It carries a table: asked by owner / added by agent's judgement / why / cost. No code before the yes.
4. **Build in layers.** Each layer works end to end before the next:
   1. Read-only table with real rows; row count checked against the source.
   2. Search, sort, filters, summary line.
   3. Marks and other writes.
   4. Optional features the owner chose.
5. **Verify** (below).
6. **Report** (below).

## What a finished page looks like

The owner's most complete page (about 8,300 rows) is the bar. Example: a book catalogue page at that level has a search box, 12 sortable columns, chips such as `status: unread (212)`, a line "Showing 40 of 4,200", a star and a note on every row, a bar "12 selected (3 not in the current filter): star, mark, copy ids", and a button that copies the row's id. Anything less is a draft.

## Always built, never asked

- Search box.
- Sortable columns.
- Filter chips that show counts.
- A summary / totals line at the top.
- Star and note on every row (never ask whether to build them; the only star question is what a star means).
- Multi-select with a bulk action bar.
- A copy button for the row's primary identifier (file path, id or URL).

## Always asked, never assumed

- A **can-delete mark**: does the page need one, and what does it feed?
- **Duplicate grouping**: which signals count as "the same", and does the page group by them?

## Always built too _(agent default)_

- Four states: loading, load error with Retry, empty source (say how to fill it), no match (with Clear filters).
- "N of M rows" after filtering.
- Sort with empty values last and a stable tiebreak.
- Filter logic: OR inside one dimension, AND across dimensions.
- Page index resets on any filter or sort change.
- Shift+click range selection.
- The bulk bar says how many selected rows sit outside the current filter before it acts.

Behaviour and traps for each item: [references/patterns.md](references/patterns.md).

## Reading the owner's reply

The owner answers short: "1 yes, 2 default, 5 no". Map each number to its question; "default" takes your proposed default. "Rest default" makes every unnamed item take its default. Without those words, an item the reply skips is still open: ask it again in a second, shorter round on its own, not folded into the spec message. Never treat silence as yes for a write, a disk action, the can-delete mark or duplicate grouping.

## Optional features

Offered in the interview, built only on a yes _(agent default)_: expandable detail row (lazy-loaded), inline editing of data cells, multi-state status marks, add-row form, merge duplicates, per-row delete, hide-columns "study" mode, export, view state in the URL, sticky header, auto-refresh, row links, dialogs for dangerous actions.

## Hard rules

- **The page never deletes, moves or sends anything.** Marks are labels; the owner acts on them elsewhere (a "copy paths" button is the usual delete workflow).
- Any action that touches disk or another system needs all four: the owner's explicit yes in the interview; an explicit click plus a confirm dialog that states exactly what will happen; a server-side check that every path resolves inside the allowed roots; the server, not the browser, decides what is done.
- Filter, sort, paginate and selection logic lives in a pure module with unit tests _(agent default)_. Example: `applyFilters(rows, {status:["open"]})` returns 3 of 5 rows in a test, with no browser.
- Every write validates strictly at the server boundary; every write is all-or-nothing.
- Update the repo's docs in the same task and record who decided each item (owner / tech lead / agent assumption).

## Verify

Example: 5,413 rows listed + 37 skipped = 5,450 files on disk. A page that shows 5,400 passes lint and still misses 13 rows.

1. Counts against the source, with the arithmetic written out.
2. Logic and API tests pass.
3. Lint and build pass.
4. In the owner's real browser, exercise every feature, including one write that survives a reload, with a clean console.
5. Look at a screenshot at real width. A row-height defect of 209 px and a never-eyeballed layout both shipped because nobody looked.
6. Live checks of anything that writes or moves run against a copy or fake data, never the live store.
7. Merge is not deploy: build, restart the serving process, check again.

Done when each step has its output in the report. A step you could not run is listed as not verified.

## Report

- First line: the URL to open (a clickable address or one launcher command).
- Two lists: what the owner asked for; what the agent added _(agent default)_. The owner cuts from the second.
- What was not verified, plainly.
- Where the spec, docs and tests live, as full paths.

## Files

- [references/interview.md](references/interview.md) — question bank, defaults, a worked batched message.
- [references/patterns.md](references/patterns.md) — how each feature behaves, and the traps.
- [references/spec-template.md](references/spec-template.md) — the one-page spec.
