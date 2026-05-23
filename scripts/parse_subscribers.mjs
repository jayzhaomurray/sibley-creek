#!/usr/bin/env node
/*
 * parse_subscribers.mjs — reads business/subscribers.md and reports count,
 * deduped list, and optional latest-N preview.
 *
 * Usage:
 *   node scripts/parse_subscribers.mjs
 *   node scripts/parse_subscribers.mjs --latest 5
 *   node scripts/parse_subscribers.mjs --source subscribe
 *
 * business/subscribers.md format: blocks of key:value pairs separated by
 * blank lines. Required keys: timestamp, email, source.
 * Optional key: message
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOG_PATH = path.resolve(__dirname, "..", "business", "subscribers.md");

function parseArgs(argv) {
  const out = { latest: null, source: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--latest") out.latest = parseInt(argv[++i], 10);
    if (argv[i] === "--source") out.source = argv[++i];
  }
  return out;
}

function parseBlocks(raw) {
  // Strip comment lines, then split on blank lines.
  const lines = raw.split(/\r?\n/).filter((l) => !l.trimStart().startsWith("#"));
  const blocks = lines.join("\n").split(/\n\s*\n/).filter((b) => b.trim());
  const entries = [];
  for (const block of blocks) {
    const obj = {};
    for (const line of block.split(/\r?\n/)) {
      const m = line.match(/^(\w+)\s*:\s*(.*)/);
      if (m) obj[m[1].trim()] = m[2].trim();
    }
    if (obj.email && obj.timestamp) entries.push(obj);
  }
  return entries;
}

function dedup(entries) {
  // Keep latest entry per email (by timestamp string sort).
  const map = new Map();
  for (const e of entries) {
    const key = e.email.toLowerCase();
    if (!map.has(key) || e.timestamp > map.get(key).timestamp) map.set(key, e);
  }
  return [...map.values()].sort((a, b) => (b.timestamp > a.timestamp ? 1 : -1));
}

function main() {
  if (!fs.existsSync(LOG_PATH)) {
    console.error(`subscribers.md not found at ${LOG_PATH}`);
    console.error("Pull from formsubmit API first:  node scripts/pull_subscribers.mjs");
    process.exit(1);
  }

  const args = parseArgs(process.argv.slice(2));
  const raw = fs.readFileSync(LOG_PATH, "utf-8");
  const all = parseBlocks(raw);
  const filtered = args.source ? all.filter((e) => e.source === args.source) : all;
  const unique = dedup(filtered);

  console.log(`\nSibley Creek subscribers`);
  console.log(`------------------------`);
  console.log(`Total submissions : ${filtered.length}`);
  console.log(`Unique emails     : ${unique.length}`);
  if (filtered.length !== all.length) {
    console.log(`Filter active     : source=${args.source}`);
  }

  const show = args.latest ? unique.slice(0, args.latest) : unique;
  if (show.length === 0) {
    console.log("\n(no entries yet)");
    return;
  }

  console.log(`\n${ args.latest ? `Latest ${args.latest}` : "All" } (newest first):`);
  for (const e of show) {
    const msg = e.message ? `  "${e.message.slice(0, 60)}${e.message.length > 60 ? "..." : ""}"` : "";
    console.log(`  ${e.timestamp}  [${e.source}]  ${e.email}${msg}`);
  }
  console.log("");
}

main();
