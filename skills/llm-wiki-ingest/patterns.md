# Advanced Patterns

Real-world ingest patterns learned from production work. Use these when SKILL.md's basic workflow is not enough.

---

## Pattern 1: Newsletter Consolidation

**Problem:** A newsletter archive (Substack, Medium, blog) contains 50-500 articles. Naively creating one source summary per article would produce hundreds of shallow wiki pages with massive overlap.

**Solution:** Consolidate by topic and series.

### Multi-part series → one source summary

If the raw collection contains multi-part series like:
- `A Crash Course in Caching - Part 1.md`
- `A Crash Course in Caching - Part 2.md`
- `A Crash Course in Caching - Final Part.md`

Create ONE source summary: `caching-deep-dive.md` that covers all parts. List all three raw files in the `sources` frontmatter. Do NOT create three separate summaries.

### Related standalone articles → one thematic summary

If the raw collection contains several related but independent articles like:
- `How to Choose a Message Queue.md`
- `Why is Kafka so fast.md`
- `Why Do We Need a Message Queue.md`

Group them into ONE thematic summary: `message-queue-and-kafka.md`. List all three raw files in the `sources` frontmatter. This captures the topic without producing three duplicative pages.

### Thematic groupings that work well

From real newsletter ingests:

| Thematic group | Candidate article topics |
|----------------|--------------------------|
| `caching-deep-dive` | Caching crash courses, Redis production use cases, distributed caching |
| `database-scaling-and-sharding` | Scaling strategies, sharding, data replication |
| `microservices-patterns` | Communication patterns, design patterns, data sharing |
| `api-design-and-versioning` | REST fundamentals, versioning, security, design best practices |
| `authentication-methods` | Cookies/sessions, JWT, OAuth, PASETO, password hashing |
| `http-evolution` | HTTP/1 vs 2 vs 3, TCP handshake, WebSocket, SSE |

### Enrich existing pages, don't duplicate

Most newsletter content is a reformulation of concepts already covered in primary sources (books, whitepapers, RFCs). The pattern:

1. Read the newsletter article
2. Identify the concepts it covers (e.g., "consistent hashing", "cap theorem")
3. Check `wiki/concepts/` for existing pages on those concepts
4. If a page exists: UPDATE it. Add the newsletter URL/path to `sources` frontmatter. If the newsletter adds genuine new depth (diagram, example, benchmark), incorporate it into the page body.
5. If no page exists: CREATE it. This is rare for established topics.

### Triage filters for newsletters

Newsletters often mix technical content with career/marketing content. Aggressive triage is essential.

Skip these article types:

| Pattern | Example titles |
|---------|---------------|
| Career / compensation | "I Was Under Leveled", "The Tech Promotion Algorithm", "Top 3 Resume Mistakes" |
| Productivity / process | "Shipping to Production" (if vague), "Tidying Code" |
| Marketing / listicles | "15 Open-Source Projects That Changed the World" |
| Product recommendations | "15 Tools Every Developer Needs" |
| Author personal | "Why I Left Google", personal reflections |

Keep these:

| Pattern | Example titles |
|---------|---------------|
| Technical deep dives | "A Crash Course in Caching", "How Kafka Works" |
| Case studies | "A Brief History of Scaling Netflix" |
| Protocol explanations | "Network Protocols Behind Server Push" |
| Benchmarks or post-mortems | "Common Failure Causes", "What Happens When a SQL is Executed?" |

When in doubt, read the first 30 lines. If the article opens with advice rather than technical content, it is likely operational and should be skipped.

---

## Pattern 2: Notion Export Handling

**Problem:** Notion exports produce directories with thousands of files: markdown files with UUID suffixes, co-located image subdirectories, deeply nested paths (5-14 levels), mixed languages, CSVs, PNGs, PDFs.

**Solution:** Preprocess the raw/ directory before ingesting.

### Step 1: Strip Notion UUIDs from filenames

Notion appends a 32-character hex UUID to every filename and directory:

```
Lido Oracle ef2f42980a9c43dbb6b25de0918cb174.md
```

This breaks the `sources` frontmatter (paths become unreadable) and makes wikilinks impossible to write cleanly. Strip them before ingesting.

```bash
#!/bin/bash
# strip-notion-uuids.sh — rename files and dirs, removing trailing UUIDs

find raw/notion-export -depth \
  -regextype posix-extended \
  -regex '.* [0-9a-f]{32}($|\..*$)' \
  -print0 | while IFS= read -r -d '' path; do
    # Strip " <32-hex-chars>" before extension
    new_path=$(echo "$path" | sed -E 's/ [0-9a-f]{32}(\.[^/]+)?$/\1/')
    if [ "$path" != "$new_path" ]; then
      mv "$path" "$new_path"
      echo "Renamed: $path -> $new_path"
    fi
  done
```

**Handle collisions:** If stripping the UUID creates a duplicate filename in the same directory, append `(2)`, `(3)`, etc. This happens when the same page was edited and re-saved.

**Process depth-first (innermost first):** Use `find -depth` so child files are renamed before their parent directories. Otherwise the parent path changes mid-operation and the child rename fails.

### Step 2: Classify the flat file list

A Notion export dump will contain three very different kinds of files mixed together:

1. **Knowledge** — technical research, protocol analyses, design docs
2. **Operational** — TODOs, meeting notes, backlogs, status pages
3. **Non-domain** — content unrelated to the wiki's subject (e.g., UI framework comparisons in a Web3 wiki)

Before ingesting, have an agent scan every markdown file's first 30 lines and classify it. Output a table:

```markdown
## Knowledge (N files)
| Path | Topic |
|------|-------|
| notion-export/.../Lido Oracle.md | Lido oracle architecture |
| ...                               | ... |

## Operational (N files)
| Path | Reason |
|------|--------|
| notion-export/.../Research plan.md | Internal task tracking |
| notion-export/.../Contract Monitor/Todos/* | Individual TODO items |

## Non-domain (N files)
| Path | Topic | Reason |
|------|-------|--------|
| notion-export/.../Chakra UI comparison.md | UI frameworks | Not Web3 |
```

### Step 3: Move non-domain files to a reference directory

Create `raw/non-domain-reference/` (or similar). Move all non-domain files there. Document in the wiki's schema that this directory is NOT ingested.

```bash
mkdir -p raw/non-domain-reference
mv raw/notion-export/.../Chakra\ UI\ comparison.md raw/non-domain-reference/
# ... repeat for all non-domain files
```

### Step 4: Handle co-located images

Notion exports place images in subdirectories next to the markdown file that references them:

```
raw/notion-export/.../Lido Oracle/
  Untitled.png
  Untitled 1.png
raw/notion-export/.../Lido Oracle.md  # references ![Untitled](Lido Oracle/Untitled.png)
```

**Do NOT move these images to a central `raw/assets/` directory.** The markdown references are relative paths; moving the images without rewriting every reference will break rendering. Leave images co-located with their source markdown.

The `wiki/` pages can reference raw images via the relative path from the raw file, or can describe the images textually in the source summary without embedding them.

### Step 5: Update CLAUDE.md to reflect the new directory structure

If the wiki's `CLAUDE.md` describes the raw/ structure, update it to match the actual layout after preprocessing. Document any skip directories explicitly.

---

## Pattern 3: Cross-Domain Meta-Wiki

**Problem:** In a monorepo, some topics span multiple domains. For example, "caching" appears in system-design (distributed caches), mobile-system-design (local caches), and implicit in other domains. A user asking "how do caching strategies differ across system-design and mobile?" needs a synthesized comparison, not five separate pages.

**Solution:** Create a dedicated meta-wiki at the monorepo root that contains ONLY comparison pages synthesizing across domains.

### Structure

```
monorepo-root/
├── CLAUDE.md                      Shared methodology
├── index.md                       Master domain router
├── cross-domain/                  Meta-wiki
│   ├── WIKI.md                    Schema: no raw/, uses wiki: prefix sources
│   └── wiki/
│       ├── index.md
│       ├── log.md
│       └── comparisons/           The actual comparison pages
└── ood/                           Regular domain wiki
    ├── WIKI.md
    ├── raw/
    └── wiki/
```

### Key characteristics

1. **No `raw/` directory.** Meta-wiki pages do not ingest raw files. They synthesize across existing domain wiki pages.
2. **Source citations use a `wiki:` prefix.** In frontmatter:
   ```yaml
   sources:
     - wiki:system-design/concepts/distributed-caching.md
     - wiki:mobile-system-design/concepts/in-memory-cache.md
     - wiki:mobile-system-design/concepts/offline-first.md
   ```
3. **Only one page type: `comparison`.** No source-summaries, no concepts, no techniques.
4. **Every cell in the comparison table must cite a specific wiki page.** If a dimension only has content on one side, explicitly say "Not discussed in [other domain]'s wiki". This is a traceability requirement.

### Creating a cross-domain comparison

1. Identify all wiki pages across all domains that discuss the topic
2. Read each page in full
3. Extract actual claims — do NOT use general knowledge
4. Build a comparison table with dimensions as rows and domains as columns
5. Each cell references a specific wiki page
6. Add an Analysis section explaining the trade-offs in prose
7. Add a "When to choose" section
8. List all cited wiki pages in the Sources section at the bottom

### When to create a cross-domain page

Create one when:
- The topic appears in 2+ domain wikis
- The comparison reveals meaningful differences (not just "both cover X")
- A user would realistically ask a cross-domain question about it

Do NOT create one when:
- Only one domain covers the topic (even if other domains mention it in passing)
- The comparison would be shallow ("both use HTTP")
- The topic is too broad ("software architecture")

### Example comparison page naming

- `caching-system-design-vs-mobile.md`
- `video-platforms-across-domains.md` (when 3+ domains are involved)
- `state-machines-ood-vs-mobile.md`

Use `-vs-` for two-domain comparisons and `-across-domains.md` for three or more.

---

## Pattern 4: Monorepo Restructuring

**Problem:** A single wiki has grown to cover multiple loosely related domains (e.g., both OOD interviews and Web3 protocols). The single CLAUDE.md is trying to describe two different worlds, and wiki pages from different domains are mixing in the same directories.

**Solution:** Split the single wiki into a monorepo with per-domain sub-wikis.

### When to split

Trigger signs that a split is needed:

- CLAUDE.md's "Project Overview" section lists 3+ unrelated topics
- The `wiki/` directory has pages that would never cross-link (e.g., an `erc20.md` page and a `parking-lot-design.md` page)
- The user asks questions that feel scoped to one domain
- Different domains have different conventions (different page types, different tags)
- The single CLAUDE.md exceeds ~600 lines trying to document everything

### Split procedure

1. **Plan the domains.** List the distinct domains and decide the directory names:
   ```
   monorepo/
   ├── ood/
   ├── system-design/
   ├── ml-system-design/
   ├── genai-system-design/
   ├── mobile-system-design/
   ```

2. **Create the subdirectories.** Each gets `raw/` and `wiki/` subdirectories.

3. **Move files by domain.** `git mv` (if using git) to preserve history. Example:
   ```bash
   git mv "raw/oo-design-interview" "ood/raw/oo-design-interview"
   git mv "wiki/design-problems/parking-lot-design.md" "ood/wiki/design-problems/parking-lot-design.md"
   # ... for each file
   ```

4. **Rewrite CLAUDE.md as shared methodology.** The root CLAUDE.md now defines what's SHARED across all domains:
   - Three-layer architecture
   - Frontmatter format
   - File naming conventions
   - Internal linking rules
   - Operations (Ingest, Query, Lint) workflow
   - Log format
   - Rules and constraints (immutability, source citation, etc.)
   It does NOT define page types or raw directory structure — those are per-domain.

5. **Create per-domain WIKI.md files.** Each domain gets its own `WIKI.md` that defines:
   - Domain overview (what the wiki covers)
   - Raw directory structure (specific source files)
   - Page types for this domain (source-summary, concept, design-problem, protocol, etc.)
   - Page structure guidelines per type
   - Tags vocabulary
   - Source naming conventions

6. **Create a master `index.md` at the monorepo root.** This is the query router. It contains:
   - Domain router table (5 rows, one per domain, with link to `WIKI.md` and `wiki/index.md`)
   - Cross-domain topic map (topics that span domains, with pointers to the most relevant wiki)
   - Query/Ingest/Lint workflow summaries
   - Any navigation shortcuts

7. **Update each domain's `wiki/index.md` path references.** If source paths were previously `raw/...`, they must now be `domain/raw/...` — or kept as `raw/...` if the convention is domain-relative. Choose one and apply consistently.

8. **Delete the old root-level `wiki/` directory** if it's fully migrated. Verify no files are lost via `diff` before deletion.

9. **Run a verification script** across all domains to catch broken wikilinks, missing frontmatter, orphan pages.

### What NOT to restructure

Do not split if:
- The domains genuinely cross-reference each other on most pages (strong coupling)
- The wiki is small (<50 pages total)
- The user is actively working in the single-wiki mode and the structure is not blocking them

---

## Pattern 5: Verification Script

**Problem:** Over time, a wiki accumulates broken wikilinks, orphaned pages, stale dates, and missing frontmatter. Manual linting is slow.

**Solution:** A bash script that runs the same checks a review agent would run, but in seconds.

### Script template

Save as `<repo-root>/scripts/verify-wiki.sh`:

```bash
#!/bin/bash
# verify-wiki.sh — Quality checks for an llm-wiki
#
# Usage:
#   bash scripts/verify-wiki.sh [--verbose] [--domain <name>]
#
# Exit code: 0 if all checks pass, 1 if any check fails.

set -uo pipefail

VERBOSE=0
DOMAIN=""
FAIL_COUNT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --verbose) VERBOSE=1; shift ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Determine wiki roots to check
if [ -n "$DOMAIN" ]; then
  WIKI_ROOTS=("$DOMAIN/wiki")
else
  # Auto-detect: find every wiki/ subdirectory in the repo
  mapfile -t WIKI_ROOTS < <(find . -type d -name "wiki" -not -path "*/node_modules/*" -not -path "*/.git/*")
fi

for WIKI_ROOT in "${WIKI_ROOTS[@]}"; do
  echo ""
  echo "=== Verifying $WIKI_ROOT ==="

  # Check 1: every .md file has frontmatter
  while IFS= read -r -d '' file; do
    if ! head -1 "$file" | grep -q '^---$'; then
      fail "Missing frontmatter: $file"
    elif [ "$VERBOSE" = "1" ]; then
      pass "Frontmatter: $file"
    fi
  done < <(find "$WIKI_ROOT" -name "*.md" -type f -print0)

  # Check 2: every .md file has a ## Sources section (except index.md and log.md)
  while IFS= read -r -d '' file; do
    base=$(basename "$file")
    if [ "$base" = "index.md" ] || [ "$base" = "log.md" ]; then continue; fi
    if ! grep -q '^## Sources' "$file"; then
      fail "Missing ## Sources: $file"
    elif [ "$VERBOSE" = "1" ]; then
      pass "Sources section: $file"
    fi
  done < <(find "$WIKI_ROOT" -name "*.md" -type f -print0)

  # Check 3: wikilink integrity
  # Extract all [[target]] patterns and verify each target exists
  mapfile -t all_md < <(find "$WIKI_ROOT" -name "*.md" -type f)
  declare -A page_names
  for f in "${all_md[@]}"; do
    name=$(basename "$f" .md)
    page_names["$name"]=1
  done

  while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    link=$(echo "$line" | grep -oE '\[\[[^]|]+' | sed 's/\[\[//')
    if [ -z "$link" ]; then continue; fi
    # Strip alias syntax [[target|alias]]
    target=$(echo "$link" | cut -d'|' -f1)
    if [ -z "${page_names[$target]:-}" ]; then
      fail "Broken wikilink in $file: [[$target]]"
    fi
  done < <(grep -rHoE '\[\[[^]]+\]\]' "$WIKI_ROOT" 2>/dev/null)

  # Check 4: every page listed in index.md exists
  INDEX="$WIKI_ROOT/index.md"
  if [ -f "$INDEX" ]; then
    while IFS= read -r target; do
      if [ -z "${page_names[$target]:-}" ]; then
        fail "Index references non-existent page: [[$target]]"
      fi
    done < <(grep -oE '\[\[[^]|]+' "$INDEX" | sed 's/\[\[//' | cut -d'|' -f1 | sort -u)
  fi

  # Check 5: updated >= created in frontmatter
  while IFS= read -r -d '' file; do
    created=$(awk '/^created:/{print $2; exit}' "$file")
    updated=$(awk '/^updated:/{print $2; exit}' "$file")
    if [ -n "$created" ] && [ -n "$updated" ]; then
      if [[ "$updated" < "$created" ]]; then
        fail "updated ($updated) < created ($created): $file"
      fi
    fi
  done < <(find "$WIKI_ROOT" -name "*.md" -type f -print0)
done

echo ""
echo "=== Summary ==="
if [ "$FAIL_COUNT" -eq 0 ]; then
  echo -e "${GREEN}All checks passed.${NC}"
  exit 0
else
  echo -e "${RED}$FAIL_COUNT check(s) failed.${NC}"
  exit 1
fi
```

### When to run

- After every batch ingest (as part of the quality gate pipeline)
- Before committing wiki changes to git
- On a schedule (weekly) to catch slow drift

### Extending

Add more checks as patterns emerge. Candidate additions:
- Orphan detection (pages with zero inbound wikilinks)
- Duplicate index entries
- Bare generic types outside code blocks (`<T>` not wrapped in backticks)
- Emoji presence in wiki pages
- Source paths pointing to files that don't exist in raw/

---

## Pattern 6: Session Startup for Cold-Start Agents

**Problem:** A fresh LLM session needs to operate on an unfamiliar wiki without getting lost.

**Solution:** A strict, ordered read sequence. Skip nothing.

### Monorepo cold-start (5 reads)

```
1. Read <repo-root>/CLAUDE.md           — shared methodology
2. Read <repo-root>/index.md            — master domain router
3. Identify target domain                — from user request + cross-domain topic map
4. Read <domain>/WIKI.md                — domain-specific schema
5. Read <domain>/wiki/index.md          — what pages already exist
```

### Single-wiki cold-start (3 reads)

```
1. Read <repo-root>/CLAUDE.md           — full schema
2. Read <repo-root>/wiki/index.md       — what pages already exist
3. Read <repo-root>/wiki/overview.md    — high-level synthesis (if exists)
```

### Why each read matters

| File | Why it matters |
|------|---------------|
| `CLAUDE.md` | Operations workflow, conventions, rules. Without this, the agent guesses at format. |
| `index.md` (master) | Domain routing. Without this, monorepo agents may work in the wrong domain. |
| `WIKI.md` (domain) | Page types, source structure, domain-specific tags. Without this, the agent may create wrong page types. |
| `wiki/index.md` (domain) | What already exists. Without this, the agent creates duplicate pages instead of updating. |
| `wiki/overview.md` | High-level context. Helps with cross-referencing. |

### Anti-patterns

- Reading only CLAUDE.md and immediately acting: misses the domain-specific rules
- Reading raw files before the schema: the agent commits to an interpretation that may conflict with the wiki's conventions
- Skipping `wiki/index.md`: guarantees duplicate page creation
- Reading `wiki/log.md` first: the log is useful for history, but the index is the catalog. Log is secondary.

---

## Pattern 7: Backlink Sync Procedure

### When to Use
After a batch ingest that touches 10+ pages, or when lint detects >5 missing backlinks.

### Procedure
1. Build a map: for each page P touched in this batch, list pages that
   reference P (search body wikilinks + frontmatter `related` across all
   of wiki/).
2. For each (P, Q) pair where Q references P but P does not reference Q:
   - Read both pages.
   - Decide: is the reverse link warranted? (e.g., P is a general concept,
     Q is a specific application of P — yes, add backlink in P's Connections.)
   - If warranted, add bullet in P's Connections: `- [[Q]] — <relation>`.
   - If tangential, skip. Log the skip decision.
3. For each page P where Connections section exists but contains broken
   wikilinks (target page no longer exists), flag to lint (do not silently delete).
4. Update `updated:` frontmatter of every page you modified.

### Parallelization
- Safe to parallelize by partitioning pages across agents (agent A handles
  concepts, agent B handles techniques, etc.) IF each agent only writes to
  pages in its partition and queues cross-partition backlink updates to a
  consolidation agent.
- Otherwise sequential is safer.

### Anti-patterns
- Adding reverse links mechanically without judgement → floods Connections
  sections with noise.
- Adding backlinks to body prose instead of Connections → confuses readers.
- Overwriting existing Connections bullets instead of appending.
