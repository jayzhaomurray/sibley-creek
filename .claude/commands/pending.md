---
name: pending
description: Surface decisions made in this conversation that haven't been triggered yet, then dispatch them. Also resurface open questions the user was asked but never answered. Short bullet list, then fire.
version: 2
---

# /pending — resurface and trigger

When the user runs `/pending`, do this. Keep it terse — bullet output, no preamble, no recap of how you found things.

## 1. Scan the conversation

Two scans, two output sections.

**Scan A — pending actions** (things already decided, not yet fired):

- **Ratified decisions** the user made via `AskUserQuestion` answers, explicit directives ("do X", "let's do Y", "kill that and do Z"), or accepted-without-pushback proposals.
- **Page/chart/page-order changes** the user approved (plate moves, archives to `_alternatives/`, slot renumbers, retires).
- **Canon updates** the user agreed to but haven't been propagated to `design/`, `editorial/`, or `.claude/agents/`.
- **Memory notes** the user codified that haven't been written to the memory dir yet.
- **Edits or refactors** the user asked for but I deferred (e.g. "I'll do that after X lands").

Exclude from Scan A:

- Work already dispatched and **still in flight** — note as `[in flight]`, do not re-fire.
- Work already completed in this session.
- Speculative ideas the user floated but didn't pick.

**Scan B — pending decisions** (asks left hanging on the user):

- **`AskUserQuestion` prompts** I posed where the user replied on a different track without ever picking an option.
- **Direct questions in prose** ("which framing do you want", "OK to swap?", "should I dispatch X or Y") where the user moved on without answering.
- **Audit menus / option lists** I surfaced for the user to select from where the user neither selected nor dismissed (e.g. "20-item swap menu — pick which to swap tomorrow").
- **Veto windows** opened per `feedback_audit_recommendations_need_user_veto.md` that the user neither approved nor rejected.

Exclude from Scan B:

- Questions the user explicitly deferred ("tomorrow", "park it", "later") — still surface them, but mark `[parked: <reason>]` so the deferral is visible.
- Questions the user implicitly answered through subsequent direction (the answer is in their next instruction).
- Rhetorical questions or "want me to..." closers I posed that the user reasonably ignored.

## 2. Surface a tight bullet list

Two sections, each one line per item, max ~20 words per line. Omit a section entirely if empty.

**Pending actions:**

- **<decision>** — <state: ready | blocked-by-X | in-flight> — next: <action>

**Pending decisions (awaiting user):**

- **<question>** — <state: open | parked: <reason>> — needs: <what the user has to pick>

If both sections are empty, say so in one sentence and stop.

## 3. Fire what's ready

For every item marked `ready`:

- Dispatch the appropriate agent (background where it makes sense), or execute the edit directly when it's trivial (file moves, small text trims, memory writes).
- Per the project's standing **dispatch-don't-flag** rule (memory note `feedback_dispatch_dont_flag.md`): act. Don't ask for permission on items the user already ratified.
- Per the **auto-chain** rule: when one step has a natural downstream (data → chart → page reflow), chain them unless they touch the same files concurrently.
- Concurrent-edit safety: if two pending items would both modify `src/pages/<section>.astro`, `src/layouts/SectionLayout.astro`, or `pipeline/io/panel_data.py`, do them sequentially. Concurrent edits on those shared files have caused SSR breakage in past sessions.

For items marked `blocked-by-<X>`:

- Don't fire. Note the blocker.
- If the blocker is an in-flight agent, queue the action mentally for after the agent completes. Do not poll.

## 4. Report

After triggering, output:

- One line per fired item: `dispatched: <description>` or `done: <description>`.
- One line per blocked item still on hold.
- Open-decision items are NOT fired — they surface in the bullet list above and stay there until the user picks. Do not re-ask via `AskUserQuestion` inside `/pending`; just keep them visible.

End. No summary paragraph, no recap, no "let me know if you want me to..." closer.

## Voice constraints (carry forward from project canon)

- No math symbols in any prose — plain variable names only (memory: `feedback_no_math_symbols_in_prose.md`).
- Cap response at ~300 tokens (memory: `feedback_terse_responses.md`).
- No "load-bearing", no canon-jargon in reader-facing output (memory: `feedback_load_bearing_banned.md`).
