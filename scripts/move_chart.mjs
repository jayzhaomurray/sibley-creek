#!/usr/bin/env node
/*
 * move_chart.mjs — path-aware chart mover.
 *
 * Moves a chart file across the holding-zone topology (or in/out of
 * production), rewriting relative `_shared/` imports inside the file
 * and updating the source + destination `index.ts` manifests.
 *
 * Usage:
 *   node scripts/move_chart.mjs <from-path> <to-path> [--dry-run]
 *
 * Behavior:
 *   1. Validates `from-path` exists and `to-path` does not already.
 *   2. Computes the depth-delta between `from-path` and `to-path` and
 *      rewrites any relative imports that reference `_shared/` so the
 *      number of `../` segments matches the new location. Handles
 *      `import ... from "..."` and `Astro.glob("...")` patterns.
 *   3. If the source has an `index.ts` next to it (an `_alternatives/
 *      <section>/` or `_archive/<section>/` manifest), removes the entry
 *      whose file basename matches the move and writes the manifest
 *      back. Preserves the rest of the manifest verbatim.
 *   4. If the destination has an `index.ts` AND the destination is under
 *      `_alternatives/` or `_archive/` (a holding zone), inserts the
 *      removed entry into the destination manifest (preserving the same
 *      metadata, with the `Component` import pointed at the new path
 *      and the `file` field updated). Live destinations (under
 *      `src/components/charts/<section>/`) have no manifest; the
 *      registry update happens in SectionLayout.astro by hand.
 *   5. Runs `git mv` to move the file.
 *   6. Prints a summary of what changed.
 *
 * Flags:
 *   --dry-run  Print what would happen; touch no files; do not git mv.
 *
 * Conventions assumed:
 *   - Holding-zone manifests at
 *     src/components/charts/_alternatives/<section>/index.ts and
 *     src/components/charts/_archive/<section>/index.ts.
 *   - Each manifest exports `entries: ChartShelfEntry[]`. Entries carry
 *     a `Component:` import bound and a `file:` string. The script
 *     edits the manifest text directly — it does NOT parse TS — using
 *     boundary markers. See `extractEntryBlock` below for the parser.
 *
 * Out of scope:
 *   - Updating the live chartRegistry in SectionLayout.astro. The
 *     promote-to-live skill handles that step separately; this script
 *     just moves files and manifest entries.
 */

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

// ---------------------------------------------------------------------------
// Arg parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const positional = [];
  const flags = { dryRun: false };
  for (const a of argv) {
    if (a === "--dry-run") flags.dryRun = true;
    else if (a.startsWith("--")) die(`Unknown flag: ${a}`);
    else positional.push(a);
  }
  if (positional.length !== 2) {
    die(
      "Usage: node scripts/move_chart.mjs <from-path> <to-path> [--dry-run]",
    );
  }
  return { from: positional[0], to: positional[1], ...flags };
}

function die(msg) {
  console.error(`move_chart: ${msg}`);
  process.exit(1);
}

function abs(p) {
  return path.isAbsolute(p) ? p : path.resolve(repoRoot, p);
}

function rel(p) {
  return path.relative(repoRoot, p).split(path.sep).join("/");
}

// ---------------------------------------------------------------------------
// Import-path rewriting
// ---------------------------------------------------------------------------

/**
 * Rewrite relative imports inside the moved file so any path that
 * references a directory above the file (typically `_shared/`) still
 * resolves after the depth change.
 *
 * Algorithm:
 *   For each matched path string (in `import ... from "..."`, `import(
 *   "..." )`, or `Astro.glob("...")`):
 *     - If it does not start with `../` (i.e. it's local or
 *       node-resolved), leave it.
 *     - Resolve it relative to the OLD file's directory to get its
 *       absolute target.
 *     - Re-relativize it from the NEW file's directory and write it
 *       back (with POSIX separators).
 */
function rewriteImports(text, oldFileAbs, newFileAbs) {
  const oldDir = path.dirname(oldFileAbs);
  const newDir = path.dirname(newFileAbs);

  // Match the three import shapes we care about. Group 1 captures the
  // path literal. We intentionally only match double-quoted forms (Astro
  // frontmatter convention).
  const patterns = [
    /(\bfrom\s+")([^"]+)(")/g,
    /(\bimport\s*\(\s*")([^"]+)(")/g,
    /(\bAstro\.glob\s*\(\s*")([^"]+)(")/g,
  ];

  let out = text;
  for (const re of patterns) {
    out = out.replace(re, (match, pre, importPath, post) => {
      // Only rewrite relative paths. `./` and `../` only — leave bare
      // module names and absolute paths alone.
      if (!importPath.startsWith("./") && !importPath.startsWith("../")) {
        return match;
      }
      const target = path.resolve(oldDir, importPath);
      let rebased = path.relative(newDir, target).split(path.sep).join("/");
      // Re-relativizing can produce a bare name (same-dir sibling); add
      // `./` back for clarity in matched imports.
      if (!rebased.startsWith(".")) rebased = "./" + rebased;
      return `${pre}${rebased}${post}`;
    });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Manifest editing
// ---------------------------------------------------------------------------

/**
 * Given a manifest text and a file basename (e.g. "Alt1_X.astro"), find
 * the entry block. Returns `{ block, importLine, importedName, before,
 * after }` — the raw text fragments needed for surgery.
 *
 * The parser is line-based, not full TS. It looks for an entry object
 * whose `file:` field ends in the supplied basename, then walks brace
 * depth to find the closing `}`. The import line is matched by
 * destination file path.
 *
 * Returns null when the entry isn't present in the manifest.
 */
function extractEntryBlock(text, fileBasename, fileSubpath) {
  const lines = text.split(/\r?\n/);
  // Locate the entries array start ("export const entries: ... = [").
  let entriesArrayStart = -1;
  for (let i = 0; i < lines.length; i++) {
    if (/export const entries\b.*=\s*\[/.test(lines[i])) {
      entriesArrayStart = i;
      break;
    }
  }
  if (entriesArrayStart === -1) return null;

  // Find the entry whose `file:` line carries fileSubpath as suffix.
  // We accept either "<section>/<basename>" or just the basename to be
  // permissive about manifest authoring style.
  let entryStart = -1;
  let entryEnd = -1;
  let fileLineIndex = -1;
  for (let i = entriesArrayStart + 1; i < lines.length; i++) {
    const ln = lines[i];
    // Heuristic for entry start: a `{` line at base indent inside the
    // entries array.
    if (/^\s*\{\s*$/.test(ln)) {
      // Tentatively walk forward to find the matching `}`.
      let depth = 1;
      let matchedFile = false;
      let localFileLine = -1;
      for (let j = i + 1; j < lines.length; j++) {
        const lj = lines[j];
        for (const ch of lj) {
          if (ch === "{") depth++;
          else if (ch === "}") depth--;
        }
        const m = lj.match(/^\s*file:\s*"([^"]+)"/);
        if (m) {
          const fileVal = m[1];
          if (fileVal === fileSubpath || fileVal.endsWith("/" + fileBasename)) {
            matchedFile = true;
            localFileLine = j;
          }
        }
        if (depth === 0) {
          if (matchedFile) {
            entryStart = i;
            entryEnd = j;
            fileLineIndex = localFileLine;
          }
          i = j; // jump past this entry
          break;
        }
      }
      if (entryStart !== -1) break;
    }
  }
  if (entryStart === -1) return null;

  // Trailing comma on the entry line: standard manifest style ends each
  // entry with `},`. We swallow that too so the array stays well-formed.
  let entryEndAdj = entryEnd;
  if (entryEnd + 1 < lines.length || lines[entryEnd].endsWith(",")) {
    // entryEnd line is the `}` line; check if it has a trailing comma
    if (/^\s*\},?\s*$/.test(lines[entryEnd])) {
      // Already on its own line; nothing extra to swallow.
    }
  }

  // Find the Component import bound to this entry. The block has a line
  // like `Component: SomeName,`; we resolve that name to the import.
  let importedName = null;
  for (let i = entryStart + 1; i <= entryEnd; i++) {
    const m = lines[i].match(/^\s*Component:\s*([A-Za-z_$][\w$]*)\s*,?\s*$/);
    if (m) {
      importedName = m[1];
      break;
    }
  }
  let importLineIndex = -1;
  if (importedName) {
    for (let i = 0; i < entriesArrayStart; i++) {
      const re = new RegExp(`^import\\s+${importedName}\\s+from\\s+"([^"]+)"`);
      if (re.test(lines[i])) {
        importLineIndex = i;
        break;
      }
    }
  }

  return {
    lines,
    entriesArrayStart,
    entryStart,
    entryEnd: entryEndAdj,
    fileLineIndex,
    importedName,
    importLineIndex,
  };
}

/**
 * Remove an entry (and its import line) from a manifest text. Returns
 * the rewritten manifest text plus the extracted block fragments so the
 * destination manifest can re-insert them.
 */
function removeEntryFromManifest(manifestText, fileBasename, fileSubpath) {
  const ex = extractEntryBlock(manifestText, fileBasename, fileSubpath);
  if (!ex) return null;
  const { lines, entryStart, entryEnd, importedName, importLineIndex } = ex;

  // Capture the block + the import line text before mutating.
  const block = lines.slice(entryStart, entryEnd + 1).join("\n");
  const importLine = importLineIndex >= 0 ? lines[importLineIndex] : null;

  // Mark lines for removal: importLine, entryStart..entryEnd. Also drop
  // the trailing empty line right after the entry to avoid double-blank
  // gaps.
  const drop = new Set();
  if (importLineIndex >= 0) drop.add(importLineIndex);
  for (let i = entryStart; i <= entryEnd; i++) drop.add(i);
  if (lines[entryEnd + 1] !== undefined && lines[entryEnd + 1].trim() === "") {
    drop.add(entryEnd + 1);
  }

  const out = lines.filter((_, i) => !drop.has(i)).join("\n");

  return {
    newText: out,
    block,
    importLine,
    importedName,
  };
}

/**
 * Insert an entry block (with import line) into a manifest. The import
 * goes after the last existing import; the entry goes at the END of the
 * entries array.
 */
function insertEntryIntoManifest(manifestText, block, importLine, newFileSubpath) {
  const lines = manifestText.split(/\r?\n/);

  // 1) Insert importLine after the last `^import ` line above the
  // entries array. If no import exists, insert at top of file.
  let lastImportIdx = -1;
  let entriesArrayStart = -1;
  for (let i = 0; i < lines.length; i++) {
    if (entriesArrayStart === -1 && /export const entries\b.*=\s*\[/.test(lines[i])) {
      entriesArrayStart = i;
    }
    if (entriesArrayStart === -1 && /^import\s/.test(lines[i])) {
      lastImportIdx = i;
    }
  }
  if (entriesArrayStart === -1) {
    throw new Error("destination manifest missing `export const entries = [` line");
  }
  if (lastImportIdx === -1) {
    // No existing imports — put it right above the entries array with a
    // blank line.
    lines.splice(entriesArrayStart, 0, importLine, "");
  } else {
    lines.splice(lastImportIdx + 1, 0, importLine);
  }

  // After insertion, re-locate entriesArrayStart since indices shifted.
  let newEntriesStart = -1;
  for (let i = 0; i < lines.length; i++) {
    if (/export const entries\b.*=\s*\[/.test(lines[i])) {
      newEntriesStart = i;
      break;
    }
  }

  // 2) Walk forward from newEntriesStart to find the closing `];` of the
  // array. Track brace + bracket depth so we don't get fooled by braces
  // inside individual entries.
  let bracketDepth = 0;
  let arrayCloseIdx = -1;
  for (let i = newEntriesStart; i < lines.length; i++) {
    for (const ch of lines[i]) {
      if (ch === "[") bracketDepth++;
      else if (ch === "]") {
        bracketDepth--;
        if (bracketDepth === 0) {
          arrayCloseIdx = i;
          break;
        }
      }
    }
    if (arrayCloseIdx !== -1) break;
  }
  if (arrayCloseIdx === -1) {
    throw new Error("destination manifest entries array has no closing `]`");
  }

  // Rewrite the `file:` field inside the block to match newFileSubpath.
  const blockLines = block.split(/\r?\n/).map((ln) => {
    return ln.replace(/^(\s*file:\s*)"[^"]+"/, `$1"${newFileSubpath}"`);
  });
  // Ensure the block ends with `},` (with trailing comma).
  for (let i = blockLines.length - 1; i >= 0; i--) {
    if (/^\s*\}\s*,?\s*$/.test(blockLines[i])) {
      if (!/,\s*$/.test(blockLines[i])) {
        blockLines[i] = blockLines[i].replace(/\}\s*$/, "},");
      }
      break;
    }
  }

  lines.splice(arrayCloseIdx, 0, ...blockLines);
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Path classification
// ---------------------------------------------------------------------------

function classifyZone(absPath) {
  const r = rel(absPath);
  if (r.includes("/_alternatives/")) return "alternatives";
  if (r.includes("/_archive/")) return "archive";
  if (r.startsWith("src/components/charts/")) return "live";
  return "unknown";
}

function sectionDirOf(absPath) {
  // Returns the directory holding the file (where index.ts lives, if at
  // all). For "src/.../_alternatives/labour/Foo.astro" returns the
  // labour dir.
  return path.dirname(absPath);
}

function manifestPath(absDir) {
  return path.join(absDir, "index.ts");
}

function hasManifest(absDir) {
  return fs.existsSync(manifestPath(absDir));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const args = parseArgs(process.argv.slice(2));
const fromAbs = abs(args.from);
const toAbs = abs(args.to);

if (!fs.existsSync(fromAbs)) die(`from-path does not exist: ${rel(fromAbs)}`);
if (fs.existsSync(toAbs)) die(`to-path already exists: ${rel(toAbs)}`);

const fromZone = classifyZone(fromAbs);
const toZone = classifyZone(toAbs);
const fromDir = sectionDirOf(fromAbs);
const toDir = sectionDirOf(toAbs);
const basename = path.basename(fromAbs);
if (path.basename(toAbs) !== basename) {
  // Renames are allowed, but warn — the manifest entry will carry the
  // new basename in its `file:` string regardless.
  // (Soft warning; not fatal.)
  console.warn(
    `move_chart: warning — renaming during move (${basename} -> ${path.basename(toAbs)})`,
  );
}

// Plan summary
console.log("move_chart plan:");
console.log(`  from:  ${rel(fromAbs)}  (zone: ${fromZone})`);
console.log(`  to:    ${rel(toAbs)}    (zone: ${toZone})`);
console.log("");

// 1) Read the file, rewrite imports for the new depth.
const fileTextOrig = fs.readFileSync(fromAbs, "utf-8");
const fileTextNew = rewriteImports(fileTextOrig, fromAbs, toAbs);
const importsChanged = fileTextOrig !== fileTextNew;
if (importsChanged) {
  console.log(`  imports rewritten inside ${path.basename(fromAbs)} for new depth`);
} else {
  console.log(`  no import-path rewrites needed inside ${path.basename(fromAbs)}`);
}

// 2) Source manifest — remove entry.
let sourceManifestUpdate = null;
let extracted = null;
if (hasManifest(fromDir)) {
  const srcManifestText = fs.readFileSync(manifestPath(fromDir), "utf-8");
  // Section sub-path used in `file:` strings is conventionally
  // "<section>/<basename>".
  const fromSection = path.basename(fromDir);
  const fileSubpath = `${fromSection}/${basename}`;
  const r = removeEntryFromManifest(srcManifestText, basename, fileSubpath);
  if (r) {
    extracted = r;
    sourceManifestUpdate = {
      path: manifestPath(fromDir),
      newText: r.newText,
    };
    console.log(
      `  source manifest: ${rel(manifestPath(fromDir))} (remove "${fileSubpath}" entry${r.importLine ? " + import" : ""})`,
    );
  } else {
    console.log(
      `  source manifest: ${rel(manifestPath(fromDir))} (no entry matched basename "${basename}"; nothing to remove)`,
    );
  }
}

// 3) Destination manifest — only when destination is a holding zone.
let destManifestUpdate = null;
if ((toZone === "alternatives" || toZone === "archive") && hasManifest(toDir)) {
  if (!extracted) {
    console.log(
      `  destination manifest: ${rel(manifestPath(toDir))} — no source entry to transfer; manifest will need manual entry`,
    );
  } else {
    const destManifestText = fs.readFileSync(manifestPath(toDir), "utf-8");
    const toSection = path.basename(toDir);
    const newFileSubpath = `${toSection}/${path.basename(toAbs)}`;

    // Compute the new import line. The component name stays the same;
    // the path becomes `./<basename-without-ext>` relative to the
    // destination manifest.
    let importLine = extracted.importLine;
    if (importLine) {
      const nameNoExt = path.basename(toAbs);
      importLine = importLine.replace(
        /from\s+"([^"]+)"/,
        `from "./${nameNoExt}"`,
      );
    } else {
      // No prior import — synthesize one from the component name.
      const componentName = extracted.importedName ?? "MovedChart";
      const nameNoExt = path.basename(toAbs);
      importLine = `import ${componentName} from "./${nameNoExt}";`;
    }

    const newDestText = insertEntryIntoManifest(
      destManifestText,
      extracted.block,
      importLine,
      newFileSubpath,
    );
    destManifestUpdate = {
      path: manifestPath(toDir),
      newText: newDestText,
    };
    console.log(
      `  destination manifest: ${rel(manifestPath(toDir))} (insert entry with file "${newFileSubpath}" + import)`,
    );
  }
} else if (toZone === "live") {
  console.log(
    `  destination zone is live (src/components/charts/<section>/) — no manifest update; SectionLayout.astro chartRegistry edit is required separately`,
  );
}

if (args.dryRun) {
  console.log("");
  console.log("--dry-run set; no files touched, no git mv run");
  process.exit(0);
}

// 4) Apply.
// Ensure destination directory exists.
fs.mkdirSync(toDir, { recursive: true });

// git mv first so git tracks the rename. If git is unavailable or the
// file is untracked, fall back to fs.renameSync.
const gitRes = spawnSync("git", ["mv", fromAbs, toAbs], {
  cwd: repoRoot,
  encoding: "utf-8",
});
if (gitRes.status !== 0) {
  console.warn(
    `  git mv failed (${gitRes.stderr.trim() || "non-zero exit"}); falling back to fs.renameSync`,
  );
  fs.renameSync(fromAbs, toAbs);
}

// Write the import-rewritten file at the new location (if changed).
if (importsChanged) {
  fs.writeFileSync(toAbs, fileTextNew, "utf-8");
}

// Update manifests.
if (sourceManifestUpdate) {
  fs.writeFileSync(sourceManifestUpdate.path, sourceManifestUpdate.newText, "utf-8");
}
if (destManifestUpdate) {
  fs.writeFileSync(destManifestUpdate.path, destManifestUpdate.newText, "utf-8");
}

console.log("");
console.log("move_chart: done.");
