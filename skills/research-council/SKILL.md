---
name: research-council
description: Researches an external topic, trend, controversy, or claim through a five-advisor evidence council (Practitioner, Skeptic, Economist, Historian, Academic), maps where the perspectives conflict, and delivers a CEO summary with findings ranked by confidence plus a peer review of its own synthesis. Use whenever Gareth asks to research a topic, verify whether a popular claim or narrative is true, understand a trend or industry shift from multiple angles, or says "研究一下", "這是真的嗎", "多角度分析", or "deep dive" on a non-decision subject. For evaluating his own ideas or decisions, use ai-council instead.
---

# Research Council

Research a topic through five evidence-oriented advisors, surface their disagreements as findings, and close with a ranked, self-reviewed synthesis. Reply in Traditional Chinese; keep technical terms, product names, and citations in English.

This skill answers「這件事的真相是什麼？」. If the input is Gareth's own idea, decision, or plan（「我該不該做 X」）, use the `ai-council` skill instead and say you switched.

## Evidence rule (applies to every phase)

Specific claims — numbers, study results, effect sizes, prices, funding flows, market sizes, historical figures — follow the `researching-with-citations` standard: verify by web search or fetch before asserting, cite the source and date inline, and mark anything unverifiable as 「未驗證」. An advisor voiced with confidence but built on training memory is the primary failure mode of this format; a labeled gap is always better than a fluent guess. Distinguish 已驗證事實 / 推論 / 假設 throughout.

## Phase 1 — Independent Assessment

One labeled section per advisor. For each, answer three questions: core position, strongest supporting evidence, and the one thing this advisor can tell you that no other perspective can. 3–6 substantive sentences each; do not sand disagreements into consensus.

1. **The Practitioner（實務者）** — Lives with the topic daily. Reports the ground reality textbooks omit: caveats, workarounds, what actually breaks, the gap between marketing and daily use. Source from practitioner-written material (forums, postmortems, issue trackers, first-hand accounts), not vendor copy.
2. **The Skeptic（懷疑者）** — Believes the mainstream consensus is wrong. Presents the strongest argument against the default narrative and names the assumption everyone repeats without examining. Must attack the best version of the consensus, not a strawman.
3. **The Economist（經濟學家）** — Follows the money. Who profits, what the incentive structures are, which financial forces drive the narrative that polite explanations skip. Funding sources, business models, and conflicts of interest are claims — cite them.
4. **The Historian（歷史學家）** — Has seen the pattern before. Maps the closest historical episodes, how they resolved, and rules on whether today's topic is genuinely new or history repeating. Name the specific precedent, not「歷史上常有類似情況」.
5. **The Academic（學者）** — Reads the studies. What the evidence actually shows: effect sizes, which findings replicated, which collapsed, and where research is thin relative to what headlines suggest. This advisor is under the strictest evidence rule — every study-level claim needs a fetched source or the 「未驗證」 label.

## Phase 2 — Cross-Critique

Map the conflicts in one tight section (reference arguments anonymously:「其中一個視角主張…」):

- Where two or more perspectives directly contradict each other, and which side the evidence favors
- Which perspective has the strongest evidence and which the weakest
- What all five agree on — consensus across hostile viewpoints is itself a finding
- What none of them addressed — the shared blind spot

## Phase 3 — The Chairman's Synthesis

A section titled **主席總結**, containing:

1. **CEO summary** — one paragraph, no hedging padding
2. **五大發現** — ranked by reliability, each tagged 已驗證 / 推論 / 未驗證 with its source where verified
3. **隱藏關聯** — one connection that surfaced across multiple perspectives without any single advisor stating it
4. **行動建議** — one specific thing Gareth should do differently based on the evidence

## Phase 4 — Peer Review

Immediately audit your own synthesis:

- Score each of the five findings on a 1–10 confidence scale, with one line justifying scores at 8+ (why so sure) and 4− (what is missing)
- Name the weakest claim you made anywhere in the output
- Name which perspective dominated the synthesis and what that bias likely cost

## Rules

- Search before writing Phase 1, not after — advisors argue from fetched evidence, not from memory retrofitted with citations.
- The five voices come from one model. The council structures analysis; it does not create independent judgment. For decisions with legal, tax, medical, or large financial consequences, the synthesis must recommend validation by a qualified human.
- If the topic is too vague to research (no claim, no timeframe, no scope), ask one clarifying question instead of producing five sections of padding.
- Scale output to the weight of the question; not every topic deserves 2,000 words.
