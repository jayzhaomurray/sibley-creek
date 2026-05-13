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

const ALL_SECTIONS = ["gdp", "inflation", "labour", "housing", "policy", "markets", "trade"];

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
  if (!arrayText || arrayText[0] !== "[") return [];
  const inner = arrayText.slice(1, -1);
  const objs = splitTopLevelObjects(inner);
  const out = [];
  for (const objText of objs) {
    const phrase = extractField(objText, "phrase");
    const source = extractField(objText, "source");
    const note = extractField(objText, "note");
    if (phrase?.text && source?.text) {
      out.push({
        phrase: phrase.text,
        source: source.text,
        note: note?.text ?? null,
      });
    }
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
    const interpretationHtml = extractField(objText, "interpretationHtml");
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
function annotateProse(prose, citations, registry) {
  if (!prose) return { html: "", resolved: [] };
  const resolved = [];
  // We render plaintext-ish: keep the existing HTML in the blurb (it has
  // <a> tags etc.) but wrap occurrences of each citation phrase.
  let html = prose;
  citations.forEach((c, idx) => {
    const phrase = c.phrase;
    const card = resolveSource(c.source, registry);
    resolved.push({ ...c, ...card, refNum: idx + 1 });
    // First-occurrence replace, escape regex
    const safe = phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const replacement = `<span class="claim" data-ref="${idx + 1}">${escapeHtml(phrase)}<sup class="claim-sup">[${idx + 1}]</sup></span>`;
    html = html.replace(new RegExp(safe), replacement);
  });
  return { html, resolved };
}

function resolveSource(srcId, registry) {
  if (!srcId) return { kind: "unknown", label: "(no source)", url: null, excerpt: null };
  if (srcId.startsWith("card:")) {
    const id = srcId.slice(5);
    const card = registry.get(id);
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
    };
  }
  if (srcId.startsWith("pipeline:")) {
    return {
      kind: "pipeline",
      label: srcId,
      url: null,
      excerpt: "Auto-refreshed via the data pipeline. Latest value is whatever the pipeline emitted on its most recent run.",
    };
  }
  if (srcId === "derived") {
    return { kind: "derived", label: "Derived (arithmetic from other tagged claims)", url: null, excerpt: null };
  }
  return { kind: "other", label: srcId, url: null, excerpt: null };
}

function renderPage(slug, headlineQuestion, abstract, abstractCitations, plates, registry, now) {
  const sectionAbs = annotateProse(abstract, abstractCitations || [], registry);
  const plateRenders = plates.map((p) => {
    const blurb = annotateProse(p.interpretationHtml, p.citations || [], registry);
    return { ...p, blurb };
  });

  // Aggregate all claims into a sidebar ledger
  const allClaims = [];
  if (sectionAbs.resolved.length > 0) {
    sectionAbs.resolved.forEach((r) => allClaims.push({ surface: "abstract", ...r }));
  }
  plateRenders.forEach((p) => {
    (p.blurb.resolved || []).forEach((r) => allClaims.push({ surface: p.id || p.number, plate: p, ...r }));
  });

  const css = `
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
.claim-sup {
  color: #b07b00;
  font-weight: 700;
  font-size: 0.8em;
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
`;

  const renderLedgerItem = (r) => {
    const kindClass = r.kind || "unknown";
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
    return `
      <div class="ledger-item">
        <span class="ledger-ref ${kindClass}">[${r.refNum}]</span>
        <span class="ledger-source-label">${escapeHtml(r.label)}</span>
        <div class="ledger-phrase">"${escapeHtml(r.phrase)}"</div>
        ${excerptBlock}
        ${metaBlock}
        ${noteBlock}
        ${linkBlock}
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
        <h3 class="plate-title">${escapeHtml(p.title || "")} <button class="edit-btn" onclick="document.getElementById('edit-plate-${idx}').classList.toggle('open')">✎ Propose edit</button></h3>
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
<style>${css}</style>
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
  </script>
</body>
</html>`;
}

function renderIndex(sections, now) {
  const css = `
body { font-family: Georgia, serif; max-width: 720px; margin: 40px auto; padding: 24px; line-height: 1.55; background: #f7f6f1; }
h1 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 16px; text-transform: uppercase; letter-spacing: 0.18em; }
ul { list-style: none; padding: 0; }
li { padding: 12px 0; border-bottom: 1px solid #ddd; }
a { color: #006699; text-decoration: none; font-size: 18px; }
a:hover { text-decoration: underline; }
.tally { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 12px; color: #777; margin-left: 8px; }
footer { font-size: 12px; color: #888; margin-top: 32px; font-family: "Helvetica Neue", Arial, sans-serif; }
`;
  const items = sections.map((s) => `
    <li>
      <a href="./${escapeHtml(s.slug)}.html">${escapeHtml(s.slug)}</a>
      <span class="tally">${s.plateCount} plates · ${s.claimCount} tagged claims</span>
    </li>`).join("");
  return `<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Source audit · index</title><style>${css}</style></head>
<body>
  <h1>Source audit · all sections</h1>
  <ul>${items}</ul>
  <footer>Generated ${now}. Run <code>node scripts/source_audit.mjs</code> to regenerate.</footer>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  const sections = args.length ? args : ALL_SECTIONS;
  const registry = loadRegistry();
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const now = new Date().toISOString().slice(0, 16).replace("T", " ");
  const summaries = [];

  for (const slug of sections) {
    const pagePath = path.join(PAGES_DIR, `${slug}.astro`);
    if (!fs.existsSync(pagePath)) {
      console.error(`skip ${slug}: ${pagePath} not found`);
      continue;
    }
    const { headlineQuestion, abstract, abstractCitations } = extractSectionAbstract(slug);
    const plates = extractPlates(pagePath);
    const html = renderPage(slug, headlineQuestion, abstract, abstractCitations, plates, registry, now);
    const outPath = path.join(OUTPUT_DIR, `${slug}.html`);
    fs.writeFileSync(outPath, html, "utf-8");
    const claimCount = (abstractCitations?.length || 0) + plates.reduce((s, p) => s + (p.citations?.length || 0), 0);
    summaries.push({ slug, plateCount: plates.length, claimCount });
    console.log(`wrote ${path.relative(repoRoot, outPath)} - ${plates.length} plates, ${claimCount} tagged claims`);
  }

  const indexHtml = renderIndex(summaries, now);
  const indexPath = path.join(OUTPUT_DIR, "index.html");
  fs.writeFileSync(indexPath, indexHtml, "utf-8");
  console.log(`wrote ${path.relative(repoRoot, indexPath)}`);
}

main();
