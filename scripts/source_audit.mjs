#!/usr/bin/env node
/*
 * source_audit.mjs - per-section source-coverage audit page generator.
 *
 * Reads:
 *   - src/pages/<section>.astro for plate definitions (title, interpretationHtml,
 *     source, citations[]).
 *   - src/data/sections.ts for the section's blurb.body + headlineQuestion.
 *   - editorial/source_cards/registry.yaml for source-card metadata.
 *
 * Writes:
 *   - editorial/source_cards/audit/<section>.html - per-section audit page.
 *   - editorial/source_cards/audit/index.html - landing index across sections.
 *
 * Per page: the prose AS WRITTEN (section abstract + each plate's title + blurb)
 * with each tagged claim marked by a superscript reference, an inline verbatim
 * excerpt from the source card, and a clickable link that opens the source URL
 * (with optional deep anchor) in a new tab. Untagged numeric tokens are flagged
 * with a yellow background + warning tooltip.
 *
 * Usage:
 *   node scripts/source_audit.mjs [<section>...]    # default: all sections
 *
 * Designed for human review: read the page, click a number, confirm.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const REGISTRY_PATH = path.join(repoRoot, "editorial", "source_cards", "registry.yaml");
const PAGES_DIR = path.join(repoRoot, "src", "pages");
const SECTIONS_TS = path.join(repoRoot, "src", "data", "sections.ts");
const OUTPUT_DIR = path.join(repoRoot, "editorial", "source_cards", "audit");

// Section slugs are auto-discovered from src/pages/*.astro on every run.
// Any .astro file that declares `const plates: Plate[] = [` is a citable
// surface and gets an audit page. Pages that don't (about, methodology,
// chart-archive, etc.) pass through silently.
//
// To exclude a page that has plates but should NOT be audited (rare),
// add its slug to AUDIT_EXEMPTIONS below with a one-line reason.
const AUDIT_EXEMPTIONS = new Set([
  // example: "experimental-foo" — "in-progress alternative, not in production"
]);

function discoverSections() {
  if (!fs.existsSync(PAGES_DIR)) return [];
  const slugs = [];
  for (const file of fs.readdirSync(PAGES_DIR)) {
    if (!file.endsWith(".astro")) continue;
    const slug = file.replace(/\.astro$/, "");
    if (AUDIT_EXEMPTIONS.has(slug)) continue;
    const text = fs.readFileSync(path.join(PAGES_DIR, file), "utf-8");
    if (!/const\s+plates\s*:\s*Plate\[\]\s*=\s*\[/.test(text)) continue;
    slugs.push(slug);
  }
  return slugs.sort();
}

const ALL_SECTIONS = discoverSections();

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

function loadRegistry() {
  const raw = fs.readFileSync(REGISTRY_PATH, "utf-8");
  const reg = parseYaml(raw);
  const sources = reg?.sources ?? [];
  const byId = new Map();
  for (const s of sources) byId.set(s.id, s);
  return byId;
}

// ---------------------------------------------------------------------------
// Plate extraction
// ---------------------------------------------------------------------------

function readAstroFrontmatter(astroPath) {
  let text = fs.readFileSync(astroPath, "utf-8");
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  return m ? m[1] : "";
}

/**
 * Walk forward from `startIdx` (just after an opening `[` or `{`), track
 * brace and bracket depth while staying string-aware. Return the index of
 * the matching closing token.
 */
function findMatchingClose(source, startIdx, openChar, closeChar) {
  let depth = 1;
  let inString = null;
  let escape = false;
  for (let i = startIdx; i < source.length; i++) {
    const ch = source[i];
    if (escape) { escape = false; continue; }
    if (inString) {
      if (ch === "\\") { escape = true; continue; }
      if (ch === inString) inString = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") { inString = ch; continue; }
    if (ch === "/" && source[i + 1] === "/") {
      // line comment
      const nl = source.indexOf("\n", i);
      i = nl === -1 ? source.length : nl;
      continue;
    }
    if (ch === "/" && source[i + 1] === "*") {
      const end = source.indexOf("*/", i + 2);
      i = end === -1 ? source.length : end + 1;
      continue;
    }
    if (ch === openChar) depth++;
    else if (ch === closeChar) {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function splitTopLevelObjects(arrayBody) {
  // arrayBody is the content between `[` and `]` of `const plates = [...]`.
  // We extract each top-level `{...}` object, comma-separated.
  const objects = [];
  let i = 0;
  while (i < arrayBody.length) {
    // skip whitespace + commas + comments
    while (i < arrayBody.length) {
      const ch = arrayBody[i];
      if (ch === " " || ch === "\n" || ch === "\t" || ch === "\r" || ch === ",") {
        i++;
        continue;
      }
      if (ch === "/" && arrayBody[i + 1] === "/") {
        const nl = arrayBody.indexOf("\n", i);
        i = nl === -1 ? arrayBody.length : nl + 1;
        continue;
      }
      if (ch === "/" && arrayBody[i + 1] === "*") {
        const end = arrayBody.indexOf("*/", i + 2);
        i = end === -1 ? arrayBody.length : end + 2;
        continue;
      }
      break;
    }
    if (i >= arrayBody.length) break;
    if (arrayBody[i] !== "{") {
      // unexpected
      break;
    }
    const closeIdx = findMatchingClose(arrayBody, i + 1, "{", "}");
    if (closeIdx === -1) break;
    objects.push(arrayBody.slice(i, closeIdx + 1));
    i = closeIdx + 1;
  }
  return objects;
}

/** Extract `key: <value>` from an object source. Handles string literals,
 *  string concatenation (`"a" + "b"`), and array literals. Returns the raw
 *  value source (un-parsed) or null if not found.
 *
 *  Implementation: single linear scan. No substring slicing — earlier
 *  versions did `objText.slice(i)` at every character position, which is
 *  O(n^2) memory and OOM'd on the GDP page.
 */
function extractField(objText, key) {
  let depth = 0;
  let inString = null;
  let escape = false;
  const keyLen = key.length;
  const n = objText.length;
  const wordBoundary = (c) => c === " " || c === "\t" || c === "\n" || c === "\r" || c === "," || c === "{";

  for (let i = 0; i < n; i++) {
    const ch = objText[i];
    if (escape) { escape = false; continue; }
    if (inString) {
      if (ch === "\\") { escape = true; continue; }
      if (ch === inString) inString = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") { inString = ch; continue; }
    if (ch === "{" || ch === "[") { depth++; continue; }
    if (ch === "}" || ch === "]") { depth--; continue; }

    if (depth !== 1) continue;
    if (i + keyLen >= n) continue;
    // word-boundary check on preceding char
    const prev = i === 0 ? "{" : objText[i - 1];
    if (!wordBoundary(prev)) continue;
    // literal-character match of the key
    let ok = true;
    for (let j = 0; j < keyLen; j++) {
      if (objText[i + j] !== key[j]) { ok = false; break; }
    }
    if (!ok) continue;
    // after key, skip horizontal whitespace, expect ":"
    let j = i + keyLen;
    while (j < n && (objText[j] === " " || objText[j] === "\t")) j++;
    if (objText[j] !== ":") continue;
    // skip ":" + whitespace
    let v = j + 1;
    while (v < n && /\s/.test(objText[v])) v++;
    return extractValue(objText, v);
  }
  return null;
}

function extractValue(source, startIdx) {
  // Skip leading whitespace
  let i = startIdx;
  while (i < source.length && /\s/.test(source[i])) i++;
  const ch = source[i];
  if (ch === '"' || ch === "'") {
    // single string or concatenated chain
    return extractStringChain(source, i);
  }
  if (ch === "[") {
    const close = findMatchingClose(source, i + 1, "[", "]");
    return { kind: "array", text: source.slice(i, close + 1), end: close + 1 };
  }
  if (ch === "{") {
    const close = findMatchingClose(source, i + 1, "{", "}");
    return { kind: "object", text: source.slice(i, close + 1), end: close + 1 };
  }
  // bare token until comma or newline
  let end = i;
  while (end < source.length && source[end] !== "," && source[end] !== "\n") end++;
  return { kind: "literal", text: source.slice(i, end).trim(), end };
}

function extractStringChain(source, startIdx) {
  // Build up `"a" + "b" + "c"` into one concatenated string.
  let i = startIdx;
  let out = "";
  while (i < source.length) {
    // skip whitespace
    while (i < source.length && /\s/.test(source[i])) i++;
    const ch = source[i];
    if (ch !== '"' && ch !== "'") break;
    // read literal
    const quote = ch;
    let str = "";
    i++;
    let escape = false;
    while (i < source.length) {
      const c = source[i];
      if (escape) { str += c; escape = false; i++; continue; }
      if (c === "\\") { escape = true; i++; continue; }
      if (c === quote) { i++; break; }
      str += c;
      i++;
    }
    out += str;
    // skip whitespace, look for `+`
    while (i < source.length && /\s/.test(source[i])) i++;
    if (source[i] === "+") {
      i++;
      continue;
    }
    break;
  }
  return { kind: "string", text: out, end: i };
}

function parseCitations(arrayText) {
  // arrayText is like `[ { phrase: "...", source: "..." }, ... ]`. Strip
  // the outer brackets, split into top-level objects, then parse each.
  //
  // Citation schema (current + new):
  //   { phrase: "<literal>", source: "<src>", note?: "..." }                  -- literal
  //   { slot: "<key>", source: "pipeline:...", at?, value_format?, context?,
  //     note? }                                                                -- slot-bound
  //   { compute: "<expr>", source: "derived", value_format?, context?, note? } -- derived
  //
  // Slot-bound citations carry no `phrase:` — the phrase is computed at build
  // time from `data/site/panel_data/<section>.json` so the citation auto-
  // tracks the live pipeline value. Derived citations evaluate `compute:` over
  // slot values.
  if (!arrayText || arrayText[0] !== "[") return [];
  const inner = arrayText.slice(1, -1);
  const objs = splitTopLevelObjects(inner);
  const out = [];
  for (const objText of objs) {
    const phrase = extractField(objText, "phrase");
    const source = extractField(objText, "source");
    const note = extractField(objText, "note");
    const slot = extractField(objText, "slot");
    const at = extractField(objText, "at");
    const valueFormat = extractField(objText, "value_format");
    const context = extractField(objText, "context");
    const compute = extractField(objText, "compute");
    const expectedCount = extractField(objText, "expected_count");
    if (!source?.text) continue;
    const hasAnchor = phrase?.text || slot?.text || compute?.text;
    if (!hasAnchor) continue;
    out.push({
      phrase: phrase?.text ?? null,
      source: source.text,
      note: note?.text ?? null,
      slot: slot?.text ?? null,
      at: at?.text ?? null,
      value_format: valueFormat?.text ?? null,
      context: context?.text ?? null,
      compute: compute?.text ?? null,
      expected_count: expectedCount?.text ? parseInt(expectedCount.text, 10) : null,
    });
  }
  return out;
}

function extractPlates(sectionAstroPath) {
  const fm = readAstroFrontmatter(sectionAstroPath);
  // find `const plates: Plate[] = [`
  const m = fm.match(/const\s+plates\s*:\s*Plate\[\]\s*=\s*\[/);
  if (!m) return [];
  const arrayStart = m.index + m[0].length;
  const arrayClose = findMatchingClose(fm, arrayStart, "[", "]");
  if (arrayClose === -1) return [];
  const arrayBody = fm.slice(arrayStart, arrayClose);
  const objs = splitTopLevelObjects(arrayBody);
  const plates = [];
  for (const objText of objs) {
    const id = extractField(objText, "id");
    const number = extractField(objText, "number");
    const indicator = extractField(objText, "indicator");
    const plateIndexLabel = extractField(objText, "plateIndexLabel");
    const asOf = extractField(objText, "asOf");
    const title = extractField(objText, "title");
    // Accept both `interpretationHtml:` (canonical) and `interpretation:` (legacy)
    // — some early plates were authored with the unsuffixed name and never
    // migrated; treat them as equivalent so their citations have prose to
    // anchor against.
    const interpretationHtml =
      extractField(objText, "interpretationHtml") ||
      extractField(objText, "interpretation");
    const source = extractField(objText, "source");
    const chartKey = extractField(objText, "chartKey");
    const citations = extractField(objText, "citations");
    plates.push({
      id: id?.text ?? null,
      number: number?.text ?? null,
      indicator: indicator?.text ?? null,
      plateIndexLabel: plateIndexLabel?.text ?? null,
      asOf: asOf?.text ?? null,
      title: title?.text ?? null,
      interpretationHtml: interpretationHtml?.text ?? null,
      source: source?.text ?? null,
      chartKey: chartKey?.text ?? null,
      citations: citations ? parseCitations(citations.text) : [],
    });
  }
  return plates;
}

// ---------------------------------------------------------------------------
// Section abstract extraction (from src/data/sections.ts)
// ---------------------------------------------------------------------------

/** Extract the splashHero { abstract, citations } block from sections.ts. */
function extractSplashHero() {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  const m = text.match(/export const splashHero[:\s][^=]*=\s*\{/);
  if (!m) return { abstract: null, citations: [] };
  const blockStart = m.index + m[0].length;
  const blockClose = findMatchingClose(text, blockStart, "{", "}");
  if (blockClose === -1) return { abstract: null, citations: [] };
  const block = text.slice(blockStart, blockClose);
  const absMatch = block.match(/abstract:\s*/);
  let abstract = null;
  if (absMatch) {
    const aStart = absMatch.index + absMatch[0].length;
    abstract = extractStringChain(block, aStart).text;
  }
  let citations = [];
  const cMatch = block.match(/citations:\s*\[/);
  if (cMatch) {
    const cStart = cMatch.index + cMatch[0].length;
    const cClose = findMatchingClose(block, cStart, "[", "]");
    if (cClose !== -1) {
      citations = parseCitations("[" + block.slice(cStart, cClose) + "]");
    }
  }
  return { abstract, citations };
}

/** Extract { tileLine, tileLineCitations } for one section by slug. */
function extractTileLine(slug) {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  const slugRe = new RegExp(`slug:\\s*"${slug}"`);
  const m = text.match(slugRe);
  if (!m) return { tileLine: null, citations: [] };
  // Walk forward until the NEXT `slug: "..."` or end of file — bounding the
  // slice prevents cross-section citation leakage (e.g. gdp picking up
  // inflation's `tileLineCitations` because no slug delimiter was respected).
  const after = text.slice(m.index + m[0].length);
  const nextSlugMatch = after.match(/slug:\s*"/);
  const sliceEnd = nextSlugMatch ? m.index + m[0].length + nextSlugMatch.index : text.length;
  const slice = text.slice(m.index, sliceEnd);
  const tlMatch = slice.match(/tileLine:\s*/);
  let tileLine = null;
  if (tlMatch) {
    const tlStart = tlMatch.index + tlMatch[0].length;
    tileLine = extractStringChain(slice, tlStart).text;
  }
  let citations = [];
  const cMatch = slice.match(/tileLineCitations:\s*\[/);
  if (cMatch) {
    const cStart = cMatch.index + cMatch[0].length;
    const cClose = findMatchingClose(slice, cStart, "[", "]");
    if (cClose !== -1) {
      citations = parseCitations("[" + slice.slice(cStart, cClose) + "]");
    }
  }
  return { tileLine, citations };
}

function extractSectionAbstract(slug) {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  // Find the section's slug block: `slug: "<slug>",` then within ~3KB find the
  // `blurb: { ... body: "..." ... }` literal.
  const slugRe = new RegExp(`slug:\\s*"${slug}"`);
  const m = text.match(slugRe);
  if (!m) return { headlineQuestion: null, abstract: null };
  const start = m.index;
  // search ahead for `headlineQuestion:` and `body:`
  const slice = text.slice(start, start + 5000);
  const hqMatch = slice.match(/headlineQuestion:\s*([\s\S]*?),\n/);
  const headlineQuestion = hqMatch ? extractStringChain(hqMatch[1], 0).text : null;
  const bodyMatch = slice.match(/body:\s*/);
  let abstract = null;
  if (bodyMatch) {
    const bodyStart = bodyMatch.index + bodyMatch[0].length;
    abstract = extractStringChain(slice, bodyStart).text;
  }
  // ALSO extract `abstractCitations:` if it exists on this section (added below).
  let abstractCitations = [];
  const acMatch = slice.match(/abstractCitations:\s*\[/);
  if (acMatch) {
    const acStart = acMatch.index + acMatch[0].length;
    const acClose = findMatchingClose(slice, acStart, "[", "]");
    if (acClose !== -1) {
      abstractCitations = parseCitations("[" + slice.slice(acStart, acClose) + "]");
    }
  }
  return { headlineQuestion, abstract, abstractCitations };
}

// ---------------------------------------------------------------------------
// HTML rendering
// ---------------------------------------------------------------------------

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function stripHtml(s) {
  return String(s ?? "").replace(/<[^>]+>/g, "").replace(/&mdash;/g, "—").replace(/&[a-z]+;/g, "");
}

/** Given prose + citations, return prose with each citation phrase wrapped in
 *  a <span class="claim" data-cit-idx="N"> marker, plus the list of resolved
 *  citation entries in order of appearance. */
// ---------------------------------------------------------------------------
// Tokenizer + matcher — ports the same logic check_citation_coverage.mjs uses,
// so the audit page can find citable tokens not literally captured by a
// citation's `phrase:` and wrap them either with the matching citation's
// ref number (fuzzy match) or with a red "uncovered" marker.
// ---------------------------------------------------------------------------

const TOKEN_PATTERNS = [
  { re: /-?\d+(?:\.\d+)?\s*%/g },
  { re: /-?\d+(?:\.\d+)?\s+per\s*cent\b/gi },
  { re: /-?\d+(?:\.\d+)?\s*pp\b/g },
  { re: /-?\d+(?:\.\d+)?\s+percentage points?/gi },
  { re: /-?\d+(?:\.\d+)?[- ]points?\b/gi },
  { re: /-?\d+\s*(?:bps|basis points?)/gi },
  { re: /-?\$?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|trillion|bn|tn)\b/gi },
  { re: /\$\d+(?:\.\d+)?(?:k|bn|m|M|tn)?\b/g },
  { re: /-?\d+(?:\.\d+)?k\b/g },
  { re: /\bQ[1-4]\s+(?:19|20)\d{2}\b/g },
  { re: /\b(?:19|20)\d{2}\s*Q[1-4]\b/g },
  { re: /\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(?:19|20)\d{2}\b/g },
  { re: /\b(?:19|20)\d{2}-\d{2}(?:-\d{2})?\b/g },
  { re: /\b(?:19|20)\d{2}\b(?!\s*-\s*\d{2})/g },
];

function stripHtmlForTokens(html) {
  return String(html ?? "")
    .replace(/<span class="claim[^"]*"[^>]*>[\s\S]*?<\/span>/g, " ") // already-wrapped claims
    .replace(/<span class="claim-uncovered"[^>]*>[\s\S]*?<\/span>/g, " ")
    .replace(/<a\b[^>]*>([\s\S]*?)<\/a>/gi, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&mdash;/g, "—")
    .replace(/&ndash;/g, "–")
    .replace(/&amp;/g, "&")
    .replace(/&[a-z]+;/g, " ");
}

function numericVariants(token) {
  const pctSign = token.match(/^(-?)(\d+)(?:\.(\d+))?\s*%$/);
  const pctWord = token.match(/^(-?)(\d+)(?:\.(\d+))?\s+per\s*cent$/i);
  const pct = pctSign || pctWord;
  if (pct) {
    const sign = pct[1] || "";
    const intPart = pct[2];
    const decPart = pct[3];
    const set = new Set([
      `${sign}${intPart}%`,
      `${sign}${intPart}.0%`,
      `${sign}${intPart} percent`,
      `${sign}${intPart} per cent`,
    ]);
    if (decPart) {
      const withDec = `${sign}${intPart}.${decPart}`;
      set.add(`${withDec}%`);
      set.add(`${withDec.replace(/\.?0+$/, "")}%`);
      set.add(`${withDec} percent`);
      set.add(`${withDec} per cent`);
    }
    return Array.from(set);
  }
  const pp = token.match(/^(-?)(\d+)(?:\.(\d+))?\s*pp$/);
  if (pp) {
    const sign = pp[1] || "";
    const intPart = pp[2];
    const decPart = pp[3];
    const base = decPart ? `${sign}${intPart}.${decPart}` : `${sign}${intPart}`;
    return [`${base}pp`, `${base} pp`, `${base} percentage points`, `${base} percentage point`];
  }
  return [];
}

function countNumericTokensInPhrase(phrase) {
  // Count distinct numeric/date tokens in a citation phrase. Used to refuse
  // fuzzy attachment of single-numeric prose tokens to multi-anchor phrases
  // (e.g. "3%" in prose absorbed by "27% of the basket runs above 3%").
  const seen = new Set();
  for (const { re } of TOKEN_PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(phrase)) !== null) {
      seen.add(m[0].trim().toLowerCase());
    }
  }
  return seen.size;
}

function findCoveringCitation(token, citations) {
  const tNorm = token.toLowerCase().replace(/\s+/g, " ").trim();
  const variants = numericVariants(token).map((v) => v.toLowerCase());
  // Numeric tokens need digit-boundary matching so "3%" doesn't bleed inside
  // "23.0%", "13%", etc. Non-numeric tokens (month-year strings, quarters)
  // fall back to plain substring.
  const isNumeric = /^-?\d/.test(tNorm);
  const matchesInPhrase = (cNorm, candidate) => {
    if (!candidate) return false;
    if (isNumeric) {
      const safe = candidate.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const re = new RegExp(`(?<!\\d)${safe}(?!\\d)`);
      return re.test(cNorm);
    }
    return cNorm.includes(candidate);
  };
  for (let i = 0; i < citations.length; i++) {
    const c = citations[i];
    const cNorm = (c.phrase || "").toLowerCase().replace(/\s+/g, " ").trim();
    // Anti-contamination guard: if a citation's phrase contains multiple
    // numeric anchors and the prose token isn't the full phrase, refuse the
    // fuzzy match. Forces the author either to include the full citation
    // phrase literally in prose, or to split the citation into single-anchor
    // entries. Catches "3%" being absorbed by "27% of basket runs above 3%".
    const phraseNumericCount = countNumericTokensInPhrase(c.phrase || "");
    if (phraseNumericCount > 1 && tNorm !== cNorm) continue;
    if (matchesInPhrase(cNorm, tNorm)) return i;
    if (!isNumeric && tNorm.includes(cNorm)) return i;
    for (const v of variants) {
      if (matchesInPhrase(cNorm, v)) return i;
    }
  }
  return -1;
}

/**
 * Wrap a token in the prose, but only at positions that are NOT already inside
 * a <span class="claim"> or <span class="claim-uncovered">. Returns the
 * modified HTML.
 */
/**
 * Same first-occurrence-skipping-existing-spans logic as wrapUnwrappedToken,
 * but takes a fully-formed replacement HTML string (rather than constructing
 * the wrapping span from a class + sup). Use when the wrap needs to include
 * arbitrary attributes (id, data-, inner anchor) that don't fit the simple
 * class-string interface.
 */
function wrapUnwrappedSpan(html, token, replacement) {
  const splitRe = /(<span class="claim[^"]*"[^>]*>[\s\S]*?<\/span>|<span class="claim-uncovered"[^>]*>[\s\S]*?<\/span>)/g;
  const parts = html.split(splitRe);
  const safe = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const tokenRe = new RegExp(`(?<![\\w.])${safe}(?![\\w%])`, "g");
  let wrapped = false;
  const out = parts.map((part, idx) => {
    if (idx % 2 === 1) return part;
    if (wrapped) return part;
    const newPart = part.replace(tokenRe, () => {
      if (wrapped) return token;
      wrapped = true;
      return replacement;
    });
    return newPart;
  });
  return out.join("");
}

function wrapUnwrappedToken(html, token, wrapClass, refSup) {
  // Split the HTML around existing claim/claim-uncovered spans; wrap inside
  // only the unwrapped segments. Using a regex with capture groups for the
  // span boundaries lets us preserve them.
  const splitRe = /(<span class="claim[^"]*"[^>]*>[\s\S]*?<\/span>|<span class="claim-uncovered"[^>]*>[\s\S]*?<\/span>)/g;
  const parts = html.split(splitRe);
  const safe = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // Use a word-ish boundary so we don't double-match "1%" inside "11%".
  const tokenRe = new RegExp(`(?<![\\w.])${safe}(?![\\w%])`, "g");
  const replacement = `<span class="${wrapClass}">${escapeHtml(token)}${refSup}</span>`;
  let wrapped = false;
  const out = parts.map((part, idx) => {
    // Even indices are unwrapped segments; odd indices are the existing spans.
    if (idx % 2 === 1) return part;
    if (wrapped) return part; // only wrap first occurrence per token
    const newPart = part.replace(tokenRe, (m) => {
      if (wrapped) return m;
      wrapped = true;
      return replacement;
    });
    return newPart;
  });
  return out.join("");
}

// Length-budget table per surface type (writing-style.md §4.1f hard caps).
// Build refuses on any cap overrun for shipping surfaces. The 140-word
// policy abstract that survived the prior process would have hard-failed
// here. Soft-target overruns surface as warnings (non-blocking).
const LENGTH_BUDGETS = {
  // Soft targets are the editorial ideal (warnings on overrun).
  // Hard caps are calibrated to the longest currently-shipping surfaces
  // the user has approved; the gate refuses anything beyond.
  // Recalibrate by hand when norms shift.
  "section-abstract": { sentenceMin: 2, sentenceMax: 3, sentenceHardCap: 5, wordMin: 45, wordMax: 75, wordHardCap: 105 },
  "tile-line":        { sentenceMin: 1, sentenceMax: 1, sentenceHardCap: 1, wordMin: 8,  wordMax: 16, wordHardCap: 20, charHardCap: 90 },
  "plate-title":      { sentenceMin: 1, sentenceMax: 1, sentenceHardCap: 2, wordMin: 6,  wordMax: 14, wordHardCap: 22, charHardCap: 110 },
  "plate-blurb":      { sentenceMin: 2, sentenceMax: 4, sentenceHardCap: 6, wordMin: 40, wordMax: 70, wordHardCap: 110 },
  // Splash hero: equalized with section-abstract budget. The hero answers
  // a question with a take + 1-2 grounding numerics, same as a section
  // abstract — just at the whole-economy scope. A heavier hero pushes the
  // tile lines below it down and changes the splash's center of gravity.
  "splash-hero":      { sentenceMin: 2, sentenceMax: 3, sentenceHardCap: 5, wordMin: 45, wordMax: 75, wordHardCap: 105 },
};

function stripHtmlToText(html) {
  return String(html ?? "")
    .replace(/<a\b[^>]*>([\s\S]*?)<\/a>/gi, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&mdash;/g, " ")
    .replace(/&ndash;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&[a-z]+;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function countSentences(text) {
  if (!text) return 0;
  // Treat .?! followed by whitespace or end-of-text as sentence terminators.
  // Em-dashes don't count. Ellipses count as one terminator.
  const parts = text.replace(/\.{3,}/g, ".").split(/[.!?](?:\s+|$)/).filter((s) => s.trim().length > 0);
  return parts.length;
}

function countWords(text) {
  if (!text) return 0;
  return text.split(/\s+/).filter((w) => w.length > 0).length;
}

let LENGTH_VIOLATIONS = [];
let LENGTH_WARNINGS = [];
function resetLengthChecks() { LENGTH_VIOLATIONS = []; LENGTH_WARNINGS = []; }
function getLengthViolations() { return LENGTH_VIOLATIONS; }
function getLengthWarnings() { return LENGTH_WARNINGS; }

function checkLengthBudget(surfaceLabel, surfaceType, rawProse) {
  const budget = LENGTH_BUDGETS[surfaceType];
  if (!budget || !rawProse) return;
  const text = stripHtmlToText(rawProse);
  const sentences = countSentences(text);
  const words = countWords(text);
  const chars = text.length;
  const violations = [];
  const warnings = [];
  if (budget.wordHardCap && words > budget.wordHardCap) {
    violations.push(`${words}W exceeds hard cap ${budget.wordHardCap}W`);
  }
  if (budget.charHardCap && chars > budget.charHardCap) {
    violations.push(`${chars} chars exceeds hard cap ${budget.charHardCap}`);
  }
  if (budget.sentenceHardCap && sentences > budget.sentenceHardCap) {
    violations.push(`${sentences} sentences exceeds hard cap ${budget.sentenceHardCap}`);
  } else if (budget.sentenceMax && sentences > budget.sentenceMax) {
    warnings.push(`${sentences} sentences (target ${budget.sentenceMin}-${budget.sentenceMax})`);
  }
  if (budget.wordMax && words > budget.wordMax && (!budget.wordHardCap || words <= budget.wordHardCap)) {
    warnings.push(`${words}W (target ${budget.wordMin}-${budget.wordMax}W)`);
  }
  if (violations.length) {
    LENGTH_VIOLATIONS.push({ surface: surfaceLabel, surfaceType, sentences, words, chars, violations });
  }
  if (warnings.length) {
    LENGTH_WARNINGS.push({ surface: surfaceLabel, surfaceType, sentences, words, chars, warnings });
  }
}

// Module-level counter for globally-unique inline anchor ids. Each
// annotateProse() call increments this so ids never collide across
// section abstracts, plate blurbs, dive bodies, etc. on the same page.
let GLOBAL_REF_COUNTER = 0;

function resetGlobalRefCounter() { GLOBAL_REF_COUNTER = 0; }

// Module-level collector for citations whose `phrase:` field failed to match
// the prose either literally (Pass 1) or fuzzily (Pass 2). The build gate
// reads this and refuses to ship if any orphans are present — a citation that
// doesn't anchor to prose is silent rot (e.g. author rewrites prose but
// leaves the old citation phrase behind, or arithmetic drifts).
let ORPHAN_CITATIONS = [];
function resetOrphanCitations() { ORPHAN_CITATIONS = []; }
function getOrphanCitations() { return ORPHAN_CITATIONS; }

// Module-level collector for enumeration-count mismatches (Option A): a
// citation declared expected_count but the card's enumeration has a
// different number of entries. Surfaced as a hard build error.
let ENUMERATION_MISMATCHES = [];
function resetEnumerationMismatches() { ENUMERATION_MISMATCHES = []; }
function getEnumerationMismatches() { return ENUMERATION_MISMATCHES; }

// Module-level collector for deep-dive cross-link violations (per
// writing-style.md §4.1f-3): blurbs / abstracts / hero / tile lines may
// not contain `/research/<slug>/` references while dives live as
// AI-generated drafts not yet to standard. Build-gate refuses.
let DEEP_DIVE_LINKS = [];
function resetDeepDiveLinks() { DEEP_DIVE_LINKS = []; }
function getDeepDiveLinks() { return DEEP_DIVE_LINKS; }

function annotateProse(prose, citations, registry, pendingMap = null, surfaceLabel = null, slots = {}) {
  if (!prose) return { html: "", resolved: [] };
  const resolved = [];
  let html = prose;

  // For slot-bound and compute-bound citations, derive the effective phrase
  // from current pipeline data. Assigns `c.phrase` in-place so the rest of
  // the matcher uses the same machinery as author-typed phrases. Failing to
  // resolve means the slot is missing from panel_data — track as a hard
  // error (build refuses) since the citation can't anchor at all.
  citations.forEach((c) => {
    if (c.phrase) return;
    if (c.slot || c.compute) {
      const eff = effectivePhraseForCitation(c, slots, registry);
      if (eff) {
        c.phrase = eff;
        c._slotResolved = true;
      } else {
        c._slotResolveFailed = true;
        c.phrase = c.phrase || `<unresolved slot:${c.slot || ""}${c.compute ? " compute:" + c.compute : ""}>`;
      }
    }
  });

  // Pass 1 — literal phrase match for each citation. Pending citations get
  // class "claim claim-pending" (amber); approved citations get the standard
  // yellow "claim" class. Both link to their ledger entry via data-ref.
  citations.forEach((c, idx) => {
    const phrase = c.phrase;
    const card = resolveSource(c.source, registry, pendingMap);
    GLOBAL_REF_COUNTER++;
    const globalId = GLOBAL_REF_COUNTER;
    // refNum == globalId. The visible [N] number is unique across the entire
    // audit page so every inline citation and ledger entry has a one-to-one
    // address. This eliminates duplicate-id bugs that arose when the same
    // card was cited from multiple plates and all inline anchors competed
    // for a single `id="card-<id>"` in the ledger.
    resolved.push({ ...c, ...card, refNum: globalId, globalId, inlineMatched: false });
    const safe = phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const klass = card.isPending ? "claim claim-pending" : "claim";
    const replacement = `<span class="${klass}" id="ref-${globalId}" data-ref="${globalId}"><a href="#ledger-${globalId}" class="claim-anchor">${escapeHtml(phrase)}<sup class="claim-sup">[${globalId}]</sup></a></span>`;
    const before = html;
    html = html.replace(new RegExp(safe), replacement);
    if (html !== before) resolved[idx].inlineMatched = true;
  });

  // Pass 2 — find citable tokens NOT already wrapped, classify each:
  //   covered (fuzzy match against a citation's normalized phrase + variants)
  //     → wrap with that citation's ref (yellow, dashed-under to distinguish)
  //   uncovered (no citation matches even fuzzily)
  //     → wrap with claim-uncovered (red underline)
  const plain = stripHtmlForTokens(html);
  const seen = new Set();
  for (const { re } of TOKEN_PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(plain)) !== null) {
      const tok = m[0].trim();
      if (!tok || seen.has(tok)) continue;
      seen.add(tok);
      const coveringIdx = findCoveringCitation(tok, citations);
      if (coveringIdx >= 0) {
        const r = resolved[coveringIdx];
        // If Pass 1 didn't place an id anchor for this citation, the fuzzy
        // match is the first inline span — mark it with the citation's
        // globalId so the ledger's [N] back-link has a target.
        const idAttr = r.inlineMatched ? "" : ` id="ref-${r.globalId}"`;
        const replacement = `<span class="claim claim-fuzzy" data-ref="${r.refNum}"${idAttr}><a href="#ledger-${r.globalId}" class="claim-anchor">${escapeHtml(tok)}<sup class="claim-sup">[${r.refNum}]</sup></a></span>`;
        const before = html;
        html = wrapUnwrappedSpan(html, tok, replacement);
        if (html !== before) resolved[coveringIdx].inlineMatched = true;
      } else {
        // Uncovered token — no citation matches. Before red-flagging, run a
        // reverse-lookup against the section's pipeline slots: if this token
        // matches a slot's current formatted value, suggest the slot in the
        // warning tooltip so the author knows which citation to add.
        const slotHint = suggestSlotForToken(tok, slots);
        const hintText = slotHint
          ? `Uncovered. Probable pipeline slot: ${slotHint.key} (${slotHint.label}) currently ${slotHint.formatted} as of ${slotHint.date}. Consider adding: { slot: "${slotHint.key}", at: "latest", value_format: "${slotHint.value_format}", context: "...", source: "..." }`
          : "No citation matches this token. Either tighten the sidecar phrase or add a new citation.";
        if (slotHint) UNCOVERED_HINTS.push({ surface: surfaceLabel || "(unknown)", token: tok, slot: slotHint.key, formatted: slotHint.formatted });
        const replacement = `<span class="claim-uncovered">${escapeHtml(tok)}<sup class="claim-uncovered-sup" title="${escapeHtml(hintText)}">⚠</sup></span>`;
        html = wrapUnwrappedSpan(html, tok, replacement);
      }
    }
  }

  // Deep-dive cross-link gate (§4.1f-3): scan prose for `/research/<slug>/`
  // references. Each match = build failure unless we relax the rule.
  const deepDiveMatches = (prose || "").match(/\/research\/[a-z0-9-]+\//g);
  if (deepDiveMatches?.length) {
    for (const m of deepDiveMatches) {
      DEEP_DIVE_LINKS.push({
        surface: surfaceLabel || "(unknown)",
        href: m,
      });
    }
  }

  // Record orphan citations (phrase failed to anchor in prose).
  for (let i = 0; i < citations.length; i++) {
    if (!resolved[i].inlineMatched) {
      ORPHAN_CITATIONS.push({
        surface: surfaceLabel || "(surface label not provided by caller)",
        phrase: citations[i].phrase,
        source: citations[i].source,
        note: citations[i].note || null,
      });
    }
    // Enumeration-count validation (Option A path): when a citation declares
    // expected_count, the referenced card MUST be an enumeration card whose
    // `enumeration:` list has exactly that many entries. Catches "fourth
    // consecutive hold" where the underlying enumeration grew/shrank but
    // prose wasn't updated.
    const c = citations[i];
    if (c.expected_count != null && typeof c.source === "string" && c.source.startsWith("card:")) {
      const cardId = c.source.slice(5);
      const card = registry?.get ? registry.get(cardId) : null;
      const enumLen = Array.isArray(card?.enumeration) ? card.enumeration.length : null;
      if (enumLen !== c.expected_count) {
        ENUMERATION_MISMATCHES.push({
          surface: surfaceLabel || "(unknown)",
          phrase: c.phrase,
          source: c.source,
          expected: c.expected_count,
          actual: enumLen,
        });
      }
    }
  }

  return { html, resolved };
}

// Canonical BoC pipeline catalog — slot name → Valet series ID. Authored
// from pipeline/catalog/boc_series.py; keep in sync if catalog entries are
// added/renamed. The map serves two purposes: (1) translate internal slot
// names (e.g. yield_2yr, fxusdcad) into the real Valet ID so the ledger
// "Open source ↗" link lands on the right Valet page, (2) drive the build-
// gate validator that refuses citations using BoC keys not in the catalog
// (catches hallucinated names like STATIC_TOTALCPICOMMON_TRIM).
const BOC_SLOT_TO_VALET = {
  yield_2yr: "BD.CDN.2YR.DQ.YLD",
  yield_5yr: "BD.CDN.5YR.DQ.YLD",
  yield_10yr: "BD.CDN.10YR.DQ.YLD",
  yield_30yr: "BD.CDN.LONG.DQ.YLD",
  tbill_3m: "V80691344",
  corra_daily: "AVG.INTWO",
  overnight_rate: "STATIC_ATABLE_V39079",
  overnight_rate_daily: "V39079",
  cpi_trim: "CPI_TRIM",
  cpi_median: "CPI_MEDIAN",
  cpi_common: "CPI_COMMON",
  cpix: "ATOM_V41693242",
  cpixfet: "STATIC_CPIXFET",
  cpi_ex_indirect_taxes: "MPR_2025M04_CPI_TAX_S1",
  infl_exp_consumer_1y: "CES_C1_SHORT_TERM",
  infl_exp_consumer_5y: "CES_C1_LONG_TERM",
  infl_exp_above3: "ABOVE3",
  bos_dist_below1: "INDINF_BOSBELOW1_Q",
  bos_dist_1to2: "INDINF_BOS1TO2_Q",
  bos_dist_2to3: "INDINF_BOS2TO3_Q",
  bos_dist_above3: "INDINF_BOSOVER3_Q",
  lfs_micro: "INDINF_LFSMICRO_M",
  output_gap_mpr: "INDINF_OUTGAPMPR_Q",
  crea_mls_hpi: "FVI_CREA_MLS_HPI_CANADA",
  crea_snlr: "FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA",
  housing_affordability: "INDINF_AFFORD_Q",
  mortgage_rate_5yr: "V80691335",
  fxusdcad: "FXUSDCAD",
  fxeurcad: "FXEURCAD",
  fxgbpcad: "FXGBPCAD",
  fxjpycad: "FXJPYCAD",
  ceer_broad_daily: "CEER_BROADN",
  ceer_broad_monthly_real: "CEER_BROADM",
  ceer_broad_excl_us_daily: "CEER_BROADN_XUS",
  bcpi: "M.BCPI",
  bcnei: "M.BCNE",
  term_premium_10y_acm: "FVI_TP_GOC_10Y_ACM",
  term_premium_10y_shadow: "FVI_TP_GOC_10Y_SHADOWRATE",
  financial_stress_index_can: "FVI_FSI_CAN",
  boc_total_assets: "V36610",
  boc_goc_bonds: "V36613",
  boc_settlement_balances: "V36636",
  boc_tbills: "V36612",
  boc_repos: "V44201362",
  boc_advances: "V36634",
  boc_total_liabilities: "V36624",
  boc_banknotes: "V36625",
  boc_goc_deposits: "V36628",
  boc_reverse_repos: "V1203435186",
  // V-aliases the catalog uses informally
  V39079: "V39079",
};
const BOC_VALID_VALET = new Set(Object.values(BOC_SLOT_TO_VALET));

// -----------------------------------------------------------------------
// Slot-bound citation resolver — single-source-of-truth for pipeline data
// in prose.
// -----------------------------------------------------------------------
// Citations bound by `slot:` reference a series key in
// data/site/panel_data/<section>.json. The annotator looks up the slot's
// current value, formats it, and finds the matching span in prose. When
// pipeline refreshes, the slot value changes; the only thing the author
// must update is the prose numeric (and the build fails until they do).
// Eliminates hardcoded `phrase: "2.3% in March"` strings that drift on
// every refresh.

const PANEL_SLOT_CACHE = {};
function loadPanelSlots(sectionSlug) {
  if (PANEL_SLOT_CACHE[sectionSlug] !== undefined) return PANEL_SLOT_CACHE[sectionSlug];
  const p = path.join(repoRoot, "data", "site", "panel_data", `${sectionSlug}.json`);
  if (!fs.existsSync(p)) {
    PANEL_SLOT_CACHE[sectionSlug] = {};
    return PANEL_SLOT_CACHE[sectionSlug];
  }
  const data = JSON.parse(fs.readFileSync(p, "utf-8"));
  const slots = {};
  function walk(node) {
    if (!node || typeof node !== "object") return;
    if (Array.isArray(node.data) && typeof node.key === "string") {
      slots[node.key] = { label: node.label || node.key, series: node.data };
      return;
    }
    if (Array.isArray(node)) { for (const x of node) walk(x); return; }
    for (const k of Object.keys(node)) walk(node[k]);
  }
  walk(data);
  PANEL_SLOT_CACHE[sectionSlug] = slots;
  return slots;
}

function resolveSlotValue(slotEntry, atSpec) {
  // atSpec: "latest" (default), "T-N" for N steps back, "YYYY-MM" or
  // "YYYY-MM-DD" for an explicit observation.
  if (!slotEntry?.series?.length) return null;
  const s = slotEntry.series.filter((p) => p?.value != null);
  if (!s.length) return null;
  const at = (atSpec || "latest").trim();
  if (at === "latest") return s[s.length - 1];
  const tMatch = at.match(/^T-(\d+)$/i);
  if (tMatch) {
    const n = parseInt(tMatch[1], 10);
    return s[s.length - 1 - n] ?? null;
  }
  // Explicit date — accept YYYY-MM (anchor to month-1) or YYYY-MM-DD.
  const monthOnly = at.match(/^(\d{4})-(\d{2})$/);
  if (monthOnly) {
    const target = `${monthOnly[1]}-${monthOnly[2]}-01`;
    return s.find((p) => (p.date || "").startsWith(target)) || s.find((p) => (p.date || "").startsWith(`${monthOnly[1]}-${monthOnly[2]}`)) || null;
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(at)) {
    return s.find((p) => p.date === at) || null;
  }
  return null;
}

function formatSlotValue(value, fmt) {
  // Format spec for NUMBERS: "{0.1}%" = one decimal, % suffix; "{int}%" =
  // integer percent; "{0.2}" = two decimals no unit; "{0.1}-point" = one
  // decimal, hyphen-point suffix; etc. Default: "{0.1}%".
  //
  // Format spec for DATE values (returned by prior_above/prior_below): any
  // spec containing date tokens like "{quarter}", "{month_year}", "{month}",
  // "{year}" — substituted from the ISO date string.
  if (value == null || (typeof value === "number" && Number.isNaN(value))) return null;
  const spec = (fmt || "{0.1}%").trim();
  // Date input — value is an ISO date string.
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    if (/\{(month|month_abbr|year|month_year|quarter)\}/.test(spec)) {
      return substituteDateTokens(spec, value);
    }
    return value;
  }
  // Numeric input.
  const m = spec.match(/^\{(int|\d*\.?\d+)\}(.*)$/);
  if (!m) return null;
  const precision = m[1];
  const suffix = m[2] || "";
  let formatted;
  if (precision === "int") {
    formatted = String(Math.round(value));
  } else if (precision.startsWith("0.")) {
    const decimals = (precision.split(".")[1] || "0").length;
    formatted = value.toFixed(decimals);
  } else {
    formatted = String(value);
  }
  return `${formatted}${suffix}`;
}

function evalCompute(expr, slots, registryCards = {}) {
  // Compute DSL has two forms:
  //   1. Arithmetic:  `cpi_all_items_yoy@latest - cpi_all_items_yoy@T-1`
  //   2. Function:    `count_consecutive_at_latest(overnight_rate)`
  //                    `prior_below(output_gap_mpr, output_gap_mpr@latest)`
  //                    `count_enumeration(boc_fad_calendar_2026, after="2025-10-29")`
  //
  // Function form is detected when the trimmed expr matches `<name>(...)`
  // with balanced parens. Arithmetic form is the existing simple-arithmetic
  // path (numbers, slot refs, + - * / ( )).
  //
  // Returns either a number (counts, arithmetic) or an ISO date string
  // (prior_above, prior_below). The formatter handles both — number specs
  // like `{0.1}%` for numbers, date-token specs like `{quarter}` for dates.
  if (typeof expr !== "string") return null;
  const trimmed = expr.trim();
  const fnMatch = trimmed.match(/^([a-z_][a-z0-9_]*)\s*\(([\s\S]*)\)\s*$/i);
  if (fnMatch) {
    // Verify the parens are the outermost (not e.g. `a(b) + c(d)`).
    let depth = 0;
    let outermost = true;
    for (let i = 0; i < trimmed.length; i++) {
      if (trimmed[i] === "(") depth++;
      else if (trimmed[i] === ")") { depth--; if (depth === 0 && i < trimmed.length - 1) { outermost = false; break; } }
    }
    if (outermost) return evalComputeFunction(fnMatch[1], fnMatch[2], slots, registryCards);
  }
  // Arithmetic form — existing logic.
  const tokens = trimmed.match(/[A-Za-z_][A-Za-z0-9_]*(?:@[A-Za-z0-9\-_]+)?|[\d.]+|[+\-*/() ]/g);
  if (!tokens) return null;
  const substituted = tokens.map((t) => {
    if (/^[+\-*/() ]$/.test(t) || /^[\d.]+$/.test(t)) return t;
    const [key, atSpec] = t.split("@");
    if (!slots[key]) return null;
    const obs = resolveSlotValue(slots[key], atSpec || "latest");
    if (!obs) return null;
    return String(obs.value);
  });
  if (substituted.includes(null)) return null;
  const safeExpr = substituted.join("");
  if (!/^[\d.+\-*/() ]+$/.test(safeExpr)) return null;
  try {
    // eslint-disable-next-line no-new-func
    return Function(`"use strict"; return (${safeExpr});`)();
  } catch {
    return null;
  }
}

// Compute-DSL function dispatch — handles countable/enumeration primitives.
// Each primitive takes positional or named args and returns either a number
// (counts) or an ISO date (prior_above/prior_below).
function evalComputeFunction(name, argsText, slots, registryCards) {
  const args = parseComputeArgs(argsText);
  if (args === null) return null;
  const slotArg = (idx) => {
    const a = args.positional[idx];
    if (!a || a.kind !== "ref") return null;
    return a;
  };
  const numArg = (idx) => {
    const a = args.positional[idx];
    if (!a) return null;
    if (a.kind === "number") return a.value;
    if (a.kind === "ref") {
      const obs = resolveSlotValue(slots[a.key], a.atSpec || "latest");
      if (!obs) return null;
      return obs.value;
    }
    return null;
  };
  switch (name) {
    case "count_consecutive_at_latest": {
      // count_consecutive_at_latest(slot) — N successive obs from end where
      // value == latest observation's value.
      const ref = slotArg(0); if (!ref) return null;
      const entry = slots[ref.key]; if (!entry?.series?.length) return null;
      const s = entry.series.filter((p) => p?.value != null);
      if (!s.length) return null;
      const latest = s[s.length - 1].value;
      let n = 0;
      for (let i = s.length - 1; i >= 0; i--) {
        if (s[i].value === latest) n++; else break;
      }
      return n;
    }
    case "count_consecutive_above": {
      // count_consecutive_above(slot, threshold)
      const ref = slotArg(0); if (!ref) return null;
      const threshold = numArg(1); if (threshold == null) return null;
      const entry = slots[ref.key]; if (!entry?.series?.length) return null;
      const s = entry.series.filter((p) => p?.value != null);
      let n = 0;
      for (let i = s.length - 1; i >= 0; i--) {
        if (s[i].value > threshold) n++; else break;
      }
      return n;
    }
    case "count_consecutive_below": {
      const ref = slotArg(0); if (!ref) return null;
      const threshold = numArg(1); if (threshold == null) return null;
      const entry = slots[ref.key]; if (!entry?.series?.length) return null;
      const s = entry.series.filter((p) => p?.value != null);
      let n = 0;
      for (let i = s.length - 1; i >= 0; i--) {
        if (s[i].value < threshold) n++; else break;
      }
      return n;
    }
    case "prior_below": {
      // prior_below(slot, threshold) — earliest prior obs (excluding latest)
      // where slot value < threshold. Returns ISO date.
      const ref = slotArg(0); if (!ref) return null;
      const threshold = numArg(1); if (threshold == null) return null;
      const entry = slots[ref.key]; if (!entry?.series?.length) return null;
      const s = entry.series.filter((p) => p?.value != null);
      for (let i = s.length - 2; i >= 0; i--) {
        if (s[i].value < threshold) return s[i].date;
      }
      return null;
    }
    case "prior_above": {
      const ref = slotArg(0); if (!ref) return null;
      const threshold = numArg(1); if (threshold == null) return null;
      const entry = slots[ref.key]; if (!entry?.series?.length) return null;
      const s = entry.series.filter((p) => p?.value != null);
      for (let i = s.length - 2; i >= 0; i--) {
        if (s[i].value > threshold) return s[i].date;
      }
      return null;
    }
    case "count_enumeration": {
      // count_enumeration(card_id, after=<date>?, before=<date>?)
      // Counts entries in a registered card's `enumeration:` field within
      // an optional date window. Used for FAD sequences, calendar lists, etc.
      const refArg = args.positional[0];
      if (!refArg || refArg.kind !== "ref") return null;
      const card = registryCards?.get ? registryCards.get(refArg.key) : registryCards[refArg.key];
      if (!card?.enumeration) return null;
      const after = args.named.after;
      const before = args.named.before;
      let n = 0;
      for (const entry of card.enumeration) {
        const date = typeof entry === "string" ? entry : entry.date;
        if (!date) continue;
        if (after && date <= after) continue;
        if (before && date > before) continue;
        n++;
      }
      return n;
    }
    default:
      return null;
  }
}

// Parse compute function args. Supports positional + named.
//   arg := <number> | <slot_or_card_ref> | <quoted_string> | <name>=<value>
// Returns { positional: [...], named: {...} } or null on parse failure.
function parseComputeArgs(text) {
  const out = { positional: [], named: {} };
  const trimmed = (text || "").trim();
  if (!trimmed) return out;
  // Split on top-level commas (no nesting expected in v1).
  const parts = trimmed.split(",").map((s) => s.trim()).filter(Boolean);
  for (const raw of parts) {
    // Named: name=value
    const namedMatch = raw.match(/^([a-z_][a-z0-9_]*)\s*=\s*(.+)$/i);
    if (namedMatch) {
      const key = namedMatch[1];
      const valRaw = namedMatch[2].trim();
      const strMatch = valRaw.match(/^["'](.+)["']$/);
      out.named[key] = strMatch ? strMatch[1] : valRaw;
      continue;
    }
    // Number
    if (/^-?\d+(?:\.\d+)?$/.test(raw)) {
      out.positional.push({ kind: "number", value: parseFloat(raw) });
      continue;
    }
    // Quoted string
    const strMatch = raw.match(/^["'](.+)["']$/);
    if (strMatch) {
      out.positional.push({ kind: "string", value: strMatch[1] });
      continue;
    }
    // Slot / card ref (with optional @at)
    const refMatch = raw.match(/^([a-z_][a-z0-9_]*)(?:@([a-z0-9\-_]+))?$/i);
    if (refMatch) {
      out.positional.push({ kind: "ref", key: refMatch[1], atSpec: refMatch[2] || null });
      continue;
    }
    return null;
  }
  return out;
}

const MONTH_ABBRS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function substituteDateTokens(text, isoDate) {
  // Replace {month}, {month_abbr}, {year}, {month_year}, {quarter} in `text`
  // with values derived from the observation date. Returns null if any token
  // is referenced but the date is missing.
  if (!text) return text;
  if (!/\{(month|month_abbr|year|month_year|quarter)\}/.test(text)) return text;
  if (!isoDate) return null;
  const m = isoDate.match(/^(\d{4})-(\d{2})/);
  if (!m) return null;
  const year = m[1];
  const monthIdx = parseInt(m[2], 10) - 1;
  const month = MONTH_NAMES[monthIdx];
  const monthAbbr = MONTH_ABBRS[monthIdx];
  const quarter = `Q${Math.floor(monthIdx / 3) + 1}`;
  return text
    .replace(/\{month_abbr\}/g, monthAbbr)
    .replace(/\{month_year\}/g, `${month} ${year}`)
    .replace(/\{month\}/g, month)
    .replace(/\{year\}/g, year)
    .replace(/\{quarter\}/g, `${quarter} ${year}`);
}

// Reverse-lookup hint: given an uncovered prose token (e.g. "2.3%"), check
// whether it matches the current formatted value of any pipeline slot in
// this section. If yes, surface the slot so the author knows which
// citation they probably forgot to add.
function suggestSlotForToken(token, slots) {
  if (!token || !slots) return null;
  const formats = ["{0.1}%", "{0.2}%", "{int}%", "{0.1}-point", "{0.1}pp", "{int} bps"];
  for (const key of Object.keys(slots)) {
    const entry = slots[key];
    const obs = resolveSlotValue(entry, "latest");
    if (!obs) continue;
    for (const fmt of formats) {
      const formatted = formatSlotValue(obs.value, fmt);
      if (!formatted) continue;
      if (formatted.toLowerCase() === token.toLowerCase()) {
        return { key, label: entry.label, formatted, value_format: fmt, date: obs.date };
      }
    }
  }
  return null;
}

// Module-level collector for reverse-lookup hints — surfaced at end of build
// as advisory output (non-blocking).
let UNCOVERED_HINTS = [];
function resetUncoveredHints() { UNCOVERED_HINTS = []; }
function getUncoveredHints() { return UNCOVERED_HINTS; }

// Compose the effective phrase a slot-bound citation expects to find in
// prose. Used in place of the author-typed `phrase:` field. Supports
// date-token substitution in `context:` ({month}, {year}, etc.) so a
// refresh that bumps the latest observation also updates the prose
// expectation automatically.
function effectivePhraseForCitation(citation, slots, registryCards = null) {
  if (citation.phrase) return citation.phrase;
  if (citation.slot) {
    const entry = slots[citation.slot];
    if (!entry) return null;
    const obs = resolveSlotValue(entry, citation.at);
    if (!obs) return null;
    const formatted = formatSlotValue(obs.value, citation.value_format);
    if (!formatted) return null;
    const ctx = substituteDateTokens(citation.context, obs.date);
    if (ctx === null) return null;
    return ctx ? `${formatted} ${ctx}`.trim() : formatted;
  }
  if (citation.compute) {
    const value = evalCompute(citation.compute, slots, registryCards);
    if (value == null) return null;
    const formatted = formatSlotValue(value, citation.value_format);
    if (!formatted) return null;
    // For compute, use the latest observation date across referenced slots.
    let latestDate = null;
    const refs = (citation.compute.match(/[A-Za-z_][A-Za-z0-9_]*(?:@[A-Za-z0-9\-_]+)?/g) || []);
    for (const ref of refs) {
      const [key, atSpec] = ref.split("@");
      if (!slots[key]) continue;
      const obs = resolveSlotValue(slots[key], atSpec || "latest");
      if (obs?.date && (!latestDate || obs.date > latestDate)) latestDate = obs.date;
    }
    const ctx = substituteDateTokens(citation.context, latestDate);
    if (ctx === null) return null;
    return ctx ? `${formatted} ${ctx}`.trim() : formatted;
  }
  return null;
}

// Module-level collector for invalid BoC pipeline keys. Refused by the
// build gate (next to ORPHAN_CITATIONS).
let INVALID_BOC_KEYS = [];
function resetInvalidBocKeys() { INVALID_BOC_KEYS = []; }
function getInvalidBocKeys() { return INVALID_BOC_KEYS; }

/**
 * Build an external source URL for a pipeline:<provider>:<key> citation.
 * Returns the URL string + a human-readable label for the provider/key.
 */
function resolvePipelineUrl(pipelineKey) {
  // Format: pipeline:<provider>:<key>  e.g. pipeline:statcan:14-10-0287-01
  // Some entries omit the provider (legacy): pipeline:yield_2yr → unknown.
  const parts = pipelineKey.split(":");
  if (parts.length < 3) {
    return {
      label: `pipeline series: ${parts.slice(1).join(":")}`,
      url: null,
      providerLabel: "pipeline (provider unspecified)",
    };
  }
  const provider = parts[1];
  const key = parts.slice(2).join(":");

  switch (provider) {
    case "statcan": {
      // Strip dashes for the pid query param.
      const pid = key.replace(/-/g, "");
      return {
        label: `StatCan Table ${key}`,
        url: `https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=${pid}`,
        providerLabel: "Statistics Canada",
      };
    }
    case "boc": {
      // BoC Valet resolution path:
      //   1. If key is a known internal slot (e.g. yield_2yr, cpi_trim,
      //      fxusdcad), resolve to the catalog's canonical Valet ID.
      //   2. If key already looks like a Valet ID format AND is in our
      //      registered set, use it directly.
      //   3. If key is uppercase-Valet-shaped but not in the registry, the
      //      author may be citing a Valet ID we haven't catalogued — link
      //      to it speculatively but flag for review.
      //   4. Anything else (lowercase non-slot, or otherwise unknown) is
      //      an invalid citation; the build gate will refuse.
      // Use the OBSERVATIONS endpoint, not the series-metadata endpoint.
      // /valet/series/<key> returns only {name, label, description} — useless
      // for verifying a value. /valet/observations/<key>/json?recent=24
      // returns the recent observations as JSON, which browsers render as a
      // tree and lets the editor eye-check the cited value against the data.
      const valetObsUrl = (k) => `https://www.bankofcanada.ca/valet/observations/${k}/json?recent=24`;
      const slotResolved = BOC_SLOT_TO_VALET[key];
      if (slotResolved) {
        return {
          label: `BoC Valet ${slotResolved} (pipeline slot ${key}) — recent 24 observations`,
          url: valetObsUrl(slotResolved),
          providerLabel: "Bank of Canada (Valet observations)",
        };
      }
      const looksLikeValet = /^[A-Z][A-Z0-9_.]*$/.test(key) || /^V\d+$/.test(key);
      if (looksLikeValet && BOC_VALID_VALET.has(key)) {
        return {
          label: `BoC Valet ${key} — recent 24 observations`,
          url: valetObsUrl(key),
          providerLabel: "Bank of Canada (Valet observations)",
        };
      }
      // Unknown key — log for the build gate, but still emit a URL the
      // editor can click through to confirm/deny existence.
      INVALID_BOC_KEYS.push(key);
      return {
        label: `BoC pipeline series ${key} (UNVERIFIED)`,
        url: looksLikeValet
          ? valetObsUrl(key)
          : `https://www.bankofcanada.ca/valet/lists/series?term=${encodeURIComponent(key)}`,
        providerLabel: "Bank of Canada (Valet · unverified)",
      };
    }
    case "fred": {
      return {
        label: `FRED ${key}`,
        url: `https://fred.stlouisfed.org/series/${key}`,
        providerLabel: "FRED (St. Louis Fed)",
      };
    }
    case "dof": {
      return {
        label: `DoF Fiscal Monitor ${key}`,
        url: "https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor.html",
        providerLabel: "Department of Finance Canada",
      };
    }
    case "gov_ab": {
      return {
        label: `Alberta gov ${key}`,
        url: "https://economicdashboard.alberta.ca/dashboard/",
        providerLabel: "Government of Alberta",
      };
    }
    case "ircc": {
      return {
        label: `IRCC ${key}`,
        url: "https://www.canada.ca/en/immigration-refugees-citizenship.html",
        providerLabel: "Immigration, Refugees and Citizenship Canada",
      };
    }
    case "indeed": {
      return {
        label: `Indeed Hiring Lab ${key}`,
        url: "https://www.hiringlab.org/canada/",
        providerLabel: "Indeed Hiring Lab",
      };
    }
    default:
      return {
        label: `pipeline:${provider}:${key}`,
        url: null,
        providerLabel: `provider unknown: ${provider}`,
      };
  }
}

/**
 * Render the verification-tier badge for a resolved citation.
 * Returns inline HTML; empty string if no badge applies.
 *
 * Pipeline citations → "PIPELINE" (green) — auto-refreshed, primary chain.
 * Derived citations → no badge (arithmetic from other tagged claims).
 * Card citations → tier-specific badge:
 *   Tier A → "PRIMARY VERIFIED" (green) — researcher fetched primary.
 *   Tier B with user_confirmed_at → "TRIANGULATED · approved YYYY-MM-DD" (amber).
 *   Tier B unconfirmed → "AWAITING VERIFICATION" (red, pending).
 *   Tier C → "SECONDARY · approved YYYY-MM-DD" (orange) or "AWAITING VERIFICATION".
 *   Mode 3 → "ANALYSIS · approved YYYY-MM-DD" (red) or "AWAITING APPROVAL".
 *   Grandfathered Tier B → same as approved Tier B but suffixed " · grandfathered".
 */
function renderTierBadge(r) {
  if (r.kind === "pipeline") {
    return `<span class="tier-badge tier-pipeline" title="Auto-refreshed via the data pipeline; reproducible from primary URL">PIPELINE</span>`;
  }
  if (r.kind === "card") {
    const tier = r.verification_tier;
    const isMode3 = r.mode === 3;
    if (isMode3) {
      if (r.user_approved_at) {
        return `<span class="tier-badge tier-mode3" title="Analysis citation of a named third-party; user approved ${r.user_approved_at}">ANALYSIS · approved ${r.user_approved_at}</span>`;
      }
      return `<span class="tier-badge tier-pending" title="Mode 3 analysis citation pending user approval">AWAITING APPROVAL</span>`;
    }
    if (tier === "A") {
      return `<span class="tier-badge tier-a" title="Primary verified — researcher fetched the primary source and extracted the verbatim excerpt">PRIMARY VERIFIED</span>`;
    }
    if (tier === "B") {
      if (r.user_confirmed_at) {
        const gf = r.grandfathered ? " · grandfathered" : "";
        return `<span class="tier-badge tier-b" title="Triangulated across 2+ independent credible secondaries; user approved ${r.user_confirmed_at}">TRIANGULATED · approved ${r.user_confirmed_at}${gf}</span>`;
      }
      return `<span class="tier-badge tier-pending" title="Tier B card pending user approval; site cannot ship until walked">AWAITING VERIFICATION</span>`;
    }
    if (tier === "C") {
      if (r.user_confirmed_at) {
        return `<span class="tier-badge tier-c" title="Single credible secondary; user approved ${r.user_confirmed_at}">SECONDARY · approved ${r.user_confirmed_at}</span>`;
      }
      return `<span class="tier-badge tier-pending" title="Tier C card pending user approval">AWAITING VERIFICATION</span>`;
    }
    return `<span class="tier-badge tier-untagged" title="Card has no verification_tier — backfill needed">UNTAGGED</span>`;
  }
  if (r.kind === "card-missing") {
    return `<span class="tier-badge tier-error" title="Referenced card not in registry">CARD MISSING</span>`;
  }
  if (r.kind === "other") {
    return `<span class="tier-badge tier-other" title="other: source — should be promoted to a registered card">OTHER (deprecated)</span>`;
  }
  return "";
}

/**
 * Load all pending cards under editorial/source_cards/_pending/<surface>/<id>.yaml
 * into a single Map<id, card> with a `pendingSurface` field tagging which
 * directory the card came from. Used by resolveSource to surface pending
 * cards as a verifiable kind="card" with isPending=true.
 */
function loadAllPendingCards() {
  const dir = path.join(repoRoot, "editorial", "source_cards", "_pending");
  const map = new Map();
  if (!fs.existsSync(dir)) return map;
  for (const sub of fs.readdirSync(dir)) {
    const subPath = path.join(dir, sub);
    let isDir;
    try { isDir = fs.statSync(subPath).isDirectory(); } catch { continue; }
    if (!isDir) continue;
    for (const f of fs.readdirSync(subPath)) {
      if (!f.endsWith(".yaml")) continue;
      try {
        const raw = fs.readFileSync(path.join(subPath, f), "utf-8");
        const parsed = parseYaml(raw);
        if (parsed?.id) map.set(parsed.id, { ...parsed, pendingSurface: sub });
      } catch (e) {
        console.error(`failed to parse pending card ${path.join(subPath, f)}: ${e.message}`);
      }
    }
  }
  return map;
}

function resolveSource(srcId, registry, pendingMap = null) {
  if (!srcId) return { kind: "unknown", label: "(no source)", url: null, excerpt: null };
  if (srcId.startsWith("card:")) {
    const id = srcId.slice(5);
    let card = registry.get(id);
    let isPending = false;
    if (!card && pendingMap) {
      card = pendingMap.get(id);
      if (card) isPending = true;
    }
    if (!card) return { kind: "card-missing", label: `card:${id} (NOT IN REGISTRY)`, url: null, excerpt: null };
    return {
      kind: "card",
      cardId: id,
      label: card.title,
      url: (card.url || "") + (card.anchor || ""),
      excerpt: card.excerpt || null,
      verified_at: card.verified_at,
      next_expected: card.next_expected,
      vintage_label: card.vintage_label,
      verification_tier: card.verification_tier || null,
      user_confirmed_at: card.user_confirmed_at || null,
      user_confirmed_by: card.user_confirmed_by || null,
      grandfathered: card.grandfathered === true,
      mode: card.mode || null,
      user_approved_at: card.user_approved_at || null,
      isPending,
      pendingSurface: card.pendingSurface || null,
      triangulation: card.triangulation || null,
      cardNotes: card.notes || null,
      verified_value: card.verified_value || null,
    };
  }
  if (srcId.startsWith("pipeline:")) {
    const p = resolvePipelineUrl(srcId);
    return {
      kind: "pipeline",
      label: p.label,
      url: p.url,
      providerLabel: p.providerLabel,
      excerpt: "Auto-refreshed via the Sibley Creek data pipeline. Click through to verify the upstream source publishes the same value.",
    };
  }
  if (srcId === "derived") {
    return { kind: "derived", label: "Derived (arithmetic from other tagged claims)", url: null, excerpt: null };
  }
  if (srcId.startsWith("other:")) {
    return {
      kind: "other",
      label: srcId.slice(6),
      url: null,
      excerpt: "Source flagged as outside the registered source-card set. Add to editorial/source_cards/registry.yaml when promoted to a load-bearing claim.",
    };
  }
  return { kind: "other", label: srcId, url: null, excerpt: null };
}

function loadPipelineFreshness(slug) {
  const panelDataPath = path.join(repoRoot, "data", "site", "panel_data", `${slug}.json`);
  if (!fs.existsSync(panelDataPath)) return null;
  try {
    const raw = JSON.parse(fs.readFileSync(panelDataPath, "utf-8"));
    return {
      generatedAt: raw.generatedAt ?? null,
      panelCount: raw.panels ? Object.keys(raw.panels).length : 0,
    };
  } catch (e) {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Reference date resolution — every pipeline citation note carries the
// underlying print's reference date so a verifier can eye-scan WHICH print.
// ---------------------------------------------------------------------------

const PANEL_DATA_CACHE = new Map();
function loadPanelData(slug) {
  if (PANEL_DATA_CACHE.has(slug)) return PANEL_DATA_CACHE.get(slug);
  const p = path.join(repoRoot, "data", "site", "panel_data", `${slug}.json`);
  if (!fs.existsSync(p)) {
    PANEL_DATA_CACHE.set(slug, null);
    return null;
  }
  try {
    const raw = JSON.parse(fs.readFileSync(p, "utf-8"));
    PANEL_DATA_CACHE.set(slug, raw);
    return raw;
  } catch {
    PANEL_DATA_CACHE.set(slug, null);
    return null;
  }
}

/** Classify cadence from the gap between the last two dates in a series. */
function inferCadence(data) {
  if (!data || data.length < 2) return "unknown";
  const last = new Date(data[data.length - 1].date);
  const prior = new Date(data[data.length - 2].date);
  const gapDays = (last - prior) / (1000 * 60 * 60 * 24);
  if (gapDays > 80) return "quarterly";
  if (gapDays > 20) return "monthly";
  if (gapDays > 5) return "weekly";
  return "daily";
}

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function formatReferenceDate(isoDate, cadence) {
  if (!isoDate) return null;
  const d = new Date(isoDate);
  if (Number.isNaN(d.getTime())) return null;
  const year = d.getUTCFullYear();
  const month = d.getUTCMonth();
  const day = d.getUTCDate();
  if (cadence === "quarterly") {
    const q = Math.floor(month / 3) + 1;
    return `Q${q} ${year}`;
  }
  if (cadence === "monthly") return `${MONTH_NAMES[month]} ${year}`;
  // weekly / daily / unknown → full date
  return `${MONTH_NAMES[month]} ${day}, ${year}`;
}

/** Latest date + cadence for a specific panel's primary series. */
function plateReferenceDate(slug, chartKey) {
  if (!chartKey) return null;
  const pd = loadPanelData(slug);
  if (!pd?.panels) return null;
  // chartKey is "gdp-panel-1" → panel key "panel-1"
  const panelKey = chartKey.replace(/^[^-]+-/, "");
  const panel = pd.panels[panelKey];
  if (!panel?.primary?.data?.length) return null;
  const data = panel.primary.data;
  const cadence = inferCadence(data);
  return { isoDate: data[data.length - 1].date, cadence, formatted: formatReferenceDate(data[data.length - 1].date, cadence) };
}

/** Freshest date across every panel for a section — used for section abstracts
 *  and splash tile lines where the claim isn't scoped to a specific plate. */
function sectionFreshestDate(slug) {
  const pd = loadPanelData(slug);
  if (!pd?.panels) return null;
  let best = null;
  for (const panel of Object.values(pd.panels)) {
    const data = panel?.primary?.data;
    if (!data?.length) continue;
    const cadence = inferCadence(data);
    const iso = data[data.length - 1].date;
    if (!best || new Date(iso) > new Date(best.isoDate)) {
      best = { isoDate: iso, cadence, formatted: formatReferenceDate(iso, cadence) };
    }
  }
  return best;
}

/** Augment a citation note with the reference date when the note doesn't
 *  already name a date. Only applies to pipeline-tagged citations. */
function augmentNoteWithDate(note, source, refDate) {
  if (!refDate?.formatted) return note;
  if (!source || !source.startsWith("pipeline:")) return note;
  if (!note) return `Reference period: ${refDate.formatted}.`;
  // If the note already names a year (e.g. "2024") or a month name,
  // assume the writer has already dated it.
  if (/\b(19|20)\d{2}\b/.test(note)) return note;
  if (/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b/i.test(note)) return note;
  if (/\bQ[1-4]\b/i.test(note)) return note;
  const stripped = note.replace(/\.\s*$/, "");
  return `${stripped}, ${refDate.formatted}.`;
}

const SHARED_CSS = `
* { box-sizing: border-box; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 16px;
  line-height: 1.55;
  color: #111;
  background: #f7f6f1;
  margin: 0;
}
.wrap {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 40px;
  align-items: start;
}
header.page-head {
  grid-column: 1 / -1;
  border-bottom: 2px solid #111;
  padding-bottom: 16px;
  margin-bottom: 16px;
}
header.page-head h1 {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #444;
}
header.page-head .breadcrumb a {
  color: #666;
  text-decoration: none;
  margin-right: 16px;
}
header.page-head .breadcrumb a:hover { color: #000; text-decoration: underline; }
main {
  background: white;
  padding: 32px;
  border: 1px solid #ddd;
}
.headline-q {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #111;
}
.section-label {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #888;
  margin-bottom: 4px;
}
.abstract {
  font-size: 17px;
  line-height: 1.6;
  border-left: 3px solid #c00;
  padding-left: 16px;
  margin: 24px 0 40px 0;
  color: #222;
}
.plate {
  border-top: 1px solid #ccc;
  padding: 24px 0;
}
.plate-number {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #888;
  margin-bottom: 4px;
}
.plate-title {
  font-size: 20px;
  font-weight: 700;
  margin: 4px 0 10px 0;
  color: #111;
}
.plate-meta {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  color: #777;
  margin-bottom: 12px;
}
.plate-blurb { font-size: 16px; line-height: 1.6; color: #222; }
.plate-source-line {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  color: #666;
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px dotted #ccc;
}
.claim {
  background: #fffbcc;
  padding: 1px 2px;
  border-bottom: 2px solid #e6c200;
  cursor: pointer;
}
.claim:hover {
  background: #fff299;
}
.claim-pending {
  background: #ffe5a0;
  border-bottom: 2px solid #c83a00;
}
.claim-pending:hover {
  background: #ffd680;
}
.claim-anchor {
  color: inherit;
  text-decoration: none;
}
.ledger-ref-link {
  text-decoration: none;
}
.ledger-ref-link:hover .ledger-ref {
  filter: brightness(1.1);
  outline: 2px solid #006699;
}
/* Flash the target when the user clicks a cross-link, both directions. */
.claim:target,
.claim-pending:target {
  animation: flash-yellow 1.5s ease-out;
  scroll-margin-top: 80px;
}
.ledger-item:target {
  animation: flash-blue 1.5s ease-out;
  scroll-margin-top: 80px;
}
@keyframes flash-yellow {
  0% { background: #ff8c00; outline: 3px solid #ff8c00; outline-offset: 2px; }
  100% { background: inherit; outline: none; }
}
@keyframes flash-blue {
  0% { background: #b3d9ff; outline: 3px solid #006699; outline-offset: 2px; }
  100% { background: inherit; outline: none; }
}
.verify-toolbar {
  background: #fbe8e8;
  border: 1px solid #c83a00;
  padding: 12px 16px;
  margin-top: 14px;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  align-items: center;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.verify-toolbar .nav-btn {
  background: white;
  color: #c83a00;
  border: 1px solid #c83a00;
  padding: 6px 12px;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  font-family: "Helvetica Neue", Arial, sans-serif;
  margin-right: 6px;
}
.verify-toolbar .nav-btn:hover { background: #c83a00; color: white; }
.verify-toolbar-counts { line-height: 1.5; }
.verify-toolbar-counts .amber { color: #c83a00; font-weight: 600; }
.verify-toolbar-counts .green { color: #2a7a30; font-weight: 600; }
.verify-toolbar-counts .red { color: #c33; font-weight: 600; }
.export-btn {
  background: #006699;
  color: white;
  border: none;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  font-family: "Helvetica Neue", Arial, sans-serif;
}
.export-btn:hover { background: #00557e; }
.export-btn:disabled { background: #888; cursor: not-allowed; }
.export-toast {
  font-size: 12px;
  color: #2a7a30;
  font-weight: 600;
  margin-left: 8px;
  display: none;
}
.export-toast.show { display: inline; }
.ledger-item-pending {
  border-left: 4px solid #c83a00;
  padding-left: 8px;
  background: #fff7e6;
  margin-top: 8px;
}
.ledger-item-pending.decision-approve { border-left-color: #2a7a30; background: #f0f8f0; }
.ledger-item-pending.decision-reject { border-left-color: #c33; background: #fbe8e8; }
.ledger-item-pending.flash-target {
  animation: flash-amber 1.5s ease-out;
}
@keyframes flash-amber {
  0% { background: #ff8c00; outline: 3px solid #ff8c00; outline-offset: 2px; }
  100% { background: #fff7e6; outline: none; }
}
.pending-decision-block { margin-top: 10px; }
.pending-values, .pending-triangulation, .pending-card-notes {
  margin: 8px 0;
  font-size: 12px;
}
.pending-triangulation.muted { color: #888; font-style: italic; }
.secondaries { list-style: none; padding: 0; margin: 4px 0 0 0; }
.secondary { padding: 6px 8px; background: #f8f7ec; border-left: 2px solid #999; margin-bottom: 4px; font-size: 12px; }
.secondary-credibility { font-size: 11px; color: #555; margin-top: 2px; }
.secondary-excerpt { margin: 4px 0 0 0; padding: 4px 8px; background: white; font-style: italic; color: #444; font-size: 11px; line-height: 1.4; }
.verified-values { list-style: none; padding: 0; margin: 4px 0; }
.verified-values li { padding: 3px 6px; background: #f3f3ef; margin-bottom: 2px; font-family: var(--font-mono, monospace); font-size: 11px; }
.verified-values code { background: transparent; font-size: 10px; color: #444; }
fieldset.decision {
  border: 1px solid #c83a00;
  padding: 10px 14px;
  margin-top: 8px;
  background: white;
}
fieldset.decision legend {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #c83a00;
  padding: 0 6px;
}
fieldset.decision label {
  display: block;
  margin: 4px 0;
  font-size: 12px;
  cursor: pointer;
}
fieldset.decision label input { margin-right: 6px; }
.comment-row { margin-top: 8px; }
.comment-row label { font-size: 10px; color: #555; }
.comment-row textarea {
  width: 100%;
  font-family: Georgia, serif;
  font-size: 11px;
  padding: 4px 6px;
  border: 1px solid #c8c0a0;
  box-sizing: border-box;
  resize: vertical;
}
.claim-fuzzy {
  /* Fuzzy match — same yellow as a literal phrase match, but with a dashed
     underline to flag that the citation's phrase: didn't match verbatim and
     the sidecar should be tightened on the next editorial pass. */
  border-bottom-style: dashed;
}
.claim-sup {
  color: #b07b00;
  font-weight: 700;
  font-size: 0.8em;
  margin-left: 1px;
}
.claim-uncovered {
  /* No citation matches this token at all — true gap. The audit page surfaces
     it so the user can either tighten a sidecar phrase or add a new citation. */
  background: #fbe8e8;
  padding: 1px 2px;
  border-bottom: 2px solid #c33;
  cursor: help;
}
.claim-uncovered-sup {
  color: #c33;
  font-weight: 700;
  font-size: 0.85em;
  margin-left: 1px;
}
aside.ledger {
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  background: #fff;
  border: 1px solid #ddd;
  padding: 16px;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
}
aside.ledger h2 {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  margin: 0 0 12px 0;
  color: #444;
}
.ledger-group { margin-bottom: 20px; }
.ledger-group-h {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
  color: #555;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid #ddd;
}
.ledger-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.ledger-ref {
  display: inline-block;
  background: #e6c200;
  color: white;
  padding: 1px 6px;
  font-weight: 700;
  font-size: 11px;
  border-radius: 2px;
  margin-right: 6px;
}
.ledger-ref.pipeline { background: #2a7a30; }
.ledger-ref.derived { background: #888; }
.ledger-ref.unknown, .ledger-ref.card-missing, .ledger-ref.other { background: #c33; }
.ledger-phrase {
  font-style: italic;
  color: #333;
  display: block;
  margin: 4px 0;
}
.ledger-source-label { font-weight: 600; color: #222; font-size: 12px; }
.tier-badge {
  display: inline-block;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  margin-left: 6px;
  border-radius: 2px;
  vertical-align: middle;
  white-space: nowrap;
}
.tier-pipeline { background: #2a7a30; color: white; }
.tier-a { background: #2a7a30; color: white; }
.tier-b { background: #b07b00; color: white; }
.tier-c { background: #c47000; color: white; }
.tier-mode3 { background: #8a3a4a; color: white; }
.tier-pending { background: #c33; color: white; }
.tier-untagged { background: #777; color: white; }
.tier-error { background: #c33; color: white; }
.tier-other { background: #888; color: white; font-style: italic; }
.no-inline-match {
  display: inline-block;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  margin-left: 6px;
  border-radius: 2px;
  vertical-align: middle;
  background: #c33;
  color: white;
  cursor: help;
}
.ledger-excerpt {
  margin: 6px 0;
  padding: 8px 10px;
  background: #f3f3ef;
  color: #444;
  font-size: 12px;
  font-style: italic;
  line-height: 1.4;
  border-left: 2px solid #999;
}
.ledger-meta { font-size: 11px; color: #777; }
.ledger-link {
  display: inline-block;
  margin-top: 4px;
  color: #006699;
  text-decoration: none;
  font-weight: 600;
}
.ledger-link:hover { text-decoration: underline; }
.freshness {
  margin-top: 10px;
  padding: 8px 12px;
  background: #eef5f3;
  border-left: 3px solid #2a7a30;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  color: #2a4f30;
}
.freshness-label { font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; font-size: 10px; }
.freshness-stamp { font-family: var(--font-mono, monospace); margin-left: 6px; }
.freshness-meta { color: #555; margin-left: 12px; }
.freshness-hint { display: block; margin-top: 4px; color: #555; font-style: italic; }
.note-line { font-size: 11px; color: #888; margin-top: 4px; font-style: italic; }
footer.audit-foot {
  grid-column: 1 / -1;
  border-top: 1px solid #ccc;
  padding: 20px 0;
  font-size: 12px;
  color: #777;
  font-family: "Helvetica Neue", Arial, sans-serif;
}
.edit-btn {
  display: inline-block;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #006699;
  background: transparent;
  border: 1px solid #006699;
  padding: 3px 8px;
  margin-left: 8px;
  cursor: pointer;
  vertical-align: middle;
}
.edit-btn:hover { background: #006699; color: white; }
.edit-form {
  margin-top: 12px;
  padding: 14px;
  background: #f8f7ec;
  border: 1px solid #d8c773;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
  display: none;
}
.edit-form.open { display: block; }
.edit-form label {
  display: block;
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #666;
  margin: 8px 0 4px 0;
}
.edit-form textarea, .edit-form input[type="text"] {
  width: 100%;
  font-family: Georgia, serif;
  font-size: 14px;
  padding: 6px 8px;
  border: 1px solid #c8c0a0;
  background: white;
  box-sizing: border-box;
}
.edit-form textarea { min-height: 80px; line-height: 1.5; resize: vertical; }
.edit-form .row { display: flex; gap: 8px; align-items: center; margin-top: 12px; }
.edit-form .row .primary {
  background: #006699;
  color: white;
  border: none;
  padding: 6px 14px;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
}
.edit-form .row .primary:hover { background: #00557e; }
.edit-form .row .toast {
  font-size: 12px;
  color: #2a7a30;
  font-weight: 600;
  margin-left: 8px;
  display: none;
}
.edit-form .row .toast.show { display: inline; }
.edit-form .hint {
  font-size: 11px;
  color: #888;
  font-style: italic;
  margin-top: 4px;
}
.tile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 32px;
}
.tile {
  border: 1px solid #ddd;
  padding: 16px;
  background: #fbfaf5;
}
.tile-section-label {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #888;
  margin-bottom: 6px;
}
.tile-line {
  font-size: 15px;
  line-height: 1.5;
  color: #222;
}
.dive-body {
  font-size: 16px;
  line-height: 1.65;
  color: #222;
}
.dive-body h1, .dive-body h2, .dive-body h3 {
  font-family: "Helvetica Neue", Arial, sans-serif;
  color: #111;
  margin-top: 32px;
}
.dive-body h1 { font-size: 22px; }
.dive-body h2 { font-size: 18px; }
.dive-body h3 { font-size: 15px; text-transform: uppercase; letter-spacing: 0.1em; color: #444; }
.dive-body p { margin: 12px 0; }
.dive-body ul, .dive-body ol { margin: 12px 0; padding-left: 24px; }
.dive-body code { font-family: var(--font-mono, monospace); font-size: 0.92em; background: #f0efe8; padding: 1px 4px; }
`;

function renderPage(slug, headlineQuestion, abstract, abstractCitations, plates, registry, now, pendingMap = null) {
  resetGlobalRefCounter();
  const freshness = loadPipelineFreshness(slug);
  const sectionRefDate = sectionFreshestDate(slug);
  const slots = loadPanelSlots(slug);

  checkLengthBudget(`${slug} · section abstract`, "section-abstract", abstract);
  const sectionAbs = annotateProse(abstract, abstractCitations || [], registry, pendingMap, `${slug} · section abstract`, slots);
  sectionAbs.resolved.forEach((r) => { r.note = augmentNoteWithDate(r.note, r.source, sectionRefDate); });

  const plateRenders = plates.map((p) => {
    checkLengthBudget(`${slug} · ${p.id || "plate"} title`, "plate-title", p.title);
    checkLengthBudget(`${slug} · ${p.id || "plate"} blurb`, "plate-blurb", p.interpretationHtml);
    // Combine plate title + blurb so a single citation phrase can match in
    // either surface. The sentinel `<<SC_SPLIT>>` separates them — it
    // contains no digit/percent tokens so TOKEN_PATTERNS won't touch it,
    // and the literal phrase matcher won't span it because the regex
    // engine respects the dot-not-newline default and our prose phrases
    // don't include the sentinel string anyway.
    const SPLIT = "<<SC_SPLIT>>";
    const combined = `${p.title || ""}\n${SPLIT}\n${p.interpretationHtml || ""}`;
    const annotated = annotateProse(combined, p.citations || [], registry, pendingMap, `${slug} · ${p.id || "plate"}`, slots);
    const sentinelIdx = annotated.html.indexOf(SPLIT);
    const titleHtml = sentinelIdx >= 0 ? annotated.html.slice(0, sentinelIdx).trim() : escapeHtml(p.title || "");
    const blurbHtml = sentinelIdx >= 0 ? annotated.html.slice(sentinelIdx + SPLIT.length).trim() : annotated.html;
    const blurb = { html: blurbHtml, resolved: annotated.resolved };
    const plateRef = plateReferenceDate(slug, p.chartKey) || sectionRefDate;
    blurb.resolved.forEach((r) => { r.note = augmentNoteWithDate(r.note, r.source, plateRef); });
    return { ...p, blurb, titleHtml, referenceDate: plateRef };
  });

  // Aggregate every resolved citation across the section to drive the
  // verification toolbar + script (only rendered when pending claims exist).
  const allResolved = [
    ...sectionAbs.resolved,
    ...plateRenders.flatMap((p) => p.blurb.resolved || []),
  ];
  const pendingCount = allResolved.filter((r) => r.isPending).length;

  const renderLedgerItem = (r) => {
    const kindClass = r.kind || "unknown";
    const itemClass = r.isPending ? "ledger-item ledger-item-pending" : "ledger-item";
    // Every ledger entry gets a unique id keyed off globalId so each prose
    // citation lands on its own entry — no duplicate-id collisions when the
    // same card backs multiple claims across plates.
    const anchorId = `id="ledger-${r.globalId}"`;
    const linkBlock = r.url
      ? `<a class="ledger-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener">Open source ↗</a>`
      : "";
    const excerptBlock = r.excerpt
      ? `<div class="ledger-excerpt">${escapeHtml(r.excerpt)}</div>`
      : "";
    const metaBits = [];
    if (r.vintage_label) metaBits.push(escapeHtml(r.vintage_label));
    if (r.verified_at) metaBits.push(`verified ${escapeHtml(r.verified_at)}`);
    if (r.next_expected) metaBits.push(`next ${escapeHtml(r.next_expected)}`);
    const metaBlock = metaBits.length ? `<div class="ledger-meta">${metaBits.join(" · ")}</div>` : "";
    const noteBlock = r.note ? `<div class="note-line">${escapeHtml(r.note)}</div>` : "";

    // Pending cards get a triangulation block + decision radios inline.
    let pendingBlock = "";
    if (r.isPending) {
      const triHtml = (r.triangulation || []).map((sec) => `
        <li class="secondary">
          ${sec.url ? `<a href="${escapeHtml(sec.url)}" target="_blank" rel="noopener"><strong>${escapeHtml(sec.source || "")}</strong></a>` : `<strong>${escapeHtml(sec.source || "")}</strong>`}
          ${sec.credibility ? `<div class="secondary-credibility">${escapeHtml(sec.credibility)}</div>` : ""}
          ${sec.excerpt ? `<blockquote class="secondary-excerpt">${escapeHtml(sec.excerpt)}</blockquote>` : ""}
        </li>`).join("");
      const triBlock = r.triangulation && r.triangulation.length
        ? `<div class="pending-triangulation"><strong>Triangulated secondaries:</strong><ul class="secondaries">${triHtml}</ul></div>`
        : `<div class="pending-triangulation muted">No triangulation block on the card. Either verify the primary directly in your browser, or reject.</div>`;
      const verifiedValuesHtml = (r.verified_value && typeof r.verified_value === "object")
        ? `<div class="pending-values"><strong>Data points the card establishes:</strong><ul class="verified-values">${Object.entries(r.verified_value).map(([k, v]) => `<li><code>${escapeHtml(k)}</code>: <strong>${escapeHtml(String(v))}</strong></li>`).join("")}</ul></div>`
        : "";
      const cardNotesBlock = r.cardNotes ? `<div class="pending-card-notes">${escapeHtml(r.cardNotes)}</div>` : "";
      pendingBlock = `
        <div class="pending-decision-block">
          ${verifiedValuesHtml}
          ${triBlock}
          ${cardNotesBlock}
          <fieldset class="decision" data-claim-id="${escapeHtml(r.cardId)}">
            <legend>Your decision</legend>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="pending" checked> Not yet verified</label>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="approve"> Approve</label>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="reject"> Reject</label>
            <div class="comment-row">
              <label for="comment-${escapeHtml(r.cardId)}">Comment (required if rejecting):</label>
              <textarea id="comment-${escapeHtml(r.cardId)}" rows="2"></textarea>
            </div>
          </fieldset>
        </div>`;
    }

    // Suppress back-link to inline span when the citation didn't match the
    // prose — there's no #ref-globalId target to land on.
    const refBlock = r.inlineMatched === false
      ? `<span class="ledger-ref ${kindClass} ledger-ref-orphan">[${r.refNum}]</span>`
      : `<a href="#ref-${r.globalId}" class="ledger-ref-link"><span class="ledger-ref ${kindClass}">[${r.refNum}]</span></a>`;
    return `
      <div class="${itemClass}" ${anchorId}>
        ${refBlock}
        <span class="ledger-source-label">${escapeHtml(r.label)}</span>${renderTierBadge(r)}${r.inlineMatched === false ? `<span class="no-inline-match" title="The citation phrase does not appear in the published prose. Either tighten the phrase to match verbatim, or the citation is orphaned (no longer referenced).">no inline match</span>` : ``}
        <div class="ledger-phrase">"${escapeHtml(r.phrase)}"</div>
        ${excerptBlock}
        ${metaBlock}
        ${noteBlock}
        ${linkBlock}
        ${pendingBlock}
      </div>`;
  };

  const ledgerHtml = `
    <aside class="ledger">
      <h2>Claims ledger</h2>
      ${
        sectionAbs.resolved.length > 0
          ? `<div class="ledger-group">
               <div class="ledger-group-h">Section abstract</div>
               ${sectionAbs.resolved.map(renderLedgerItem).join("")}
             </div>`
          : ""
      }
      ${
        plateRenders
          .filter((p) => p.blurb.resolved && p.blurb.resolved.length > 0)
          .map(
            (p) => `
              <div class="ledger-group">
                <div class="ledger-group-h">${escapeHtml(p.number || p.id || "")} · ${escapeHtml(p.plateIndexLabel || p.title || "")}</div>
                ${(p.blurb.resolved || []).map(renderLedgerItem).join("")}
              </div>`,
          )
          .join("")
      }
    </aside>
  `;

  const editForm = (formId, currentTitle, currentBlurb, surfaceLabel) => `
    <div class="edit-form" id="${formId}">
      <label>Title (current)</label>
      <input type="text" data-field="title" value="${escapeHtml(currentTitle || "")}" />
      <label>Blurb (current)</label>
      <textarea data-field="body">${escapeHtml(stripHtml(currentBlurb || ""))}</textarea>
      <label>Reason for the change</label>
      <textarea data-field="reason" placeholder="factual correction / wording / cite a new source / etc."></textarea>
      <div class="row">
        <button class="primary" onclick="copyEditSpec(this, '${escapeHtml(slug)}', '${escapeHtml(surfaceLabel)}')">Copy edit-spec to clipboard</button>
        <span class="toast">Copied. Paste in your terminal.</span>
      </div>
      <div class="hint">The clipboard will contain a structured EDIT REQUEST you paste into chat. Claude applies the change + re-runs Gate 1 if numbers changed.</div>
    </div>`;

  const plateHtml = plateRenders
    .map(
      (p, idx) => `
      <section class="plate">
        <div class="plate-number">${escapeHtml(p.number || "")} · ${escapeHtml(p.plateIndexLabel || "")}</div>
        <h3 class="plate-title">${p.titleHtml || escapeHtml(p.title || "")} <button class="edit-btn" onclick="document.getElementById('edit-plate-${idx}').classList.toggle('open')">✎ Propose edit</button></h3>
        <div class="plate-meta">${escapeHtml(p.indicator || "")}${p.asOf ? " · " + escapeHtml(p.asOf) : ""}</div>
        <div class="plate-blurb">${p.blurb.html}</div>
        <div class="plate-source-line">${escapeHtml(p.source || "")}</div>
        ${editForm(`edit-plate-${idx}`, p.title, p.interpretationHtml, p.id || p.number || `plate-${idx + 1}`)}
      </section>`,
    )
    .join("");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Source audit · ${escapeHtml(slug)}</title>
<style>${SHARED_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="page-head">
      <div class="breadcrumb">
        <a href="./index.html">← All sections</a>
        <span style="color:#999">·</span>
        <a href="https://sibleycreek.ca/${escapeHtml(slug)}/" target="_blank" rel="noopener">Live page ↗</a>
      </div>
      <h1>Source audit · ${escapeHtml(slug)}</h1>
      ${freshness && freshness.generatedAt ? `
      <div class="freshness">
        <span class="freshness-label">Pipeline run:</span>
        <span class="freshness-stamp">${escapeHtml(freshness.generatedAt)}</span>
        <span class="freshness-meta">${freshness.panelCount} panels</span>
        <span class="freshness-hint">Pipeline-tagged claims read the value as of this run. Click any source link to verify against the live upstream page.</span>
      </div>` : ""}
      ${pendingCount > 0 ? `
      <div class="verify-toolbar">
        <div class="verify-toolbar-counts">
          <strong>${pendingCount} claim${pendingCount === 1 ? "" : "s"} awaiting your verification.</strong>
          <span class="amber">${pendingCount} pending</span> ·
          <span class="green" id="approved-count">0 approved</span> ·
          <span class="red" id="rejected-count">0 rejected</span>
        </div>
        <div>
          <button class="nav-btn" onclick="jumpToNextPending()">Next pending ↓</button>
          <button class="export-btn" id="export-btn" onclick="exportDecisions('${escapeHtml(slug)}')" disabled>Copy decisions to clipboard</button>
          <span class="export-toast" id="export-toast">Copied — paste into PowerShell</span>
        </div>
      </div>` : ""}
    </header>
    <main>
      <div class="section-label">Section abstract <button class="edit-btn" onclick="document.getElementById('edit-abstract').classList.toggle('open')">✎ Propose edit</button></div>
      <h2 class="headline-q">${escapeHtml(headlineQuestion || "")}</h2>
      <div class="abstract">${sectionAbs.html || "<em>(no section abstract found)</em>"}</div>
      ${editForm("edit-abstract", "", abstract || "", "section-abstract")}
      ${plateHtml}
    </main>
    ${ledgerHtml}
    <footer class="audit-foot">
      Generated ${now} · Tagged claims show a yellow highlight with a [N] reference. Hover or click to see the source. Sidebar lists all claims with verbatim excerpts. Sources marked as "pipeline" auto-refresh; "card" entries are managed in editorial/source_cards/registry.yaml. Use "Propose edit" to send a structured EDIT REQUEST back to Claude.
    </footer>
  </div>
  <script>
    function copyEditSpec(btn, slug, surface) {
      const form = btn.closest('.edit-form');
      const title = form.querySelector('[data-field="title"]').value.trim();
      const body = form.querySelector('[data-field="body"]').value.trim();
      const reason = form.querySelector('[data-field="reason"]').value.trim();
      const spec = [
        'EDIT REQUEST',
        'section: ' + slug,
        'surface: ' + surface,
        '',
        'proposed_title:',
        title,
        '',
        'proposed_body:',
        body,
        '',
        'reason:',
        reason,
      ].join('\\n');
      navigator.clipboard.writeText(spec).then(function () {
        const toast = btn.parentElement.querySelector('.toast');
        toast.classList.add('show');
        setTimeout(function () { toast.classList.remove('show'); }, 2500);
      });
    }
    function updateVerifyTally() {
      const approved = document.querySelectorAll('input[type=radio][value=approve]:checked').length;
      const rejected = document.querySelectorAll('input[type=radio][value=reject]:checked').length;
      const total = document.querySelectorAll('.pending-decision-block fieldset.decision').length;
      const pending = total - approved - rejected;
      const pendEl = document.querySelector('.verify-toolbar-counts .amber');
      const apprEl = document.getElementById('approved-count');
      const rejEl = document.getElementById('rejected-count');
      if (pendEl) pendEl.textContent = pending + ' pending';
      if (apprEl) apprEl.textContent = approved + ' approved';
      if (rejEl) rejEl.textContent = rejected + ' rejected';
      document.querySelectorAll('.ledger-item-pending').forEach(function (el) {
        const fs = el.querySelector('.decision');
        if (!fs) return;
        const id = fs.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        el.classList.toggle('decision-approve', choice === 'approve');
        el.classList.toggle('decision-reject', choice === 'reject');
      });
      const btn = document.getElementById('export-btn');
      if (btn) btn.disabled = (approved + rejected) === 0;
    }
    function exportDecisions(surfaceSlug) {
      const lines = ['# Generated ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ', surface: ' + surfaceSlug, ''];
      document.querySelectorAll('.pending-decision-block fieldset.decision').forEach(function (fs) {
        const id = fs.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        if (choice === 'approve') {
          lines.push('npm run approve-claim ' + surfaceSlug + ':' + id);
        } else if (choice === 'reject') {
          const comment = (document.getElementById('comment-' + id)?.value || '').replace(/"/g, '\\\\"');
          lines.push('npm run reject-claim ' + surfaceSlug + ':' + id + (comment ? ' -- --reason "' + comment + '"' : ''));
        }
      });
      const text = lines.join('\\n');
      navigator.clipboard.writeText(text).then(function () {
        const toast = document.getElementById('export-toast');
        if (toast) {
          toast.classList.add('show');
          setTimeout(function () { toast.classList.remove('show'); }, 2500);
        }
      });
    }
    function jumpToNextPending() {
      // Find the first pending card that hasn't been decided yet.
      const pendingCards = document.querySelectorAll('.ledger-item-pending');
      for (const card of pendingCards) {
        const fs = card.querySelector('.decision');
        if (!fs) continue;
        const id = fs.dataset.claimId;
        const approved = document.querySelector('input[name="decision-' + id + '"][value="approve"]:checked');
        const rejected = document.querySelector('input[name="decision-' + id + '"][value="reject"]:checked');
        if (!approved && !rejected) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('flash-target');
          setTimeout(function () { card.classList.remove('flash-target'); }, 1500);
          return;
        }
      }
      // All decided — alert.
      alert('All pending claims on this surface have been marked. Hit "Copy decisions to clipboard" to export.');
    }
    document.addEventListener('change', function (e) {
      if (e.target.matches('input[type=radio]')) updateVerifyTally();
    });
    updateVerifyTally();
  </script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Minimal markdown → HTML for audit-page rendering. Not a complete spec —
// just enough to keep prose readable while citation phrases are highlighted.
// ---------------------------------------------------------------------------

function renderMarkdown(md) {
  if (!md) return "";
  const lines = md.split(/\r?\n/);
  const out = [];
  let inList = false;
  let inPara = [];
  const flushPara = () => {
    if (inPara.length) {
      out.push(`<p>${inlineMd(inPara.join(" "))}</p>`);
      inPara = [];
    }
  };
  const closeList = () => {
    if (inList) {
      out.push("</ul>");
      inList = false;
    }
  };
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) {
      flushPara();
      closeList();
      continue;
    }
    const h = line.match(/^(#{1,3})\s+(.*)$/);
    if (h) {
      flushPara();
      closeList();
      const level = h[1].length;
      out.push(`<h${level}>${inlineMd(h[2])}</h${level}>`);
      continue;
    }
    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    if (bullet) {
      flushPara();
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${inlineMd(bullet[1])}</li>`);
      continue;
    }
    closeList();
    inPara.push(line);
  }
  flushPara();
  closeList();
  return out.join("\n");
}

function inlineMd(s) {
  // Don't escape — the annotation step will inject <span> tags; HTML in the
  // source is rare here. Only handle bold/italic/code/links.
  return s
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

// ---------------------------------------------------------------------------
// Research deep-dive extraction + audit page rendering
// ---------------------------------------------------------------------------

function extractDeepDives() {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  // Find `export const deepDives` block.
  const m = text.match(/export const deepDives[:\s][^=]*=\s*\[/);
  if (!m) return [];
  const arrStart = m.index + m[0].length;
  const arrClose = findMatchingClose(text, arrStart, "[", "]");
  if (arrClose === -1) return [];
  const body = text.slice(arrStart, arrClose);
  const objs = splitTopLevelObjects(body);
  const dives = [];
  for (const objText of objs) {
    const slug = extractField(objText, "slug");
    const title = extractField(objText, "title");
    const deck = extractField(objText, "deck");
    const draftPath = extractField(objText, "draftPath");
    const publishedPath = extractField(objText, "publishedPath");
    const publishedAt = extractField(objText, "publishedAt");
    const sectionAffinity = extractField(objText, "sectionAffinity");
    if (slug?.text) {
      dives.push({
        slug: slug.text,
        title: title?.text ?? null,
        deck: deck?.text ?? null,
        draftPath: draftPath?.text ?? null,
        publishedPath: publishedPath?.text ?? null,
        publishedAt: publishedAt?.text ?? null,
        sectionAffinity: sectionAffinity?.text ?? null,
      });
    }
  }
  return dives;
}

function loadDiveSidecar(slug) {
  const p = path.join(repoRoot, "editorial", "source_cards", "research", `${slug}.yaml`);
  if (!fs.existsSync(p)) return null;
  try {
    const raw = fs.readFileSync(p, "utf-8");
    const parsed = parseYaml(raw);
    return parsed || null;
  } catch {
    return null;
  }
}

function renderDivePage(dive, sidecar, registry, now, pendingMap = null) {
  resetGlobalRefCounter();
  // Live render reads from publishedPath (editorial/published/), not draftPath
  // (editorial/drafts/, the writer's working copy). Audit must reflect what is
  // actually on the site — so we read publishedPath first and only fall back
  // to draftPath if the dive hasn't been published yet.
  const sourcePathRel = dive.publishedPath || dive.draftPath || null;
  const sourceFull = sourcePathRel ? path.join(repoRoot, sourcePathRel) : null;
  const body = sourceFull && fs.existsSync(sourceFull) ? fs.readFileSync(sourceFull, "utf-8") : "";
  const sourceLabel = dive.publishedPath ? "published" : (dive.draftPath ? "draft (not yet on site)" : "no body");
  const citations = sidecar?.citations || [];

  // For dives, reference date falls back to the freshest pipeline date overall.
  let diveRef = null;
  for (const slug of ALL_SECTIONS) {
    const d = sectionFreshestDate(slug);
    if (!d) continue;
    if (!diveRef || new Date(d.isoDate) > new Date(diveRef.isoDate)) diveRef = d;
  }

  // Annotate prose: phrase-match against citations, then render markdown after.
  // Because annotateProse uses regex replacement on plain text, we run it on
  // the raw markdown source, then pass the result through the markdown
  // renderer. Citation spans survive because they don't conflict with markdown
  // syntax.
  const annotated = annotateProse(body, citations, registry, pendingMap, `research/${dive.slug}`);
  annotated.resolved.forEach((r) => { r.note = augmentNoteWithDate(r.note, r.source, diveRef); });
  const bodyHtml = renderMarkdown(annotated.html);
  const pendingCount = annotated.resolved.filter((r) => r.isPending).length;

  const renderLedgerItem = (r) => {
    const kindClass = r.kind || "unknown";
    const itemClass = r.isPending ? "ledger-item ledger-item-pending" : "ledger-item";
    // Each ledger entry gets a unique id keyed off globalId; multiple
    // citations of the same card render as separate entries (one per
    // inline claim) so links are bijective.
    const anchorId = `id="ledger-${r.globalId}"`;
    const linkBlock = r.url ? `<a class="ledger-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener">Open source ↗</a>` : "";
    const excerptBlock = r.excerpt ? `<div class="ledger-excerpt">${escapeHtml(r.excerpt)}</div>` : "";
    const metaBits = [];
    if (r.vintage_label) metaBits.push(escapeHtml(r.vintage_label));
    if (r.verified_at) metaBits.push(`verified ${escapeHtml(r.verified_at)}`);
    if (r.next_expected) metaBits.push(`next ${escapeHtml(r.next_expected)}`);
    const metaBlock = metaBits.length ? `<div class="ledger-meta">${metaBits.join(" · ")}</div>` : "";
    const noteBlock = r.note ? `<div class="note-line">${escapeHtml(r.note)}</div>` : "";

    let pendingBlock = "";
    if (r.isPending) {
      const triHtml = (r.triangulation || []).map((sec) => `
        <li class="secondary">
          ${sec.url ? `<a href="${escapeHtml(sec.url)}" target="_blank" rel="noopener"><strong>${escapeHtml(sec.source || "")}</strong></a>` : `<strong>${escapeHtml(sec.source || "")}</strong>`}
          ${sec.credibility ? `<div class="secondary-credibility">${escapeHtml(sec.credibility)}</div>` : ""}
          ${sec.excerpt ? `<blockquote class="secondary-excerpt">${escapeHtml(sec.excerpt)}</blockquote>` : ""}
        </li>`).join("");
      const triBlock = r.triangulation && r.triangulation.length
        ? `<div class="pending-triangulation"><strong>Triangulated secondaries:</strong><ul class="secondaries">${triHtml}</ul></div>`
        : `<div class="pending-triangulation muted">No triangulation block on the card. Either verify the primary directly in your browser, or reject.</div>`;
      const verifiedValuesHtml = (r.verified_value && typeof r.verified_value === "object")
        ? `<div class="pending-values"><strong>Data points the card establishes:</strong><ul class="verified-values">${Object.entries(r.verified_value).map(([k, v]) => `<li><code>${escapeHtml(k)}</code>: <strong>${escapeHtml(String(v))}</strong></li>`).join("")}</ul></div>`
        : "";
      const cardNotesBlock = r.cardNotes ? `<div class="pending-card-notes">${escapeHtml(r.cardNotes)}</div>` : "";
      pendingBlock = `
        <div class="pending-decision-block">
          ${verifiedValuesHtml}
          ${triBlock}
          ${cardNotesBlock}
          <fieldset class="decision" data-claim-id="${escapeHtml(r.cardId)}">
            <legend>Your decision</legend>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="pending" checked> Not yet verified</label>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="approve"> Approve</label>
            <label><input type="radio" name="decision-${escapeHtml(r.cardId)}" value="reject"> Reject</label>
            <div class="comment-row">
              <label for="comment-${escapeHtml(r.cardId)}">Comment (required if rejecting):</label>
              <textarea id="comment-${escapeHtml(r.cardId)}" rows="2"></textarea>
            </div>
          </fieldset>
        </div>`;
    }

    const refBlock = r.inlineMatched === false
      ? `<span class="ledger-ref ${kindClass} ledger-ref-orphan">[${r.refNum}]</span>`
      : `<a href="#ref-${r.globalId}" class="ledger-ref-link"><span class="ledger-ref ${kindClass}">[${r.refNum}]</span></a>`;
    return `<div class="${itemClass}" ${anchorId}>
      ${refBlock}
      <span class="ledger-source-label">${escapeHtml(r.label)}</span>${renderTierBadge(r)}${r.inlineMatched === false ? `<span class="no-inline-match" title="The citation phrase does not appear in the published prose. Either tighten the phrase to match verbatim, or the citation is orphaned (no longer referenced).">no inline match</span>` : ``}
      <div class="ledger-phrase">"${escapeHtml(r.phrase)}"</div>
      ${excerptBlock}${metaBlock}${noteBlock}${linkBlock}${pendingBlock}
    </div>`;
  };

  const ledgerHtml = `<aside class="ledger">
    <h2>Claims ledger</h2>
    <div class="ledger-group">
      <div class="ledger-group-h">${escapeHtml(dive.title || dive.slug)} (${annotated.resolved.length})</div>
      ${annotated.resolved.map(renderLedgerItem).join("")}
    </div>
  </aside>`;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Source audit · research / ${escapeHtml(dive.slug)}</title>
<style>${SHARED_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="page-head">
      <div class="breadcrumb">
        <a href="../index.html">← All audits</a>
        <span style="color:#999">·</span>
        ${dive.publishedPath ? `<a href="https://sibleycreek.ca/research/${escapeHtml(dive.slug)}/" target="_blank" rel="noopener">Live dive ↗</a>` : `<span style="color:#c83a00;font-weight:600">DRAFT — not yet published</span>`}
      </div>
      <h1>Source audit · research / ${escapeHtml(dive.slug)}</h1>
      ${pendingCount > 0 ? `
      <div class="verify-toolbar">
        <div class="verify-toolbar-counts">
          <strong>${pendingCount} claim${pendingCount === 1 ? "" : "s"} awaiting your verification.</strong>
          <span class="amber">${pendingCount} pending</span> ·
          <span class="green" id="approved-count">0 approved</span> ·
          <span class="red" id="rejected-count">0 rejected</span>
        </div>
        <div>
          <button class="nav-btn" onclick="jumpToNextPending()">Next pending ↓</button>
          <button class="export-btn" id="export-btn" onclick="exportDecisions('${escapeHtml(dive.slug)}')" disabled>Copy decisions to clipboard</button>
          <span class="export-toast" id="export-toast">Copied — paste into PowerShell</span>
        </div>
      </div>` : ""}
    </header>
    <main>
      <h2 class="headline-q">${escapeHtml(dive.title || "")}</h2>
      ${dive.deck ? `<div class="abstract">${escapeHtml(dive.deck)}</div>` : ""}
      <div class="dive-body">${bodyHtml || "<em>(no draft body found)</em>"}</div>
    </main>
    ${ledgerHtml}
    <footer class="audit-foot">
      Generated ${now} · ${annotated.resolved.length} tagged claims · body source: ${escapeHtml(sourceLabel)} (${escapeHtml(sourcePathRel || "—")}) · sidecar: editorial/source_cards/research/${escapeHtml(dive.slug)}.yaml.
    </footer>
  </div>
  <script>
    function updateVerifyTally() {
      const approved = document.querySelectorAll('input[type=radio][value=approve]:checked').length;
      const rejected = document.querySelectorAll('input[type=radio][value=reject]:checked').length;
      const total = document.querySelectorAll('.pending-decision-block fieldset.decision').length;
      const pending = total - approved - rejected;
      const pendEl = document.querySelector('.verify-toolbar-counts .amber');
      const apprEl = document.getElementById('approved-count');
      const rejEl = document.getElementById('rejected-count');
      if (pendEl) pendEl.textContent = pending + ' pending';
      if (apprEl) apprEl.textContent = approved + ' approved';
      if (rejEl) rejEl.textContent = rejected + ' rejected';
      document.querySelectorAll('.ledger-item-pending').forEach(function (el) {
        const fs = el.querySelector('.decision');
        if (!fs) return;
        const id = fs.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        el.classList.toggle('decision-approve', choice === 'approve');
        el.classList.toggle('decision-reject', choice === 'reject');
      });
      const btn = document.getElementById('export-btn');
      if (btn) btn.disabled = (approved + rejected) === 0;
    }
    function exportDecisions(surfaceSlug) {
      const lines = ['# Generated ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ', surface: ' + surfaceSlug, ''];
      document.querySelectorAll('.pending-decision-block fieldset.decision').forEach(function (fs) {
        const id = fs.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        if (choice === 'approve') {
          lines.push('npm run approve-claim ' + surfaceSlug + ':' + id);
        } else if (choice === 'reject') {
          const comment = (document.getElementById('comment-' + id)?.value || '').replace(/"/g, '\\\\"');
          lines.push('npm run reject-claim ' + surfaceSlug + ':' + id + (comment ? ' -- --reason "' + comment + '"' : ''));
        }
      });
      const text = lines.join('\\n');
      navigator.clipboard.writeText(text).then(function () {
        const toast = document.getElementById('export-toast');
        if (toast) {
          toast.classList.add('show');
          setTimeout(function () { toast.classList.remove('show'); }, 2500);
        }
      });
    }
    function jumpToNextPending() {
      // Find the first pending card that hasn't been decided yet.
      const pendingCards = document.querySelectorAll('.ledger-item-pending');
      for (const card of pendingCards) {
        const fs = card.querySelector('.decision');
        if (!fs) continue;
        const id = fs.dataset.claimId;
        const approved = document.querySelector('input[name="decision-' + id + '"][value="approve"]:checked');
        const rejected = document.querySelector('input[name="decision-' + id + '"][value="reject"]:checked');
        if (!approved && !rejected) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('flash-target');
          setTimeout(function () { card.classList.remove('flash-target'); }, 1500);
          return;
        }
      }
      // All decided — alert.
      alert('All pending claims on this surface have been marked. Hit "Copy decisions to clipboard" to export.');
    }
    document.addEventListener('change', function (e) {
      if (e.target.matches('input[type=radio]')) updateVerifyTally();
    });
    updateVerifyTally();
  </script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Splash audit — hero abstract + 6 tile lines
// ---------------------------------------------------------------------------

function renderSplashPage(registry, now) {
  resetGlobalRefCounter();
  const hero = extractSplashHero();
  // For the hero, use the freshest date across ALL section panel_data —
  // the hero pulls from every section so the broadest anchor is right.
  let heroRefDate = null;
  for (const slug of ALL_SECTIONS) {
    const d = sectionFreshestDate(slug);
    if (!d) continue;
    if (!heroRefDate || new Date(d.isoDate) > new Date(heroRefDate.isoDate)) heroRefDate = d;
  }
  checkLengthBudget("splash · hero abstract", "splash-hero", hero.abstract);
  const heroAnnotated = annotateProse(hero.abstract, hero.citations || [], registry, null, "splash · hero abstract");
  heroAnnotated.resolved.forEach((r) => { r.note = augmentNoteWithDate(r.note, r.source, heroRefDate); });

  // 6 tile lines (one per non-trade section + trade) — every section that has a tileLine.
  const tiles = [];
  for (const slug of ALL_SECTIONS) {
    const { tileLine, citations } = extractTileLine(slug);
    if (!tileLine) continue;
    const ref = sectionFreshestDate(slug);
    checkLengthBudget(`splash · ${slug} tile`, "tile-line", tileLine);
    const annotated = annotateProse(tileLine, citations || [], registry, null, `splash · ${slug} tile`);
    annotated.resolved.forEach((r) => { r.note = augmentNoteWithDate(r.note, r.source, ref); });
    tiles.push({ slug, tileLine, annotated, referenceDate: ref });
  }

  const renderLedgerItem = (r) => {
    const kindClass = r.kind || "unknown";
    const linkBlock = r.url ? `<a class="ledger-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener">Open source ↗</a>` : "";
    const excerptBlock = r.excerpt ? `<div class="ledger-excerpt">${escapeHtml(r.excerpt)}</div>` : "";
    const metaBits = [];
    if (r.vintage_label) metaBits.push(escapeHtml(r.vintage_label));
    if (r.verified_at) metaBits.push(`verified ${escapeHtml(r.verified_at)}`);
    if (r.next_expected) metaBits.push(`next ${escapeHtml(r.next_expected)}`);
    const metaBlock = metaBits.length ? `<div class="ledger-meta">${metaBits.join(" · ")}</div>` : "";
    const noteBlock = r.note ? `<div class="note-line">${escapeHtml(r.note)}</div>` : "";
    const anchorId = `id="ledger-${r.globalId}"`;
    const refBlock = r.inlineMatched === false
      ? `<span class="ledger-ref ${kindClass} ledger-ref-orphan">[${r.refNum}]</span>`
      : `<a href="#ref-${r.globalId}" class="ledger-ref-link"><span class="ledger-ref ${kindClass}">[${r.refNum}]</span></a>`;
    return `<div class="ledger-item" ${anchorId}>
      ${refBlock}
      <span class="ledger-source-label">${escapeHtml(r.label)}</span>${renderTierBadge(r)}${r.inlineMatched === false ? `<span class="no-inline-match" title="The citation phrase does not appear in the published prose. Either tighten the phrase to match verbatim, or the citation is orphaned (no longer referenced).">no inline match</span>` : ``}
      <div class="ledger-phrase">"${escapeHtml(r.phrase)}"</div>
      ${excerptBlock}${metaBlock}${noteBlock}${linkBlock}
    </div>`;
  };

  const ledgerHtml = `<aside class="ledger">
    <h2>Claims ledger</h2>
    ${heroAnnotated.resolved.length > 0 ? `<div class="ledger-group">
      <div class="ledger-group-h">Hero abstract</div>
      ${heroAnnotated.resolved.map(renderLedgerItem).join("")}
    </div>` : ""}
    ${tiles.filter((t) => t.annotated.resolved.length > 0).map((t) => `<div class="ledger-group">
      <div class="ledger-group-h">Tile · ${escapeHtml(t.slug)}</div>
      ${t.annotated.resolved.map(renderLedgerItem).join("")}
    </div>`).join("")}
  </aside>`;

  const tileHtml = tiles.map((t) => `<div class="tile">
    <div class="tile-section-label">${escapeHtml(t.slug)}</div>
    <div class="tile-line">${t.annotated.html}</div>
  </div>`).join("");

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Source audit · splash</title>
<style>${SHARED_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="page-head">
      <div class="breadcrumb">
        <a href="./index.html">← All audits</a>
        <span style="color:#999">·</span>
        <a href="https://sibleycreek.ca/" target="_blank" rel="noopener">Live splash ↗</a>
      </div>
      <h1>Source audit · splash (hero + tile lines)</h1>
    </header>
    <main>
      <div class="section-label">Hero abstract</div>
      <div class="abstract">${heroAnnotated.html || "<em>(no hero abstract found)</em>"}</div>
      <div class="section-label" style="margin-top:32px">Section tile lines</div>
      <div class="tile-grid">${tileHtml}</div>
    </main>
    ${ledgerHtml}
    <footer class="audit-foot">
      Generated ${now} · Hero + 6 tile lines. Tagged claims show a yellow highlight with a [N] reference. Sidebar lists all claims; pipeline-tagged claims auto-resolve their reference date from the corresponding section's panel_data.
    </footer>
  </div>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Verification view — pending queue UX for drafts in editorial/drafts/_holding/
// ---------------------------------------------------------------------------

const PENDING_DIR = path.join(repoRoot, "editorial", "source_cards", "_pending");
const HOLDING_DIR = path.join(repoRoot, "editorial", "drafts", "_holding");

function discoverHoldingDrafts() {
  if (!fs.existsSync(PENDING_DIR)) return [];
  return fs.readdirSync(PENDING_DIR)
    .filter((d) => {
      const p = path.join(PENDING_DIR, d);
      return fs.statSync(p).isDirectory() && d !== "node_modules";
    })
    .filter((d) => {
      // A draft slug is valid if either a _holding/<slug>.md exists OR the
      // pending subdir has at least one .yaml file. We accept either; if only
      // YAMLs exist (no draft body), the verification view renders the cards
      // alone with a "draft body not yet written" placeholder.
      const yamls = fs.readdirSync(path.join(PENDING_DIR, d))
        .filter((f) => f.endsWith(".yaml"));
      return yamls.length > 0;
    });
}

function loadPendingCards(draftSlug) {
  const dir = path.join(PENDING_DIR, draftSlug);
  if (!fs.existsSync(dir)) return [];
  const cards = [];
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith(".yaml")) continue;
    try {
      const raw = fs.readFileSync(path.join(dir, f), "utf-8");
      const parsed = parseYaml(raw);
      if (parsed) cards.push(parsed);
    } catch (e) {
      console.error(`failed to parse ${path.join(dir, f)}: ${e.message}`);
    }
  }
  return cards;
}

function loadHoldingDraft(draftSlug) {
  const p = path.join(HOLDING_DIR, `${draftSlug}.md`);
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, "utf-8");
}

/**
 * Find every citation in the project that references a given card id, and
 * return a list of { phrase, surface, note } entries. The verification view
 * uses this to surface the actual prose tokens at stake — instead of just
 * the card's title (which is a source name, not a claim).
 */
function findCitationsReferencingCard(cardId) {
  const matches = [];
  // 1. Section .astro files — scan plates' citations[] and abstractCitations/tileLineCitations in sections.ts.
  for (const f of fs.readdirSync(PAGES_DIR)) {
    if (!f.endsWith(".astro")) continue;
    const text = fs.readFileSync(path.join(PAGES_DIR, f), "utf-8");
    // Find every { phrase: "...", source: "card:<id>", note: "..." } entry referencing this card.
    const re = new RegExp(`\\{\\s*phrase:\\s*"([^"]+)"\\s*,\\s*source:\\s*"card:${cardId}"(?:\\s*,\\s*note:\\s*"([^"]+)")?\\s*\\}`, "g");
    let m;
    while ((m = re.exec(text)) !== null) {
      matches.push({ phrase: m[1], surface: `src/pages/${f}`, note: m[2] || null });
    }
  }
  // 2. sections.ts
  const sectionsText = fs.readFileSync(SECTIONS_TS, "utf-8");
  const re2 = new RegExp(`\\{\\s*phrase:\\s*"([^"]+)"\\s*,\\s*source:\\s*"card:${cardId}"(?:\\s*,\\s*note:\\s*"([^"]+)")?\\s*\\}`, "g");
  let m2;
  while ((m2 = re2.exec(sectionsText)) !== null) {
    matches.push({ phrase: m2[1], surface: "src/data/sections.ts", note: m2[2] || null });
  }
  // 3. Dive sidecars — YAML format, different regex.
  const researchDir = path.join(repoRoot, "editorial", "source_cards", "research");
  if (fs.existsSync(researchDir)) {
    for (const f of fs.readdirSync(researchDir)) {
      if (!f.endsWith(".yaml")) continue;
      const text = fs.readFileSync(path.join(researchDir, f), "utf-8");
      // YAML citation block:
      //   - phrase: "..."
      //     source: card:<id>
      //     note: "..."
      // We split on `- phrase:` blocks and scan each.
      const blocks = text.split(/\n\s*-\s*phrase:/);
      for (let i = 1; i < blocks.length; i++) {
        const block = blocks[i];
        // Does this block reference our card?
        if (!new RegExp(`source:\\s*card:${cardId}\\b`).test(block)) continue;
        const phraseMatch = block.match(/^\s*["']?(.+?)["']?\s*$/m);
        const noteMatch = block.match(/note:\s*"([^"]+)"/);
        matches.push({
          phrase: phraseMatch?.[1] || "(could not parse phrase)",
          surface: `editorial/source_cards/research/${f}`,
          note: noteMatch?.[1] || null,
        });
      }
    }
  }
  return matches;
}

function renderVerificationView(draftSlug, cards, draftBody, now) {
  // Annotate the draft body: replace [CLAIM-PENDING:<id>] markers with
  // amber-highlighted spans that reference the sidebar card.
  let annotated = draftBody || "<em>(no holding draft body found — the writer has not yet produced a draft; the pending cards below are queued for your review independently.)</em>";
  if (draftBody) {
    annotated = renderMarkdown(draftBody);
    annotated = annotated.replace(/\[CLAIM-PENDING:([a-z0-9_-]+)\]/g, (_, id) => {
      const card = cards.find((c) => c.id === id);
      const label = card?.proposed_claim || id;
      return `<span class="claim-pending" data-claim-id="${escapeHtml(id)}"><sup class="claim-pending-sup">[PENDING]</sup>${escapeHtml(label)}</span>`;
    });
  }

  const renderPendingCardEntry = (card) => {
    const id = card.id;
    const tier = card.verification_tier || "B";
    const isMode3 = card.mode === 3;
    const tierLabel = isMode3 ? "MODE 3 · ANALYSIS" : `TIER ${tier}`;
    const tierClass = isMode3 ? "tier-mode3" : (tier === "B" ? "tier-b" : tier === "C" ? "tier-c" : "tier-a");

    const triangulationHtml = (card.triangulation || []).map((sec) => `
      <li class="secondary">
        <div class="secondary-source"><a href="${escapeHtml(sec.url)}" target="_blank" rel="noopener">${escapeHtml(sec.source)}</a></div>
        <div class="secondary-credibility">${escapeHtml(sec.credibility || "")}</div>
        ${sec.excerpt ? `<blockquote class="secondary-excerpt">${escapeHtml(sec.excerpt)}</blockquote>` : ""}
      </li>`).join("");

    const frameTest = isMode3 ? `<div class="frame-test-reminder"><strong>Frame test:</strong> read the prose aloud. Replace "X argues Y" with "Y is true." Does it still work? If yes, framing is honest. If you'd lose the punch by adding "X argues," reject or reframe.</div>` : "";

    // The actual factual claims this card backs. Two layers:
    //  (1) verified_value — the data points the card establishes (if any).
    //  (2) citations referencing this card in the project — the actual prose
    //      tokens at stake, with their surfaces. Without this, the
    //      verification view shows source titles instead of claims.
    const verifiedValuesHtml = (card.verified_value && typeof card.verified_value === "object")
      ? `<ul class="verified-values">${Object.entries(card.verified_value).map(([k, v]) => `<li><code>${escapeHtml(k)}</code>: <strong>${escapeHtml(String(v))}</strong></li>`).join("")}</ul>`
      : "";

    const referencingCitations = findCitationsReferencingCard(id);
    const citationsListHtml = referencingCitations.length > 0
      ? `<ul class="referencing-citations">${referencingCitations.map((c) => `
          <li>
            <div class="cite-phrase">"${escapeHtml(c.phrase)}"</div>
            <div class="cite-surface">— ${escapeHtml(c.surface)}</div>
            ${c.note ? `<div class="cite-note">${escapeHtml(c.note)}</div>` : ""}
          </li>`).join("")}</ul>`
      : `<div class="muted">No prose currently references this card. The card may be orphaned. Reject to remove from registry.</div>`;

    const sourceTitle = card.title ? `<div class="source-title"><strong>Source:</strong> ${escapeHtml(card.title)}</div>` : "";
    const excerptBlock = card.excerpt ? `<blockquote class="card-excerpt">${escapeHtml(card.excerpt)}</blockquote>` : "";
    const notesBlock = card.notes ? `<div class="card-notes">${escapeHtml(card.notes)}</div>` : "";

    return `
      <article class="pending-card" id="card-${escapeHtml(id)}" data-claim-id="${escapeHtml(id)}">
        <header class="pending-card-head">
          <span class="tier-badge ${tierClass}">${tierLabel}</span>
          <span class="pending-id">${escapeHtml(id)}</span>
        </header>
        <div class="claims-block">
          <div class="claims-label"><strong>Claims this card backs (${referencingCitations.length} prose reference${referencingCitations.length === 1 ? "" : "s"}):</strong></div>
          ${citationsListHtml}
        </div>
        ${verifiedValuesHtml ? `<div class="claims-block">
          <div class="claims-label"><strong>Data points the card establishes:</strong></div>
          ${verifiedValuesHtml}
        </div>` : ""}
        ${frameTest}
        ${sourceTitle}
        <div class="primary-row">
          <strong>Primary (would-be):</strong>
          ${card.url ? `<a href="${escapeHtml(card.url)}" target="_blank" rel="noopener">${escapeHtml(card.url)}</a>` : "<em>(no URL)</em>"}
          <div class="primary-hint">Open in a browser to verify directly. If the URL 404s or doesn't reach the claim, reject the card.</div>
        </div>
        ${excerptBlock}
        ${notesBlock}
        ${card.triangulation?.length ? `
          <div class="triangulation-block">
            <strong>Triangulated secondaries:</strong>
            <ul class="secondaries">${triangulationHtml}</ul>
          </div>` : `<div class="triangulation-block muted">No triangulation block on the card. To approve as Tier B, the card should have 2+ independent credible secondaries. If you can verify the primary directly in your browser, approve. Otherwise reject or request a researcher pass to triangulate.</div>`}
        <fieldset class="decision">
          <legend>Your decision</legend>
          <label><input type="radio" name="decision-${escapeHtml(id)}" value="pending" checked> Not yet verified</label>
          <label><input type="radio" name="decision-${escapeHtml(id)}" value="approve"> Approve</label>
          <label><input type="radio" name="decision-${escapeHtml(id)}" value="reject"> Reject</label>
          <div class="comment-row">
            <label for="comment-${escapeHtml(id)}">Comment (required if rejecting):</label>
            <textarea id="comment-${escapeHtml(id)}" data-claim-id="${escapeHtml(id)}" rows="2"></textarea>
          </div>
        </fieldset>
      </article>`;
  };

  const cardsHtml = cards.map(renderPendingCardEntry).join("");

  const totalCount = cards.length;

  const css = `
${SHARED_CSS}
body { background: #f7f6f1; }
.verify-wrap {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 480px;
  gap: 32px;
}
.verify-head {
  grid-column: 1 / -1;
  border-bottom: 2px solid #c83a00;
  padding-bottom: 16px;
  margin-bottom: 16px;
}
.verify-head h1 {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 8px 0;
  color: #c83a00;
}
.verify-head .tagline { font-family: Georgia, serif; font-size: 16px; color: #444; }
.tally-bar {
  background: white;
  border: 1px solid #d8c773;
  padding: 14px 18px;
  margin-bottom: 16px;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
}
.tally-counts { font-weight: 600; }
.tally-counts .approved { color: #2a7a30; }
.tally-counts .rejected { color: #c33; }
.tally-counts .pending { color: #b07b00; }
.export-btn {
  background: #006699;
  color: white;
  border: none;
  padding: 8px 18px;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  font-family: "Helvetica Neue", Arial, sans-serif;
}
.export-btn:hover { background: #00557e; }
.export-btn:disabled { background: #888; cursor: not-allowed; }
.export-toast {
  font-size: 12px;
  color: #2a7a30;
  font-weight: 600;
  margin-left: 8px;
  display: none;
}
.export-toast.show { display: inline; }
.draft-body {
  background: white;
  padding: 24px 32px;
  border: 1px solid #ddd;
  font-family: Georgia, serif;
  font-size: 16px;
  line-height: 1.65;
}
.draft-body h1, .draft-body h2, .draft-body h3 {
  font-family: "Helvetica Neue", Arial, sans-serif;
  color: #111;
}
.claim-pending {
  background: #ffe5a0;
  border-bottom: 2px solid #c83a00;
  padding: 1px 3px;
}
.claim-pending-sup {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 9px;
  font-weight: 700;
  color: #c83a00;
  margin-right: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pending-sidebar {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}
.pending-card {
  background: white;
  border: 1px solid #d8c773;
  padding: 16px;
  margin-bottom: 12px;
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
}
.pending-card.approved { border-color: #2a7a30; background: #f0f8f0; }
.pending-card.rejected { border-color: #c33; background: #fbe8e8; }
.pending-card-head { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
.pending-id { color: #888; font-family: var(--font-mono, monospace); font-size: 11px; }
.proposed-claim {
  background: #f8f7ec;
  padding: 8px 10px;
  border-left: 3px solid #c83a00;
  margin-bottom: 10px;
  font-size: 13px;
  line-height: 1.5;
}
.claims-block { margin: 10px 0; font-size: 13px; }
.claims-label { margin-bottom: 4px; }
.referencing-citations { list-style: none; padding: 0; margin: 4px 0; }
.referencing-citations li { background: #fffbcc; border-left: 3px solid #c83a00; padding: 6px 10px; margin-bottom: 4px; }
.cite-phrase { font-style: italic; }
.cite-surface { font-family: var(--font-mono, monospace); font-size: 10px; color: #666; margin-top: 2px; }
.cite-note { font-size: 11px; color: #555; margin-top: 4px; font-style: italic; }
.verified-values { list-style: none; padding: 0; margin: 4px 0; }
.verified-values li { padding: 4px 8px; background: #f3f3ef; margin-bottom: 2px; font-family: var(--font-mono, monospace); font-size: 12px; }
.verified-values code { background: transparent; font-size: 11px; color: #444; }
.source-title { font-size: 12px; color: #555; margin: 8px 0; }
.card-excerpt { background: #f3f3ef; padding: 8px 10px; margin: 8px 0; font-style: italic; font-size: 12px; border-left: 2px solid #999; }
.card-notes { font-size: 11px; color: #555; margin: 8px 0; font-style: italic; }
.muted { color: #888; font-style: italic; }
.proposed-surface { font-size: 11px; color: #555; margin-bottom: 8px; }
.frame-test-reminder { background: #fbe8e8; padding: 8px 10px; border-left: 3px solid #8a3a4a; margin: 8px 0; font-size: 12px; line-height: 1.4; }
.primary-row { margin: 10px 0; font-size: 12px; }
.primary-row a { word-break: break-all; }
.primary-hint { font-size: 11px; color: #888; font-style: italic; margin-top: 2px; }
.triangulation-block { margin: 10px 0; font-size: 12px; }
.triangulation-block.muted { color: #888; font-style: italic; }
.secondaries { list-style: none; padding: 0; margin: 6px 0 0 0; }
.secondary { padding: 8px; background: #f8f7ec; border-left: 2px solid #999; margin-bottom: 6px; font-size: 12px; }
.secondary-source { font-weight: 600; }
.secondary-credibility { font-size: 11px; color: #555; margin: 2px 0; }
.secondary-excerpt { margin: 4px 0 0 0; padding: 4px 8px; background: white; font-style: italic; color: #444; font-size: 11px; line-height: 1.4; }
.decision { border: 1px solid #ccc; padding: 10px 14px; margin-top: 12px; }
.decision legend { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: #444; padding: 0 6px; }
.decision label { display: block; margin: 4px 0; font-size: 13px; cursor: pointer; }
.decision label input { margin-right: 6px; }
.comment-row { margin-top: 8px; }
.comment-row label { font-size: 11px; color: #555; }
.comment-row textarea { width: 100%; font-family: Georgia, serif; font-size: 12px; padding: 4px 6px; border: 1px solid #c8c0a0; box-sizing: border-box; resize: vertical; }
`;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Verification view · ${escapeHtml(draftSlug)}</title>
<style>${css}</style>
</head>
<body>
  <div class="verify-wrap">
    <header class="verify-head">
      <div class="breadcrumb"><a href="../index.html">← Audit index</a></div>
      <h1>Verification view · ${escapeHtml(draftSlug)}</h1>
      <div class="tagline">${totalCount} claim${totalCount === 1 ? "" : "s"} pending your review. The site cannot ship these until each is approved or rejected.</div>
    </header>
    <div class="tally-bar" id="tally-bar">
      <div class="tally-counts">
        <span class="pending">${totalCount} not yet verified</span> ·
        <span class="approved" id="approved-count">0 approved</span> ·
        <span class="rejected" id="rejected-count">0 rejected</span>
      </div>
      <div>
        <button class="export-btn" id="export-btn" onclick="exportDecisions()" disabled>Copy decisions to clipboard</button>
        <span class="export-toast" id="export-toast">Copied — paste into PowerShell</span>
      </div>
    </div>
    <main class="draft-body">${annotated}</main>
    <aside class="pending-sidebar">${cardsHtml}</aside>
  </div>
  <script>
    function updateTally() {
      const approved = document.querySelectorAll('input[type=radio][value=approve]:checked').length;
      const rejected = document.querySelectorAll('input[type=radio][value=reject]:checked').length;
      const total = document.querySelectorAll('.pending-card').length;
      const pending = total - approved - rejected;
      document.querySelector('.tally-counts .pending').textContent = pending + ' not yet verified';
      document.getElementById('approved-count').textContent = approved + ' approved';
      document.getElementById('rejected-count').textContent = rejected + ' rejected';
      // Style each card by its decision state.
      document.querySelectorAll('.pending-card').forEach(function (card) {
        const id = card.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        card.classList.toggle('approved', choice === 'approve');
        card.classList.toggle('rejected', choice === 'reject');
      });
      document.getElementById('export-btn').disabled = (approved + rejected) === 0;
    }
    function exportDecisions() {
      const lines = ['# Generated ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ', draft: ${escapeHtml(draftSlug)}', ''];
      document.querySelectorAll('.pending-card').forEach(function (card) {
        const id = card.dataset.claimId;
        const choice = document.querySelector('input[name="decision-' + id + '"]:checked')?.value;
        if (choice === 'approve') {
          lines.push('npm run approve-claim ${escapeHtml(draftSlug)}:' + id);
        } else if (choice === 'reject') {
          const comment = (document.getElementById('comment-' + id)?.value || '').replace(/"/g, '\\\\"');
          lines.push('npm run reject-claim ${escapeHtml(draftSlug)}:' + id + (comment ? ' --reason "' + comment + '"' : ''));
        }
      });
      const text = lines.join('\\n');
      navigator.clipboard.writeText(text).then(function () {
        const toast = document.getElementById('export-toast');
        toast.classList.add('show');
        setTimeout(function () { toast.classList.remove('show'); }, 2500);
      });
    }
    document.addEventListener('change', function (e) {
      if (e.target.matches('input[type=radio]')) updateTally();
    });
    updateTally();
  </script>
</body>
</html>`;
}

function renderPendingMasterIndex(allPending, now) {
  const items = allPending.map((d) => `<li>
    <a href="${SECTION_SLUGS_FOR_INDEX.has(d.slug) ? './' + escapeHtml(d.slug) + '.html' : './research/' + escapeHtml(d.slug) + '.html'}">${escapeHtml(d.slug)}</a>
    <span class="tally">${d.count} pending</span>
  </li>`).join("");
  return `<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Verification queue</title>
<style>
body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 24px; line-height: 1.55; background: #f7f6f1; }
h1 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 16px; text-transform: uppercase; letter-spacing: 0.18em; color: #c83a00; }
.label { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 12px; color: #555; margin-bottom: 24px; }
ul { list-style: none; padding: 0; }
li { padding: 12px 0; border-bottom: 1px solid #ddd; }
a { color: #006699; text-decoration: none; font-size: 17px; }
a:hover { text-decoration: underline; }
.tally { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 12px; color: #b07b00; margin-left: 8px; font-weight: 600; }
.empty { color: #2a7a30; font-style: italic; margin: 24px 0; }
footer { font-size: 12px; color: #888; margin-top: 32px; font-family: "Helvetica Neue", Arial, sans-serif; }
</style></head>
<body>
  <a href="./index.html" style="color:#666;font-family:Helvetica Neue,Arial;font-size:12px;">← Audit index</a>
  <h1>⚠ Verification queue</h1>
  <div class="label">Drafts with claims pending your review. Each draft has a verification view where you walk every pending citation, mark Approve / Reject / Not yet verified, and export decisions to clipboard for paste into PowerShell.</div>
  ${allPending.length === 0 ? '<div class="empty">All claims verified. No drafts in flight.</div>' : `<ul>${items}</ul>`}
  <footer>Generated ${now}. Cards live under editorial/source_cards/_pending/; drafts under editorial/drafts/_holding/.</footer>
</body>
</html>`;
}

function renderIndex({ splash, sections, dives, pending }, now) {
  const css = `
body { font-family: Georgia, serif; max-width: 760px; margin: 40px auto; padding: 24px; line-height: 1.55; background: #f7f6f1; }
h1 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 16px; text-transform: uppercase; letter-spacing: 0.18em; margin-bottom: 8px; }
h2 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 12px; text-transform: uppercase; letter-spacing: 0.14em; color: #555; margin: 32px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 6px; }
ul { list-style: none; padding: 0; margin: 0; }
li { padding: 10px 0; border-bottom: 1px solid #e6e4d8; }
a { color: #006699; text-decoration: none; font-size: 17px; }
a:hover { text-decoration: underline; }
.tally { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 12px; color: #777; margin-left: 8px; }
.label { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 11px; color: #888; margin-bottom: 16px; }
footer { font-size: 12px; color: #888; margin-top: 40px; font-family: "Helvetica Neue", Arial, sans-serif; }
`;
  const splashItem = splash ? `<ul><li>
    <a href="./splash.html">splash (hero + tile lines)</a>
    <span class="tally">${splash.heroCount} hero claims · ${splash.tileCount} tile claims</span>
  </li></ul>` : "";
  const sectionItems = sections.map((s) => `<li>
    <a href="./${escapeHtml(s.slug)}.html">${escapeHtml(s.slug)}</a>
    <span class="tally">${s.plateCount} plates · ${s.claimCount} tagged claims</span>
  </li>`).join("");
  const diveItems = dives.map((d) => `<li>
    <a href="./research/${escapeHtml(d.slug)}.html">${escapeHtml(d.slug)}</a>
    <span class="tally">${d.claimCount} tagged claims</span>
  </li>`).join("");
  const pendingBlock = (pending && pending.length > 0)
    ? `<ul>${pending.map((d) => `<li>
        <a href="${SECTION_SLUGS_FOR_INDEX.has(d.slug) ? './' + escapeHtml(d.slug) + '.html' : './research/' + escapeHtml(d.slug) + '.html'}">${escapeHtml(d.slug)} (draft)</a>
        <span class="tally pending-count">${d.count} pending</span>
      </li>`).join("")}
      <li><a href="./_pending.html">→ master queue (all pending across drafts)</a></li>
      </ul>`
    : `<div class="all-clear">✓ All claims verified. No drafts in flight.</div>`;

  return `<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Source audit · index</title><style>${css}
.pending-count { color: #b07b00; font-weight: 600; }
.all-clear { color: #2a7a30; font-style: italic; padding: 12px 0; }
h2.verify-header { color: #c83a00; }
</style></head>
<body>
  <h1>Source audit</h1>
  <div class="label">Every reader-facing surface, with claims tagged and clickable to upstream sources. Pipeline-tagged claims auto-resolve their reference date from panel_data.</div>
  <h2 class="verify-header">⚠ Verification queue</h2>
  ${pendingBlock}
  <h2>Front page</h2>
  ${splashItem}
  <h2>Topic sections</h2>
  <ul>${sectionItems}</ul>
  <h2>Research deep dives</h2>
  <ul>${diveItems}</ul>
  <footer>Generated ${now}. Run <code>node scripts/source_audit.mjs</code> to regenerate.</footer>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function summarizeSection(slug) {
  const pagePath = path.join(PAGES_DIR, `${slug}.astro`);
  if (!fs.existsSync(pagePath)) return null;
  const { abstractCitations } = extractSectionAbstract(slug);
  const plates = extractPlates(pagePath);
  const claimCount = (abstractCitations?.length || 0) + plates.reduce((s, p) => s + (p.citations?.length || 0), 0);
  return { slug, plateCount: plates.length, claimCount };
}

// Module-level map of all pending cards, populated by main() at startup.
// Threaded through resolveSource so card:<id> references to pending cards
// resolve as kind="card" with isPending=true, surfacing the verification UI
// on the regular audit page rather than failing as "card-missing".
let ALL_PENDING_CARDS = new Map();
let SECTION_SLUGS_FOR_INDEX = new Set();

function main() {
  const args = process.argv.slice(2);
  const sectionsToWrite = args.length ? args : ALL_SECTIONS;
  const registry = loadRegistry();
  ALL_PENDING_CARDS = loadAllPendingCards();
  SECTION_SLUGS_FOR_INDEX = new Set(ALL_SECTIONS);
  resetOrphanCitations();
  resetInvalidBocKeys();
  resetUncoveredHints();
  resetEnumerationMismatches();
  resetDeepDiveLinks();
  resetLengthChecks();
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const now = new Date().toISOString().slice(0, 16).replace("T", " ");

  for (const slug of sectionsToWrite) {
    const pagePath = path.join(PAGES_DIR, `${slug}.astro`);
    if (!fs.existsSync(pagePath)) {
      console.error(`skip ${slug}: ${pagePath} not found`);
      continue;
    }
    const { headlineQuestion, abstract, abstractCitations } = extractSectionAbstract(slug);
    const plates = extractPlates(pagePath);
    const pendingMap = ALL_PENDING_CARDS;
    const html = renderPage(slug, headlineQuestion, abstract, abstractCitations, plates, registry, now, pendingMap);
    const outPath = path.join(OUTPUT_DIR, `${slug}.html`);
    fs.writeFileSync(outPath, html, "utf-8");
    const claimCount = (abstractCitations?.length || 0) + plates.reduce((s, p) => s + (p.citations?.length || 0), 0);
    console.log(`wrote ${path.relative(repoRoot, outPath)} - ${plates.length} plates, ${claimCount} tagged claims`);
  }

  // Splash audit — hero + 6 tile lines. Always regenerated (cheap).
  const splashHtml = renderSplashPage(registry, now);
  const splashPath = path.join(OUTPUT_DIR, "splash.html");
  fs.writeFileSync(splashPath, splashHtml, "utf-8");
  console.log(`wrote ${path.relative(repoRoot, splashPath)}`);

  // Research deep dive audits — one per dive. Always regenerated (cheap).
  const researchDir = path.join(OUTPUT_DIR, "research");
  fs.mkdirSync(researchDir, { recursive: true });
  const dives = extractDeepDives();
  const diveSummaries = [];
  for (const dive of dives) {
    const sidecar = loadDiveSidecar(dive.slug);
    // If publishedPath is gone (dive in draft), fall back to holding draft.
    // The renderDivePage already prefers publishedPath but falls through to
    // draftPath; with holding-draft support we cover the in-flight case too.
    if (!dive.publishedPath) {
      const holdingPath = path.join(repoRoot, "editorial", "drafts", "_holding", `${dive.slug}.md`);
      if (fs.existsSync(holdingPath)) {
        dive.draftPath = path.relative(repoRoot, holdingPath).replace(/\\/g, "/");
      }
    }
    const diveHtml = renderDivePage(dive, sidecar, registry, now, ALL_PENDING_CARDS);
    const divePath = path.join(researchDir, `${dive.slug}.html`);
    fs.writeFileSync(divePath, diveHtml, "utf-8");
    const claimCount = sidecar?.citations?.length || 0;
    // Only published dives surface in the "Research deep dives" index group.
    // Drafted dives (publishedPath null) appear only in the Verification queue
    // group, so the user has one place to act on them instead of two listings.
    if (dive.publishedPath) {
      diveSummaries.push({ slug: dive.slug, title: dive.title, claimCount });
    }
    console.log(`wrote ${path.relative(repoRoot, divePath)} - ${claimCount} tagged claims${dive.publishedPath ? "" : " (DRAFT)"}`);
  }

  // Index reflects ALL sections with an existing audit page on disk — a
  // partial regen (e.g. `node scripts/source_audit.mjs policy`) must not
  // truncate the index to just the regenerated subset.
  const sectionSummaries = [];
  for (const slug of ALL_SECTIONS) {
    const auditPath = path.join(OUTPUT_DIR, `${slug}.html`);
    if (!fs.existsSync(auditPath)) continue;
    const summary = summarizeSection(slug);
    if (summary) sectionSummaries.push(summary);
  }

  // Splash summary — quick count.
  const hero = extractSplashHero();
  let tileCount = 0;
  for (const slug of ALL_SECTIONS) {
    const { citations } = extractTileLine(slug);
    tileCount += (citations || []).length;
  }
  const splashSummary = { heroCount: (hero.citations || []).length, tileCount };

  // Pending summaries — derived from _pending/<surface>/<id>.yaml directories.
  // Verification UI is now integrated into the regular audit pages
  // (audit/<slug>.html and audit/research/<slug>.html), so there is no
  // separate _verify/ directory. Clean it up if it exists from earlier runs.
  const verifyDir = path.join(OUTPUT_DIR, "_verify");
  if (fs.existsSync(verifyDir)) {
    fs.rmSync(verifyDir, { recursive: true, force: true });
    console.log(`removed legacy _verify/ directory; verification UI lives on regular audit pages now`);
  }
  const pendingDrafts = discoverHoldingDrafts();
  const pendingSummaries = pendingDrafts.map((slug) => ({
    slug,
    count: loadPendingCards(slug).length,
  }));

  // Master pending queue page.
  const masterPath = path.join(OUTPUT_DIR, "_pending.html");
  fs.writeFileSync(masterPath, renderPendingMasterIndex(pendingSummaries, now), "utf-8");
  console.log(`wrote ${path.relative(repoRoot, masterPath)}`);

  const indexHtml = renderIndex({ splash: splashSummary, sections: sectionSummaries, dives: diveSummaries, pending: pendingSummaries }, now);
  const indexPath = path.join(OUTPUT_DIR, "index.html");
  fs.writeFileSync(indexPath, indexHtml, "utf-8");
  console.log(`wrote ${path.relative(repoRoot, indexPath)}`);

  // Build-gate refusal: orphan citations (phrase declared in `citations:` but
  // doesn't anchor to prose). Catches author drift like "4.9-point" citation
  // left behind after prose was edited to "5.0-point". Audit pages still
  // wrote — the user can open them and see the "no inline match" markers —
  // but the build chain stops here so nothing ships with stale citations.
  // Invalid BoC pipeline keys (not in pipeline/catalog/boc_series.py) — refuse
  // ship until citations are fixed. Catches hallucinated Valet IDs that 404
  // the upstream link while pipeline data still flows from a different slot.
  const invalidBoc = [...new Set(getInvalidBocKeys())];
  if (invalidBoc.length > 0) {
    console.error("");
    console.error(`source_audit: ${invalidBoc.length} unrecognized BoC pipeline key(s) — not in pipeline/catalog/boc_series.py.`);
    console.error("Fix each by either (a) using the catalog slot name, (b) using a verified Valet ID, or (c) adding the series to the catalog.");
    console.error("");
    for (const k of invalidBoc) console.error(`  - pipeline:boc:${k}`);
    console.error("");
    process.exit(1);
  }

  // Reverse-lookup hints (advisory, non-blocking): uncovered prose tokens
  // that match a pipeline slot's current value — likely missing citations.
  const hints = getUncoveredHints();
  if (hints.length > 0) {
    console.log("");
    console.log(`source_audit: ${hints.length} reverse-lookup hint(s) — uncovered prose tokens that match a pipeline slot.`);
    console.log("Author probably wanted to cite the slot. Build continues; review the suggestions:");
    console.log("");
    for (const h of hints) console.log(`  ~ [${h.surface}] uncovered "${h.token}" → matches slot "${h.slot}" (latest = ${h.formatted})`);
    console.log("");
  }

  // Length-budget gate (writing-style.md §4.1f): HARD FAIL on hard-cap
  // overruns; soft-target overruns surface as warnings (non-blocking).
  const lengthWarnings = getLengthWarnings();
  if (lengthWarnings.length > 0) {
    console.log("");
    console.log(`source_audit: ${lengthWarnings.length} length-budget warning(s) (over soft target, within hard cap):`);
    for (const w of lengthWarnings) {
      console.log(`  ~ [${w.surface}] ${w.warnings.join("; ")}`);
    }
    console.log("");
  }
  const lengthViolations = getLengthViolations();
  if (lengthViolations.length > 0) {
    console.error("");
    console.error(`source_audit: ${lengthViolations.length} length-budget violation(s) — build refuses.`);
    console.error("Each surface below exceeds its hard cap from editorial/writing-style.md §4.1f. Trim or restructure.");
    console.error("");
    for (const v of lengthViolations) {
      console.error(`  - [${v.surface}] (${v.surfaceType}): ${v.violations.join("; ")}`);
    }
    console.error("");
    process.exit(1);
  }

  // Derived-slot materialization queue: HARD FAIL if any entries are
  // pending. The queue is a TODO that fires immediately, not a backlog.
  // Per `feedback_derived_slot_queue.md`: "as soon as something hits the
  // queue we start building infra." Stale entries = stale state.
  const queuePath = path.join(repoRoot, "editorial", "_derived_slot_queue.yaml");
  if (fs.existsSync(queuePath)) {
    try {
      const queueRaw = fs.readFileSync(queuePath, "utf-8");
      const queue = parseYaml(queueRaw);
      const pending = (queue?.queue || []).filter((q) => q.status === "pending_materialization");
      if (pending.length > 0) {
        console.error("");
        console.error(`source_audit: ${pending.length} derived-slot(s) pending materialization — build refuses.`);
        console.error("Each entry below is a derivation the fact-checker had to compute ad-hoc; backend must materialize it as a slot in pipeline/io/panel_data.py + pipeline/io/site_data.py before the build can pass. Queue is NOT a backlog.");
        console.error("");
        for (const p of pending) {
          console.error(`  - ${p.slot_name} (added ${p.added_at}, surface: ${p.surface})`);
          console.error(`      rule: ${(p.aggregation_rule || "").trim().slice(0, 120)}`);
        }
        console.error("");
        console.error("After materializing each entry: delete it from editorial/_derived_slot_queue.yaml.");
        process.exit(1);
      }
    } catch (e) {
      console.error(`(warn) failed to read derived-slot queue: ${e.message}`);
    }
  }

  // Deep-dive cross-link gate (§4.1f-3): blurbs cannot reference dives
  // until the dives are user-approved. Refuse build on any match.
  const deepDiveLinks = getDeepDiveLinks();
  if (deepDiveLinks.length > 0) {
    console.error("");
    console.error(`source_audit: ${deepDiveLinks.length} deep-dive cross-link(s) in reader-facing prose — banned per writing-style.md §4.1f-3.`);
    console.error("Cut the cross-link; deliver the blurb's macro point itself. Dives are AI-drafts not yet to standard.");
    console.error("");
    for (const d of deepDiveLinks) {
      console.error(`  - [${d.surface}] contains href: ${d.href}`);
    }
    console.error("");
    process.exit(1);
  }

  // Enumeration-count mismatches (Option A): a citation declared
  // expected_count but the referenced card's enumeration list has a different
  // number of entries — usually means the author updated the count in prose
  // (or the card's enumeration grew/shrank) without keeping them aligned.
  const enumMismatches = getEnumerationMismatches();
  if (enumMismatches.length > 0) {
    console.error("");
    console.error(`source_audit: ${enumMismatches.length} enumeration-count mismatch(es).`);
    console.error("Citation's expected_count doesn't match the card's enumeration list length:");
    console.error("");
    for (const m of enumMismatches) {
      console.error(`  - [${m.surface}] phrase "${m.phrase}" source ${m.source}: expected_count=${m.expected} but enumeration has ${m.actual} entries.`);
    }
    console.error("");
    process.exit(1);
  }

  // Orphan-citation gate: enforce only on SHIPPING surfaces. Dive sidecars
  // for dives in `_holding` (no `publishedPath` in sections.ts) are drafts
  // in flight; their orphans are expected and not ship-blocking.
  const heldDiveSlugs = new Set();
  for (const dive of dives) {
    if (!dive.publishedPath) heldDiveSlugs.add(dive.slug);
  }
  const allOrphans = getOrphanCitations();
  const orphans = allOrphans.filter((o) => {
    if (!o.surface?.startsWith?.("research/")) return true; // section surfaces always enforce
    const slug = o.surface.split("/")[1]?.split(" ")[0];
    return slug && !heldDiveSlugs.has(slug);
  });
  const skippedDraftOrphans = allOrphans.length - orphans.length;
  if (skippedDraftOrphans > 0) {
    console.log(`(skipping ${skippedDraftOrphans} orphan(s) from research dives in _holding — not ship-blocking)`);
  }
  if (orphans.length > 0) {
    console.error("");
    console.error(`source_audit: ${orphans.length} orphan citation(s) — phrase declared in sidecar/citations: but does NOT appear in the prose.`);
    console.error("Fix each by either (a) updating the citation's phrase: to match the prose verbatim, or (b) deleting the citation if it no longer belongs.");
    console.error("");
    for (const o of orphans) {
      console.error(`  - [${o.surface}] phrase: "${o.phrase}"  source: ${o.source}${o.note ? `  note: ${o.note}` : ""}`);
    }
    console.error("");
    process.exit(1);
  }
}

main();
