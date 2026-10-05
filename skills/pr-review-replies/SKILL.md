---
name: pr-review-replies
description: >
  Close the loop on GitHub pull-request review comments (Copilot, human reviewers,
  review bots): fix each comment, push, then reply IN THAT COMMENT'S THREAD with the
  commit hash that fixed it and one line on what changed, and resolve the thread.
  Use whenever you address PR review feedback — "fix the Copilot comments", "address
  the review", "there are high severity findings on the PR", "resolve the PR
  comments", or after any fix pushed in response to a review. Also covers replying
  when you decide NOT to change something.
---

# PR review replies

A fix nobody can see is not finished: a reviewer (human or Copilot) sees an open
thread and assumes the problem is still there. Every review comment you act on ends
with a reply in its own thread that names the commit, and a resolved thread.

## The loop, per PR

1. **List open threads** (GraphQL gives thread ids and resolution state; REST gives
   comment ids for replies):
   ```bash
   gh api graphql -f query='query{repository(owner:"OWNER",name:"REPO"){pullRequest(number:N){reviewThreads(first:50){nodes{id isResolved path line comments(first:1){nodes{databaseId author{login} body}}}}}}}' \
     --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved|not) | "\(.id) \(.comments.nodes[0].databaseId) \(.path):\(.line) \(.comments.nodes[0].author.login)"'
   ```
2. **Judge, then fix.** Read the full comment (`gh api repos/OWNER/REPO/pulls/comments/<id>`)
   and check it against the code before acting: Copilot is often right and sometimes
   wrong. Fix each comment you accept, following the repo's own rules (AGENTS.md,
   architecture skills). One commit per comment or per coherent group, so each reply
   can cite a hash that contains exactly that fix. Run the repo's checks.
3. **Push**, then confirm the commit is on the PR:
   ```bash
   gh pr view N --json commits --jq '.commits[].oid[0:9]'
   ```
   Never cite a hash that is not in that list (local-only or rebased-away commits
   break the link). Then re-run the repo's merge gate on the new head: a push may reset
   it. Example — superpacks-site runs tests only under the `Run CI` label and requires
   `ci/verified` = success: `gh pr edit N --add-label "Run CI"`, then
   `gh run watch <run id> --exit-status`. Check the repo's AGENTS.md for its gate.
4. **Reply in the thread** — not a top-level PR comment:
   ```bash
   gh api -X POST repos/OWNER/REPO/pulls/N/comments/<first-comment-databaseId>/replies \
     -f body="Fixed in <9-char sha>: <what changed, one or two sentences>. <test/verification if any>."
   ```
5. **Resolve** the thread:
   ```bash
   gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"<thread id>"}){thread{isResolved}}}'
   ```
6. **Re-read** the thread list; the count of open threads you addressed must be zero.

## Reply shapes

| Situation | Reply | Resolve? |
|---|---|---|
| Fixed | `Fixed in abc123def: <what changed>. <test added / check that now passes>.` | Yes |
| Already fixed by an earlier commit (review ran on an older head) | `Already fixed in abc123def (pushed after this review): <what changed>.` | Yes |
| Won't change | `Not changing: <reason, with the rule or fact behind it>.` | No — leave it for the reviewer to accept |
| Needs a human decision | `Needs <owner>'s call: <the question>.` | No |

Be specific: name the function, the test, the check. "Addressed" or "done" alone is
not a reply.

## Rules

- **Do not ask before replying.** Invoking this skill, or asking to fix review
  comments, authorizes the reply and the resolve on every thread you fixed. Ask only
  before posting anything else (a top-level PR comment, a reply to a thread you did
  not address).
- Iterate thread ids with `while read -r t; do …; done` rather than `for t in $ids`:
  zsh does not word-split an unquoted variable, so the loop runs once with all ids.
- Never resolve a thread you did not address, and never resolve a "won't change" or
  "needs a decision" thread yourself.
- Copilot re-reviews do not reopen resolved threads; if a new review raises the same
  point, reply in the new thread with the same hash.
- The reply is data for the reviewer, not a status report for the user; tell the user
  separately which threads you replied to and resolved, with links.
