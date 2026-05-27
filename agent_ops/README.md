# Agent Operations

This folder is the model-neutral operating layer for Sibley Creek.

It does not replace `CLAUDE.md`, `STATUS.md`, `editorial/`, `pipeline/`, or `work/`. It sits above them and defines how AI agents should be assigned, reviewed, and reconciled.

## Core Rule

No model is trusted because of its name. A model is trusted only when it works inside a written task contract, leaves auditable artifacts, and passes the appropriate review gates.

## Default Roles

- Codex / GPT-5.5: coordinator, implementation lead, repo navigator, referee, and final synthesizer.
- Claude: specialist drafter, research analyst, red-team reviewer, prose/style reviewer, and alternative-framing generator.
- Gemini, if added later: third-opinion reviewer, long-context document reviewer, and external-source sanity checker.

The coordinator owns task classification and final synthesis. Other models may disagree, but raw disagreement should be converted into a short referee memo before it reaches Jay.

## Folder Map

```text
agent_ops/
  README.md
  model_roles.md
  task_risk_rubric.md
  active/
    README.md
    index.md
  workflows/
    r0_mechanical_task.md
    r1_editorial_task.md
    r2_research_cell.md
    r3_quant_methodology.md
  templates/
    task_brief.md
    model_assignment.md
    red_team_audit.md
    referee_memo.md
    handoff_note.md
    claim_card.md
```

## How Jay Uses This

1. Start new work by asking the coordinator to classify the task risk level.
2. The coordinator creates or updates a task brief.
3. The coordinator decides whether a second model is needed.
4. Worker models write assigned artifacts, not free-form project state.
5. The coordinator produces one decision memo or implementation summary.
6. Jay reads the synthesis, not every raw model output.

## Escalation Rule

Use adversarial multi-model work only when the claim, code, or methodology is high consequence.

Escalate to R2 or R3 when a task involves:

- a central reader-facing claim;
- new derived methodology;
- predictive modelling;
- causal inference;
- surprising results;
- uncertain source interpretation;
- subscriber-facing signal, score, ranking, or framework.

Do not escalate routine site work, copyedits, mechanical refactors, or normal release blurbs unless they affect a central claim.
