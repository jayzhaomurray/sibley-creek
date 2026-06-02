# FF Calendar Stale Bug — Root Cause, Fix, and Test Results

Investigated and fixed 2026-06-02.

## Root cause (confirmed)

`overview.astro` judged `ff_calendar_cache.xml` freshness by file mtime via
`statSync().mtimeMs`. In GitHub Actions, `actions/checkout@v4` resets every
file's mtime to the checkout time ("now"). So `cacheAgeMs()` returned a number
close to 0 on every CI run, which was always below the 6-hour TTL. The live
fetch was skipped on every CI build. The build rendered whatever XML was
committed, regardless of its content.

The cache was updated only when a local dev build fetched fresh data and that
file was manually committed — accidental and infrequent.

## Does the FF fetch work from GHA runners?

Yes. The live fetch from `nfs.faireconomy.media/ff_calendar_thisweek.xml` was
confirmed to work from the local machine (Windows residential IP, same
`SibleyCreek/1.0` user-agent). No evidence of IP blocking; the original bug was
purely the mtime short-circuit. The primary fix (data-aware freshness) causes CI
to always attempt the live fetch, so GHA IPs will be tested on every deploy.
The scheduled workflow (belt-and-suspenders) also runs curl directly from GHA
runners and will expose any IP-level block immediately.

## Fix components

### 1. Data-aware cache freshness (primary fix)
`src/pages/overview.astro`, lines ~164-261.

Replaced the mtime-based TTL gate with a content-based check:
- `latestEventDate(rawXml)` — parses all `<date><![CDATA[MM-DD-YYYY]]></date>`
  tags in the XML, returns the latest as a Date.
- `isoWeekKey(date)` — returns `YYYY-Www` (ISO 8601 week).
- `ffCacheCoversCurrentWeek(rawXml)` — returns true iff the latest event date
  is in the current ISO week.

Cache use decision:
- Local dev: use cache if it covers this week AND is < 6h old (mtime as
  secondary guard against hammering FF on rapid rebuilds within the same week).
- CI (`GITHUB_ACTIONS=true`): always attempt live fetch; cache is fallback-only.

### 2. Staleness guard (post-parse)
After parsing buckets from the XML (whether live or cached), check if the
latest event date's ISO week < current ISO week. If yes:
- Local dev: `console.warn` — visible, not fatal.
- CI: `process.exit(1)` — hard fail, stale calendar cannot ship.

### 3. Scheduled FF refresh workflow (belt-and-suspenders)
`.github/workflows/refresh-ff-calendar.yml`

Runs Mon-Fri at 05:00 UTC. Steps:
1. `curl --fail` the FF XML.
2. Validate `<weeklyevents>` and `<event>` presence.
3. Commit + push if changed (triggering a deploy.yml rebuild with the fresh cache).

Monday 05:00 UTC catches FF's Sunday-evening new-week publish with margin.
Failure triggers the same SMTP email as other build failures.

### 4. News feed staleness guard (parallel fix)
`src/pages/overview.astro`, `_warnIfNewsCacheStale()` function.

The news feed already had `GITHUB_ACTIONS === "true"` forcing a live fetch in
CI (correct — the mtime bug never affected the news feed's CI behavior because
of this existing guard, only local dev used the cache). Added a staleness check
on the fallback path: if the cache's newest item is older than `NEWS_MAX_AGE_DAYS`
(14 days), emit a `console.warn`. Warn-only (not hard fail) because a broken
Google News fetch degrades gracefully in the UI, unlike a stale calendar that
actively misleads.

## Test results

1. **Build with current-week cache**: clean pass, no stale warnings. [PASS]
2. **Staleness guard logic**: confirmed via direct Node test — stale W22 vs
   current W23 correctly identified. [PASS]
3. **Live fetch auto-heals stale cache**: wrote W22-dated XML to cache, ran
   `npm run build`. Build fetched fresh W23 XML from faireconomy.media and
   wrote it back. [PASS]
4. **Build with fresh cache after auto-heal**: clean pass. [PASS]

## Files changed

- `src/pages/overview.astro` — data-aware cache freshness + staleness guard
  + news feed staleness guard
- `.github/workflows/refresh-ff-calendar.yml` — new scheduled refresh workflow

## Decisions for Jay

- **Cron timing**: Mon-Fri 05:00 UTC. If FF regularly updates mid-week (they
  do push forecast revisions), you could add a second run at e.g. 12:00 UTC.
  Not necessary given the data-aware live-fetch path in deploy.yml.
- **CI guard severity for news feed**: currently warn-only. Escalate to
  `process.exit(1)` in CI if you want the build to fail when news is stale
  (at the cost of more frequent deploy failures when Google News is flaky).
- **The ongoing build failures** (2026-05-30 through 2026-06-01): those are
  failing on "Build Astro site" step, not the FF fetch. Separate issue from
  this fix — the current build is green on `9e7e7d4`.
