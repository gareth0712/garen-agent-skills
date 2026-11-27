# Patterns and traps

Stack-neutral. Each item: what to do, then why. Examples use invented subjects.

## Data

- **Load all rows in one request, filter client-side, up to roughly 10,000 rows.** Two pages of 5,000 to 8,000 rows work this way. Above that, measure payload and time first.
- **Derive at read time, never store.** Example: a row in `/photos/2024/may/a.jpg` gets folder `2024` computed on each read; if you store it, a moved file shows the old folder. Duplicate groups, status and totals follow the same rule.
- **Paginate on the client, 100 to 200 rows per page; no virtualization.** Simpler, and search/sort stay trivial. Clamp the page index; reset it to 0 on any filter or sort change.
- **An unmigrated or empty source returns an empty list plus an empty summary, not an error.** The page then shows the empty state with the command that fills it.
- **A rescan or re-import must never overwrite user marks.** The importer upsert names no mark column. Example: rescan sets `size=10` on row 7 but leaves `starred=1`. An edit to a data cell keeps the original value beside the new one.
- **If a mark can follow a moved or renamed row, re-link by a stable key (size plus content hash)**; reset derived hashes when content at the same key changes.
- **A code or id read out of a longer token is not a match.** Example: `inv-2024-0017` must not match code `0017` inside `ref-30017`; match whole tokens only.
- **A scan of an absent or empty root writes nothing and exits non-zero** (a drive not plugged in must not wipe rows).

## Filters, sort, summary

- **Chips are toggle buttons with `aria-pressed`, showing counts.** Counts are over all rows (not the filtered set) unless the owner asks otherwise. A dimension with no options renders nothing.
- **OR inside one dimension, AND across dimensions; empty selection = no restriction.** Example: status in {open, held} AND shelf in {A}.
- **Quick chips are derived views of the same filter object**, not a second state.
- **Sort: empty values last in both directions, stable tiebreak on the identifier, `aria-sort` on the header.** A new column starts ascending for text, descending for numbers and sizes.
- **Summary line**: totals at the top (rows, bytes or sums), plus "N of M rows" after filtering. A duplicate total counts each row once: one signal per row (the strongest), reclaimable = group total minus the largest member.
- **Search**: case-insensitive substring over named fields; fold script variants the data needs (e.g. katakana to hiragana). No debounce for client-side search; debounce 300 ms only when it hits the server.
- **Keep filter/sort/paginate/selection in one pure module** with unit tests: each dimension, AND across dimensions, nulls last, stable ties, page clamp, no mutation of input.

## Selection and bulk actions

- **Shift+click selects a range over the filtered, sorted order**; keep an anchor; prevent text selection on shift+mousedown.
- **Selection survives filter changes, so say so.** Example: 40 selected, 12 outside the filter: the bar reads "40 selected (12 not in the current filter)" with buttons "select all matching", "keep only filtered", "clear".
- **Header checkbox means this page**, with an indeterminate state.
- **Bulk writes: one request, one transaction, all or nothing.** Cap ids per request (e.g. 2,000 to 5,000); above it, chunk. A mid-way failure reports "n saved, m not saved".
- Disable bulk buttons while any save is in flight.

## Marks and editing

- **Optimistic marks with per-row request sequencing.** A per-row counter ignores stale responses. On failure, revert only the fields the request touched, only for rows not saved, and show an error banner. Disable that row's buttons while pending.
- **Text-cell editing**: Enter saves, Esc cancels, the save is awaited ("Saving..."), a server error shows under the cell, and focus returns to the editor (a disabled input loses focus, so Esc would otherwise stop working). Decide blur behaviour once (commit or cancel) and use it everywhere.
- **A duplicate collision on edit** returns 409 with what collides; offer "merge into that row" that repeats the edit and merges in one transaction.
- **A protection mark (star) must be honoured by every deleter in the repo.** Grep for each one (cleanup scripts, prune commands, import dedup) and make it skip starred rows; fail closed on a path it cannot judge. List them in the spec.
- Copy buttons: clipboard write, a "copied" flash of about 1.5 s, an error banner on failure. Bulk copy joins with newlines.

## Server boundary

- **Validate strictly**: JSON object, unknown keys rejected, size caps (note at most 500 characters), at least one field, ids unique. Errors are plain sentences in JSON `{error}`; every error under the API prefix is JSON, never an HTML page.
- **A busy database is a readable 503** ("database busy, try again"); other database errors stay a generic 500 with the detail logged.
- **Reads open read-only; a write uses its own short-lived connection** and touches no table beyond the page's own. Build config per request, not at import, so an env change or missing drive is seen live.
- **A column migration must tolerate two processes adding the same column** (ignore "duplicate column").
- **Local-server write guard**: exact Host allow-list (`127.0.0.1:<port>`, `localhost:<port>`); any Origin present must match; JSON content type required; a custom header (e.g. `X-Page: 1`) required on writes. Register it at app level (not on one blueprint) so 404 and 405 answers are covered; treat HEAD and OPTIONS as reads; grant no CORS headers and pin that in a test. Test by setting the base URL, never by loosening the allow-list. A development server on another origin therefore gets 403 by design; verify against the served build.
- **Paths**: refuse any file operation whose path does not resolve inside the allowed roots (typed paths can contain `..`); refuse over-long paths on Windows. The server decides the operation (e.g. same-drive rename vs copy), and the client uses that field rather than guessing.

## Frontend behaviour

- **Drop stale responses.** Number each list request when sent; ignore a response older than the last accepted one. Poll only while something is busy, and skip a tick while a request is in flight.
- **Show the reason for any wait** ("next download starts 20:00", "worker not answering") instead of a silent stuck row. A request older than 60 s with no consumer means the consumer is not running; say that.
- **Stored URLs become links only when `http` or `https`.**
- **Sticky header needs one scroll container** around a raw `<table>`; a table component that adds its own overflow wrapper breaks stickiness.
- **A dialog shows a snapshot**: re-check the live row before sending, and block closing while saving.
- Status read from a marker file must survive a restart (store pid and boot id).

## Process

- **Tests**: pure logic and API tests; when the repo has no frontend test runner, keep logic needing tests in the pure module or the API.
- **Merge is not deploy**: build, restart the serving process (the old one runs old code), re-check the page. If another process reads what the page writes, deploy it first.
- **Docs in the same task**: the repo's pipeline or page docs updated, text no longer true deleted, and who decided each item written down.
- **Live checks run on a copy or fake data**; a build from a worktree never points at the live data directory.
