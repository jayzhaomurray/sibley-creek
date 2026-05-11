/**
 * URL helper for base-path-aware internal links.
 *
 * Astro's `base` config (in astro.config.mjs) prepends a path prefix to
 * built assets and Astro-managed routes, but raw `<a href="/foo/">` tags
 * are NOT auto-rewritten - they remain root-relative and break at
 * `username.github.io/sibley-creek/`.
 *
 * `withBase(path)` resolves an internal absolute path against the current
 * deployment's base. Same component code works at both:
 *
 *   - GitHub Pages: base = '/sibley-creek' -> withBase('/gdp/') = '/sibley-creek/gdp/'
 *   - Cloudflare Pages w/ custom domain: base = '/' -> withBase('/gdp/') = '/gdp/'
 *
 * The migration to Cloudflare later this week is therefore a single
 * astro.config.mjs edit: drop the `base` line. No component edits required.
 *
 * Pass internal paths with a leading slash; the helper strips it before
 * joining. For external URLs (https://...), do NOT route through this.
 */
const RAW_BASE = import.meta.env.BASE_URL || "/";
const BASE = RAW_BASE.endsWith("/") ? RAW_BASE : `${RAW_BASE}/`;

export function withBase(path: string): string {
  const clean = path.startsWith("/") ? path.slice(1) : path;
  return `${BASE}${clean}`;
}
