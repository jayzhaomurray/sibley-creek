# /check-sources

Probes `editorial/source_cards/registry.yaml` for stale source-card entries. Same script the weekly cron runs, but on demand.

When the user runs `/check-sources`, do this:

1. Run `node scripts/check_sources.mjs --report` from the repo root.
2. Read the report from stdout. The script also writes `editorial/source_cards/report-YYYY-MM-DD.md` — that file is gitignored if the user prefers; otherwise let it commit.
3. Summarize the findings in ~150 tokens:
   - How many PAST-DUE entries (publication's `next_expected` date has passed).
   - How many NEWER-VINTAGE-MAYBE hints (probe-URL response contains a date newer than the entry's `verified_at`).
   - Name the specific entries flagged.

4. For each PAST-DUE entry, propose the next action:
   - If the user wants, dispatch `researcher` to WebFetch the entry's `currency_probe_url`, identify whether a new vintage has actually shipped, and re-verify the entry's values against the new publication.
   - If a new vintage is confirmed, the researcher's output should propose the registry update (new `url`, `verified_value`, `verified_at`, `vintage_label`, `next_expected`).

5. For NEWER-VINTAGE-MAYBE hints, note them but don't auto-dispatch — these are imprecise and often false positives (listing-page noise, archived dates, etc.).

## Voice constraints

- Cap status output at ~150 tokens.
- Don't paste the full report — surface the punch list.
- Don't auto-update the registry. User decides per-entry whether to dispatch.

## When NOT to use

- The cron runs weekly. Don't run /check-sources manually right after a successful cron run unless the user is specifically following up on a flagged entry.
- API-backed series (BoC Valet, StatCan tables, FRED) aren't in the registry — pipeline catches their staleness. /check-sources only covers PDF/HTML publications.
