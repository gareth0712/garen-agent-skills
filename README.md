# Garen Agent Skills

A collection of skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

| Skill | Description |
|-------|-------------|
| [non-violent-communication](skills/non-violent-communication/) | Rewrites drafts (emails, messages, reviews) using Marshall Rosenberg's NVC framework — turning blame and judgment into observation / feeling / need / request. |

## Usage

Consume this repo with the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
# List available skills in this repo (no install)
npx skills add gareth0712/garen-agent-skills --list

# Install a specific skill globally
npx skills add gareth0712/garen-agent-skills --skill non-violent-communication -g

# Install all skills for Claude Code at project level
npx skills add gareth0712/garen-agent-skills --all --agent claude-code
```

## Validating skills

Each skill follows the [Agent Skills specification](https://agentskills.io/specification) — `name` must be kebab-case and match the directory name, and `description` must state *what* the skill does and *when* to use it.

Validate locally with:

```bash
npx skills-ref validate ./skills/<skill-name>
```
