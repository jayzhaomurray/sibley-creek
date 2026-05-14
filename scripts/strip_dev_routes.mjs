// Strip internal/dev-only routes from `dist/` after `astro build`.
//
// These pages exist for local development (chart triage shelves, OG-card
// render target) but should not be reachable on the public site. They are
// already excluded from the sitemap (astro.config.mjs `sitemap.filter`);
// this script removes the generated HTML/assets so the URLs return 404.
//
// `astro dev` is unaffected — it doesn't touch dist/.
//
// Pattern: maintain DEV_ONLY_ROUTES as the source-of-truth list. Add a
// route here when you add a new internal page; the script is idempotent
// and skips routes that don't exist on disk.

import { existsSync, rmSync } from "node:fs";
import { join, resolve } from "node:path";

const DIST_DIR = resolve(process.cwd(), "dist");

const DEV_ONLY_ROUTES = [
  "chart-alternatives",
  "chart-archive",
  "og-preview",
];

let stripped = 0;
for (const route of DEV_ONLY_ROUTES) {
  const target = join(DIST_DIR, route);
  if (existsSync(target)) {
    rmSync(target, { recursive: true, force: true });
    console.log(`stripped: dist/${route}/`);
    stripped += 1;
  }
}

if (stripped === 0) {
  console.log("strip_dev_routes: nothing to strip (dist/ does not contain any of the listed routes)");
} else {
  console.log(`strip_dev_routes: removed ${stripped} dev-only route(s) from dist/`);
}
