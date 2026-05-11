// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
//
// site: canonical production origin (custom domain at sibleycreek.ca).
//   Used by Astro for absolute URLs (canonical, OG image, sitemap).
//
// base: not set. The site serves from root at https://sibleycreek.ca/
//   thanks to the GitHub Pages CNAME -> public/CNAME pointer. Internal
//   links route through src/lib/urls.ts `withBase()`, which becomes a
//   no-op when base is unset (returns the path unchanged). Same component
//   code works at root here and on any future Cloudflare Pages migration.
//
// trailingSlash: 'always' — matches the in-page nav (we link to
//   "/gdp/" not "/gdp") so canonical and link href stay aligned and we
//   avoid 308 hops in production.
//
// build.format: 'directory' — every page emits as /path/index.html,
//   which pairs with trailingSlash=always for clean URLs.
//
// Keep this file minimal. Integrations (sitemap, mdx, etc.) get added
// here when there is a concrete reader-facing reason — not preemptively.
export default defineConfig({
  site: 'https://sibleycreek.ca',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
});
