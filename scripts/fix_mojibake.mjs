// Recover files corrupted by a botched mojibake-fix pass.
//
// Background:
//   1. PowerShell Get-Content + Set-Content -Encoding utf8 round-trip
//      double-encoded multi-byte UTF-8 chars (em-dashes became the
//      classic three-char mojibake sequence).
//   2. A first version of this script used Buffer.from(str, 'latin1')
//      to undo that -- which only handles codepoints 0-255. Win-1252-
//      specific chars (Euro, right curly quote, TM) got truncated to
//      their low byte, producing invalid UTF-8, which Node replaced
//      with the U+FFFD replacement character on re-decode.
//
// Net effect after that botched fix:
//   - em-dash         (U+2014) -> U+FFFD + U+001D
//   - right dbl quote (U+201D) -> U+FFFD + U+001D  (same; defaults to em-dash)
//   - right sgl quote (U+2019) -> U+FFFD + U+0022  (FFFD + ASCII double-quote)
//   - left  dbl quote (U+201C) -> U+FFFD + U+001C
//   - left  sgl quote (U+2018) -> U+FFFD + U+0018
//   - the leading UTF-8 BOM    -> lone U+FFFD at position 0
//
// Pattern recovery is approximate. Em-dash and right double quote
// share a mojibake fingerprint; we default to em-dash because it's
// dominant in Sibley Creek prose. Manual review welcome.
//
// All special chars built via String.fromCharCode so the source file
// is pure ASCII and survives any encoding hazard during edits.
//
// Usage:  node scripts/fix_mojibake.mjs <file>

import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const [, , inputArg] = process.argv;
if (!inputArg) {
  console.error("usage: node scripts/fix_mojibake.mjs <file>");
  process.exit(1);
}

const path = resolve(process.cwd(), inputArg);
let content = readFileSync(path, "utf8");
const before = content;

const FFFD = String.fromCharCode(0xFFFD);
const EM_DASH = String.fromCharCode(0x2014);
const RIGHT_SINGLE = String.fromCharCode(0x2019);
const LEFT_DOUBLE = String.fromCharCode(0x201C);
const LEFT_SINGLE = String.fromCharCode(0x2018);

// 1. Strip the leading replacement-char if it's the corrupted BOM.
if (content.charCodeAt(0) === 0xFFFD) {
  content = content.slice(1);
}

// 2. Pattern recovery, most specific first.
const patterns = [
  [FFFD + String.fromCharCode(0x001D), EM_DASH],
  [FFFD + String.fromCharCode(0x0022), RIGHT_SINGLE],
  [FFFD + String.fromCharCode(0x001C), LEFT_DOUBLE],
  [FFFD + String.fromCharCode(0x0018), LEFT_SINGLE],
];

for (const [from, to] of patterns) {
  content = content.split(from).join(to);
}

// 3. Any remaining lone U+FFFD defaults to em-dash.
const remainingMatches = content.match(new RegExp(FFFD, "g"));
const remainingCount = remainingMatches ? remainingMatches.length : 0;
if (remainingCount > 0) {
  content = content.split(FFFD).join(EM_DASH);
}

if (content === before) {
  console.log("no change: " + path);
} else {
  writeFileSync(path, content, "utf8");
  console.log("fixed:    " + path + "  (" + remainingCount + " lone FFFD defaulted to em-dash)");
}
