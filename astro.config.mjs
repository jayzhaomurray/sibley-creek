// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
//
// site: the canonical production origin. Used by Astro for absolute
//   URLs (canonical, OG image, sitemap). Placeholder until the domain
//   is committed; mirrors src/data/sections.ts `site.url`.
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
  site: 'https://example.invalid',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
});
