# R3 Quantitative and Methodology Workflow

Use this for high-risk quantitative work where AI error could create false confidence.

## When To Use

- predictive models;
- derived indicators;
- proprietary scores;
- causal or regime-break claims;
- statistical validation;
- methodology that may become subscriber-facing.

## Required Spec

Before implementation, define:

- exact research question;
- allowed input files and sources;
- forbidden files or methods;
- sample period;
- train/test or validation design;
- release-lag and vintage assumptions;
- transformation rules;
- output schema;
- success criteria;
- failure criteria.

## Required Process

1. Implementation A is built from the spec.
2. Implementation B or an independent audit is built from the same spec.
3. Each side audits the other.
4. The coordinator reconciles bugs, divergences, and methodology choices.
5. Final results are produced only after known bugs are corrected.
6. The referee memo states what can and cannot be trusted.

## Required Artifacts

- spec;
- implementation code;
- results;
- intermediate outputs sufficient for reconciliation;
- audit reports;
- corrected second version when bugs are found;
- referee decision.

## Minimum Checks

- no hold-out leakage;
- no future information in transformations;
- no fitting of imputers, scalers, selectors, or hyperparameters on hold-out data;
- explicit handling of overlapping horizons;
- walk-forward or time-aware validation;
- exact split dates;
- reproducible random seeds;
- saved selected variables and score vectors;
- sensitivity checks for surprising findings.

## Interpretation Rule

If two correct-looking implementations diverge materially, the result is not trusted until the divergence is explained.
