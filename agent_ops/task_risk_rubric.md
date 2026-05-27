# Task Risk Rubric

Every non-trivial task should be classified before work starts.

## R0: Mechanical Task

Use one model.

Examples:

- fix a build error;
- update a component;
- rename or organize files;
- run a test;
- apply a clear style rule;
- perform a mechanical refactor.

Required checks:

- inspect relevant files;
- make scoped changes;
- run available deterministic checks when practical;
- summarize files changed.

## R1: Routine Editorial or Analytical Task

Use one model plus the existing editorial gates.

Examples:

- release blurb from already processed data;
- chart caption;
- dashboard paragraph;
- standard section update;
- routine source-backed explanation.

Required checks:

- fact-check numbers, dates, and claims;
- apply Sibley Creek style;
- confirm surface fit;
- avoid unsupported causal language.

## R2: Important Research Judgment

Use builder plus red-team reviewer.

Examples:

- deep-dive thesis;
- important interpretation of ambiguous data;
- choice of framing for a flagship piece;
- chart that carries a central claim;
- analysis where an alternative explanation is plausible.

Required artifacts:

- task brief;
- claim cards for central claims;
- builder memo;
- red-team audit;
- referee memo.

## R3: High-Risk Quantitative or Methodological Work

Use independent implementations or independent analytical tracks, cross-audit, and referee synthesis.

Examples:

- predictive model;
- derived score or index;
- regime-break claim;
- causal claim;
- subscriber-facing signal;
- methodology that could drive product decisions.

Required artifacts:

- exact spec;
- allowed data list;
- split and lag assumptions;
- output schema;
- implementation A;
- implementation B or independent audit;
- cross-audit;
- referee decision;
- reproducibility files.

## Escalation Triggers

Escalate one level when:

- the result is surprising;
- the result would be embarrassing if wrong;
- the task uses non-primary sources;
- there is no deterministic test;
- the model claims alpha, causality, or regime change;
- the analysis will appear in a flagship or subscriber-facing product.

## De-Escalation Triggers

Do not overuse adversarial workflows when:

- the task is reversible;
- errors are caught by build tests;
- the output is not reader-facing;
- the change is mechanical;
- the task has an existing deterministic protocol.
