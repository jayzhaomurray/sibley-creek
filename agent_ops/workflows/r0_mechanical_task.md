# R0 Mechanical Task Workflow

Use this for low-risk, reversible, deterministic work.

## When To Use

- build failures;
- component fixes;
- file organization;
- simple scripts;
- mechanical refactors;
- formatting cleanup;
- small documentation updates.

## Process

1. Identify the exact files involved.
2. Inspect only the relevant files.
3. Make the smallest reasonable change.
4. Run deterministic checks when practical.
5. Summarize what changed and what was verified.

## Required Output

- files changed;
- checks run;
- any checks not run;
- residual risk, if any.

## Do Not

- escalate to multi-model review unless the task touches reader-facing claims, data methodology, or irreversible project structure;
- reorganize broad folders without an explicit brief;
- edit unrelated files encountered during inspection.
