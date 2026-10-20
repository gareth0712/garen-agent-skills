# Worked examples (real, 2026-10)

Each pair is a draft an agent actually wrote, then the rewrite. Read the BAD one and
notice that every word is correct - it fails because the reader cannot picture it.

## Contents
1. Question to a PM - order at assembly vs order at ship
2. Question to a PM - sellback after a value change
3. Explanation to the dev - who owns a disclosure sentence
4. README section - lead with the command

## 1. Question to a PM - order at assembly vs order at ship

**BAD** (the PM replied: "what does 'reserves a unit locally' mean, is it my English?")

> Interim product source. Until the Gr10 Shopify sync exists, admins hand-enter each
> tier product (name, price, stock) in the admin panel; assembly reserves a unit
> locally and we order from Gr10 when the prize ships. OK as the interim?

**GOOD**

> **Order at assembly vs order at ship.** Until the Gr10 Shopify sync exists, admins
> hand-enter each tier product (name, price, stock). e.g. Alice collects 350 T2
> fragments and assembles Pack A. Two options: (A) order Pack A from Gr10 the moment
> she assembles - stock is guaranteed, but if she sells it back we have already bought
> a unit; (B) only reserve one unit in our own counter at assembly, and order from Gr10
> when she clicks Ship - risk: Gr10 sells out in between. I've built B as the interim.
> OK? (Notion lists this as open, and whether Gr10 can hold an order without shipping
> is still a tech question.)

What changed: a named actor (Alice), a literal number (350 T2 fragments), the SAME
case run through both options, the default stated, the question last.

## 2. Question to a PM - sellback after a value change

**BAD**

> The PRD lets us change a tier's fragments-needed with 30 days' notice. That changes
> the reference value, so sellback value changes too. Intended? Do prizes already
> assembled sell back at the old value or the new one?

**GOOD** - the same text, plus:

> e.g. Bob used 700 fragments to get an ETB in Sep and didn't sell back or ship. On
> 1 Oct ops raised tier 3 from $70 to $80. On 15 Nov Bob sells back his ETB:
> $70 x 85% = $59.50, or $80 x 85% = $68?

What changed: a timeline with dates, and money the PM can add up. The question is now
"$59.50 or $68" - answerable in one word.

## 3. Explanation to the dev - who owns a disclosure sentence

**BAD**

> Does the odds/risk text need to be a fixed, legal-approved string, or can
> product/design own the wording as usual?

**GOOD**

> The chance-assembly sheet shows a sentence like "Spend 25 fragments for a 50% chance
> to win. If you lose, all 25 fragments are gone." Two ways to own it: (A) legal signs
> off the exact sentence, it lives under one i18n key, and design cannot reword it
> without going back to legal; (B) normal copy, design rewords freely. I need to know
> because (A) means a test pins the string.

What changed: the literal sentence the user reads, and the concrete engineering
consequence of each answer (a pinned test).

## 4. README section - lead with the command (illustrative script)

**BAD**

> `dedupe-emails.sh` removes duplicate users by email, keeping the oldest account, and
> writes the result next to the input file. Emails are compared case-insensitively.

**GOOD**

````markdown
```bash
./scripts/dedupe-emails.sh data/users.csv
```
```
read 1,204 rows
removed 37 duplicates (kept the oldest created_at per email)
wrote data/users.dedup.csv (1,167 rows)
```
`Alice@x.com` (created 2026-03-01) and `alice@x.com` (created 2026-05-12) count as one
user; the March row is kept. The input file is never modified.
````

What changed: the reader sees the exact command and the exact lines they will get,
and one literal duplicate pair, before reading any rule about it.
