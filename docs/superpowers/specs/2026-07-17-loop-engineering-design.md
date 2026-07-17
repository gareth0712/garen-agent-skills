# Loop Engineering Skill Design

## Purpose

Create a `loop-engineering` skill that helps a user turn a sufficiently complex task into a ready-to-paste, platform-agnostic GPT prompt. The generated prompt must describe a real bounded work loop: inspect, act, verify, diagnose, adapt, and repeat until an evidence-backed stop condition or a hard limit is reached.

The skill is a prompt designer. It does not execute the generated prompt or claim that prompt text alone can provide scheduling, persistence, or unavailable tools.

## Goals

- Detect whether the task is complex enough to benefit from a loop before starting an interview.
- Avoid burdening simple requests with a long questionnaire.
- Use a fixed, comprehensive interview for loop-worthy tasks while skipping facts the user already supplied.
- Prefer objective completion evidence and explicit thresholds over model self-judgment.
- Require a hard iteration, time, or token limit.
- Produce one copyable prompt that can be used with a general GPT-style agent.
- Require an honest incomplete result when the loop cannot succeed within its capabilities or budget.

## Non-goals

- Execute the user's task.
- Generate Claude Code-specific `/goal`, `/loop`, or `/schedule` commands.
- Emulate recurring or time-based automation using prompt text alone.
- Add a script, UI, orchestration service, or provider-specific integration.
- Guarantee that every chat model will continue across turns without host-level support.

## Skill Triggering

The description should trigger when the user wants to design an iterative agent prompt, asks an AI to keep working until a measurable result is reached, or describes work that predictably needs repeated action and verification.

The runtime complexity gate determines whether a full loop is justified. Metadata triggering and runtime suitability are intentionally separate: broad discovery helps the skill notice possible loop tasks, while the gate prevents over-engineering simple work.

## Complexity Gate

### Strong loop signals

A task is loop-worthy when at least one strong signal is present:

- Success depends on repeatedly measuring a result and revising the work.
- The task explicitly targets a threshold, such as a test count, score, error rate, or quality rubric.
- Work depends on changing external state that can be observed during the current execution.
- The agent must process a queue or collection until no eligible items remain.
- A first attempt is predictably insufficient and each next action depends on evidence from the previous attempt.

### Supporting signals

Two or more supporting signals also justify a loop:

- Multiple dependent stages are required.
- The solution path is uncertain and alternatives must be tested.
- Completion has several independent acceptance criteria.
- Failure recovery or rollback is part of the work.
- The task is large enough that premature completion is a material risk.

### Simple-task bypass

Do not start the full interview for a factual question, explanation, small deterministic rewrite, one-step transformation, or isolated change with an obvious single verification step. Briefly explain that a loop would add overhead and recommend a normal prompt instead. Do not ask the comprehensive questionnaire.

When the classification is genuinely ambiguous, state the classification and the decisive signal. Do not create a long pre-interview merely to decide whether to interview.

## Interview Contract

For loop-worthy tasks, extract all answers already present in the conversation before asking questions. Cover every category below, but ask only about missing or contradictory information. Ask two to four related questions per round so the interview remains complete without becoming unnecessarily slow.

### 1. Outcome and scope

- What concrete artifact or state should exist at completion?
- What is in scope and explicitly out of scope?
- Which constraints or invariants must remain true?
- Which requirements are mandatory versus desirable?

### 2. Inputs and environment

- What inputs, files, URLs, repositories, or external state are available?
- Which tools and integrations can the executing GPT actually use?
- What permissions does it have?
- Which dependencies, commands, or authoritative documentation are available?

### 3. Verification

- What evidence proves each mandatory requirement?
- Which tests, commands, measurements, or inspections produce that evidence?
- What numeric thresholds apply?
- When objective measurement is impossible, what explicit rubric and minimum score should the evaluator use?

### 4. Iteration strategy

- What work should happen in each attempt?
- What observations should influence the next attempt?
- Which changes should be small, reversible, or isolated?
- When should the loop change strategy rather than retry the same action?

### 5. Safety and recovery

- Which actions are forbidden or require approval?
- What state must be preserved?
- What constitutes a blocker or unsafe condition?
- What rollback or recovery action is available after a failed attempt?

### 6. Budget and termination

- What is the maximum iteration count, elapsed time, or token budget?
- What counts as meaningful progress?
- How many no-progress iterations are allowed before stopping?
- What information must the failure report contain?

If the user does not know a non-critical value, recommend a concrete default and label it as an assumption. Never silently invent tools, permissions, evidence, or success criteria.

## Feasibility Check

Before generating the prompt, verify that:

- Every mandatory success criterion has a corresponding evidence source.
- The named tools and inputs are available to the target GPT environment.
- The loop can run within one bounded execution or supported interactive session.
- Success criteria do not contradict constraints or forbidden actions.
- At least one hard cap exists.
- A failure exit exists for missing capabilities, blockers, and exhausted budget.

If a critical gap remains, continue the interview. If the request requires scheduling, persistent monitoring, or unavailable tools, explain that external orchestration is required and do not pretend a pure prompt can supply it.

## Generated Prompt Contract

The skill returns only one copyable Markdown code block containing the final prompt. The prompt should use the user's language unless they request another language.

The generated prompt contains these sections:

1. **Role and mission** — the intended outcome, scope, and invariants.
2. **Available context and capabilities** — inputs, tools, permissions, and explicit limitations.
3. **Acceptance criteria** — mandatory criteria mapped to evidence-producing checks.
4. **Loop state** — iteration number, attempt log, current hypothesis, evidence, unresolved failures, and remaining budget.
5. **Preflight** — validate capabilities and inputs before changing state.
6. **Loop cycle** — inspect, plan, act, verify, diagnose, and adapt.
7. **Strategy-change rule** — do not repeat an unchanged failed action without new evidence.
8. **Success exit** — exit only when every mandatory criterion is supported by current evidence.
9. **Failure exit** — stop on hard-cap exhaustion, missing capability, unsafe action, hard blocker, or repeated no-progress iterations.
10. **Final report** — emit either `SUCCESS` with artifacts and evidence, or `INCOMPLETE` with attempts, evidence, blockers, and the next required action.

The prompt explicitly forbids fabricated tool results, test outcomes, measurements, and claims of completion.

## Loop Control Model

The generated prompt expresses the following model in natural-language instructions:

```text
preflight()
initialize loop_state

while budget remains:
    inspect current state and prior evidence
    choose the smallest useful, verifiable next action
    execute the action within permissions
    collect fresh evidence
    evaluate every mandatory acceptance criterion

    if all mandatory criteria pass:
        return SUCCESS with evidence

    diagnose failures
    update the strategy and loop_state

    if blocked, unsafe, incapable, or no-progress limit reached:
        return INCOMPLETE with evidence and next required action

return INCOMPLETE because the hard cap was reached
```

This is bounded agent behavior, not an assertion that a language model has native process persistence.

## Error Handling

| Condition | Skill behavior |
| --- | --- |
| Task is simple | Bypass the questionnaire and recommend a normal prompt. |
| Mandatory outcome is vague | Ask for the missing deliverable or state. |
| Verification is subjective | Elicit an explicit rubric, evaluator, and pass threshold. |
| Tool or permission is unavailable | Mark the loop infeasible until the environment changes. |
| Success criteria conflict | Surface the conflict and ask the user to resolve it. |
| User cannot choose a hard cap | Recommend a task-sized cap and label it as an assumption. |
| Prompt would require recurring execution | Explain the need for scheduler or API orchestration. |
| Loop reaches its hard cap | Require an `INCOMPLETE` report; never relabel best effort as success. |

## File Layout

```text
skills/loop-engineering/
├── SKILL.md
└── evals/
    └── evals.json

skills/loop-engineering-workspace/
└── iteration-1/
    └── ... evaluation outputs and review artifacts
```

The runtime guidance should fit in `SKILL.md`. A rendering script is unnecessary because conversational answers and task-specific wording cannot be reduced to a useful static form without adding complexity. Evaluation artifacts remain outside the runtime instructions.

## Test-Driven Validation

### Baseline and with-skill cases

1. **Simple-task gate** — a small rewrite or explanation must not trigger the full questionnaire.
2. **Verifiable coding loop** — a measurable engineering target must collect environment, verification, strategy, safety, and hard-cap details before producing a prompt.
3. **Subjective quality loop** — a non-numeric task must turn quality into an explicit rubric and threshold.
4. **Impossible environment** — a recurring monitoring request given to a non-persistent chat model must be rejected as infeasible without external orchestration.

### Assertions

- Simple requests receive no comprehensive loop interview.
- Complex prompts contain explicit loop state and the inspect-plan-act-verify-diagnose-adapt cycle.
- Every mandatory success criterion maps to evidence.
- A hard cap and no-progress rule are present.
- Success and incomplete exits are distinct.
- The output forbids fabricated evidence.
- Missing tools or persistence are surfaced rather than assumed.

### Cold-start validation

A fresh agent with no prior conversation context must use only `SKILL.md` to handle representative happy-path and adversarial prompts. Record vague, missing, or guessed decisions in a concrete gap list, fix each actionable gap, and rerun affected cases. Remove temporary fixtures after testing.

Generate the standard static evaluation viewer so the human reviewer can inspect outputs and quantitative grades. Do not treat validator exit codes or agent summaries as sufficient evidence; inspect representative generated prompts directly.

## Success Criteria for the Skill

The skill is ready when:

- Its metadata validates and matches the `loop-engineering` directory name.
- A fresh agent can apply the complexity gate without prior knowledge.
- Simple requests avoid the full questionnaire.
- Loop-worthy requests receive complete but non-duplicative questioning.
- Generated prompts contain executable bounded-loop instructions, evidence-backed completion, hard limits, and honest failure exits.
- Adversarial tests demonstrate that the skill does not invent persistence, tools, permissions, or verification results.
