#!/usr/bin/env node
/*
 * parse_subscribers.mjs — reads business/recipients/recipients.yaml and reports
 * count, list, and optional latest-N preview.
 *
 * Updated 2026-05-23: switched from business/subscribers.md (deprecated) to
 * business/recipients/recipients.yaml (master list).
 *
 * Usage:
 *   node scripts/parse_subscribers.mjs
 *   node scripts/parse_subscribers.mjs --latest 5
 *   node scripts/parse_subscribers.mjs --category subscriber
 *   node scripts/parse_subscribers.mjs --category reporter
 *   node scripts/parse_subscribers.mjs --category all
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");

const RECIPIENTS_PATH = path.resolve(REPO_ROOT, "business", "recipients", "recipients.yaml");
const DEPRECATED_PATH = path.resolve(REPO_ROOT, "business", "subscribers.md");

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const out = { latest: null, category: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--latest") out.latest = parseInt(argv[++i], 10);
    if (argv[i] === "--category") out.category = argv[++i];
  }
  return out;
}

// ---------------------------------------------------------------------------
// Parser
// ---------------------------------------------------------------------------

/**
 * Parse recipients.yaml into an array of entry objects.
 *
 * We do a lightweight block-based parse rather than importing a YAML library:
 * each entry starts with "- email:" and continues until the next "- email:"
 * or end-of-file. Within each block we extract key: value pairs.
 *
 * This is intentionally simple. The file format is controlled and consistent;
 * the only edge case is multi-line `notes:` values written as YAML block
 * scalars (>-), which we read as a single merged string.
 */
function parseRecipients(raw) {
  const entries = [];

  // Split on lines that start a new list item: "- email:"
  // We use the line-by-line approach to handle the block scalar for notes.
  const lines = raw.split(/\r?\n/);
  let current = null;
  let inBlockScalar = false;
  let blockKey = null;
  let blockLines = [];

  function flushBlock() {
    if (current && blockKey) {
      current[blockKey] = blockLines.join(" ").trim();
      blockKey = null;
      blockLines = [];
      inBlockScalar = false;
    }
  }

  function pushEntry() {
    if (current && current.email) {
      entries.push(current);
    }
  }

  for (const rawLine of lines) {
    const line = rawLine;

    // Skip comment lines and blank lines at the top level.
    if (line.trimStart().startsWith("#")) continue;

    // Detect a new entry start.
    const entryStart = line.match(/^- email:\s*([^\s#]+)/);
    if (entryStart) {
      flushBlock();
      pushEntry();
      current = {
        email: entryStart[1].trim().toLowerCase(),
        name: "",
        category: "",
        tier: null,
        source: "",
        outlet: "",
        beat: "",
        added: "",
        active: false,
        notes: "",
      };
      inBlockScalar = false;
      continue;
    }

    if (!current) continue;

    // Detect block scalar continuation (indented lines after a ">-" or ">").
    if (inBlockScalar) {
      // If the line is indented (starts with spaces) and is not a new key, it
      // is a continuation of the block scalar.
      if (/^\s{2,}/.test(line) && !line.match(/^\s{2,}\w+:/)) {
        blockLines.push(line.trim());
        continue;
      } else {
        // End of block scalar.
        flushBlock();
      }
    }

    // Regular key: value line (indented, inside a list item).
    const kvMatch = line.match(/^\s{2}(\w+):\s*(.*)/);
    if (!kvMatch) continue;

    const key = kvMatch[1];
    const val = kvMatch[2].trim();

    // Detect YAML block scalars (>- or >).
    if (val === ">-" || val === ">") {
      inBlockScalar = true;
      blockKey = key;
      blockLines = [];
      continue;
    }

    // Boolean coercion.
    if (key === "active") {
      current[key] = val.toLowerCase() === "true";
      continue;
    }

    // Null coercion.
    if (val === "null" || val === "") {
      current[key] = null;
      continue;
    }

    // Strip surrounding quotes for string values.
    const stripped = val.replace(/^["']|["']$/g, "");
    current[key] = stripped;
  }

  flushBlock();
  pushEntry();

  return entries;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  // Surface deprecation notice if the old file still exists.
  if (fs.existsSync(DEPRECATED_PATH)) {
    console.warn(
      `NOTE: business/subscribers.md still exists and is DEPRECATED.`
    );
    console.warn(
      `      All data has been migrated to business/recipients/recipients.yaml.`
    );
    console.warn(
      `      Delete business/subscribers.md once you have confirmed the migration.\n`
    );
  }

  if (!fs.existsSync(RECIPIENTS_PATH)) {
    console.error(`recipients.yaml not found at ${RECIPIENTS_PATH}`);
    console.error("Run:  node scripts/pull_subscribers.mjs  to sync from formsubmit.");
    process.exit(1);
  }

  const args = parseArgs(process.argv.slice(2));
  const raw = fs.readFileSync(RECIPIENTS_PATH, "utf-8");
  const all = parseRecipients(raw);

  // Category filter. "all" or null = no filter.
  const catFilter = args.category && args.category !== "all" ? args.category : null;
  const filtered = catFilter ? all.filter((e) => e.category === catFilter) : all;

  // Dedup by email (keep last occurrence — matches pull_subscribers append order).
  const map = new Map();
  for (const e of filtered) {
    map.set(e.email, e);
  }
  const unique = [...map.values()].sort((a, b) => {
    // Sort newest-first by added date.
    if (b.added > a.added) return 1;
    if (b.added < a.added) return -1;
    return 0;
  });

  // Summary.
  const activeCount = unique.filter((e) => e.active).length;
  const label = catFilter ? ` [category: ${catFilter}]` : "";

  console.log(`\nSibley Creek recipients${label}`);
  console.log(`${"─".repeat(40)}`);
  console.log(`Total entries  : ${filtered.length}`);
  console.log(`Unique emails  : ${unique.length}`);
  console.log(`Active         : ${activeCount}`);

  // Category breakdown (only when showing all).
  if (!catFilter) {
    const cats = {};
    for (const e of unique) {
      cats[e.category] = (cats[e.category] || 0) + 1;
    }
    for (const [cat, n] of Object.entries(cats).sort()) {
      console.log(`  ${cat.padEnd(12)}: ${n}`);
    }
  }

  const show = args.latest ? unique.slice(0, args.latest) : unique;
  if (show.length === 0) {
    console.log("\n(no entries yet)");
    return;
  }

  console.log(`\n${args.latest ? `Latest ${args.latest}` : "All"} (newest added first):`);
  for (const e of show) {
    const outlet = e.outlet ? ` (${e.outlet})` : "";
    const activeTag = e.active ? "active" : "inactive";
    const notesSnippet = e.notes
      ? `  "${String(e.notes).slice(0, 60)}${String(e.notes).length > 60 ? "..." : ""}"`
      : "";
    console.log(
      `  ${e.added || "?"}  [${e.category}/${activeTag}]  ${e.email}  ${e.name}${outlet}${notesSnippet}`
    );
  }
  console.log("");
}

main();
