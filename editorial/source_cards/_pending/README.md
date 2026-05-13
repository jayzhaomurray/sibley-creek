# Pending verification queue

This directory holds candidate source cards that have NOT yet been
approved for live publication. Cards land here when a researcher's
verification chain to a primary source cannot be closed by AI alone —
either because the primary is unreachable (WAF block, PDF binary, JS
page) or because the citation is a Mode 3 analysis citation that
requires explicit user approval.

The build-time gate refuses to ship any card while its YAML lives in
this directory.

## Directory structure

```
_pending/
  <draft-slug>/                       # one subdir per draft in flight
    <claim-id>.yaml                   # one file per pending card
```

`<draft-slug>` corresponds to a markdown file in
`editorial/drafts/_holding/<draft-slug>.md`. `<claim-id>` is the
stable slug for the claim, used as a `[CLAIM-PENDING:<claim-id>]`
placeholder in the holding draft until the card is approved.

## File schema

```yaml
id: <claim-id>
title: "..."
url: "..."                           # would-be primary
proposed_claim: "<the exact prose tokens the writer wants to use>"
proposed_surface: "<file:plate or sidecar phrase the claim lands in>"

# Tier B and Tier C cards include the triangulation block:
triangulation:
  - source: "MLT Aikins client alert, Nov 2025"
    url: "https://..."
    excerpt: "verbatim quote from the secondary..."
    credibility: "Top-tier Canadian immigration law firm; reproduces GoC text under client-liability discipline"
  - source: "..."
    url: "..."
    excerpt: "..."
    credibility: "..."

# Mode 3 cards include the frame-test field:
mode: 3                              # only on Mode 3 cards
frame_test_check: "'CIBC argues that StatCan undercounts the population' framing preserved in dive prose at line X"

# Set at promotion time (by approve-claim CLI):
user_confirmed_at: null              # ISO date when user approved (Tier B/C)
user_confirmed_by: null              # user handle
user_approved_at: null               # ISO date when user approved (Mode 3)
user_approved_by: null               # user handle

verification_tier: "B"               # A | B | C
status: pending_user                 # pending_user | approved | rejected
```

## Workflow

1. **Researcher hits an unreachable primary.** Produces a candidate
   YAML in this directory with the claim, the would-be primary, and
   the triangulation block. Status is `pending_user`.
2. **Writer drafts the surrounding prose** in
   `editorial/drafts/_holding/<draft-slug>.md`, with the claim
   represented as `[CLAIM-PENDING:<claim-id>]`. The rest of the
   draft is finished prose minus the unverified claim.
3. **User opens the verification view** at
   `editorial/source_cards/audit/_verify/<draft-slug>.html`,
   reviews the candidate card alongside the draft prose, walks
   the secondary sources, attempts the primary in a browser, and
   marks Approve / Reject / Not yet verified.
4. **User exports decisions** via the button in the verification
   view — copies a multi-line shell script to clipboard.
5. **User pastes into PowerShell** or runs through Claude Code:
   `npm run approve-claim <draft-slug>:<claim-id>` for approvals,
   `npm run reject-claim ...` for rejections.
6. **approve-claim** moves the YAML from `_pending/` to
   `editorial/source_cards/registry.yaml`, fills `user_confirmed_at`
   + `user_confirmed_by`, then runs the splice pass that replaces
   `[CLAIM-PENDING:<claim-id>]` in the holding draft with the
   approved claim text.
7. **reject-claim** deletes the YAML, replaces the placeholder in
   the draft with a `[CLAIM CUT: see reject log]` marker, and
   logs the rejection.

See `editorial/review_protocol.md` for the full tier discipline.

## What the gate enforces

`scripts/check_citation_coverage.mjs` refuses:

- Any `card:<id>` reference whose YAML lives in `_pending/`
- Any Tier B/C card without `user_confirmed_at` filled
- Any Mode 3 card without `user_approved_at` filled

So a draft can only ship once every pending citation in it has been
resolved by user decision — either approved (claim splices in) or
rejected (claim cuts).
