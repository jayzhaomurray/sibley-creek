// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
//
// site: the canonical production origin. Used by Astro for absolute
//   URLs (canonical, OG image, sitemap). Currently the GitHub Pages
//   origin; will move to the custom domain when DNS lands.
//
// base: '/sibley-creek' - project-page deploy at
//   jayzhaomurray.github.io/sibley-creek/. Internal links use
//   `withBase()` from src/lib/urls.ts so the same code renders cleanly
//   at root (/) on Cloudflare Pages with a custom domain. Migration to
//   Cloudflare is a one-line edit: drop the `base` field.
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
  site: 'https://jayzhaomurray.github.io',
  base: '/sibley-creek',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
});
