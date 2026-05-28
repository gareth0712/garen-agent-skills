# ISSUES.md — Known limitations and open risks

This file tracks known limitations, untested assumptions, and open risks for the garen-skill-creator skill. It exists because some problems cannot be fixed today but must not be forgotten.

**Distinction from TEST.md:** TEST.md validates what the skill DOES handle. ISSUES.md documents what the skill MIGHT NOT handle, or handles in ways that haven't been proven in production.

**Distinction from patterns.md:** patterns.md documents workflows that work. ISSUES.md documents workflows that are untested, partially working, or known to have edge cases.

---

## Active Issues

### Issue #1: Skill is untested in production

**Severity:** HIGH — the Garen fork's reliability is theoretical until validated by independent use

**Description:**
The garen-skill-creator is a fork of the original Anthropic skill-creator, extended with Garen's test-driven workflow additions (cold-start subagent testing, adversarial fixtures, gap capture). It has not been validated for real skill creation in this repo by:
- A fresh Claude session (without the authoring session's context)
- A human user following the skill manually end-to-end
- Any session other than the one that forked and extended it

The original Anthropic skill-creator has been tested by Anthropic, but the Garen-specific additions (Steps 2–8 of the Skill Development Workflow) have not been exercised against a real new skill from scratch in this environment.

**Why this matters:**
Fork additions may silently break or conflict with the base skill's workflow. A closed loop of "author extends own work" catches obvious bugs but misses integration issues the author took for granted.

**How to resolve:**
On the next new skill creation task, start a fresh Claude session. Do not reference this session's memory. Let the fresh session discover and invoke garen-skill-creator. Observe where it struggles, makes wrong assumptions, or skips Garen-added steps. Those observations become new TEST.md scenarios or ISSUES.md entries.

**Workaround until resolved:**
Treat the skill as a hypothesis. When spawning a skill-creation subagent, explicitly instruct it to follow the Skill Development Workflow section in CLAUDE.md, not just the skill file, as a cross-check.

---

### Issue #2: Cowork headless limitation for eval-viewer

**Severity:** MEDIUM — the eval-viewer HTML artifact cannot be opened in Claude Code on the web / Cowork environments

**Description:**
The skill includes an `eval-viewer/` directory containing an HTML-based skill evaluation viewer. In Claude Code CLI environments, this file can be opened in a local browser. In Claude Code on the web (Cowork / claude.ai), there is no local browser context — the agent cannot open or render HTML files directly, and the user cannot easily view them without downloading.

**Why this matters:**
The eval-viewer is part of the skill quality measurement workflow. If it cannot be rendered, the quantitative evaluation step becomes manual or skipped entirely.

**How to resolve:**
Add a fallback path in the skill documentation: when running in a headless or web-only environment, output the evaluation results as structured plain text to the conversation instead of rendering the HTML viewer. Document the detection heuristic (check for `TERM` environment variable or `CLAUDE_ENV` if available).

**Workaround until resolved:**
In Cowork or claude.ai sessions, print evaluation results as a Markdown table directly in the conversation. Skip the `eval-viewer/` HTML step and note in the skill report that the viewer was not rendered.

---

### Issue #3: Subagent spawning restrictions on claude.ai

**Severity:** MEDIUM — the skill assumes a Claude Code CLI environment where subagents can be freely spawned

**Description:**
The garen-skill-creator requires spawning subagents (cold-start Sonnet subagents for testing, Haiku subagents for fixture reads, etc.) as a core part of its test-driven workflow. On claude.ai (web interface without the CLI), subagent spawning via the Agent tool may be restricted or unavailable entirely.

**Why this matters:**
Without subagent spawning, the cold-start test step (Step 4 of the Skill Development Workflow) cannot be executed as designed. The user would be forced to either skip validation or simulate it manually — which defeats the purpose of the test-driven workflow.

**How to resolve:**
Document a degraded-mode path for claude.ai: instead of spawning a subagent, open a new conversation on claude.ai, paste the skill file and a fixture description, and ask Claude to follow the skill with no prior context. This is a manual simulation of the cold-start test but produces equivalent feedback.

**Workaround until resolved:**
When operating on claude.ai without CLI access, treat Step 4 (cold-start subagent test) as a manual step: open a separate browser tab with a fresh claude.ai conversation and run the cold-start simulation there. Document the gap results the same way as if a subagent had reported them.

---

### Issue #4: Description optimizer requires Claude CLI

**Severity:** LOW — fallback exists but is manual

**Description:**
The `scripts/improve_description.py` script (inherited from the Anthropic base skill-creator) invokes the `claude` CLI to run LLM-assisted skill description optimization. Environments that do not have the Claude CLI installed (e.g., CI pipelines, non-developer machines, raw Python environments) will fail at this step.

**Why this matters:**
The description optimizer is one of the higher-value automation steps — a poor skill description means the skill is never triggered. If the optimizer silently fails, the user may not realize their description is suboptimal.

**How to resolve:**
Add an explicit pre-flight check in the script: detect whether `claude` CLI is available (`shutil.which('claude')`). If not found, print a clear error message: "Claude CLI not found. Run `pip install claude-cli` or optimize the description manually using the rubric in SKILL.md." Do not silently fall back to the unoptimized description.

**Workaround until resolved:**
Manually optimize the skill's `description:` frontmatter field using the description quality rubric in the base skill-creator documentation. Focus on: specificity of trigger phrases, disambiguation from similar skills, and verb-first phrasing.

---

### Issue #5: Merged Test-Driven Validation workflow is opinionated

**Severity:** LOW — causes friction for users familiar with the original Anthropic skill-creator workflow

**Description:**
The Garen fork adds a mandatory test-driven validation workflow (cold-start subagent testing, adversarial fixture design, gap capture, cleanup) that is stricter than the original Anthropic skill-creator. Users accustomed to the original workflow — write skill, test it yourself, ship it — will find the Garen additions require significant extra steps and a different mental model.

The additional steps are valuable (see CLAUDE.md Skill Development Workflow) but are not negotiable in this repo's standards. This creates a potential tension: a new user may invoke garen-skill-creator expecting the simpler Anthropic flow and find themselves required to run a cold-start subagent test they did not anticipate.

**Why this matters:**
Unexpected workflow requirements increase the chance of the user skipping or shortcutting the test steps, which undermines the entire point of the fork.

**How to resolve:**
Add an explicit "What's different in the Garen fork" section near the top of SKILL.md (after the description frontmatter). List the 3 key additions: (1) cold-start subagent test required, (2) adversarial fixtures required, (3) gap capture must be written down. Frame them as non-negotiable quality gates, not optional extras.

**Workaround until resolved:**
When spawning garen-skill-creator as a subagent, explicitly state in the task description: "This repo requires cold-start subagent testing per the Skill Development Workflow in CLAUDE.md. Do not skip Steps 2–7."

---

## Resolved Issues

(Move issues here when they are validated or fixed. Keep the record for history.)

None yet.

---

## How to Use This File

**When encountering a new problem:**
1. Check if it matches an existing issue here — if yes, apply the workaround
2. If not, add a new entry with severity, description, and how to resolve

**When fixing an issue:**
1. Implement the fix in the skill
2. Run the relevant TEST.md scenarios to verify
3. Move the issue to "Resolved Issues" with the fix date and what was done

**When compacting:**
This file is institutional memory. It should survive compaction. A fresh session reading the skill should read ISSUES.md before trusting anything.

---

## Principle

Every issue here exists because a REAL risk was identified, not a speculative "what if". If a risk isn't real or actionable, it doesn't belong here. If a risk IS real but we can't fix it today, it MUST belong here.

The goal is to prevent the next session from rediscovering problems we already know about.
