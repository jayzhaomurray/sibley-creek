# Auto-blurb pipeline design memo (v1: ARCHIVED)

**Status: superseded by `editorial/auto_blurb_process.md` on 2026-05-11.**

This v1 memo (researcher-authored, single-LLM-centric) is preserved for
reference but is no longer the canonical design. The canonical design
is the multi-agent process in `editorial/auto_blurb_process.md`, which
distributes the editorial work across researcher, writer, fact-checker,
and style-editor rather than collapsing it into a single LLM call plus
mechanical validators.

The v2 process keeps several v1 design decisions intact:

- Calendar-driven scheduling plus content-hash on fetch as the trigger
  (v1 Section 1; v2 carries this forward).
- File-on-disk, edited in VS Code as the human review surface (v1
  Section 3; v2 adds an email notification per user direction).
- File-based, git-as-source-of-truth publish flow (v1 Section 4; v2
  carries this forward).
- Snapshot-the-blurb-to-the-release-date revision policy (v1 Section
  6; v2 carries this forward).

The v2 process replaces v1 in:

- Single-LLM call replaced by four-agent flow.
- Implicit state replaced by explicit state machine.
- Open-question notification surface resolved to email.
- Failure-mode "re-prompt" replaced by retry-budgeted re-routes
  between named agents.

The historical v1 memo text follows below for reference.

---

(historical v1 content preserved; see git history for full original;
this archive note replaces the in-place content to avoid confusion
about which file is canonical. The full v1 memo lives in the
2026-05-11 commit prior to this one. To inspect: `git log --
research/auto_blurb_pipeline_design.md` then `git show <sha>:
research/auto_blurb_pipeline_design.md`.)
