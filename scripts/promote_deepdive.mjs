#!/usr/bin/env node
/*
 * promote_deepdive.mjs
 *
 * One-command promotion of a deep-dive draft to the live site.
 *
 * Steps:
 *   1) Read the draft markdown.
 *   2) Strip the editorial scratch frontmatter (everything before the
 *      first reader-facing prose; conventionally the first "## 1. Page
 *      header copy" or "## Lede" heading).
 *   3) Trim trailing scratch markers (e.g., "End of vN draft.").
 *   4) Write stripped body to editorial/published/<slug>.md.
 *   5) Patch src/data/sections.ts: set publishedPath, publishedAt,
 *      dataVintage, lastUpdated on the matching deepDive entry.
 *   6) Run `npm run build` to verify a clean build.
 *   7) Print a summary. Do not commit, do not push.
 *
 * Usage:
 *   node scripts/promote_deepdive.mjs <draft-path> <slug> [--dry-run] [--yes] [--force]
 *
 * Flags:
 *   --dry-run   Print what would happen; touch no files; do not build.
 *   --yes       Skip the interactive confirmation prompt.
 *   --force     Overwrite existing editorial/published/<slug>.md.
 */

import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------------------
// Paths + arg parsing
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const positional = [];
  const flags = {
    dryRun: false,
    yes: false,
    force: false,
    dataVintage: null,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") flags.dryRun = true;
    else if (a === "--yes" || a === "-y") flags.yes = true;
    else if (a === "--force") flags.force = true;
    else if (a === "--data-vintage") {
      flags.dataVintage = argv[++i];
      if (!/^\d{4}-\d{2}-\d{2}$/.test(flags.dataVintage || "")) {
        die(`--data-vintage requires an ISO date (YYYY-MM-DD)`);
      }
    } else if (a.startsWith("--data-vintage=")) {
      flags.dataVintage = a.slice("--data-vintage=".length);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(flags.dataVintage)) {
        die(`--data-vintage requires an ISO date (YYYY-MM-DD)`);
      }
    } else if (a.startsWith("--")) {
      die(`Unknown flag: ${a}`);
    } else positional.push(a);
  }
  if (positional.length < 2) {
    die(
      "Usage: node scripts/promote_deepdive.mjs <draft-path> <slug> " +
        "[--data-vintage YYYY-MM-DD] [--dry-run] [--yes] [--force]"
    );
  }
  return {
    draftPathArg: positional[0],
    slug: positional[1],
    ...flags,
  };
}

function die(msg, code = 1) {
  console.error(`ERROR: ${msg}`);
  process.exit(code);
}

function info(msg) {
  console.log(msg);
}

function rel(p) {
  return path.relative(repoRoot, p).split(path.sep).join("/");
}

// ---------------------------------------------------------------------------
// Strip logic
// ---------------------------------------------------------------------------

/**
 * Strip the editorial scratch block from the head of the draft, and trim
 * trailing scratch markers from the tail.
 *
 * Heuristic for the head:
 *   - Look for the first occurrence of "## 1. Page header copy" (canonical)
 *     or, if absent, "## Lede" / "## 2. Lede".
 *   - If a candidate is found at the top of the file (line 1, no scratch
 *     above it), keep the whole file as-is.
 *   - Otherwise, slice starting at the candidate.
 *   - If no candidate matches at all, return the file unchanged and warn.
 *
 * Heuristic for the tail:
 *   - Drop any trailing block that consists only of a "---" separator
 *     followed by lines like "End of vN draft." (no reader-facing content).
 *
 * Returns { stripped, headLine, tailDropped, headMatched }.
 */
function stripScratch(raw) {
  const lines = raw.split(/\r?\n/);
  const headPatterns = [
    /^##\s+1\.\s+Page header copy\s*$/i,
    /^##\s+2\.\s+Lede\s*$/i,
    /^##\s+Lede\s*$/i,
    /^##\s+Page header copy\s*$/i,
  ];

  let headLine = -1;
  let headMatched = null;
  for (let i = 0; i < lines.length; i++) {
    for (const p of headPatterns) {
      if (p.test(lines[i])) {
        headLine = i;
        headMatched = lines[i];
        break;
      }
    }
    if (headLine !== -1) break;
  }

  let body;
  if (headLine === -1) {
    // No header / Lede heading at all; keep the file as-is.
    body = lines.slice();
  } else {
    body = lines.slice(headLine);
  }

  // Trim trailing scratch markers. Walk back from the end, dropping
  // blank lines, then drop a contiguous block that looks like
  // "End of vN draft." optionally preceded by a "---" separator and
  // surrounding blank lines. Stop as soon as we see something else.
  let end = body.length;
  while (end > 0 && body[end - 1].trim() === "") end--;
  // Drop trailing "End of ... draft." lines
  while (end > 0 && /^end of .* draft\.?\s*$/i.test(body[end - 1].trim())) {
    end--;
    while (end > 0 && body[end - 1].trim() === "") end--;
  }
  // Drop a single trailing "---" separator if it's the last meaningful line
  // (this leaves a clean trailing newline; matches the canonical published
  // file which ends with a `---` then EOF).
  // NB: do NOT collapse further; the canonical published file preserves a
  // trailing `---`.
  // Add back exactly one trailing `---\n` to match canon if we ate scratch
  // markers but the published canon keeps a `---` close.
  let trimmed = body.slice(0, end);

  // Re-attach a trailing `---` + newline if we just trimmed an
  // "End of ... draft." marker (so the published file mirrors canon).
  const droppedTail = end !== body.length;
  if (droppedTail) {
    // Find the last `---` line still in `trimmed`; if there isn't one as
    // the terminal separator, append one to preserve the canonical close.
    let lastNonBlank = trimmed.length - 1;
    while (lastNonBlank >= 0 && trimmed[lastNonBlank].trim() === "")
      lastNonBlank--;
    if (lastNonBlank >= 0 && trimmed[lastNonBlank].trim() !== "---") {
      trimmed.push("");
      trimmed.push("---");
    } else {
      // Truncate any blank lines after the final `---`.
      trimmed = trimmed.slice(0, lastNonBlank + 1);
    }
  }

  // Always end with a single trailing newline.
  let stripped = trimmed.join("\n");
  if (!stripped.endsWith("\n")) stripped += "\n";

  return {
    stripped,
    headLine,
    headMatched,
    tailDropped: droppedTail,
  };
}

// ---------------------------------------------------------------------------
// dataVintage extraction
// ---------------------------------------------------------------------------

/**
 * Look for a "data vintage" hint in the draft scratch frontmatter. We
 * accept either of these conventions:
 *   - A bullet/line like:  "Data vintage: 2026-05-11"
 *   - A scratch line:      "data vintage: 2026-05-11"
 * Returns an ISO date string (YYYY-MM-DD) or null.
 */
function extractDataVintage(raw) {
  const m = raw.match(/data\s+vintage[^\n:]*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i);
  if (m) return m[1];
  return null;
}

// ---------------------------------------------------------------------------
// sections.ts patching
// ---------------------------------------------------------------------------

/**
 * Update the DeepDive entry for `slug` in sections.ts. Sets:
 *   publishedPath, publishedAt (if missing), dataVintage, lastUpdated.
 *
 * Strategy: locate the entry by `slug: "<slug>"`, then locate the
 * surrounding `{ ... }` object literal by brace-matching, then patch the
 * keys inside.
 *
 * Returns { next, changes: string[], existing: Partial<DeepDive> }.
 */
function patchSectionsTs(src, slug, vals) {
  const slugRe = new RegExp(
    `slug:\\s*["']${slug.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}["']`
  );
  const slugMatch = src.match(slugRe);
  if (!slugMatch) {
    throw new Error(
      `No deepDive entry with slug "${slug}" found in src/data/sections.ts. ` +
        `Add the entry to deepDives[] first, then re-run.`
    );
  }
  const slugIdx = slugMatch.index;

  // Walk backward to find the enclosing "{".
  let openIdx = -1;
  let depth = 0;
  for (let i = slugIdx; i >= 0; i--) {
    const ch = src[i];
    if (ch === "}") depth++;
    else if (ch === "{") {
      if (depth === 0) {
        openIdx = i;
        break;
      }
      depth--;
    }
  }
  if (openIdx === -1) throw new Error("Could not locate opening brace.");

  // Walk forward from openIdx to find the matching "}".
  let closeIdx = -1;
  depth = 0;
  for (let i = openIdx; i < src.length; i++) {
    const ch = src[i];
    if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) {
        closeIdx = i;
        break;
      }
    }
  }
  if (closeIdx === -1) throw new Error("Could not locate closing brace.");

  const blockOpen = src.slice(0, openIdx + 1);
  let block = src.slice(openIdx + 1, closeIdx);
  const blockClose = src.slice(closeIdx);

  const changes = [];
  const existing = {};

  // Helper: read existing value for `key` (quoted string only).
  function readKey(key) {
    const re = new RegExp(`(^|\\n)\\s*${key}:\\s*["']([^"']*)["']`, "");
    const m = block.match(re);
    return m ? m[2] : undefined;
  }

  // Helper: set or insert a quoted string key, preserving existing
  // surrounding indentation. Idempotent — re-setting the same value is a
  // no-op and produces no change entry.
  function setKey(key, value) {
    const before = readKey(key);
    if (before === value) return; // no-op
    const reLine = new RegExp(
      `(^|\\n)(\\s*)${key}:\\s*["'][^"']*["'],?`,
      ""
    );
    const m = block.match(reLine);
    if (m) {
      const lead = m[1];
      const indent = m[2];
      const trailingComma = block[m.index + m[0].length] === "," ? "" : "";
      // Preserve a trailing comma if the original had one or there's
      // more content in the object literal.
      const hadComma = m[0].endsWith(",");
      const replacement = `${lead}${indent}${key}: "${value}"${
        hadComma ? "," : ","
      }`;
      block = block.slice(0, m.index) + replacement + block.slice(m.index + m[0].length) + trailingComma;
      changes.push(`${key}: "${before}" -> "${value}"`);
      existing[key] = before;
    } else {
      // Insert just before the closing of the block. Use a sensible indent
      // by mirroring the indent of the slug line.
      const slugLineRe = new RegExp(
        `\\n(\\s*)slug:\\s*["']${slug.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}["']`
      );
      const sm = block.match(slugLineRe);
      const indent = sm ? sm[1] : "    ";
      // Ensure the previous content ends with a comma + newline.
      let trimmed = block.replace(/\s*$/, "");
      if (!trimmed.endsWith(",")) trimmed += ",";
      trimmed += `\n${indent}${key}: "${value}",\n  `;
      block = trimmed;
      changes.push(`${key}: (added) "${value}"`);
      existing[key] = undefined;
    }
  }

  // publishedPath: always set (idempotent).
  setKey("publishedPath", vals.publishedPath);

  // publishedAt: only set if missing OR currently "TK". Otherwise leave the
  // original publication date in place (per spec: "if not already set").
  const existingPublishedAt = readKey("publishedAt");
  if (!existingPublishedAt || existingPublishedAt === "TK") {
    setKey("publishedAt", vals.publishedAt);
  }

  // dataVintage: always set to extracted or today.
  setKey("dataVintage", vals.dataVintage);

  // lastUpdated: always bump.
  setKey("lastUpdated", vals.lastUpdated);

  const next = blockOpen + block + blockClose;
  return { next, changes, existing };
}

// ---------------------------------------------------------------------------
// Confirmation prompt
// ---------------------------------------------------------------------------

async function confirm(msg) {
  if (!process.stdin.isTTY) return true; // CI: assume yes
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) => {
    rl.question(`${msg} [Enter to continue, Ctrl-C to abort] `, () => {
      rl.close();
      resolve(true);
    });
  });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const draftPath = path.isAbsolute(args.draftPathArg)
    ? args.draftPathArg
    : path.resolve(repoRoot, args.draftPathArg);
  const publishedPathRel = `editorial/published/${args.slug}.md`;
  const publishedPathAbs = path.resolve(repoRoot, publishedPathRel);
  const sectionsTsPath = path.resolve(repoRoot, "src/data/sections.ts");

  if (!fs.existsSync(draftPath)) {
    die(`Draft not found: ${draftPath}`);
  }
  if (!fs.existsSync(sectionsTsPath)) {
    die(`sections.ts not found at ${sectionsTsPath}`);
  }

  const raw = fs.readFileSync(draftPath, "utf8");
  const { stripped, headLine, headMatched, tailDropped } = stripScratch(raw);

  const today = new Date().toISOString().slice(0, 10);
  // Precedence: explicit --data-vintage > draft-frontmatter hint > today.
  const vintageSource = args.dataVintage
    ? "flag"
    : extractDataVintage(raw)
    ? "draft"
    : "today";
  const vintage =
    args.dataVintage || extractDataVintage(raw) || today;

  info("");
  info("=== promote_deepdive ===");
  info(`Draft:           ${rel(draftPath)}`);
  info(`Slug:            ${args.slug}`);
  info(`Published path:  ${publishedPathRel}`);
  info(`Today:           ${today}`);
  info(`Data vintage:    ${vintage} (${vintageSource})`);
  if (headLine === -1) {
    info(`Strip:           NONE (no header heading found; copying as-is)`);
  } else {
    info(`Strip line:      line ${headLine + 1} -> "${headMatched.trim()}"`);
  }
  if (tailDropped) info(`Trailing scratch markers trimmed.`);

  // Sections.ts dry patch
  const sectionsRaw = fs.readFileSync(sectionsTsPath, "utf8");
  let patched;
  try {
    patched = patchSectionsTs(sectionsRaw, args.slug, {
      publishedPath: publishedPathRel,
      publishedAt: today,
      dataVintage: vintage,
      lastUpdated: today,
    });
  } catch (e) {
    die(e.message);
  }

  info("");
  info("Planned sections.ts changes:");
  if (patched.changes.length === 0) {
    info("  (none — entry already matches target state)");
  } else {
    for (const c of patched.changes) info(`  - ${c}`);
  }

  // Overwrite check. Normalize CRLF -> LF before comparing so a file
  // checked out under Windows autocrlf does not look "different" when
  // its content is in fact byte-identical to the stripped output.
  const exists = fs.existsSync(publishedPathAbs);
  const normalize = (s) => s.replace(/\r\n/g, "\n");
  if (exists && !args.force) {
    const onDisk = fs.readFileSync(publishedPathAbs, "utf8");
    if (normalize(onDisk) === normalize(stripped)) {
      info("");
      info(`Note: ${publishedPathRel} already exists and content matches.`);
    } else if (args.dryRun) {
      info("");
      info(
        `Note: ${publishedPathRel} exists with different content; ` +
          `would refuse to overwrite without --force (dry-run only).`
      );
    } else {
      die(
        `${publishedPathRel} already exists and differs from the stripped ` +
          `draft. Pass --force to overwrite.`
      );
    }
  }

  if (args.dryRun) {
    info("");
    info("Dry-run mode: no files touched, no build run.");
    info("First 12 lines of stripped output:");
    const previewLines = stripped.split("\n").slice(0, 12);
    for (const l of previewLines) info(`  | ${l}`);
    return;
  }

  if (!args.yes) {
    await confirm("About to write files and run a build.");
  }

  // Step 1: write the published file (only if changed).
  let publishedWritten = false;
  if (
    !exists ||
    args.force ||
    normalize(fs.readFileSync(publishedPathAbs, "utf8")) !== normalize(stripped)
  ) {
    fs.mkdirSync(path.dirname(publishedPathAbs), { recursive: true });
    fs.writeFileSync(publishedPathAbs, stripped, "utf8");
    publishedWritten = true;
    info(`Wrote ${publishedPathRel} (${stripped.length} chars).`);
  } else {
    info(`${publishedPathRel} unchanged.`);
  }

  // Step 2: patch sections.ts (only if changed).
  let sectionsPatched = false;
  if (patched.next !== sectionsRaw) {
    try {
      fs.writeFileSync(sectionsTsPath, patched.next, "utf8");
      sectionsPatched = true;
      info(`Patched ${rel(sectionsTsPath)}.`);
    } catch (e) {
      info("");
      info("PARTIAL STATE: published file written, sections.ts patch FAILED.");
      info(`  Published:   ${publishedPathRel}`);
      info(`  sections.ts: ${rel(sectionsTsPath)} (not modified)`);
      die(`sections.ts patch failed: ${e.message}`);
    }
  } else {
    info(`${rel(sectionsTsPath)} unchanged.`);
  }

  // Step 3: build.
  info("");
  info("Running `npm run build`...");
  const res = spawnSync("npm", ["run", "build"], {
    cwd: repoRoot,
    stdio: "inherit",
    shell: true,
  });
  if (res.status !== 0) {
    info("");
    info("BUILD FAILED. Files were modified on disk:");
    if (publishedWritten) info(`  - ${publishedPathRel}`);
    if (sectionsPatched) info(`  - ${rel(sectionsTsPath)}`);
    info("Investigate, revert if needed, and re-run.");
    process.exit(res.status ?? 1);
  }

  // Summary.
  info("");
  info("=== promotion complete ===");
  info(`  Slug:        ${args.slug}`);
  info(`  Published:   ${publishedPathRel} ${publishedWritten ? "(written)" : "(unchanged)"}`);
  info(`  sections.ts: ${sectionsPatched ? "patched" : "unchanged"}`);
  if (patched.changes.length > 0) {
    for (const c of patched.changes) info(`     - ${c}`);
  }
  info(`  Build:       OK`);
  info(`  Commit + push intentionally NOT done. Review with \`git diff\` and commit by hand.`);
}

main().catch((e) => {
  console.error("FATAL:", e);
  process.exit(1);
});
