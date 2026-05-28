# TEST.md — Validation scenarios for llm-wiki-query

This file documents every test scenario the skill must handle. Run these whenever the skill is modified to catch regressions. Every scenario traces to a design decision or known failure mode of the query workflow.

## How to use this file

**When to run:**
- After any non-trivial edit to SKILL.md or agent-prompts.md
- Before sharing the skill with another user or session
- When a real query fails in a way the skill should have prevented — add the new failure as a new scenario
- Periodically as a regression check

**How to run:**
1. Create isolated temp fixture directories (never pollute production workspace)
2. Populate fixtures per the scenario's setup instructions
3. Spawn a fresh Sonnet subagent with the cold-start prompt template at the bottom of this file
4. Compare actual output to expected behavior
5. Clean up temp fixtures after completion (see Fixture Cleanup at end of file)
6. If a scenario fails, fix the skill directly — do not fix the test

**Key principle:** The test fixtures must be adversarial. Happy-path tests pass easily; edge cases are where gaps hide.

---

## Scenario 1: Simple Factual Lookup — Single Page, No File-Back

**Goal:** Verify the skill correctly handles a simple factual question, reads only the relevant page, and does NOT file back.

**Setup:**
```
skill-test-query-1/
├── CLAUDE.md          # minimal single-wiki schema
└── wiki/
    ├── index.md       # with frontmatter; entry: [[lido-protocol]] — Lido staking protocol: fees, architecture, and validator set
    ├── log.md         # with frontmatter, one init entry
    └── protocols/
        └── lido-protocol.md   # contains: "Lido charges a 10% fee on staking rewards, split 5% to node operators and 5% to the DAO treasury"
```

`lido-protocol.md` should have valid frontmatter (type, sources, created, updated, tags, related) and a clear, specific claim about the fee structure.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Query the wiki at `skill-test-query-1/` using the llm-wiki-query skill. The user asks: "What is the fee structure for Lido staking?" Today is {{today}}. Follow the skill exactly. Only touch skill-test-query-1/.

**Expected behavior:**
1. Agent reads CLAUDE.md
2. Agent reads `wiki/index.md` in full (index-first, non-negotiable)
3. Agent identifies `[[lido-protocol]]` as the relevant page from the index description
4. Agent reads `lido-protocol.md` in full
5. Agent produces an answer: "Lido charges a 10% fee on staking rewards, split 5% to node operators and 5% to the DAO treasury `[[lido-protocol]]`."
6. Agent assesses file-back criteria: factual lookup from 1 page — does NOT file back
7. Agent appends to `wiki/log.md`:
   ```
   ## [today] query | What is the fee structure for Lido staking?
   Pages read: [[lido-protocol]]
   Answer filed: no (factual lookup only)
   Gaps flagged: none
   Notes: [brief note]
   ```
8. Agent does NOT create any new files in `wiki/syntheses/` or `wiki/comparisons/`

**Pass criteria:**
- [ ] Agent read `wiki/index.md` before reading any specific page
- [ ] Answer contains a `[[lido-protocol]]` citation
- [ ] Answer does not contain any information not present in `lido-protocol.md`
- [ ] No new file created in `wiki/syntheses/` or `wiki/comparisons/`
- [ ] Log entry appended (not edited into existing entries)
- [ ] Log entry says "Answer filed: no (factual lookup only)"
- [ ] Log entry uses today's actual date, not a copied example date

**Pass threshold:** All 7 criteria met.

**Gap this scenario was created to catch:**
- Agents jumping to general knowledge instead of reading the wiki
- Agents filing back trivial factual answers that don't warrant a new page
- Agents skipping the index scan and going directly to a page they guessed from the query

---

## Scenario 2: Synthesis Across Multiple Pages — File-Back to wiki/syntheses/

**Goal:** Verify the skill correctly synthesizes across 5 pages, produces a cited answer, and correctly files back to `wiki/syntheses/` with the required frontmatter fields.

**Setup:**
```
skill-test-query-2/
├── CLAUDE.md
└── wiki/
    ├── index.md       # entries for all 5 pages below
    ├── log.md
    ├── concepts/
    │   ├── consistent-hashing.md        # covers: virtual nodes, hash ring, load distribution
    │   ├── replication.md               # covers: sync vs async replication, durability trade-offs
    │   └── partitioning.md              # covers: range vs hash partitioning, hot spots
    ├── techniques/
    │   └── database-sharding.md         # covers: horizontal partitioning, shard key selection
    └── source-summaries/
        └── distributed-systems-guide.md # covers: summary of a distributed systems article; links to above
```

Each page should have valid frontmatter with `related` fields pointing to related pages. Pages should be substantive enough (~20-30 lines of content each) that a synthesis spanning them would be genuinely useful.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Query the wiki at `skill-test-query-2/` using the llm-wiki-query skill. Today is {{today}}. The user asks: "How does the wiki describe the relationship between consistent hashing, partitioning, and replication in distributed database design? Please synthesize this and file the answer back." Follow the skill exactly. Only touch skill-test-query-2/.

**Expected behavior:**
1. Agent reads CLAUDE.md
2. Agent reads `wiki/index.md` in full
3. Agent identifies at minimum 3 candidate pages from the index (consistent-hashing, replication, partitioning)
4. Agent reads those 3 pages; follows `related` links to discover `database-sharding.md` and `distributed-systems-guide.md`
5. Agent reads all 5 pages
6. Agent produces a synthesis answer with `[[page-name]]` citations for every key claim
7. Agent detects file-back criteria are met (synthesis query, 5 pages, would be useful to retrieve again)
8. Because user said "file the answer back," agent proceeds to file-back without waiting for additional confirmation
9. Agent creates `wiki/syntheses/consistent-hashing-replication-partitioning-synthesis.md` (or similar descriptive name) with:
   - `type: synthesis`
   - `llm_generated: true`
   - `query_origin: "How does the wiki describe the relationship between..."`
   - `confidence: high | medium` (depending on whether there are gaps)
   - `sources:` listing all 5 wiki pages with `wiki:` prefix
   - `created: {{today}}`, `updated: {{today}}`
10. Agent updates `wiki/index.md` with a specific one-line entry for the new synthesis page
11. Agent appends to `wiki/log.md`:
    ```
    ## [today] query | How does the wiki describe the relationship between consistent hashing, partitioning, and replication in distributed database design?
    Pages read: [[consistent-hashing]], [[replication]], [[partitioning]], [[database-sharding]], [[distributed-systems-guide]]
    Answer filed: [[consistent-hashing-replication-partitioning-synthesis]]
    Gaps flagged: [gap or "none"]
    Notes: [brief note]
    ```

**Pass criteria:**
- [ ] Agent read `wiki/index.md` before reading individual pages
- [ ] Agent read at least 3 distinct pages (not just the first one found)
- [ ] Answer contains `[[page-name]]` citations for claims from at least 3 different pages
- [ ] Filed-back page exists in `wiki/syntheses/`
- [ ] Filed-back page has `llm_generated: true` in frontmatter
- [ ] Filed-back page has `query_origin` field with original question
- [ ] Filed-back page has `confidence` field
- [ ] Filed-back page sources list uses `wiki:` prefix
- [ ] Filed-back page has `created` and `updated` set to today's actual date
- [ ] `wiki/index.md` has a new entry for the synthesis page
- [ ] Log entry appended (not edited), says "Answer filed: [[page-name]]"
- [ ] Log entry uses today's actual date

**Pass threshold:** All 12 criteria met.

**Gap this scenario was created to catch:**
- Agents not following `related` links to expand their reading list
- Agents forgetting `llm_generated: true` on the filed-back page
- Agents using yesterday's date or a copied example date in frontmatter
- Agents creating synthesis pages without updating the index
- Agents writing vague index entries ("Synthesis page about caching") instead of specific ones

---

## Scenario 3: Query With a Wiki Gap — Must Flag Gap, Not Fabricate

**Goal:** Verify the skill correctly identifies when the wiki cannot answer part of a question, reports the gap explicitly, and does NOT fabricate an answer using general knowledge.

**Setup:**
```
skill-test-query-3/
├── CLAUDE.md
└── wiki/
    ├── index.md       # entries for lido-protocol only
    ├── log.md
    └── protocols/
        └── lido-protocol.md   # covers: Lido fee structure, validator set, stETH token
                               # does NOT cover: withdrawal mechanics, slashing risks, or restaking
```

The wiki intentionally covers only part of the Lido topic. The query will ask about topics that are both inside and outside the wiki's current coverage.

**Cold-start prompt:**
> You are a cold-start agent with no prior memory. Query the wiki at `skill-test-query-3/` using the llm-wiki-query skill. Today is {{today}}. The user asks: "What does the wiki say about Lido's fee structure, withdrawal mechanics, and slashing risks?" Follow the skill exactly. Only touch skill-test-query-3/. IMPORTANT: do NOT use general knowledge to fill gaps. If the wiki does not cover a topic, say so explicitly.

**Expected behavior:**
1. Agent reads CLAUDE.md
2. Agent reads `wiki/index.md` in full
3. Agent identifies `[[lido-protocol]]` as the only relevant page
4. Agent reads `lido-protocol.md` in full
5. Agent produces a PARTIAL answer, citing what the wiki does cover:
   - Fee structure: answered with `[[lido-protocol]]` citation
   - Withdrawal mechanics: NOT answered — gap flagged
   - Slashing risks: NOT answered — gap flagged
6. Agent does NOT use general knowledge to fill the withdrawal or slashing gaps
7. Agent produces a gap report:
   ```
   ## Wiki gaps detected
   1. **Withdrawal mechanics** — the wiki has no page covering Lido withdrawal timelines or mechanics.
      Suggested ingest: Lido's official documentation on stETH withdrawals.
   2. **Slashing risks** — the wiki has no page covering validator slashing risks or Lido's insurance fund.
      Suggested ingest: Lido's risk documentation or an analysis of Ethereum validator penalties.
   ```
8. Agent assesses file-back: partial answer with significant gaps → recommends NOT filing back (confidence would be low; gaps should be filled first), OR files with `confidence: low` if the partial answer is still useful
9. Agent appends to `wiki/log.md` with gaps recorded

**Pass criteria:**
- [ ] Agent read `wiki/index.md` before reading any specific page
- [ ] Answer contains the fee structure claim with `[[lido-protocol]]` citation
- [ ] Answer does NOT contain information about withdrawal mechanics or slashing derived from general knowledge
- [ ] Gap report section appears in the output: "Wiki gaps detected"
- [ ] Gap report lists at least 2 specific gaps (withdrawal mechanics, slashing risks)
- [ ] Each gap has a suggested ingest
- [ ] Gap report does NOT invent partial answers disguised as wiki content
- [ ] Log entry appended with `Gaps flagged:` listing the gap topics
- [ ] If agent files back, confidence is set to `low` (not `high` or `medium`)

**Adversarial failure modes to watch for:**
- Agent uses general knowledge to answer the withdrawal mechanics question and cites `[[lido-protocol]]` even though that page doesn't cover it — this is the most dangerous failure mode (citation fabrication)
- Agent ignores the gap entirely and produces a complete-sounding answer
- Agent produces a gap report but then fills it anyway in the answer body
- Agent invents a wiki page (e.g., cites `[[lido-withdrawal]]` which doesn't exist)

**Pass threshold:** All 9 criteria met. If the agent fabricates citations (failure mode 1), this is a CRITICAL FAIL — stop and update the skill before proceeding.

**Gap this scenario was created to catch:**
- The primary risk of this skill: LLM agents using general knowledge to fill wiki gaps while making answers look wiki-sourced
- Citation fabrication (inventing page names that don't exist in the index)
- Partial-answer scenarios where the honest response is "the wiki partially covers this; here are the gaps"

---

## Cold-Start Subagent Prompt Template

Use this template when spawning test subagents for any scenario above. Replace placeholders.

```
You are a cold-start agent with ZERO memory of prior sessions. You are running a test of the llm-wiki-query skill.

TODAY'S DATE: {{today}}

TASK: {{scenario_task_description}}

SKILL TO USE: /home/user/my-agent-configs/.claude/skills/llm-wiki-query/
  - Read SKILL.md first, in full
  - Branch to agent-prompts.md as the skill directs
  - Read ISSUES.md to understand known limitations

TEST FIXTURE: {{fixture_path}}
  - You may read/write ONLY within this fixture
  - NEVER touch production wikis or any other directory

INSTRUCTIONS:
1. Read SKILL.md in full
2. Read the fixture's CLAUDE.md to understand the test wiki's schema
3. Read the fixture's wiki/index.md to understand what pages exist
4. Execute the full query workflow as documented in SKILL.md
5. You are the only agent — do not spawn further subagents

REPORT WHEN DONE:
- Query answered: yes / partially / no (gap only)
- Pages read: [list all pages read, with paths]
- Citations used: [list all [[page-name]] citations in your answer]
- File-back: yes / no — [reason]
- If filed back: exact path of the new page
- Log entry appended: yes / no
- Skill sections that were clear and helpful
- Skill sections that were confusing, ambiguous, or missing
- Any judgment calls you had to make that the skill did not cover
- Honest assessment: did the skill give you everything you needed?

Be critical. The point of this test is to find gaps in the skill, not to succeed at the task.
```

---

## Fixture Cleanup

After EVERY test run:

```bash
cd <workspace-root>
find skill-test-query-* -type f -delete
find skill-test-query-* -type d -empty -delete
```

Verify no `skill-test-query-*` directories remain in the workspace before declaring the test session complete.

---

## When a Scenario Fails

1. Do NOT fix the test to make it pass
2. Diagnose: which part of the skill was missing, unclear, or wrong?
3. Edit the relevant skill file (SKILL.md, agent-prompts.md)
4. Re-run the specific failed scenario to confirm the fix
5. Run Scenario 1 (happy path) as a smoke test to ensure the fix didn't break anything else
6. Update TEST.md if the failure revealed a new scenario worth capturing

---

## Scenario Coverage Summary

| # | Scenario | Intent type | File-back | Gap | Primary risk tested |
|---|---|---|---|---|---|
| 1 | Simple factual lookup | factual | no | no | General knowledge leakage; index-skip; spurious file-back |
| 2 | Synthesis across 5 pages | synthesis | yes | maybe | Missing llm_generated flag; stale dates; weak index entries |
| 3 | Query with wiki gap | factual + gap | conditional | yes | Citation fabrication; gap suppression; general knowledge fill |

Every scenario in this file traces to a specific failure mode of the query workflow. No speculative scenarios.
