---
name: planning
description: General-purpose planning driver for large-scale projects — every plan is stress-tested for scalability and resilience without being asked. Use when the user asks to plan, design, or architect a feature, system, service, data model, or migration, to generate or execute the next stage of a design roadmap, or for plan/roadmap status.
---

# Planning with Scalability & Resilience Lenses

Whenever this skill is active, planning means more than sequencing work: every
plan or design is stress-tested through the two lenses below **without the user
asking**. This applies to implementation plans, architecture/design docs, staged
roadmap work, migration plans, and plan-mode proposals alike.

## Design lenses (mandatory on every plan)

Apply both lenses to every component, flow, and store the plan introduces or
touches. A plan is not done until each lens item is either addressed or
explicitly deferred to a named owner/phase — silence is not an option.

**Scalability lens** — for each new service, store, queue/topic, job, and API:

- Load model: what grows (users/tenants, requests/sec, events/sec, payload
  size, fan-out) and what breaks first at 10× and 100× current assumptions.
- Horizontal scaling story: stateless vs. sharded; what the partition key is
  and whether it produces hot partitions or hot tenants.
- Backpressure and flow control: what happens when a consumer or downstream
  lags — buffering, shedding, quotas, per-tenant rate limits.
- Data growth: retention, archival, and pagination for every unbounded table,
  log, or topic; indexes justified against the actual read paths.
- Known bottleneck: name the first component to fall over under load and the
  planned mitigation (even if the mitigation is deferred).

**Resilience lens** — for each new flow and cross-service/system interaction:

- Failure modes enumerated: dependency down, timeout, partial write, duplicate
  delivery, out-of-order delivery, poison message/bad input.
- Retries with idempotency: every retried operation names its idempotency key;
  at-least-once delivery assumed unless argued otherwise.
- Timeouts and circuit breaking on every synchronous external call; what
  degraded mode looks like when a dependency is unavailable.
- State safety: no workflow or state machine may strand an entity; a
  crash-recovery path (resume, compensate, or dead-letter) stated for each
  non-terminal state.
- Blast-radius containment: one failing tenant, job, or feature must not take
  down the rest; name the isolation mechanism (quotas, per-tenant queues,
  bulkheads, feature flags).
- Recovery and replay: how operators reprocess after an outage, and what the
  data-loss window (RPO) and downtime tolerance (RTO) are for each store.

**Right-size the depth.** For a system or subsystem design, write two dedicated
sections — **Scalability** and **Resilience & Failure Modes**. For a smaller
feature plan, a short paragraph per lens inside the plan is enough. Never zero:
if a lens genuinely doesn't apply, say why in one line rather than omitting it.
Argue tradeoffs inline ("Tradeoff — X vs Y"), don't just assert choices.

## Mode 1 — one-off plan or design doc (default)

When asked to plan or design something outside a staged roadmap, structure the
output as:

1. **Context & goals** — what is being built and the constraints inherited from
   the existing system (cite files/docs, don't restate them).
2. **Scope discipline** — what this plan covers and what it deliberately does
   not, with each exclusion assigned an owner or trigger for revisiting.
3. **Design invariants** — the rules the design must never break (data
   ownership, auth boundaries, compatibility guarantees).
4. **The design itself** — topic sections; diagrams (ASCII is fine) for
   architecture and state machines; every requirement in the ask traceable to a
   section.
5. **Scalability** and **Resilience & Failure Modes** — the lens results
   (dedicated sections or inline paragraphs per the right-sizing rule).
6. **Risks & open questions** — each with a proposed resolution path.
7. **Deferred items** — anything pushed out, with the phase/owner that picks it
   up, so later work never has to rewrite this plan.

Honor the target repo's established house rules (ID schemes, multi-tenancy
patterns, event conventions, doc structure) — look for them in `CLAUDE.md`,
existing design docs, or an architecture overview before writing. Match the
house style; don't innovate on form.

## Mode 2 — staged design roadmaps

Some projects run design as a staged pipeline: a roadmap (`ROADMAP.md`,
`docs/stages/`, or similar) splits the system into ordered stages, each stage
deep-dives one subsystem, and outputs accumulate in a design directory. When
the target repo has such a structure, drive it with these conventions:

**Determine pipeline state from the docs, not from git history or memory:**

1. Find the stage briefs (e.g. `docs/stages/stage-N-*.md`). The next stage =
   the lowest N whose exit criteria contain an unticked `- [ ]`.
2. Find the design outputs (e.g. `docs/design/stage-N-*.md`) and the running
   architecture overview doc if one exists.

**Generating the next stage's prompt** (when asked for "the prompt"):

1. **Harvest the seams**: read the "deferred to later stages" section of every
   prior design doc and extract the rows owed to stage N, with their section
   references. Those are the seams the new design must plug into.
2. Read the stage brief's explicit exclusions.
3. Emit a single ready-to-paste prompt that names: the input docs to read, the
   seams to plug (one clause per prior stage, with references), the exclusions
   to respect, **the instruction to stress-test the design through the
   scalability and resilience lenses and capture the results in dedicated
   sections** (never omit this clause), the doc structure to match, the exit
   criteria to tick, the overview doc to update, and the branch to commit to.
4. Show the prompt in a fenced block, then offer to execute it directly in
   this session instead.

**Executing a stage** (when asked to "run/execute the next stage"):

- Read the stage brief plus every prior design doc in full before writing.
- **Additive only**: never redesign, rename, or move what prior stages fixed —
  extend by adding. Open with a header block linking the brief and prior docs,
  a scope-discipline paragraph, and the inherited constraints (prior stages'
  seam rows, with citations).
- Cover every item in the stage brief; include the **Scalability** and
  **Resilience & Failure Modes** sections; match the closing-section order of
  the prior design docs.
- Leave **explicit seams** for remaining stages in a final section — a later
  stage must never have to modify this doc. Deferred lens items (a scaling
  mitigation or resilience mechanism owned by a later stage) get their own
  seam rows.
- **Exit gate**: before ticking anything, verify both lenses are satisfied —
  every lens item addressed or deferred with a named seam. Then tick the exit
  criteria in the stage brief, update the architecture overview (below), and
  commit to a new branch (or the session's designated branch); do not open a
  PR unless asked.

**Keeping the architecture overview current** (after every stage, and on
"status" asks): in the same commit, flip the stage's status row, update the
system diagram if services/stores/topics changed, append a "what stage N
added" ledger entry (new entities, services, APIs, events, and the 3–5
load-bearing decisions — including the stage's key scalability/resilience
decisions such as partition keys, idempotency strategy, and degraded modes),
and refresh the remaining-seams table. Answer "where are we?" from this file
rather than re-reading all design docs.
