# table-viewer skill: design

Date: 2026-11-27. Status: skill written and trial-run; the owner decided items 1 to 5 and has not yet reviewed items 6 to 14.

## Goal
An agent asked for "a table / dashboard page to view X" reads the repo, asks every open question in one batched round (repeating until none is open), writes a one-page spec and waits for approval, builds with a fixed always-on feature set, and verifies in a real browser. The owner stops repeating himself.

## Verification
- `npx skills-ref validate skills/table-viewer` passes.
- Grep proves no private names, paths or banned strings (public repo).
- Every decision below maps to a line in the skill.
- Behavioural check, run 2026-11-27 with fresh agents on a fixture repo (a book catalogue, 3,214 rows) and the request "make me a page to browse all my books":
  - Run 1 (first draft of the skill): read the repo, sent 8 questions with defaults, wrote no code. Defect: it dropped columns, default sort, filters and deploy without asking. Reply that skipped one item -> it re-asked only that item. Next reply -> a one-page spec, then it stopped for approval. No code file was created in three turns.
  - Run 2 (after the "no group dropped" fix): 22 items, too long. Fixed with the "8 to 12 items, merge what only needs a nod" rule.
  - Run 3 (final text): 11 items, every group present, unknowns marked "not verified", its own addition labelled as cuttable, no code.
- Not checked: steps 4 to 6 (build, verify, report) have not been run on a real page. The first real page built with the skill is that test.

## Fallback
All new files plus one README row: revert the commit that adds `skills/table-viewer/`.

## Risks
- Interview is too long: mitigated by defaults and "repo-answerable questions are never asked".
- Patterns drift from the three source pages: they are a snapshot of 2026-11-27.
- Agent-default items could be unwanted: they are labelled so the owner can cut them.

## Decisions
| # | Decision | Decided by |
|---|---|---|
| 1 | Works in any repo; step one reads the stack and reuses it | Owner, 2026-11-27 |
| 2 | Always built: search, sort, count chips, totals line, star + note, multi-select + bulk bar, copy identifier | Owner, 2026-11-27 |
| 3 | Always asked: can-delete mark, duplicate grouping | Owner, 2026-11-27 |
| 4 | Interview asks until nothing is unclear, during the build too | Owner, 2026-11-27 |
| 5 | The larger vocabulary-style page is the reference for a finished page | Owner, 2026-11-27 |
| 6 | One batched message; each item = question + default / `Changes:` / `If skipped:`; no question group dropped; repo-answerable ones become one stated assumption; "rest default" accepts the remaining defaults, a skipped item is re-asked | Agent judgement (unconfirmed) |
| 7 | One-page spec with asked / added / why / cost table, approved before code | Agent judgement (unconfirmed) |
| 8 | Extra always-on behaviours: states, "N of M", nulls last, OR/AND, page reset, shift range, outside-filter count | Agent judgement (unconfirmed) |
| 9 | Optional features list offered in the interview | Agent judgement (unconfirmed) |
| 10 | Safety: page never deletes, moves or sends; actions need yes, confirm dialog, root check, server decides | Agent judgement (unconfirmed) |
| 11 | Build in layers, each working end to end | Agent judgement (unconfirmed) |
| 12 | Pure logic module with unit tests | Agent judgement (unconfirmed) |
| 13 | Verification order incl. real browser, screenshot at real width, URL first line | Agent judgement (unconfirmed) |
| 14 | Report separates asked from added | Agent judgement (unconfirmed) |

Source: the brief for this skill, 2026-11-27 (owner decisions 1 to 5 as relayed by the orchestrating session).
