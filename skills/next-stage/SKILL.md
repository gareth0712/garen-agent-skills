---
name: next-stage
description: Drives a repo's multi-stage design roadmap (see ROADMAP.md / docs/stages). Use when the user asks for the next stage's prompt, to execute/run the next design stage, for stage progress/status, or to update the architecture overview. Generates ready-to-use execution prompts by harvesting seams from prior design docs, encodes the stage-execution conventions (additive-only, doc structure, exit criteria, branch/commit), applies mandatory scalability and resilience lenses to every planning pass, and keeps docs/design/architecture-overview.md current.
---

# Multi-Stage Design Pipeline Driver

The target repo designs a platform in staged design sessions (see `ROADMAP.md`).
Each stage deep-dives one subsystem, **only adds** to what prior stages fixed, and
leaves explicit seams for later stages. This skill automates the pipeline:
figuring out where we are, generating the next execution prompt, executing a
stage to the house conventions, and keeping the architecture overview current.

**Every planning pass — prompt generation (Mode A) and stage execution (Mode B)
— must apply the two design lenses below. This is not optional and the user does
not need to ask for it.**

## Design lenses — scalability & resilience (mandatory)

Apply both lenses to every component, flow, and store the stage designs. A stage
is not done until each lens item is either addressed in the doc or explicitly
deferred with a seam row naming the owning stage.

**Scalability lens** — for each new service, store, queue/topic, and API:

- Load model: what grows (tenants, events/sec, payload size, fan-out) and the
  expected order of magnitude at 10× and 100× current assumptions.
- Horizontal scaling story: stateless vs. sharded; what the partition key is and
  whether it produces hot partitions or hot tenants.
- Backpressure and flow control: what happens when a consumer lags — buffering,
  shedding, quotas, rate limits per workspace.
- Data growth: retention, archival, and pagination for every unbounded table or
  topic; indexes justified against the read paths.
- Known bottleneck: name the first component to fall over under load and the
  planned mitigation (even if the mitigation is a deferred seam).

**Resilience lens** — for each new flow and cross-service interaction:

- Failure modes enumerated: dependency down, timeout, partial write, duplicate
  delivery, out-of-order delivery, poison message.
- Retries with idempotency: every retried operation names its idempotency key;
  at-least-once delivery assumed unless argued otherwise.
- Timeouts and circuit breaking on every synchronous cross-service call; what
  degraded mode looks like when a dependency is unavailable.
- State-machine safety: no transition may strand an entity; crash-recovery path
  (resume, compensate, or dead-letter) stated for each non-terminal state.
- Blast-radius containment: a failing workspace/tenant must not take down
  others; note isolation mechanism (quotas, per-tenant queues, RLS).
- Recovery and replay: how operators reprocess from the outbox/dead-letter, and
  what the data-loss window (RPO) is for each store.

Capture the lens results in two dedicated sections of the design doc —
**Scalability** and **Resilience & Failure Modes** — placed after the topic
sections and before the closing sections. Tradeoffs stay inline in house style
("Tradeoff — X vs Y").

## Pipeline state — how to determine it

1. Stage briefs live in `docs/stages/stage-N-*.md`. Each contains: 目標 (goal),
   前置輸入 (input docs), a fenced `Prompt` block (the design prompt), 明確不做
   (explicit exclusions), and `Exit Criteria` checkboxes.
2. **The next stage = the lowest N whose Exit Criteria contain an unticked
   `- [ ]`.** Grep the stage files; do not guess from git history.
3. Design outputs live in `docs/design/stage-N-*.md`.
   `docs/design/architecture-overview.md` is the running whole-platform picture.

## Mode A — generate the next stage's prompt (default when asked for "the prompt")

1. Identify the next stage N (above).
2. **Harvest the seams**: open the final "Deferred to Later Stages" section of
   *every* existing design doc (`docs/design/stage-1` … `stage-(N−1)`) and extract
   the row for Stage N. Those rows — with their § references — are the seams the
   new design must plug into. Stage 1's "Deferred Decisions Ledger" (§16) row for
   Stage N gives the fixed constraints.
3. Read the stage brief's 明確不做 for the exclusions to respect.
4. Emit the prompt using this template (one paragraph, ready to paste into a fresh
   session). The scalability/resilience clause is part of the template — never
   omit it:

   ```
   my-agent-platform
   read the stage file plus the {N−1} existing design docs, execute the prompt
   above additively on the seams left for Stage {N} ({seam summary: one clause
   per prior stage, each with its § reference}), respect the {count}
   exclusion(s) ({exclusions}), stress-test the design for scalability (load
   model, partitioning, backpressure, data growth) and resilience (failure
   modes, idempotent retries, timeouts, degraded modes, replay) and capture
   the results in dedicated Scalability and Resilience & Failure Modes
   sections, match the doc structure, tick the exit criteria, update
   docs/design/architecture-overview.md with what Stage {N} added, and commit
   to a new branch.
   ```

5. Show the prompt in a fenced block for copy-paste, then offer to execute it
   directly in this session instead.

## Mode B — execute a stage (when asked to "run/execute the next stage")

Read the stage brief **plus every prior design doc in full** before writing
anything. Then produce `docs/design/stage-N-<slug>.md` honoring all of the
following conventions (match them, don't innovate on form):

- **Additive only.** Never redesign, rename, or move existing entities, services,
  API routes, events, or data ownership. Extend by adding services/entities/
  events/routes (Stage 1 §8.2 rule). Reserved fields/enums may be finalized;
  everything else is new.
- **Header block**: quote block linking the stage brief and every prior design
  doc, plus the additive-only rule statement.
- **Scope discipline** paragraph: what this stage designs, what it deliberately
  does not (naming the owning stage for each exclusion).
- **Constraints inherited** numbered list: the Stage 1 ledger row + each prior
  doc's seam row for this stage, with precise § citations.
- **Table of Contents**, then **§1 Overview** with an ASCII architecture diagram
  and a "Design invariants" bullet list.
- Topic sections covering every item in the stage brief's `Prompt` block —
  both the "Support:" list and the "Explain:" list must be traceable to sections.
- **Scalability** and **Resilience & Failure Modes** sections: run both design
  lenses (above) over everything this stage adds and write up the results here,
  after the topic sections. Every retried operation names its idempotency key;
  every unbounded store names its retention; every sync call names its timeout
  and degraded mode.
- **Closing sections in this order** (matching prior docs): Event Flow ·
  Persistence Model · New Entities (table with id prefixes) · New Services &
  Components · API Changes (additive) · Event Changes (additive) · Database
  Additions (sql block) · Deferred to Later Stages (seam table for remaining
  stages).
- **House rules**: prefixed ULIDs for every entity; `workspace_id` + RLS on every
  table; outbox pattern for all events; state machines drawn in ASCII with
  transition tables; terminal states immutable; tradeoffs argued inline
  ("Tradeoff — X vs Y"); cross-references always cite `Stage N §M`; no model
  calls or credentials outside the surfaces prior stages fixed (model-proxy,
  execution gateway, secret refs).
- Leave **explicit seams** for the remaining stages in the final section — a
  later stage must never have to modify this doc. Deferred lens items (a
  scalability mitigation or resilience mechanism owned by a later stage) get
  their own seam rows.
- **Exit gate**: before ticking anything, verify both lenses are satisfied —
  every lens item addressed in the doc or deferred with a named seam. Then
  **tick the Exit Criteria** checkboxes (`- [ ]` → `- [x]`) in the stage brief.
- **Update `docs/design/architecture-overview.md`** per Mode C.
- **Commit to a new branch** `claude/stage-N-<slug>` (unless the session was given
  a designated branch — then use that), push with `-u`; do **not** open a PR
  unless asked.

## Mode C — architecture overview & status (after every stage, and on "status" asks)

`docs/design/architecture-overview.md` is the single progress-tracking artifact.
After completing a stage, update it in the same commit:

1. Flip the stage's row in the **Status** table (✅ + doc link).
2. Update the **system diagram** if services, stores, or topics changed.
3. Append a **"What Stage N added"** ledger entry: new entities (with prefixes),
   new services/deployables, new API families, new event types/topics, and the
   3–5 load-bearing design decisions — ≤ 12 bullets, link the full doc for depth.
   Include the stage's key scalability/resilience decisions (partition keys,
   idempotency strategy, degraded modes) among the load-bearing decisions.
4. Update the **entities / event topics / extension points** tables.
5. Refresh **Remaining seams** (drop the completed stage's column, keep what
   later stages still owe).

When the user asks "where are we / what's the architecture now", answer from this
file (plus the status table) rather than re-reading all design docs; offer the
per-stage ledger as the changelog.
