# Sibley News Feed Worker

Cloudflare Worker that powers the "What we're reading" section on
`/overview-ff/`. Aggregates Google News RSS across a curated list of
Canadian macro reporters (quoted-name queries), merges + dedupes by
URL, returns the top items as JSON.

Worker code: `src/index.js` (~150 lines, zero dependencies).

## Why a Worker?

Google News RSS doesn't send permissive CORS headers — a browser at
`sibleycreek.ca` can't fetch `news.google.com/rss/search?...` directly.
The Worker fetches server-side, caches at the edge, returns
CORS-friendly JSON. Also keeps the reporter list + query logic out of
the public-facing JS.

## One-time deployment (Jay)

This needs to happen once before the news feed renders on the live
site. After it's set up, every push picks up worker changes via
`wrangler deploy`.

### 1. Cloudflare account

If you don't already have a Cloudflare account, sign up at
<https://dash.cloudflare.com/sign-up>. The Workers free plan handles
100 000 requests/day — far past anything Sibley will hit. No payment
method required.

### 2. Local toolchain

```powershell
cd workers/news-feed
npm install
```

### 3. Authenticate wrangler

```powershell
npx wrangler login
```

A browser window opens, you sign into Cloudflare, click Allow. After
that, wrangler has API credentials locally (stored in
`~/.wrangler/config/`).

### 4. Deploy

```powershell
npx wrangler deploy
```

wrangler prints the deployed Worker URL — something like:

```
Published sibley-news-feed (5.2 sec)
  https://sibley-news-feed.YOUR-SUBDOMAIN.workers.dev
```

Copy that URL.

### 5. Wire the page to the Worker

Open `src/pages/overview-ff.astro` and find the `WORKER_URL` constant
near the top of the `<script>` tag. Replace the placeholder with the
URL from step 4. Commit + push — the live site now fetches from your
Worker.

## Updating the reporter list

Edit `REPORTERS` at the top of `src/index.js`. Names are exact-match
queries (`"Erik Hertzberg"`) — they catch the reporter's bylines plus
the occasional in-body mention (~5% noise).

After editing:

```powershell
npx wrangler deploy
```

No site rebuild needed — the Worker change is live in seconds.

## Cost

Free tier covers everything Sibley needs. Worker invocations are bound
by:

- Reader page loads (cached at edge: 60 s window)
- Per-reporter RSS fetches (cached at edge: 15 min window)

A busy day on `/overview-ff/` (say 1 000 page loads) triggers at most
~1 440 Worker invocations (1/min from cache misses) and ~14 RSS fetches
per 15 min × 14 reporters × 96 windows = ~18 000 fetches/day under
worst case. All well inside the free tier.

## Debugging

Tail live logs (Wrangler):

```powershell
npx wrangler tail
```

Force-refresh the cache (call the Worker with a Cloudflare bypass
header isn't free — easier path is just to wait for the 60 s page-cache
to expire, then a fresh request).
