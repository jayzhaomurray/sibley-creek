"""Drift watcher for published deep dives.

Compares the load-bearing numeric claims as cited in published deep dives
against the current pipeline data. Surfaces drift so the editorial team
can decide whether a pillar needs a re-review.

Deep dives are DATED snapshots; this module does NOT auto-refresh them.
It only flags claims whose underlying data has moved beyond a per-claim
threshold since publication.

Entry point: ``python -m pipeline.drift.watcher``.
"""
