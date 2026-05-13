# Holding drafts — pre-verification writer output

This directory holds writer drafts whose claims have NOT yet all been
approved by the user. A draft lands here when the writer has finished
the section / dive prose but at least one citation in it depends on a
Tier B / Tier C / Mode 3 card that's still in the pending queue at
`editorial/source_cards/_pending/`.

## Placeholder convention

Where the writer needs to use an unverified claim, the draft includes
a placeholder of the form:

```
[CLAIM-PENDING:<claim-id>]
```

where `<claim-id>` matches the filename of the corresponding YAML in
`editorial/source_cards/_pending/<draft-slug>/<claim-id>.yaml`.

Three writer patterns:

1. **Cut and continue.** If the claim isn't load-bearing, the writer
   simply doesn't include it. No placeholder; the draft ships
   without the claim. No file in this directory needed.
2. **Placeholder and continue.** If the claim is meaningful but the
   surrounding prose can stand without it, the writer drops the
   `[CLAIM-PENDING:<claim-id>]` marker and writes the rest. The
   placeholder later splices in approved claim text via the
   `npm run approve-claim` CLI.
3. **Halt.** If the claim is so load-bearing that the section
   collapses without it, the writer halts the section, leaves a
   note explaining the structural dependency, and waits. Rare; a
   signal the dispatch was too tightly scoped to thin-source claims.

## What gets rendered where

`editorial/source_cards/audit/_verify/<draft-slug>.html` is the
user-facing verification view. It renders the holding draft prose
with amber inline highlights for each `[CLAIM-PENDING:<claim-id>]`
marker, and a sidebar of pending-card cards with three-state radios
(Not yet verified / Approve / Reject) and an export-decisions button.

After every claim in a draft has been either approved (claim splices
in) or rejected (claim cuts), the holding draft is consumed: the
final prose moves to `editorial/published/<slug>.md` (for dives) or
to its destination Astro page (for plate blurbs, section abstracts).
The holding file is deleted.

## Where this fits in the auto-blurb pipeline

For lighter cycles (plate-blurb refreshes, splash tile lines), the
writer typically uses only existing approved cards + pipeline data,
so nothing lands in `_holding/`. The cycle completes inline and
the auto-blurb cycle's output is directly applied.

For heavier cycles (research dive drafts), the writer routinely
introduces new card-eligible claims. Those land here until
verified.
