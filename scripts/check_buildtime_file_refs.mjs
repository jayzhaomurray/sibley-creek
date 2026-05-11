#!/usr/bin/env node
/*
 * check_buildtime_file_refs.mjs
 *
 * Catches the "build references a file not in git" failure class.
 *
 * Historical context: 10 consecutive deploys failed because data/raw/*.csv
 * files referenced via readCsv() at build time were gitignored. Local
 * Windows builds passed (raw cache present); Linux CI builds failed with
 * ENOENT. We force-added the 61 specific CSVs, but nothing guarded against
 * the next component grabbing a new gitignored file.
 *
 * Scope (intentionally narrow):
 *   1. readCsv("foo.csv")           -> data/raw/foo.csv
 *   2. data/raw/<file>.{csv,json}   -> direct path references (string literals in source)
 *
 * For each hit, ask `git ls-files --error-unmatch <path>`. If git doesn't
 * track it, fail loudly with a precise message. Runs in CI before the
 * Astro build so failures are fast and the error names the offending file.
 *
 * Not in scope: every possible CI-vs-local divergence. That is a different
 * problem and would balloon this script.
 */
import { readFileSync, statSync, readdirSync } from "node:fs";
import { resolve, join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(__filename, "..", "..");
const SRC = resolve(ROOT, "src");
const RAW_DIR_REL = "data/raw";

// Patterns we hunt for. Comments are stripped before matching so that
// reference notes like `* Data. data/raw/foo.csv.` in docblocks don't
// trigger false positives.
const READ_CSV_RE = /readCsv\(\s*["'`]([^"'`]+\.csv)["'`]\s*\)/g;
const DIRECT_PATH_RE = /(?<!["'`/\w])(data\/raw\/[A-Za-z0-9_.\-/]+\.(?:csv|json))(?!["'`/\w])/g;
const DIRECT_PATH_QUOTED_RE = /["'`](data\/raw\/[A-Za-z0-9_.\-/]+\.(?:csv|json))["'`]/g;

const SCAN_EXTENSIONS = new Set([
  ".astro",
  ".ts",
  ".tsx",
  ".js",
  ".mjs",
  ".cjs",
  ".jsx",
]);

const SKIP_DIRS = new Set(["node_modules", ".astro", "dist", ".cache"]);

/** Walk `dir` recursively and yield files with extensions in SCAN_EXTENSIONS. */
function* walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const ent of entries) {
    if (SKIP_DIRS.has(ent.name)) continue;
    const p = join(dir, ent.name);
    if (ent.isDirectory()) {
      yield* walk(p);
    } else if (ent.isFile()) {
      const dot = ent.name.lastIndexOf(".");
      if (dot >= 0 && SCAN_EXTENSIONS.has(ent.name.slice(dot))) {
        yield p;
      }
    }
  }
}

/**
 * Strip JS/TS-style comments so docblock references don't false-positive.
 * Crude but sufficient: this is a guard, not a parser. We blank out the
 * comment bodies (preserving offsets is unnecessary here).
 */
function stripComments(src) {
  // Block comments
  let out = src.replace(/\/\*[\s\S]*?\*\//g, "");
  // Line comments. Astro frontmatter uses // too.
  out = out.replace(/(^|[^:"'`])\/\/[^\n]*/g, "$1");
  // Astro/HTML comments
  out = out.replace(/<!--[\s\S]*?-->/g, "");
  return out;
}

/** Resolve a discovered reference to a repo-relative path under data/raw/. */
function resolveRef(kind, captured) {
  if (kind === "readCsv") {
    return `${RAW_DIR_REL}/${captured}`;
  }
  return captured; // already `data/raw/...`
}

/** Ask git whether `relPath` is tracked. Returns true/false. */
function isTracked(relPath) {
  try {
    execFileSync("git", ["ls-files", "--error-unmatch", relPath], {
      cwd: ROOT,
      stdio: ["ignore", "ignore", "ignore"],
    });
    return true;
  } catch {
    return false;
  }
}

/** Sanity-check: does the file actually exist on disk? (Diagnostic only.) */
function existsOnDisk(relPath) {
  try {
    statSync(resolve(ROOT, relPath));
    return true;
  } catch {
    return false;
  }
}

function main() {
  const refs = new Map(); // relPath -> Set of source files referencing it

  for (const file of walk(SRC)) {
    const raw = readFileSync(file, "utf-8");
    const src = stripComments(raw);
    const rel = relative(ROOT, file).split(sep).join("/");

    for (const m of src.matchAll(READ_CSV_RE)) {
      const ref = resolveRef("readCsv", m[1]);
      if (!refs.has(ref)) refs.set(ref, new Set());
      refs.get(ref).add(rel);
    }
    // Look for `data/raw/...` inside string literals only -- the broader
    // regex would catch text inside docblocks even after comment stripping.
    for (const m of src.matchAll(DIRECT_PATH_QUOTED_RE)) {
      const ref = resolveRef("direct", m[1]);
      if (!refs.has(ref)) refs.set(ref, new Set());
      refs.get(ref).add(rel);
    }
  }

  const missing = [];
  for (const [ref, sources] of refs) {
    if (!isTracked(ref)) {
      missing.push({ ref, sources: [...sources], onDisk: existsOnDisk(ref) });
    }
  }

  if (missing.length === 0) {
    // eslint-disable-next-line no-console
    console.log(
      `[check-buildtime-refs] OK -- ${refs.size} build-time file references, all git-tracked.`,
    );
    return 0;
  }

  // eslint-disable-next-line no-console
  console.error(
    `[check-buildtime-refs] FAIL -- ${missing.length} build-time file reference(s) NOT tracked by git:`,
  );
  for (const { ref, sources, onDisk } of missing) {
    // eslint-disable-next-line no-console
    console.error(`  - ${ref}${onDisk ? "" : "  (also missing on disk)"}`);
    for (const s of sources) {
      // eslint-disable-next-line no-console
      console.error(`      referenced by: ${s}`);
    }
  }
  // eslint-disable-next-line no-console
  console.error(
    "\nFix: `git add -f <path>` for each, or stop referencing the file at build time.\n" +
      "Background: data/raw/* is gitignored by policy; build-time consumers must opt files in.",
  );
  return 1;
}

process.exit(main());
