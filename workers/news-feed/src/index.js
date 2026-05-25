// Cloudflare Worker — Sibley Creek news feed.
//
// Aggregates Google News RSS results across a curated list of Canadian
// macro reporters (one quoted-name query per reporter), merges + dedupes
// by URL, sorts by pubDate desc, returns the top N items as JSON.
//
// Caching layers:
//   - Per-reporter RSS cache (Cloudflare Cache API): 15 min TTL. Avoids
//     hammering Google News on every Worker invocation.
//   - Page-level merged-result cache: 60 s TTL. Debounces rapid page
//     loads (every visit doesn't re-merge / re-sort).
//
// CORS: Access-Control-Allow-Origin: *. The browser at sibleycreek.ca
// fetches directly from the Worker on page load.
//
// Failure mode: any reporter whose RSS fetch fails is skipped. The
// remaining reporters still return results. Total empty response only
// happens if every reporter fetch fails — extremely unlikely.
//
// Deploy: see workers/news-feed/README.md. The default deployment puts
// the Worker at:
//   https://sibley-news-feed.<your-cf-account>.workers.dev
// which is the URL the Astro page expects (configurable in
// src/pages/overview-ff.astro).

const REPORTERS = [
  "Laura Dhillon Kane",
  "Erik Hertzberg",
  "Nojoud Al Mallees",
  "Brian Platt",
  "Derek Decloet",
  "Paul Vieira",
  "Robb Stewart",
  "Promit Mukherjee",
  "David Ljunggren",
  "Matt Lundy",
  "Mark Rendell",
  "Fergal Smith",
  "Greg Quinn",
  "Kevin Carmichael",
  "Bill Curry",
];

const REPORTER_TTL_SEC = 15 * 60; // 15 min
const PAGE_TTL_SEC = 60;          // 1 min
const TOP_N = 12;

// Google News RSS query URL for a quoted reporter name.
// hl=en-CA, gl=CA, ceid=CA:en pin Canadian English + Canada index.
const newsRssUrl = (reporterName) => {
  const q = `"${reporterName}"`;
  const params = new URLSearchParams({
    q,
    hl: "en-CA",
    gl: "CA",
    ceid: "CA:en",
  });
  return `https://news.google.com/rss/search?${params.toString()}`;
};

// Extract the inner text of <tag>…</tag>, stripping any wrapping CDATA.
// Returns "" if the tag isn't present.
function extractTag(block, tagName) {
  const re = new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\\/${tagName}>`, "i");
  const m = block.match(re);
  if (!m) return "";
  const inner = m[1].trim();
  const cdata = inner.match(/<!\[CDATA\[([\s\S]*?)\]\]>/);
  return (cdata ? cdata[1] : inner).trim();
}

// Parse Google News RSS XML → array of items. Each item carries the
// reporter name we queried for so the page can show "Reporter — Source".
function parseRss(xml, reporter) {
  const items = [];
  const itemRe = /<item>([\s\S]*?)<\/item>/g;
  let m;
  while ((m = itemRe.exec(xml)) !== null) {
    const block = m[1];
    const title = extractTag(block, "title");
    const link = extractTag(block, "link");
    const pubDate = extractTag(block, "pubDate");
    const source = extractTag(block, "source");
    if (!title || !link) continue;
    items.push({ title, link, pubDate, source, reporter });
  }
  return items;
}

// Fetch one reporter's RSS, with edge cache. Returns parsed items array
// (possibly empty on failure — never throws).
async function fetchReporter(reporter, ctx) {
  const cacheKey = new Request(
    `https://sibley-news-cache/reporter/${encodeURIComponent(reporter)}`,
    { method: "GET" },
  );
  const cache = caches.default;
  const cached = await cache.match(cacheKey);
  if (cached) {
    try {
      return await cached.json();
    } catch (_e) {
      // Corrupt cache entry — fall through and refetch.
    }
  }

  let items = [];
  try {
    const res = await fetch(newsRssUrl(reporter), {
      headers: {
        "User-Agent":
          "SibleyCreek-NewsFeed/1.0 (+https://sibleycreek.ca; reporter byline aggregator)",
      },
      // Google News occasionally takes >5s; give it room before failing.
      cf: { cacheTtl: REPORTER_TTL_SEC },
    });
    if (res.ok) {
      const xml = await res.text();
      items = parseRss(xml, reporter);
    }
  } catch (_e) {
    items = [];
  }

  // Write the (possibly empty) result to cache so we don't refetch a
  // failing reporter every 60s — wait for the TTL window.
  const body = new Response(JSON.stringify(items), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": `public, max-age=${REPORTER_TTL_SEC}`,
    },
  });
  ctx.waitUntil(cache.put(cacheKey, body.clone()));
  return items;
}

export default {
  async fetch(request, env, ctx) {
    // Page-level cache. Same response served for any visitor within TTL.
    const pageCacheKey = new Request(
      "https://sibley-news-cache/page-v1",
      { method: "GET" },
    );
    const pageCache = caches.default;
    const cached = await pageCache.match(pageCacheKey);
    if (cached) {
      const headers = new Headers(cached.headers);
      headers.set("X-Cache", "HIT");
      headers.set("Access-Control-Allow-Origin", "*");
      return new Response(cached.body, { headers });
    }

    // Cold cache → fetch all reporters in parallel.
    const settled = await Promise.allSettled(
      REPORTERS.map((r) => fetchReporter(r, ctx)),
    );
    const all = settled.flatMap((s) => (s.status === "fulfilled" ? s.value : []));

    // Dedupe by canonical URL.
    const seen = new Set();
    const deduped = [];
    for (const item of all) {
      if (seen.has(item.link)) continue;
      seen.add(item.link);
      deduped.push(item);
    }

    // Sort newest first.
    deduped.sort((a, b) => {
      const at = Date.parse(a.pubDate) || 0;
      const bt = Date.parse(b.pubDate) || 0;
      return bt - at;
    });

    const top = deduped.slice(0, TOP_N);
    const payload = {
      generatedAt: new Date().toISOString(),
      reporterCount: REPORTERS.length,
      totalCandidates: deduped.length,
      items: top,
    };

    const response = new Response(JSON.stringify(payload), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": `public, max-age=${PAGE_TTL_SEC}`,
        "Access-Control-Allow-Origin": "*",
        "X-Cache": "MISS",
      },
    });
    ctx.waitUntil(pageCache.put(pageCacheKey, response.clone()));
    return response;
  },
};
