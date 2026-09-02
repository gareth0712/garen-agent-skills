---
name: ai-council
description: Evaluates an idea, decision, or plan through a five-advisor council (Contrarian Skeptic, First-Principles Engineer, Expansionist, Outsider, Executor), then cross-critiques the assessments and delivers a Chairman's verdict with a 1-hour decision, primary risk, and #1 action step. Use whenever Gareth presents a new idea, product concept, business decision, or strategic question and wants it stress-tested — including when he says "council", "議會", "五人評估", "幫我評估這個想法", "run this by the council", or asks for multi-angle analysis of a proposal. For choosing between multiple competing technical approaches (A vs B), use garen-debate instead; for researching an external topic's truth, use research-council.
---

# AI Council

Evaluate the user's idea, question, or decision through five distinct advisor lenses, run a cross-critique, and close with a Chairman's synthesis. Reply in Traditional Chinese; keep technical terms, code, and product names in English.

## Phase 1 — Independent Assessment

Give each advisor a clearly labeled section. Each advisor writes 3–6 sentences of substance — no filler, no repeating the idea back. The five voices must genuinely disagree where the material supports it; do not sand them down into consensus.

1. **The Contrarian Skeptic（唱反調者）** — Tear the idea apart. Surface hidden flaws, unstated assumptions, worst-case failure modes, and the most likely reason this dies. Name specific risks, not generic ones ("市場可能不買單" is too weak; say who won't buy and why).
2. **The First-Principles Engineer（第一性原理工程師）** — Ignore industry trends and convention. Reduce the problem to fundamental constraints (physics, economics, human behavior, protocol limits) and rebuild the minimal logical solution from those truths. If the rebuilt solution differs from the user's proposal, say so plainly.
3. **The Expansionist（擴張主義者）** — Remove budget, time, and headcount limits. Describe the maximal, hyper-scaled version of the concept and what it would unlock. This lens tests whether the idea has a ceiling worth chasing.
4. **The Outsider（局外人）** — Deliberately ignore everything known about the user's background, stack, industry, and past decisions, including memory and prior conversation context. React as someone hearing the idea for the first time: what is confusing, what is the obvious question, what would a stranger assume this is for.
5. **The Executor（執行者）** — No theory. Define the single smallest, most unglamorous step executable tomorrow morning that produces real evidence about the concept. It must be concrete: a command to run, a person to message, a page to publish, a number to measure.

## Phase 2 — Cross-Critique

Advisors review each other's points anonymously (refer to arguments, not advisor names: 「其中一個論點認為…」). Cover:

- The strongest argument on the table and why it survives attack
- The weakest or most-assumption-laden argument
- Blind spots: what all five missed, or where two advisors contradict each other and which side the evidence favors

Keep this phase to one tight section, not five more essays.

## Phase 3 — The Chairman's Synthesis

End with a section titled **主席裁決**, containing exactly three items:

1. **1 小時決策** — The call the user should make within the hour (proceed / kill / reshape into X). One sentence, no hedging.
2. **首要監控風險** — The single risk most likely to invalidate the decision, and the observable signal that it is materializing.
3. **#1 立即行動** — One concrete step, normally lifted or sharpened from the Executor's answer.

## Rules

- Ground claims in what is actually inspectable (the user's description, cited facts, known constraints). Where an advisor is speculating, mark it: 「假設」or 「需驗證：X」.
- The Outsider simulates ignorance — it must not cite the user's memory, profile, or earlier turns even when available in context.
- All five voices come from one model; the council structures analysis, it does not create independent judgment. For irreversible, high-cost, legal, or tax decisions, the Chairman's verdict must include a recommendation to validate with a real human expert.
- If the user's input is too vague to evaluate (no problem, no user, no mechanism), say so in one line and ask for the missing piece instead of producing five sections of padding.
- Formatting: use `##`/`**` headings per phase, prose within each advisor's section. Total output should fit the weight of the question — a small decision does not need 2,000 words.
