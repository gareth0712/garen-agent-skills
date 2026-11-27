# Spec template (one page)

Copy, fill, send to the owner, wait for a yes. Save it next to the repo's other specs; if the repo has none, `docs/specs/<date>-<page>-viewer.md`.

```markdown
# <Page name> viewer: spec

Date: <date>. Status: draft / approved by <owner> on <date>.

## Goal
One sentence: what the owner can do after this exists.

## Data
- One row =
- Source and read route:
- Row count now / growth:
- Refresh: <how>; marks survive: yes/no
- Derived at read time:

## Table
- Columns (primary identifier marked):
- Default sort:
- Filter dimensions (with counts: yes/no each):
- Search covers:
- Detail row: none / <contents>

## Marks and writes
- Star means: <label only / protects from: list every deleter found by grep>
- Note: yes
- Can-delete mark: yes/no. Duplicate grouping: yes/no, signals:
- Other writes:
- Disk or system actions: none (default). If yes: owner's yes quoted, confirm text, allowed roots.

## Table of scope
One row per item, so the owner can cut a single line.

| Item | Who | Why | Cost |
|---|---|---|---|
| search, sort, chips with counts, totals, star + note, bulk bar, copy identifier | owner (always built) | standing list | - |
| <each thing the owner asked for in the interview> | owner | <their words> | <files, minutes> |
| <each thing the agent added: states, "N of M", range select, ...> | agent | <reason> | <files, minutes> |

## Build layers
1. Read-only rows (count check) 2. Search / sort / filter 3. Marks and writes 4. Optional features

## Verification
- Counts vs source: <arithmetic>
- Tests: <files>
- Lint and build: <commands>
- Browser: features to exercise, one write surviving reload, console clean, screenshot at real width
- Writes tested against: <copy / fake data>

## Serving
- URL, restart, deploy, what restarts it:
- Docs to update:

## Decisions
| Item | Decided by | Source |
|---|---|---|
| ... | owner / tech lead / agent assumption (unconfirmed) | <quote or file> |

## Not verified / open
-
```
