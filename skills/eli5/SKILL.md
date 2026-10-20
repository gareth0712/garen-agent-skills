---
name: eli5
description: Lead every human-facing piece of writing with one real, concrete example (real names, 2-3 literal rows or values, the literal command, a timeline, real money) BEFORE the rule, and show the bad case beside the good case. Use this skill whenever you write anything a person will read, whoever that person is - an explanation to the user, a question or decision request to a PM, tech lead, designer or legal, a README or docs section, a PR description, a review or ticket comment, a commit body that explains a decision, a handoff note, a status update. It applies to deliverables for third parties too, not only to explanations addressed to the user - a question the reader cannot picture is a question they cannot answer. Also use for ELI5, explain like I am, break this down, dumb it down, explain this to my manager or PM, or when a reader said they did not follow.
---

# ELI5 - example first, rule second

The owner of this skill does not learn from rules; he learns from watching one
concrete case run. Neither do most readers. A PM handed "assembly reserves a unit
locally" asked "is it my English?" - she could not picture it, so she could not
answer it, and the owner could not judge the question either. The fix is the same
for every reader: show one case with literal values, then name the rule.

**Scope: every output a human will read**, not only explanations to the user.
Questions to stakeholders, README and docs, PR descriptions, review and ticket
comments, commit bodies that explain a decision, handoff notes, status updates.
"It is a deliverable for someone else" is the exact reasoning that caused the failure
above - it is not an exemption.

**Default reader:** a careful colleague who knows the domain but did not watch the
work. Adjust with `references/audience.md` when the reader is named (PM, legal, a
parent, a new hire). Write in the reader's language.

## The six rules

1. **Lead with one real, concrete example, then the rule.** Real names from the repo
   or product (`users.created_at`, Pack A, tier 3), 2-3 literal rows or values, the
   literal command or request and what it returns, a timeline ("10:00:01 lock taken...
   10:03:40 released"). Money and points in real numbers you can add up ($70 x 85% =
   $59.50), never N and M. No real figure at hand? Use a plausible one and label it
   ("e.g., numbers illustrative") rather than dropping the example.
2. **Show the bad case and the good case side by side**, with the same input:
   "without the fix, Bob's ETB sells back at X; with it, at Y."
3. **Name who is affected in human terms**: "every checkout in those 4 minutes awards
   no points", not "writes are blocked".
4. **One example per concept.** If it did not land, give a second, *different* example.
   Never reword the first.
5. **Define a term by showing it**: the two statements, the rows they touch, the
   moment each happens.
6. **Only after the example**, state the general rule in 1-2 sentences.

## Shapes by output type

- **Question to a stakeholder** - always this order:
  **Situation** (what exists today, one concrete case with a named actor and numbers)
  -> **Options** (run the SAME example through each, showing the different outcome)
  -> **Default I built** (one line) -> **Why I need you** (what changes if the answer
  differs: schema, money, legal, who is affected) -> **the question, 25 words or fewer**.
- **README / docs** - open with the literal command and its literal output, then the
  prose.
- **PR description / commit body** - one before/after with the same input.
- **Review or ticket comment** - the input that breaks it, what happens now, what
  should happen.

Worked bad/good pairs, including the real PM questions: `references/examples.md`.

## Stop check before sending

Scan the draft. If an explanation or question has **no literal value, no table, no
timeline, and no before/after**, it has failed - stop and rewrite it with one. A
clearer rewording of a rule is still a rule.

Skip only what is genuinely obvious in one sentence ("renamed `foo` to `bar`").
