# Non-Violent Communication (NVC) Rewriter

An agent skill that rewrites messages, emails, and conversations using Marshall Rosenberg's **Non-Violent Communication (NVC)** framework — transforming blame, judgment, and demands into empathetic, needs-based language.

> 「我們可以表達情緒，但不要情緒化的表達。」
> — Marshall Rosenberg, NVC

---

## What it does

Takes a draft message written in emotional, blaming, or confrontational language (**Jackal language** 財狼語言) and rewrites it in clear, empathetic language (**Giraffe language** 長頸鹿語言) that preserves the original intent while reducing conflict.

---

## When to use

Trigger this skill whenever you are about to send a message and worry the tone might come across as harsh, passive-aggressive, or accusatory. Typical triggers:

- 「幫我改這封 email」
- 「這樣說會不會太衝／太兇？」
- 「用 NVC 改寫」
- 「幫我說得好聽一點」
- 「這樣講會不會傷人？」
- Any outbound communication (email, Slack, LINE, WhatsApp, review feedback, difficult conversations) where tone matters.

---

## The NVC Framework — 4 Steps

| Step | Name | What to say | What to avoid |
|------|------|-------------|---------------|
| 1 | **Observation** 觀察 | State the observable fact | No evaluation, no "always/never", no labels |
| 2 | **Feelings** 感受 | Name your emotion ("I feel...") | Not a thought or judgment ("I feel you don't care") |
| 3 | **Needs** 需求 | The universal need behind the feeling | Not a complaint about the other person's behavior |
| 4 | **Request** 請求 | A concrete, doable action — phrased as a question | Not a demand, not vague, not a negation |

---

## Output format

The skill returns a structured rewrite:

```
### 🔍 Diagnosis
[What in the original is evaluation/blame/command/vague]

### ✏️ NVC Rewrite
Observation: [pure facts]
Feelings:    [I feel...]
Needs:       [because I need/value...]
Request:     [Would you be willing to...?]

### 💬 Natural-language version
[The four steps woven into a natural message/email]

### 📝 What changed
[Short explanation of Jackal → Giraffe transformations]
```

---

## Example

**Original (Jackal):**
> 「我叫你回來買醬油，你忘了，好煩啊！」

**NVC Rewrite (Giraffe):**
> 「老公，你今天回來沒有帶醬油，我有點沮喪，因為今晚的菜需要用到。你現在方便去便利店買一瓶嗎？」

---

## Design notes

- Rewrites should sound **natural**, not formulaic or overly formal.
- Preserve the sender's core intent — change how it is said, not what is asked for.
- For workplace email, dial down the raw emotion step while keeping observation and request crisp.
- If the sender's intent is unclear, ask them first: *"What do you most want this message to achieve?"*

---

## Files

- [SKILL.md](SKILL.md) — the full skill definition loaded by the agent
- [README.md](README.md) — this file (human-facing overview)

---

## Credits

- Framework: Marshall Rosenberg, *Nonviolent Communication: A Language of Life*
- Chinese framing: 維思維 WeisWay
