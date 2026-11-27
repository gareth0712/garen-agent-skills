# Interview question bank

The bank below is for you; the owner sees only the message. Each bank line is: question — default (what it changes).

**Message item shape.** Every numbered item has exactly three lines:

```
N. <question> Default: <proposal>.
   Changes: <what it is for, what it changes in the build>
   If skipped: <what the agent will do>
```

**No group may be dropped.** Every group A to H appears in the message. A group the repo fully answers appears as ONE numbered stated assumption the owner can overrule by number, e.g. `9. Columns I will show: id, title, author, year, genre. Default sort: year desc. Chips: genre, language, format (with counts). Search: title, author, note. OK?` Optional features (group G) are one numbered item listing all of them.

**Keep it to 8 to 12 items.** The owner misses things in a long message. Example: a first draft with 22 items had seven that only needed a nod ("one row = one book", "rows come from books.db", "load all rows"...); merged, they are one item "Data as I read it: ... OK?". Rule: inside a group, everything that only needs a nod is merged into that group's single stated-assumption item. A question gets its own item only when its answer changes the build and you cannot guess it: the purpose, an ambiguous identifier, what a star means, can-delete, duplicates, optional features, disk actions, anything "not verified".

## A. Purpose and users

1. What is the page for, in one sentence, and what will you DO after looking at it? — default: browse and mark rows for later action. (Decides which marks and bulk actions exist.)
2. Who uses it: only you, or others? — default: only you, on this machine. (Decides the write guard and the language.)

## B. The data

3. What is one row? (a file, an account, an invoice...) — no default; ask.
4. Where do rows come from (table, folder scan, API)? — default: what the repo already uses. (Decides the read route.)
5. How many rows now, and how fast do they grow? — default: measure it. (Up to about 10,000: load all, filter in the browser. Above: measure first.)
6. How is the source refreshed (rescan, import, live)? Must your marks survive that? — default: yes, marks survive. (Decides whether the importer may touch mark columns.)
7. Which values are derived rather than stored (folder from path, group id, status)? — default: derive at read time. (Nothing stale.)

## C. Columns, sort, detail

8. Which columns, in what order? Which is the primary identifier (the one the copy button copies)? — default: identifier first, then the 5 to 8 most useful fields.
9. Default sort? — default: the field you scan for first, descending; empty values last.
10. What goes in a detail row, if you want one? — default: no detail row.

## D. Filters

11. Which dimensions get chips, and which need counts? — default: every enum-like column, with counts over all rows. (A dimension with no options shows nothing.)
12. Does a text search cover one field or several? — default: identifier, name, note.

## E. Writes and marks

13. Star and note are always built; never ask whether. Beyond them, any marks (status with states, tags)? — default: none.
14. What does a star MEAN (the only star question)? Does it protect the row from any deleter or cleaner elsewhere in the repo? — default: label only. (If it protects, every deleter must honour it; the agent greps for them and lists them in the spec.)

## F. Always asked

15. **Can-delete mark**: do you want one? If yes, what reads it? — default: no. (A label only; the page never deletes.)
16. **Duplicate grouping**: which signals mean "same" (identical bytes, same title, same size and length)? Group by them, or only show a column? — default: no grouping. (Weak signals must be named weak, and a total must not count a row twice.)

## G. Optional features (decision list)

17. Which of these do you want? Default: none.
    - expandable detail row (lazy-loaded)
    - inline editing of data cells
    - multi-state status marks
    - add-row form
    - merge duplicates
    - per-row delete
    - hide-columns "study" mode
    - export
    - view state in the URL
    - sticky header
    - auto-refresh
    - row links
    - dialogs for dangerous actions
18. Does the page need to act on disk or another system (move, delete, send)? — default: no, never. (A yes triggers the four safety conditions in SKILL.md.)

## H. Running it

19. UI language? — default: the repo's existing pages.
20. How is it served, restarted and deployed? Does anything restart it for you? — default: as the existing pages. (Merge is not deploy.)
21. Who verifies in the browser, and may I use your browser? — default: the agent verifies, you glance at the screenshot.

## Worked example

Agent message (a book catalogue page):

```
I read the repo: pages live in web/src/pages, data in books.db, API in api/books.py. Open items:
1. One row = one book (title, author, year, shelf). Default: yes.
   Changes: the columns.
   If skipped: I use these four.
2. 4,200 books now, +50 a month. Default: load all, filter in the browser.
   Changes: one request, no server paging.
   If skipped: I do that.
3. Columns I will show: title, author, year, shelf. Default sort: year desc. Chips: shelf, language (with counts). Search: title, author, note. OK?
   Changes: the table layout.
   If skipped: I build exactly this.
4. Star = "read this next"; should it also stop the cleanup script from removing the book? Default: label only.
   Changes: whether I edit the cleanup script.
   If skipped: label only.
5. Can-delete mark? Default: no.
   Changes: one column and one chip.
   If skipped: none.
6. Duplicate grouping (same title + author)? Default: no.
   Changes: a Duplicate column and group view.
   If skipped: none.
7. Optional features (detail row, export, view state in URL, ...). Default: none.
   Changes: extra build layer.
   If skipped: none built.
8. UI language, serving and deploy: same as the existing pages (assumption). Verification: I check in your browser and send a screenshot. OK?
   Changes: how I serve and verify.
   If skipped: as stated.
Reply like: "1 yes, 3 ok, 4 yes protect, 7 export, rest default".
```

Owner reply: `1 yes, 3 ok, 4 yes protect, 7 export, rest default`

Read it as: 1, 3, 4, 7 answered; "rest default" makes every other item take its default (without those words, a skipped item stays open and goes into a second, shorter round). Item 4 answered "protect" means the agent now greps for every deleter and adds that to the spec.
