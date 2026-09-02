# Garen Agent Skills

A collection of skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

Skills are grouped by theme below. The **Invoke** column shows how each one fires:
🤖 **auto** — the agent can trigger it on its own from context (you can also call it by name); 👤 **manual** — only fires when you invoke it by name (e.g. `/handoff`).

### Planning & decision-making

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [planning](skills/planning/) | 🤖 | General-purpose planning driver for large-scale projects. Every plan or design it produces is automatically stress-tested for **scalability** (load model, partitioning, backpressure, data growth) and **resilience** (failure modes, idempotent retries, timeouts, degraded modes, replay) — you never have to ask. Also drives staged design roadmaps. |
| [garen-debate](skills/garen-debate/) | 🤖 | Multi-round structured debate to pick between competing technical approaches. Assigns 3–6 defender agents, runs rounds of defense + counter-attack, and synthesizes a verdict with a tradeoff table. Use when you're unsure which option is best. |
| [grilling](skills/grilling/) | 🤖 | Relentlessly interviews you about a plan or design to stress-test it before you build. Surfaces gaps, hidden assumptions, and weak spots. |
| [ai-council](skills/ai-council/) | 🤖 | Evaluates a single idea, decision, or plan through five contrasting advisors (Contrarian Skeptic, First-Principles Engineer, Expansionist, Outsider, Executor), cross-critiques them, and delivers a Chairman's verdict: 1-hour decision, primary risk, #1 action. For A-vs-B technical choices use garen-debate instead. |
| [grill-me](skills/grill-me/) | 👤 | Manual-invoke version of the same relentless plan/design interview. |

### Building & improving skills

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [garen-skill-creator](skills/garen-skill-creator/) | 🤖 | Create, edit, and optimize skills; run evals to benchmark skill performance with variance analysis; and tune descriptions for better trigger accuracy. |
| [writing-great-skills](skills/writing-great-skills/) | 👤 | Reference guide for the vocabulary and principles that make a skill predictable and well-written. |

### Research & analysis

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [research-council](skills/research-council/) | 🤖 | Researches an external topic or claim through five evidence advisors (Practitioner, Skeptic, Economist, Historian, Academic), maps their conflicts as findings, and delivers a CEO summary with confidence-ranked findings plus a self peer review. Specific claims must be search-verified and cited or labeled 未驗證. |

### Personal knowledge wiki (llm-wiki)

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [llm-wiki-ingest](skills/llm-wiki-ingest/) | 🤖 | Ingest raw sources (PDF/MHTML/HTML/SRT/Notion) into an llm-wiki — triage, format conversion, page creation, index/log updates, and quality gates. |
| [llm-wiki-query](skills/llm-wiki-query/) | 🤖 | Answer factual/synthesis/comparison questions from existing wiki pages, with optional file-back to compound knowledge over time. |
| [llm-wiki-lint](skills/llm-wiki-lint/) | 🤖 | Periodic health check for a wiki — finds contradictions, orphans, and stale pages, auto-fixes structural issues, and suggests what to ingest next. |

### Memory & cross-device config

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [garen-memory-clean-up](skills/garen-memory-clean-up/) | 👤 | Audits and optimizes `CLAUDE.md` instruction files across global/project/local scopes, producing a scorecard, anti-pattern report, and actionable edit list. |
| [garen-sync-setup](skills/garen-sync-setup/) | 🤖 | Maintains the `~/sync-setup/` config repo — regenerates integrated web-LLM preferences, produces per-platform preference files, sanitizes memories, and keeps devices in sync. |

### Communication, learning & handoff

| Skill | Invoke | What it does |
|-------|:------:|--------------|
| [non-violent-communication](skills/non-violent-communication/) | 🤖 | Rewrites drafts (emails, messages, reviews) using Marshall Rosenberg's NVC framework — turning blame and judgment into observation / feeling / need / request. |
| [japanese-learning](skills/japanese-learning/) | 🤖 | Scans any Japanese text you write for errors and returns corrections with 【日語修正】 labels; also answers "how do you say X in Japanese" questions. |
| [teach](skills/teach/) | 👤 | Teaches you a new skill or concept within the current workspace. |
| [learning-coach](skills/learning-coach/) | 🤖 | Socratic coach for taking a new domain from 看懂 to 能自己推理 — builds a knowledge map, surfaces the real expert controversies, then examines you one question at a time and debugs the broken link in your reasoning rather than handing over the answer. Keeps a persistent error bank and spaced-review schedule on disk across sessions. |
| [handoff](skills/handoff/) | 👤 | Compacts the current conversation into a handoff document so a fresh agent can pick up the work. |

## Usage

Consume this repo with the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
# List available skills in this repo (no install)
npx skills add gareth0712/garen-agent-skills --list

# Install a specific skill globally
npx skills add gareth0712/garen-agent-skills --skill non-violent-communication -g

# Install all skills for Claude Code at project level
npx skills add gareth0712/garen-agent-skills --all --agent claude-code

# Install all skills from a repo to all agents
npx skills add gareth0712/garen-agent-skills --all
```

### List installed skills

```bash
# List all installed skills (project and global)
npx skills list

# List all installed skills
npx skills ls -g
```

### Updating skills

```bash
# Update all skills (interactive scope prompt)
npx skills update

# Update a single skill by name
npx skills update my-skill

# Update multiple specific skills
npx skills update frontend-design web-design-guidelines

# Update only global or project skills
npx skills update -g
npx skills update -p

# Non-interactive (auto-detects scope: project if in a project, else global)
npx skills update -y
```

## Validating skills

Each skill follows the [Agent Skills specification](https://agentskills.io/specification) — `name` must be kebab-case and match the directory name, and `description` must state *what* the skill does and *when* to use it.

Validate locally with:

```bash
npx skills-ref validate ./skills/<skill-name>
```
