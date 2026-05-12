---
name: wrap-up
description: Session-end checklist. Stops in-flight agents, checks git state, builds clean, commits everything with a descriptive message, pushes. Reports ready-to-end state.
version: 1
---

# /wrap-up — end-of-session cleanup

When the user runs `/wrap-up`, do this. The goal: leave the repo in a known-clean, pushed state so the next session can pick up cold.

## 1. Stop in-flight agents

- Check for any background agents still running in this session.
- For each one: `TaskStop` it. Do NOT wait for completion — the user has signalled session end.
- If an agent was mid-edit and left a file dirty, that's fine — the file state will get committed below as-is. Note this in the report.

## 2. Build + sanity check

- Run `npm run build` from the project root.
- If it fails: tell the user, fix the surface error (likely a syntax issue from an interrupted edit), retry.
- If it still fails after one attempt: abort wrap-up, surface the error, ask the user how to proceed.
- If clean: proceed.

## 3. Stage and inspect git state

- `git status --short` — look at every file.
- Flag any of these as **NOT to commit** (move to the user's attention for veto):
  - Files matching `*.tmp`, `*.bak`, `*.html` (loose HTML at repo root — usually debug artifacts left by agents)
  - Files in `dist/` (build output — gitignored normally, flag if showing)
  - Files with `secrets`, `.env`, `credentials`, `api_key` in path
  - Files larger than 5 MB
- Everything else: stage with `git add -A` (or selective adds if there's a sensitive file to exclude).

## 4. Compose the commit message

- Read `git diff --cached --stat` and the last 5 commits in `git log --oneline` to understand the project's commit style.
- Compose ONE commit covering the session's net work. Format:
  - First line: `<area>: <one-line summary>.` Under 70 chars.
  - Body: bullet list of what changed, grouped by area (charts, canon, skills, data, etc.). One bullet per logical change, not per file.
  - Footer: `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`
- Pass the message via HEREDOC to preserve formatting.

## 5. Commit + push

- `git commit -m "<message>"` via HEREDOC.
- `git push`.
- If push is rejected (remote ahead): `git pull --no-rebase --no-edit`, resolve any conflicts (take MINE for files where the local session was the authoritative editor; take THEIRS for files outside the session's scope; for generated files like `data/site/panel_data/*.json`, prefer regenerating from the pipeline over manual merge), rebuild, push again.
- If push fails for any other reason: surface the error to the user; do NOT force-push.

## 6. Memory check

- Look for any **durable rules** the user codified in this session that haven't been written to memory yet. Common patterns:
  - "Let's always X" / "Don't ever Y" / "From now on Z"
  - User explicitly approved an unusual approach without pushback
  - User corrected a recurring mistake and the correction generalizes
- For each: write a memory note to `C:\Users\jayzh\.claude\projects\C--Users-jayzh-projects-macro-research-department\memory\` and add an index entry to `MEMORY.md`.
- Do NOT manufacture memory notes from session ephemera (this-session task state, in-progress decisions, etc.).

## 7. Report

End with a tight status block:

- `committed: <commit hash> — <one-line summary>`
- `pushed: <branch> → origin/<branch>`
- `agents stopped: <count>` (if any)
- `memory notes added: <count>` (if any)
- `flagged for veto: <files>` (if anything was excluded from commit and needs the user's call)
- One closing line: `ready to end session.` OR `cannot end cleanly — <reason>.`

No recap of the session, no "let me know if you want me to..." closer.

## Voice constraints

- Cap response at ~300 tokens.
- No math symbols in prose.
- Match the standing tracker register.
