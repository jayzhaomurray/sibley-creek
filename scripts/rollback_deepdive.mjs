#!/usr/bin/env node
/*
 * rollback_deepdive.mjs
 *
 * One-command rollback for a published deep dive. Inverts the
 * `promote_deepdive.mjs` step: unlinks the public route, archives the
 * published markdown for diagnostic / re-promote, and stamps the audit
 * trail in `src/data/sections.ts`.
 *
 * Usage:
 *   node scripts/rollback_deepdive.mjs <slug>
 *   node scripts/rollback_deepdive.mjs <slug> --dry-run
 *   node scripts/rollback_deepdive.mjs <slug> --yes
 *
 * What it does:
 *   1. Confirm `<slug>` exists in `deepDives[]` with a non-null
 *      `publishedPath`. Abort otherwise.
 *   2. Print the preview: route URL that will disappear, the file
 *      that will be archived, and the metadata that will be stamped.
 *   3. Require Enter (or `--yes`).
 *   4. Move `editorial/published/<slug>.md` -> `editorial/_archive/<slug>-<ts>.md`.
 *   5. Patch `sections.ts`: remove the `publishedPath` line, preserve
 *      `publishedAt` / `dataVintage`, insert `rolledBackAt: "<today>"`.
 *   6. Build (Astro) and verify `dist/research/<slug>/` is gone.
 *   7. Print summary + git diff of `sections.ts`.
 *
 * Safe: the markdown body is archived, never deleted. The audit-trail
 * fields stay intact, and `rolledBackAt` is added so a later auditor can
 * see this entry was published and then withdrawn. Re-promotion is the
 * inverse: point a future promote run at the archived file.
 *
 * Pure Node + standard libs. No npm deps.
 */
import {
  readFileSync,
  writeFileSync,
  existsSync,
  mkdirSync,
  renameSync,
  statSync,
  readdirSync,
  rmSync,
} from "node:fs";
import { resolve, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync, spawnSync } from "node:child_process";
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(__filename, "..", "..");
const SECTIONS_TS = resolve(ROOT, "src", "data", "sections.ts");
const PUBLISHED_DIR = resolve(ROOT, "editorial", "published");
const ARCHIVE_DIR = resolve(ROOT, "editorial", "_archive");
const DIST_DIR = resolve(ROOT, "dist");

// --------------------------------------------------------------------
// CLI parsing
// --------------------------------------------------------------------
const argv = process.argv.slice(2);
const flags = new Set(argv.filter((a) => a.startsWith("--")));
const positional = argv.filter((a) => !a.startsWith("--"));
const slug = positional[0];
const DRY_RUN = flags.has("--dry-run");
const ASSUME_YES = flags.has("--yes");
const SKIP_BUILD = flags.has("--skip-build"); // hidden: for self-test only

function die(msg, code = 1) {
  console.error(`[rollback] ABORT: ${msg}`);
  process.exit(code);
}

if (!slug) {
  die(
    "missing <slug>. usage: node scripts/rollback_deepdive.mjs <slug> [--dry-run] [--yes]",
    2,
  );
}
if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) {
  die(`bad slug "${slug}" - expected lowercase, hyphenated.`, 2);
}

// --------------------------------------------------------------------
// 1. Locate the deepDive entry in sections.ts
// --------------------------------------------------------------------
if (!existsSync(SECTIONS_TS)) {
  die(`sections.ts not found at ${SECTIONS_TS}`);
}
const sectionsSrc = readFileSync(SECTIONS_TS, "utf-8");

/**
 * Find the `deepDives: DeepDive[] = [ ... ]` array body. We scan from the
 * declaration to the matching closing bracket so the per-entry parse only
 * touches that region.
 */
function locateDeepDivesArray(src) {
  const declRe = /export const deepDives\s*:\s*DeepDive\[\]\s*=\s*\[/;
  const m = declRe.exec(src);
  if (!m) return null;
  const start = m.index + m[0].length; // index just after the opening [
  let depth = 1;
  for (let i = start; i < src.length; i++) {
    const c = src[i];
    if (c === "[") depth++;
    else if (c === "]") {
      depth--;
      if (depth === 0) return { start, end: i };
    }
  }
  return null;
}

const arrSpan = locateDeepDivesArray(sectionsSrc);
if (!arrSpan) die("could not find `deepDives` array in sections.ts.");

/**
 * Find the object literal in `deepDives[]` whose `slug` matches. Returns
 * `{ start, end, body }` where `start..end` are absolute file offsets
 * spanning the entire object literal (from `{` to matching `}`).
 *
 * Scan the array region for top-level `{ ... }` objects (depth=1 inside
 * the array). For each, read its slug field and match.
 */
function findEntryBySlug(src, span, wantSlug) {
  let i = span.start;
  while (i < span.end) {
    const ch = src[i];
    if (ch === "{") {
      // Find matching closing brace.
      let depth = 1;
      let j = i + 1;
      while (j < span.end && depth > 0) {
        const c = src[j];
        if (c === "{") depth++;
        else if (c === "}") depth--;
        if (depth === 0) break;
        j++;
      }
      if (depth !== 0) return null;
      const body = src.slice(i, j + 1);
      const slugMatch = body.match(/\bslug\s*:\s*["'`]([^"'`]+)["'`]/);
      if (slugMatch && slugMatch[1] === wantSlug) {
        return { start: i, end: j + 1, body };
      }
      i = j + 1;
      continue;
    }
    i++;
  }
  return null;
}

const entry = findEntryBySlug(sectionsSrc, arrSpan, slug);
if (!entry) {
  die(`slug "${slug}" not found in deepDives[]. Did you mistype it?`);
}

// Pull the fields we care about out of the entry body.
function extractField(body, name) {
  // Match `name: "value"` or `name: 'value'` or `name: \`value\``.
  const re = new RegExp(
    `\\b${name}\\s*:\\s*["'\`]([^"'\`]+)["'\`]\\s*,?`,
    "m",
  );
  const m = body.match(re);
  return m ? m[1] : undefined;
}

const publishedPath = extractField(entry.body, "publishedPath");
const publishedAt = extractField(entry.body, "publishedAt");
const dataVintage = extractField(entry.body, "dataVintage");
const existingRolledBackAt = extractField(entry.body, "rolledBackAt");

if (!publishedPath) {
  die(
    `slug "${slug}" is in deepDives[] but has no publishedPath. ` +
      `not currently published - nothing to rollback.`,
    0,
  );
}

// --------------------------------------------------------------------
// 2. Preview
// --------------------------------------------------------------------
const publishedAbs = resolve(ROOT, publishedPath);
const publishedExists = existsSync(publishedAbs);
const now = new Date();
const todayIso = now.toISOString().slice(0, 10); // YYYY-MM-DD
// Timestamped archive filename, e.g. 2026-05-11T143052Z.
const stamp =
  now.toISOString().replace(/[:.]/g, "").replace(/-/g, "").slice(0, 15) + "Z";
const archiveBase = `${slug}-${stamp}.md`;
const archivePathAbs = join(ARCHIVE_DIR, archiveBase);
const archivePathRel = `editorial/_archive/${archiveBase}`;

console.log("[rollback] plan");
console.log(`  slug              ${slug}`);
console.log(`  route to remove   /research/${slug}/`);
console.log(`  publishedPath     ${publishedPath}`);
console.log(
  `  archive target    ${archivePathRel}` +
    (publishedExists ? "" : "  (SOURCE MISSING - sections.ts cleanup only)"),
);
console.log(`  publishedAt       ${publishedAt ?? "(none)"} (preserved)`);
console.log(`  dataVintage       ${dataVintage ?? "(none)"} (preserved)`);
console.log(
  `  rolledBackAt      ${todayIso}` +
    (existingRolledBackAt
      ? `  (overwriting prior ${existingRolledBackAt})`
      : "  (new field)"),
);
if (DRY_RUN) {
  console.log("[rollback] --dry-run: no filesystem changes, exiting.");
  process.exit(0);
}

// --------------------------------------------------------------------
// 3. Confirm
// --------------------------------------------------------------------
if (!ASSUME_YES) {
  const rl = createInterface({ input, output });
  const ans = await rl.question(
    "[rollback] proceed? press Enter to confirm, anything else to abort: ",
  );
  rl.close();
  if (ans.trim() !== "") {
    die("user aborted.", 0);
  }
}

// --------------------------------------------------------------------
// 4. Archive the published file
// --------------------------------------------------------------------
if (publishedExists) {
  if (!existsSync(ARCHIVE_DIR)) {
    mkdirSync(ARCHIVE_DIR, { recursive: true });
    console.log(`[rollback] created ${archivePathRel.replace(/\/[^/]+$/, "/")}`);
  }
  renameSync(publishedAbs, archivePathAbs);
  console.log(`[rollback] archived ${publishedPath} -> ${archivePathRel}`);
} else {
  console.warn(
    `[rollback] WARN: ${publishedPath} not found on disk; ` +
      `skipping archive step (orphan publishedPath).`,
  );
}

// --------------------------------------------------------------------
// 5. Patch sections.ts
//    - delete the `publishedPath:` line entirely
//    - if `rolledBackAt` already exists, overwrite it
//    - otherwise insert `rolledBackAt: "<today>"` right after publishedAt
//      (or right after slug if publishedAt is absent), matching surrounding indent
// --------------------------------------------------------------------
function patchEntry(srcAll, entrySpan, todayIsoStr) {
  const body = srcAll.slice(entrySpan.start, entrySpan.end);

  // Detect indentation of inner fields by sampling the first non-{ line.
  const lines = body.split("\n");
  // Find a line that contains a field, e.g. "    slug: ...", to copy the indent.
  let innerIndent = "    ";
  for (const ln of lines) {
    const m = ln.match(/^(\s+)\w+\s*:/);
    if (m) {
      innerIndent = m[1];
      break;
    }
  }

  let next = body;

  // Drop the publishedPath line. Match the whole line including its newline
  // so we don't leave a blank gap.
  const publishedPathLineRe =
    /^[ \t]*publishedPath\s*:\s*["'`][^"'`]+["'`]\s*,?\s*\r?\n/m;
  if (publishedPathLineRe.test(next)) {
    next = next.replace(publishedPathLineRe, "");
  } else {
    throw new Error("could not locate publishedPath line to remove.");
  }

  // rolledBackAt handling
  const rolledBackLineRe =
    /^([ \t]*)rolledBackAt\s*:\s*["'`][^"'`]+["'`]\s*,?\s*\r?\n/m;
  const insertLine = `${innerIndent}rolledBackAt: "${todayIsoStr}",\n`;

  if (rolledBackLineRe.test(next)) {
    next = next.replace(rolledBackLineRe, insertLine);
  } else {
    // Try to insert after publishedAt line; if absent, after slug line; if
    // neither, just before the closing brace.
    const afterPublishedAt =
      /^[ \t]*publishedAt\s*:\s*["'`][^"'`]+["'`]\s*,?\s*\r?\n/m;
    const afterSlug =
      /^[ \t]*slug\s*:\s*["'`][^"'`]+["'`]\s*,?\s*\r?\n/m;
    if (afterPublishedAt.test(next)) {
      next = next.replace(afterPublishedAt, (m) => m + insertLine);
    } else if (afterSlug.test(next)) {
      next = next.replace(afterSlug, (m) => m + insertLine);
    } else {
      // Fallback: insert before the closing brace.
      next = next.replace(/\}\s*$/, insertLine + "}");
    }
  }

  return srcAll.slice(0, entrySpan.start) + next + srcAll.slice(entrySpan.end);
}

const patched = patchEntry(sectionsSrc, entry, todayIso);
if (patched === sectionsSrc) {
  die("sections.ts patch produced no change - aborting before write.");
}
writeFileSync(SECTIONS_TS, patched, "utf-8");
console.log("[rollback] patched src/data/sections.ts");

// --------------------------------------------------------------------
// 6. Build + verify the route no longer generates
// --------------------------------------------------------------------
let buildVerified = false;
if (SKIP_BUILD) {
  console.log("[rollback] --skip-build: not rebuilding (self-test path).");
} else {
  console.log("[rollback] rebuilding (npm run build:fast) ...");
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  const proc = spawnSync(npm, ["run", "build:fast"], {
    cwd: ROOT,
    stdio: "inherit",
  });
  if (proc.status !== 0) {
    console.error(
      "[rollback] WARN: build failed. sections.ts and archive are already updated; " +
        "fix the build before deploying.",
    );
  } else {
    const routeDir = resolve(DIST_DIR, "research", slug);
    if (existsSync(routeDir)) {
      console.error(
        `[rollback] WARN: build succeeded but /research/${slug}/ still exists at ${routeDir}.`,
      );
    } else {
      buildVerified = true;
      console.log(
        `[rollback] verified: dist/research/${slug}/ is gone.`,
      );
    }
  }
}

// --------------------------------------------------------------------
// 7. Summary + git diff
// --------------------------------------------------------------------
console.log("\n[rollback] SUMMARY");
console.log(`  slug              ${slug}`);
console.log(`  route             /research/${slug}/  -> removed`);
console.log(
  `  archive           ${publishedExists ? archivePathRel : "(none - source was missing)"}`,
);
console.log(`  sections.ts       publishedPath cleared, rolledBackAt=${todayIso}`);
console.log(
  `  build verified    ${buildVerified ? "yes" : "no (see warnings above)"}`,
);
console.log("");

try {
  const diff = execFileSync(
    "git",
    ["--no-pager", "diff", "--", "src/data/sections.ts"],
    { cwd: ROOT, encoding: "utf-8" },
  );
  if (diff.trim()) {
    console.log("[rollback] git diff src/data/sections.ts:");
    console.log(diff);
  } else {
    console.log("[rollback] (no git diff output - is sections.ts tracked?)");
  }
} catch (e) {
  console.warn(
    "[rollback] could not run `git diff`: " + (e.message ?? String(e)),
  );
}

console.log(
  "[rollback] done. Review the diff, then commit + deploy on your usual cadence.",
);
console.log(
  "[rollback] to restore: re-promote the archived file at " +
    (publishedExists ? archivePathRel : "(archive was skipped)") +
    ".",
);
