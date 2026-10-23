---
name: eli5
description: Lead every human-facing piece of writing with one real, concrete example (real names, 2-3 literal rows or values, the literal command, a timeline, real money) BEFORE the rule, and show the bad case beside the good case. Use this skill whenever you write anything a person will read, whoever that person is - an explanation to the user, a question or decision request to a PM, tech lead, designer or legal, a README or docs section, a PR description, a review or ticket comment, a commit body that explains a decision, a handoff note, a status update. It applies to deliverables for third parties too, not only to explanations addressed to the user - a question the reader cannot picture is a question they cannot answer. Also use for ELI5, explain like I am, break this down, dumb it down, explain this to my manager or PM, or when a reader said they did not follow.
---

# ELI5 - example first, rule second

The owner of this skill learns from watching one concrete case run, not from rules.
So do most readers. A PM handed "assembly reserves a unit locally" asked "is it my
English?" - she could not picture it, so could not answer. Show one case with
literal values, then name the rule.

**Scope: every output a human will read**, including deliverables for third parties
(stakeholder questions, README/docs, PR descriptions, review and ticket comments,
commit bodies, handoff notes, status updates). "It is for someone else" is not an
exemption; it caused the failure above.

**Default reader:** a careful colleague who knows the domain but did not watch the
work; adjust with `references/audience.md` when named. Write in their language.

## The rules

1. **Lead with one real, concrete example, then the rule.** Real names, 2-3 literal
   rows or values, the literal command and its output, a timeline. Money in numbers
   you can add up ($70 x 85% = $59.50), never N and M. No real figure? Label a
   plausible one "illustrative".
2. **Bad case beside good case**, same input.
3. **Name who is affected in human terms**: "checkouts in those 4 minutes award no
   points", not "writes are blocked".
4. **One example per concept.** If it did not land, give a *different* second example,
   never a reworded first.
5. **Define a term by showing it**, once, in parentheses, where it first bites:
   "(ref value follows the highest valued product)".
6. **State the general rule only after the example**, in 1-2 sentences.

## Walking through steps

Numbered scenarios are where readers get lost; each rule closes a real gap.

7. **Every pronoun is a bug.** "Edits it" had two referents (the tier's field, or
   product B's price). Name the field and actor each time: "sets the ref value of
   Tier 2.5 to $48".
8. **After each step, print the resulting state**: "-> ref value of T2.5 becomes $50".
   The reader never computes. A step changing no state earns no line.
9. **Pick numbers the reader can do in their head**: small, round, distinct, with the
   derived number obvious ($48 -> 480 fragments, not $160 -> 1600 beside $165 -> 1650).
10. **Show the knock-on effect on neighbours** as before -> after: a new tier forces
    other drop weights to move (50->40, 30->25, 0->20, 20->15; sums to 100). Stopping
    at the thing itself omits what the reader must do.
11. **If the reader could imagine a scary case, name it and close it**: "no machine can
    drop T2.5 fragments before Confirm" is what rules out a user seeing 12/165 turn
    into 12/160. "Warning only" needs a literal pair: "won't block a $80 product in a
    $40 tier".
12. **Use the reader's vocabulary** (her spec ids SC-02, her words "confirmed", "drop
    weight"), not internal names (`reference_overridden`, `confirmed_at`).

## Shapes by output type

- **Question to a stakeholder:** **Situation** (one case, named actor, numbers) -> **Options** (run the SAME example through each) -> **Default I built**
  (one line) -> **Why I need you** (what changes per answer) -> **the
  question, 25 words or fewer**. Close the loop: "Does this align with your spec? If yes, I will update
  SC-02 and SC-13 as follows..." - the reply is one word.
- **README / docs:** literal command and output first, then prose.
- **PR / commit body:** one before/after with the same input.
- **Review or ticket comment:** the input that breaks it, what happens now, what
  should happen.

Worked bad/good pairs, incl. the T2.5 tier example: `references/examples.md`.

## Stop check before sending

1. No literal value, table, timeline or before/after? It failed - add one. A clearer
   rewording of a rule is still a rule.
2. Read each sentence and ask: **could the reader point at the row, field or person
   this refers to?** If "it", "that" or "the value" could mean two things, rewrite.

Skip only the obvious.
