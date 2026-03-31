---
name: post-slack-msg
description: Use when about to call slack_send_message, slack_send_message_draft, or slack_schedule_message — guards every Slack post with claim verification, sensitive data scanning, and independent Codex review before sending
---

# Post Slack Message

## Overview

**Mandatory gate before every Slack message.** Verify claims, scan for sensitive data, confirm destination, and get independent Codex review before posting anything to Slack.

## When to Use

**Every time** you are about to call `slack_send_message`, `slack_send_message_draft`, or `slack_schedule_message`. No exceptions.

## The Gate

```dot
digraph slack_gate {
    "About to post Slack message" [shape=doublecircle];
    "Did user ask for this?" [shape=diamond];
    "STOP - don't post" [shape=box, style=filled, fillcolor="#ffcccc"];
    "Draft the message" [shape=box];
    "Fast path eligible?" [shape=diamond];
    "Sensitive data scan" [shape=diamond];
    "Remove/redact sensitive data" [shape=box];
    "Message has factual claims?" [shape=diamond];
    "Were claims already /verified?" [shape=diamond];
    "Run /verify on claims" [shape=box];
    "Dispatch Codex reviewer" [shape=box];
    "Show draft + destination to user" [shape=box];
    "User approves?" [shape=diamond];
    "Post message" [shape=box, style=filled, fillcolor="#ccffcc"];

    "About to post Slack message" -> "Did user ask for this?";
    "Did user ask for this?" -> "STOP - don't post" [label="no"];
    "Did user ask for this?" -> "Draft the message" [label="yes"];
    "Draft the message" -> "Fast path eligible?";
    "Fast path eligible?" -> "Show draft + destination to user" [label="yes"];
    "Fast path eligible?" -> "Sensitive data scan" [label="no"];
    "Sensitive data scan" -> "Remove/redact sensitive data" [label="found"];
    "Remove/redact sensitive data" -> "Message has factual claims?";
    "Sensitive data scan" -> "Message has factual claims?" [label="clean"];
    "Message has factual claims?" -> "Were claims already /verified?" [label="yes"];
    "Message has factual claims?" -> "Dispatch Codex reviewer" [label="no claims"];
    "Were claims already /verified?" -> "Dispatch Codex reviewer" [label="yes, skip verify"];
    "Were claims already /verified?" -> "Run /verify on claims" [label="no"];
    "Run /verify on claims" -> "Dispatch Codex reviewer";
    "Dispatch Codex reviewer" -> "Show draft + destination to user";
    "Show draft + destination to user" -> "User approves?";
    "User approves?" -> "Post message" [label="yes"];
    "User approves?" -> "Draft the message" [label="no, revise"];
}
```

## Instructions

### Step 1: Confirm User Intent

Before anything else — did the user explicitly ask you to post this message? Not implied, not "would be helpful", not proactive. **Explicitly asked.**

If no: stop. Do not post. Do not ask "would you like me to post this?" unprompted.

### Step 2: Draft the Message

Write the full message text and identify:

- **Destination:** channel name/ID, thread timestamp (if reply)
- **Recipients:** any @mentions or DM targets

**Resolve channel ID:** Use `slack_search_channels` to resolve the channel name to an ID. Do not rely on channel names alone — duplicates exist and names can be misleading. Confirm the channel description/topic matches the intended destination.

### Step 3: Fast Path Check

If ALL of the following are true, skip to Step 8 (present to user):

- Message is under 50 words
- Contains zero factual claims about code, architecture, or services
- Contains no data that could be sensitive (no URLs, hostnames, IPs, keys, names)
- Is purely social/coordination (e.g., "PR is up for review", "joining the meeting late", "thanks!")

If any condition fails, continue with the full gate.

### Step 4: Sensitive Data Scan

Scan the draft for anything that looks sensitive:

| Category           | Examples                                                 |
| ------------------ | -------------------------------------------------------- |
| **Credentials**    | Passwords, API keys, tokens, connection strings          |
| **Infrastructure** | Internal hostnames, IPs, ports, DB names                 |
| **Personal**       | Performance reviews, salary, personal contact info       |
| **Business**       | Revenue numbers, unreleased product names, legal matters |
| **Auth artifacts** | Session tokens, cookies, JWTs, OAuth codes               |

If found: redact and replace with safe alternatives (e.g., "credentials are in Vault under `payments/prod`"). Tell the user what you removed and why.

**Do not dismiss infrastructure details as "low risk".** Internal hostnames, DB table names, cache technologies — flag them to the user and let them decide. Your job is to surface, not to judge risk.

### Step 5: Verify Factual Claims

**Skip this step if claims in the message were already verified with /verify earlier in this conversation.**

If the message contains factual claims about code, architecture, services, or behavior:

1. Extract each verifiable claim
2. Invoke /verify on those claims
3. If any claim is REFUTED or PARTIALLY TRUE — correct the message before proceeding
4. If UNCERTAIN — flag to the user and let them decide whether to include

### Step 6: Codex Independent Review

Dispatch Codex to independently review the message and destination:

```
Agent tool:
  subagent_type: "codex:codex-rescue"
  prompt: |
    --fresh --model spark
    Review this Slack message for issues before posting.

    MESSAGE:
    <paste full message text>

    DESTINATION: <channel/DM + thread if applicable>
    CONTEXT: <1-2 sentences on what the conversation was about>

    Check for:
    1. Wrong audience — is this message appropriate for this channel/person? Would it make sense to someone reading the channel?
    2. Tone mismatch — too casual for an incident channel? too formal for team chat? off-putting?
    3. Missing context — would readers need background to understand this? Are there implicit references that won't land?
    4. Anything else that looks off

    Note: Sensitive data and factual claims have already been checked. Focus on audience, tone, and clarity.

    Report: List any issues found, or confirm 'No issues found' if clean.
  run_in_background: true
  name: "codex-slack-review"
```

Read the rescue subagent's output. If issues found, fix them before proceeding.

**Codex fallback:** If the rescue subagent returns a failure (Codex unavailable), use a Claude subagent with the same review prompt.

If the rescue subagent failed, note it in the verification summary but don't block the post — the other checks still ran.

### Step 7: Present to User for Approval

Show the user:

```
**Posting to Slack:**
- Channel: #channel-name (or DM to @person)
- Thread: [if applicable]

**Message:**
> [full message text]

**Verification:**
- Sensitive data scan: Clean / [issues found and fixed]
- Claim verification: [verified/skipped/corrected]
- Codex review: [clean/issues fixed/unavailable — other checks passed]

Send this?
```

**Do NOT post until the user explicitly approves.** "Looks good", "yes", "send it" = approval. Silence or ambiguity = do not send.

**On revision:**

- **Minor edits** (wording, formatting, typos): re-run only Step 4 (sensitive data scan). Skip claim verification and Codex review.
- **Substantive changes** (new claims, different audience, added technical details): re-run Steps 4-6 (sensitive scan, verify, Codex review).

### Step 8: Post

Only now call the Slack tool.

## Red Flags — You're Skipping the Gate

| Thought                               | Reality                                                           |
| ------------------------------------- | ----------------------------------------------------------------- |
| "User said send it, I should be fast" | Speed doesn't matter. Accuracy does. Run the gate.                |
| "It's just a simple message"          | Simple messages leak credentials too. Run the gate.               |
| "I already checked mentally"          | Mental checks miss things. Use Codex.                             |
| "Codex is overkill for this"          | Codex takes 15 seconds. Undoing a bad Slack post takes forever.   |
| "The user will see it before I send"  | Step 7 is showing them. Steps 1-6 catch things they won't notice. |
| "I already verified the claims"       | Great — then Step 5 is a no-op. Still run Steps 4 and 6.          |
| "This is a draft, not a real post"    | Drafts become posts. Gate applies to drafts too.                  |

## Common Mistakes

| Mistake                                           | Fix                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------- |
| Posting without user explicitly asking            | Step 1 is non-negotiable. User must ask.                                  |
| Skipping Codex because "message is simple"        | Always run Codex. It catches what you miss.                               |
| Re-verifying already-verified claims              | Check conversation history. If /verify ran, skip Step 5.                  |
| Showing draft without verification results        | User needs to see what checks were done (Step 7 format).                  |
| Posting to wrong channel because name was similar | Verify channel ID, not just name. Use `slack_search_channels` to confirm. |
| Running full 8-step gate for "thanks!" messages   | Use the fast path for trivial social/coordination messages.               |
| Re-running all checks on minor wording tweaks     | Minor edits only need sensitive data re-scan.                             |
| Not resolving channel ID before posting           | Always use `slack_search_channels` to confirm channel ID.                 |
