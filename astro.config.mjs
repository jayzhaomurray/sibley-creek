// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

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
// Integrations:
//   sitemap — auto-discovers static routes that Astro emits during the
//     build. Emits /sitemap-index.xml + /sitemap-0.xml, honoring `site`
//     above. Dynamic /research/<slug>/ pages are already gated by the
//     getStaticPaths publishedPath filter in src/pages/research/[slug].astro,
//     so unpublished deep-dives never reach the sitemap. The `filter`
//     defensively excludes /_experiments/* (Astro already skips _-prefixed
//     pages, but we don't want one to ever leak via a future rename) and
//     /og-preview/ (the OG-card render-target page, not a reader route).
export default defineConfig({
  site: 'https://sibleycreek.ca',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  redirects: {
    '/chart-improvements': '/chart-alternatives',
    '/chart-improvements/': '/chart-alternatives/',
  },
  integrations: [
    sitemap({
      filter: (page) =>
        !page.includes('/_experiments/') &&
        !page.includes('/og-preview/') &&
        !page.includes('/chart-alternatives/') &&
        !page.includes('/chart-archive/'),
    }),
  ],
});
