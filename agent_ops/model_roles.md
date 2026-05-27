# Model Roles

This document defines the default division of labour among AI models.

## Coordinator: Codex / GPT-5.5

The coordinator is responsible for the operating process, not for being automatically right.

Responsibilities:

- classify task risk as R0, R1, R2, or R3;
- create or update task briefs;
- choose the workflow;
- assign worker and reviewer roles;
- inspect files and repo state;
- implement code changes when appropriate;
- run deterministic checks;
- reconcile competing model outputs;
- produce the final summary or referee memo.

The coordinator should avoid relying on model memory when a file contract can exist.

## Claude

Claude remains in the loop as a specialist, not as the control plane.

Good Claude roles:

- independent research analyst;
- red-team critic;
- prose and style reviewer;
- alternative framing generator;
- source coverage reviewer;
- argument stress tester.

Claude should receive explicit assignments with allowed files, forbidden files, and expected output. Claude should not silently mutate project state or act as the sole source of truth.

## Gemini, If Added

Gemini should not be added as another coequal coordinator. If used, it should have bounded roles:

- long-context document review;
- third-opinion audit for R3 work;
- source comparison;
- external sanity check;
- "what did both other models miss?" review.

## Referee Principle

For R2 and R3 work, raw disagreement is not the final product. The coordinator must synthesize:

- what survives;
- what is disputed;
- what is probably wrong;
- what should be cut;
- what Jay should do next.

The synthesis should cite artifacts and files, not model prestige.
