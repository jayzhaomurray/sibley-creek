#!/usr/bin/env node
/*
 * check_citation_coverage.mjs - build-time citation coverage gate.
 *
 * For every reader-facing prose surface on every section page:
 *   1. Tokenizes the title + interpretationHtml + section abstract for
 *      citable claims (percentages, dollar amounts, basis points,
 *      percentage points, dates, year markers, "first since X" patterns).
 *   2. Cross-checks each token against the surface's `citations[]` array.
 *   3. Fails the build if any STRICT surface has an uncovered token.
 *
 * Strict mode: a surface enters strict mode the moment it has any
 * citations[] entries. Surfaces without any citations stay in warn-only
 * mode (the script prints them as "needs-tagging" but does not fail the
 * build). This lets sections roll into the gate one at a time.
 *
 * The script is wired into `npm run build` via package.json so no prose
 * ships to the live site without passing the gate.
 *
 * Usage:
 *   node scripts/check_citation_coverage.mjs [<section>...]
 *
 * Exit codes:
 *   0 - no strict failures (build proceeds)
 *   1 - one or more strict surfaces have uncovered tokens (build halts)
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const PAGES_DIR = path.join(repoRoot, "src", "pages");
const SECTIONS_TS = path.join(repoRoot, "src", "data", "sections.ts");
const RESEARCH_DIR = path.join(repoRoot, "editorial", "published");
const RESEARCH_CITATIONS_DIR = path.join(repoRoot, "editorial", "source_cards", "research");
const ALL_SECTIONS = ["gdp", "inflation", "labour", "housing", "policy", "markets", "trade"];

// Mechanically rendered sections (src/lib/prose): coverage by construction
// via prose renderer + slot binding — every figure in the prose is
// slot-interpolated from panel_data at build time, and the page's surface
// fields are expressions (prose.surfaces[...].text) this script's static
// tokenizer cannot see. The audit-time anchoring of their slot-bound
// citations is enforced by scripts/source_audit.mjs, which resolves the
// rendered text. Intentional exemption, not tokenizer-blindness.
const MECHANICAL_SECTIONS = new Set(["markets"]);

// ---------------------------------------------------------------------------
// Parser (copied from source_audit.mjs - share via lib once both stabilize)
// ---------------------------------------------------------------------------

function readAstroFrontmatter(astroPath) {
  let text = fs.readFileSync(astroPath, "utf-8");
  // Strip UTF-8 BOM if present — silently dropped by the OS or by some
  // editors. Without this, the ^---\n frontmatter regex misses and the
  // gate sees zero plates in the file.
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  return m ? m[1] : "";
}

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
    else if (ch === closeChar) { depth--; if (depth === 0) return i; }
  }
  return -1;
}

function splitTopLevelObjects(arrayBody) {
  const objects = [];
  let i = 0;
  while (i < arrayBody.length) {
    while (i < arrayBody.length) {
      const ch = arrayBody[i];
      if (ch === " " || ch === "\n" || ch === "\t" || ch === "\r" || ch === ",") { i++; continue; }
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
    if (arrayBody[i] !== "{") break;
    const closeIdx = findMatchingClose(arrayBody, i + 1, "{", "}");
    if (closeIdx === -1) break;
    objects.push(arrayBody.slice(i, closeIdx + 1));
    i = closeIdx + 1;
  }
  return objects;
}

function extractStringChain(source, startIdx) {
  let i = startIdx;
  let out = "";
  while (i < source.length) {
    while (i < source.length && /\s/.test(source[i])) i++;
    const ch = source[i];
    if (ch !== '"' && ch !== "'") break;
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
    while (i < source.length && /\s/.test(source[i])) i++;
    if (source[i] === "+") { i++; continue; }
    break;
  }
  return { kind: "string", text: out, end: i };
}

function extractValue(source, startIdx) {
  let i = startIdx;
  while (i < source.length && /\s/.test(source[i])) i++;
  const ch = source[i];
  if (ch === '"' || ch === "'") return extractStringChain(source, i);
  if (ch === "[") {
    const close = findMatchingClose(source, i + 1, "[", "]");
    return { kind: "array", text: source.slice(i, close + 1), end: close + 1 };
  }
  if (ch === "{") {
    const close = findMatchingClose(source, i + 1, "{", "}");
    return { kind: "object", text: source.slice(i, close + 1), end: close + 1 };
  }
  let end = i;
  while (end < source.length && source[end] !== "," && source[end] !== "\n") end++;
  return { kind: "literal", text: source.slice(i, end).trim(), end };
}

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
    const prev = i === 0 ? "{" : objText[i - 1];
    if (!wordBoundary(prev)) continue;
    let ok = true;
    for (let j = 0; j < keyLen; j++) {
      if (objText[i + j] !== key[j]) { ok = false; break; }
    }
    if (!ok) continue;
    let j = i + keyLen;
    while (j < n && (objText[j] === " " || objText[j] === "\t")) j++;
    if (objText[j] !== ":") continue;
    let v = j + 1;
    while (v < n && /\s/.test(objText[v])) v++;
    return extractValue(objText, v);
  }
  return null;
}

function parseCitations(arrayText) {
  if (!arrayText || arrayText[0] !== "[") return [];
  const inner = arrayText.slice(1, -1);
  const objs = splitTopLevelObjects(inner);
  const out = [];
  for (const objText of objs) {
    const phrase = extractField(objText, "phrase");
    const source = extractField(objText, "source");
    if (phrase?.text && source?.text) out.push({ phrase: phrase.text, source: source.text });
  }
  return out;
}

/**
 * Registered-source rule (editorial/review_protocol.md, editorial/writing-style.md §4.1d):
 * every citation source must be `pipeline:<provider>:<key>`, `card:<id>`, or `derived`.
 * `other:<freeform>` is banned. This validator collects every `other:` source it sees
 * and fails the build after printing the offenders.
 */
function isValidSource(src) {
  if (!src) return false;
  if (src === "derived") return true;
  if (src.startsWith("pipeline:")) return true;
  if (src.startsWith("card:")) return true;
  return false;
}

function loadRegistryCards() {
  const yaml = fs.readFileSync(path.join(repoRoot, "editorial", "source_cards", "registry.yaml"), "utf-8");
  const cards = new Map();
  const blocks = yaml.split(/\n(?=  - id:)/);
  for (const block of blocks) {
    const idMatch = block.match(/^\s*-?\s*id:\s*(.+?)\s*$/m);
    if (!idMatch) continue;
    const id = idMatch[1].trim();
    const tier = block.match(/verification_tier:\s*"?([A-C])"?/)?.[1] ?? null;
    const userConfirmed = block.match(/user_confirmed_at:\s*"?(\d{4}-\d{2}-\d{2})/)?.[1] ?? null;
    const userApproved = block.match(/user_approved_at:\s*"?(\d{4}-\d{2}-\d{2})/)?.[1] ?? null;
    const mode = parseInt(block.match(/^\s+mode:\s*(\d+)/m)?.[1] ?? "0", 10);
    cards.set(id, { id, tier, userConfirmed, userApproved, mode });
  }
  return cards;
}

function loadPendingCardIds() {
  const dir = path.join(repoRoot, "editorial", "source_cards", "_pending");
  if (!fs.existsSync(dir)) return new Set();
  const ids = new Set();
  for (const sub of fs.readdirSync(dir)) {
    const p = path.join(dir, sub);
    try {
      if (!fs.statSync(p).isDirectory()) continue;
    } catch { continue; }
    for (const f of fs.readdirSync(p)) {
      if (f.endsWith(".yaml")) ids.add(f.replace(/\.yaml$/, ""));
    }
  }
  return ids;
}

function checkCardTier(src, registryCards, pendingIds) {
  if (!src.startsWith("card:")) return { valid: true };
  const id = src.slice(5);
  if (pendingIds.has(id)) {
    return { valid: false, reason: `card:${id} is in _pending/ — awaiting user approval` };
  }
  const card = registryCards.get(id);
  if (!card) {
    return { valid: false, reason: `card:${id} is not in registry.yaml` };
  }
  if (!card.tier) {
    return { valid: false, reason: `card:${id} has no verification_tier (untagged)` };
  }
  if (card.mode === 3 && !card.userApproved) {
    return { valid: false, reason: `card:${id} is Mode 3 without user_approved_at` };
  }
  if ((card.tier === "B" || card.tier === "C") && !card.userConfirmed) {
    return { valid: false, reason: `card:${id} is Tier ${card.tier} without user_confirmed_at` };
  }
  return { valid: true };
}

function extractPlates(sectionAstroPath) {
  const fm = readAstroFrontmatter(sectionAstroPath);
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
    const title = extractField(objText, "title");
    const interpretationHtml = extractField(objText, "interpretationHtml");
    const citations = extractField(objText, "citations");
    plates.push({
      id: id?.text ?? null,
      title: title?.text ?? null,
      interpretationHtml: interpretationHtml?.text ?? null,
      citations: citations ? parseCitations(citations.text) : [],
    });
  }
  return plates;
}

function extractSectionAbstract(slug) {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  const slugRe = new RegExp(`slug:\\s*"${slug}"`);
  const m = text.match(slugRe);
  if (!m) return { abstract: null, abstractCitations: [], tileLine: null, tileLineCitations: [] };
  const start = m.index;
  const slice = text.slice(start, start + 5000);
  const bodyMatch = slice.match(/body:\s*/);
  let abstract = null;
  if (bodyMatch) {
    const bodyStart = bodyMatch.index + bodyMatch[0].length;
    abstract = extractStringChain(slice, bodyStart).text;
  }
  let abstractCitations = [];
  const acMatch = slice.match(/abstractCitations:\s*\[/);
  if (acMatch) {
    const acStart = acMatch.index + acMatch[0].length;
    const acClose = findMatchingClose(slice, acStart, "[", "]");
    if (acClose !== -1) {
      abstractCitations = parseCitations("[" + slice.slice(acStart, acClose) + "]");
    }
  }
  // tileLine: the splash-tile sub-headline. Same per-section scope as abstract.
  let tileLine = null;
  const tlMatch = slice.match(/tileLine:\s*/);
  if (tlMatch) {
    const tlStart = tlMatch.index + tlMatch[0].length;
    tileLine = extractStringChain(slice, tlStart).text;
  }
  let tileLineCitations = [];
  const tlcMatch = slice.match(/tileLineCitations:\s*\[/);
  if (tlcMatch) {
    const tlcStart = tlcMatch.index + tlcMatch[0].length;
    const tlcClose = findMatchingClose(slice, tlcStart, "[", "]");
    if (tlcClose !== -1) {
      tileLineCitations = parseCitations("[" + slice.slice(tlcStart, tlcClose) + "]");
    }
  }
  return { abstract, abstractCitations, tileLine, tileLineCitations };
}

/**
 * Extract the splashHero const + its citations from sections.ts.
 * Format: `export const splashHero: {...} = { abstract: "...", citations: [...] };`
 */
function extractSplashHero() {
  const text = fs.readFileSync(SECTIONS_TS, "utf-8");
  const m = text.match(/export const splashHero[:\s][^=]*=\s*{/);
  if (!m) return { abstract: null, citations: [] };
  const objStart = m.index + m[0].length - 1;
  const objClose = findMatchingClose(text, objStart + 1, "{", "}");
  if (objClose === -1) return { abstract: null, citations: [] };
  const objText = text.slice(objStart, objClose + 1);
  const abstractField = extractField(objText, "abstract");
  const citationsField = extractField(objText, "citations");
  return {
    abstract: abstractField?.text ?? null,
    citations: citationsField ? parseCitations(citationsField.text) : [],
  };
}

// ---------------------------------------------------------------------------
// Tokenizer — extract citable tokens from prose.
// ---------------------------------------------------------------------------

const TOKEN_PATTERNS = [
  // Percentages: 2.3%, -1.0%
  { name: "percentage", re: /-?\d+(?:\.\d+)?\s*%/g },
  // Percentages in word form: "1 percent", "1 per cent", "2.3 percent"
  { name: "percent-word", re: /-?\d+(?:\.\d+)?\s+per\s*cent\b/gi },
  // Percentage points: 0.5pp, 4.9 percentage points
  { name: "pp", re: /-?\d+(?:\.\d+)?\s*pp\b/g },
  { name: "pp-long", re: /-?\d+(?:\.\d+)?\s+percentage points?/gi },
  // Basis points
  { name: "bps", re: /-?\d+\s*(?:bps|basis points?)/gi },
  // Dollar amounts with magnitude
  { name: "dollar", re: /-?\$?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|trillion|bn|tn)\b/gi },
  // Dollar with explicit $
  { name: "dollar-bare", re: /\$\d+(?:\.\d+)?(?:k|bn|m|M|tn)?\b/g },
  // Counts in thousands shorthand: 67k, 282k
  { name: "count-k", re: /-?\d+(?:\.\d+)?k\b/g },
  // Date tokens: Q4 2025, 2026Q1, January 2026, Jan 2026
  { name: "quarter", re: /\bQ[1-4]\s+(?:19|20)\d{2}\b/g },
  { name: "quarter-rev", re: /\b(?:19|20)\d{2}\s*Q[1-4]\b/g },
  { name: "month-year", re: /\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(?:19|20)\d{2}\b/g },
  // ISO dates
  { name: "iso-date", re: /\b(?:19|20)\d{2}-\d{2}(?:-\d{2})?\b/g },
  // Year-only tokens (cautious — only when not in a "since 20XX" or chart-axis context)
  { name: "year-decade", re: /\b(?:19|20)\d{2}\b(?!\s*-\s*\d{2})/g },
  // "first since X", "deepest since Y", "Nth straight/consecutive/in a row"
  { name: "first-since", re: /\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+(?:st|nd|rd|th)|deepest|highest|lowest|biggest|smallest)\s+(?:since|in)\s+\d/gi },
  { name: "nth-straight", re: /\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+(?:st|nd|rd|th))\s+(?:consecutive|straight|in a row)/gi },
];

// Strip HTML tags + anchor URLs from prose before tokenizing, so we don't
// match year tokens inside href="/research/..." links or HTML entity codes.
function plainText(html) {
  if (!html) return "";
  return html
    .replace(/<a\b[^>]*>([\s\S]*?)<\/a>/gi, "$1") // keep anchor text, drop href
    .replace(/<[^>]+>/g, " ")
    .replace(/&mdash;/g, "—")
    .replace(/&ndash;/g, "–")
    .replace(/&amp;/g, "&")
    .replace(/&[a-z]+;/g, " ");
}

function tokenize(text) {
  const plain = plainText(text);
  const tokens = new Map();
  for (const { name, re } of TOKEN_PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(plain)) !== null) {
      const tok = m[0].trim();
      if (!tok) continue;
      if (!tokens.has(tok)) tokens.set(tok, { token: tok, kind: name });
    }
  }
  return Array.from(tokens.values());
}

function numericVariants(token) {
  // Match either "1%" or "1 percent" / "1 per cent" forms. Produce the
  // complete set of equivalent surface forms so a citation tagging any
  // one of them covers all of them.
  const pctSign = token.match(/^(-?)(\d+)(?:\.(\d+))?\s*%$/);
  const pctWord = token.match(/^(-?)(\d+)(?:\.(\d+))?\s+per\s*cent$/i);
  const pct = pctSign || pctWord;
  if (pct) {
    const sign = pct[1] || "";
    const intPart = pct[2];
    const decPart = pct[3];
    const set = new Set();
    // sign variants
    set.add(`${sign}${intPart}%`);
    set.add(`${sign}${intPart}.0%`);
    set.add(`${sign}${intPart}.00%`);
    // word variants (both "percent" and "per cent")
    set.add(`${sign}${intPart} percent`);
    set.add(`${sign}${intPart} per cent`);
    set.add(`${sign}${intPart}.0 percent`);
    set.add(`${sign}${intPart}.0 per cent`);
    if (decPart) {
      const withDec = `${sign}${intPart}.${decPart}`;
      const stripped = withDec.replace(/\.?0+$/, "");
      set.add(`${withDec}%`);
      set.add(`${stripped}%`);
      set.add(`${withDec} percent`);
      set.add(`${withDec} per cent`);
    }
    return Array.from(set);
  }
  // pp variants: "0.5pp" / "0.50pp" / "0.5 pp" / "0.5 percentage points"
  const pp = token.match(/^(-?)(\d+)(?:\.(\d+))?\s*pp$/);
  if (pp) {
    const sign = pp[1] || "";
    const intPart = pp[2];
    const decPart = pp[3];
    const base = decPart ? `${sign}${intPart}.${decPart}` : `${sign}${intPart}`;
    return [
      `${base}pp`,
      `${base} pp`,
      `${base} percentage points`,
      `${base} percentage point`,
      `${sign}${intPart}.0pp`,
      `${sign}${intPart}.00pp`,
    ];
  }
  return [];
}

function isCovered(token, citations) {
  const tNorm = token.toLowerCase().replace(/\s+/g, " ").trim();
  const variants = numericVariants(token).map((v) => v.toLowerCase());
  for (const c of citations) {
    const cNorm = c.phrase.toLowerCase().replace(/\s+/g, " ").trim();
    if (cNorm.includes(tNorm)) return true;
    if (tNorm.includes(cNorm)) return true;
    for (const v of variants) {
      if (cNorm.includes(v)) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function checkSurface(slug, surfaceLabel, prose, citations) {
  const tokens = tokenize(prose);
  const uncovered = tokens.filter((t) => !isCovered(t.token, citations));
  return { tokens, uncovered, mode: citations.length > 0 ? "strict" : "needs-tagging" };
}

// STRICT_NEEDS_TAGGING: when true, a surface that has citable tokens but
// no citations[] FAILS the build (instead of WARN). Codifies the rule
// that no prose with verifiable claims may ship without explicit
// citations. Per the editorial canon: every reader-facing claim — user-
// or LLM-written — gets the same gate.
const STRICT_NEEDS_TAGGING = true;

/**
 * Strip markdown formatting from a deep-dive body so the tokenizer
 * doesn't trip over heading hashes, list bullets, link syntax, etc.
 */
function stripMarkdown(md) {
  if (!md) return "";
  return md
    .replace(/^---\n[\s\S]*?\n---\n/, "")       // YAML frontmatter
    .replace(/```[\s\S]*?```/g, " ")             // fenced code blocks
    .replace(/`[^`]*`/g, " ")                    // inline code
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")       // images
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")     // links: keep text
    .replace(/^#+\s+/gm, "")                     // heading hashes
    .replace(/^>\s?/gm, "")                      // blockquote markers
    .replace(/\*\*([^*]+)\*\*/g, "$1")           // bold
    .replace(/\*([^*]+)\*/g, "$1")               // italic
    .replace(/_([^_]+)_/g, "$1")                 // underscore italic
    .replace(/^\s*[-*+]\s+/gm, "")               // list bullets
    .replace(/^\s*\d+\.\s+/gm, "");              // ordered list markers
}

function loadResearchSidecar(slug) {
  const sidecarPath = path.join(RESEARCH_CITATIONS_DIR, `${slug}.yaml`);
  if (!fs.existsSync(sidecarPath)) return null;
  try {
    const raw = fs.readFileSync(sidecarPath, "utf-8");
    const parsed = parseYaml(raw);
    return Array.isArray(parsed?.citations) ? parsed.citations : [];
  } catch (e) {
    console.error(`error parsing ${sidecarPath}: ${e.message}`);
    return [];
  }
}

function discoverResearchDives() {
  if (!fs.existsSync(RESEARCH_DIR)) return [];
  return fs.readdirSync(RESEARCH_DIR)
    .filter((f) => f.endsWith(".md") && f !== "README.md")
    .map((f) => f.replace(/\.md$/, ""));
}

function main() {
  const args = process.argv.slice(2);
  // Default: scan all sections + all research dives. With explicit args,
  // limit to those slugs.
  const allDives = discoverResearchDives();
  let sections = args.length ? args.filter((a) => ALL_SECTIONS.includes(a)) : ALL_SECTIONS;
  let dives = args.length ? args.filter((a) => allDives.includes(a)) : allDives;
  // If user passed args that match neither sections nor dives, treat them
  // as section slugs (backward compat) and let the section path skip them.
  if (args.length && sections.length === 0 && dives.length === 0) {
    sections = args;
  }

  let strictFails = 0;
  let warnSurfaces = 0;
  let strictPasses = 0;

  const report = [];
  // Registered-source rule: collect any citation whose `source:` is not
  // pipeline:* / card:* / derived. These fail the build at the end.
  const invalidSources = [];
  // Tier-verification rule: collect card:* references whose card is in _pending/,
  // whose tier is B/C without user_confirmed_at, or whose mode=3 lacks user_approved_at.
  const tierViolations = [];
  const registryCards = loadRegistryCards();
  const pendingIds = loadPendingCardIds();
  const recordInvalid = (where, citations) => {
    for (const c of citations || []) {
      if (!isValidSource(c.source)) {
        invalidSources.push({ where, phrase: c.phrase, source: c.source });
      } else if (c.source.startsWith("card:")) {
        const tierCheck = checkCardTier(c.source, registryCards, pendingIds);
        if (!tierCheck.valid) {
          tierViolations.push({ where, phrase: c.phrase, source: c.source, reason: tierCheck.reason });
        }
      }
    }
  };

  for (const slug of sections) {
    const pagePath = path.join(PAGES_DIR, `${slug}.astro`);
    if (!fs.existsSync(pagePath)) continue;

    if (MECHANICAL_SECTIONS.has(slug)) {
      console.error(`  (${slug}: mechanical prose — coverage by construction via prose renderer + slot binding; see source_audit.mjs)`);
      continue;
    }

    const { abstract, abstractCitations, tileLine, tileLineCitations } = extractSectionAbstract(slug);
    const plates = extractPlates(pagePath);

    const surfaces = [];
    if (abstract) {
      surfaces.push({
        label: "section-abstract",
        prose: abstract,
        citations: abstractCitations,
      });
    }
    if (tileLine) {
      surfaces.push({
        label: "tile-line",
        prose: tileLine,
        citations: tileLineCitations,
      });
    }
    for (const p of plates) {
      const combined = [p.title, p.interpretationHtml].filter(Boolean).join(" ");
      surfaces.push({
        label: p.id || "plate-?",
        prose: combined,
        citations: p.citations || [],
      });
    }

    for (const s of surfaces) {
      recordInvalid(`${slug}/${s.label}`, s.citations);
      const r = checkSurface(slug, s.label, s.prose, s.citations);
      if (r.mode === "strict") {
        if (r.uncovered.length > 0) {
          strictFails++;
          report.push({ slug, label: s.label, kind: "FAIL", uncovered: r.uncovered, totalTokens: r.tokens.length, citationsCount: s.citations.length });
        } else {
          strictPasses++;
        }
      } else {
        if (r.tokens.length > 0) {
          if (STRICT_NEEDS_TAGGING) {
            strictFails++;
            report.push({ slug, label: s.label, kind: "FAIL", uncovered: r.tokens, totalTokens: r.tokens.length, citationsCount: 0, reason: "no citations[] on a surface with citable tokens" });
          } else {
            warnSurfaces++;
            report.push({ slug, label: s.label, kind: "WARN", uncovered: r.tokens, totalTokens: r.tokens.length, citationsCount: 0 });
          }
        }
      }
    }
  }

  // Splash hero abstract — top-of-page synthesis on /
  if (!args.length || args.includes("splash")) {
    const hero = extractSplashHero();
    if (hero.abstract) {
      recordInvalid("splash/hero-abstract", hero.citations);
      const r = checkSurface("splash", "hero-abstract", hero.abstract, hero.citations);
      if (r.mode === "strict") {
        if (r.uncovered.length > 0) {
          strictFails++;
          report.push({ slug: "splash", label: "hero-abstract", kind: "FAIL", uncovered: r.uncovered, totalTokens: r.tokens.length, citationsCount: hero.citations.length });
        } else {
          strictPasses++;
        }
      } else if (r.tokens.length > 0) {
        warnSurfaces++;
        report.push({ slug: "splash", label: "hero-abstract", kind: "WARN", uncovered: r.tokens, totalTokens: r.tokens.length, citationsCount: 0 });
      }
    }
  }

  // Research deep dives — each as a single surface (the full body)
  for (const diveSlug of dives) {
    const mdPath = path.join(RESEARCH_DIR, `${diveSlug}.md`);
    if (!fs.existsSync(mdPath)) continue;
    const md = fs.readFileSync(mdPath, "utf-8");
    const body = stripMarkdown(md);
    const citations = loadResearchSidecar(diveSlug) || [];
    recordInvalid(`research/${diveSlug}`, citations);
    const r = checkSurface(`research/${diveSlug}`, "body", body, citations);
    if (r.mode === "strict") {
      if (r.uncovered.length > 0) {
        strictFails++;
        report.push({ slug: `research/${diveSlug}`, label: "body", kind: "FAIL", uncovered: r.uncovered, totalTokens: r.tokens.length, citationsCount: citations.length });
      } else {
        strictPasses++;
      }
    } else {
      if (r.tokens.length > 0) {
        if (STRICT_NEEDS_TAGGING) {
          strictFails++;
          report.push({ slug: `research/${diveSlug}`, label: "body", kind: "FAIL", uncovered: r.tokens, totalTokens: r.tokens.length, citationsCount: 0, reason: "no sidecar at editorial/source_cards/research/" });
        } else {
          warnSurfaces++;
          report.push({ slug: `research/${diveSlug}`, label: "body", kind: "WARN", uncovered: r.tokens, totalTokens: r.tokens.length, citationsCount: 0 });
        }
      }
    }
  }

  // Print report.
  for (const r of report) {
    const head = `${r.kind} ${r.slug} ${r.label} (${r.citationsCount} citations, ${r.totalTokens} tokens, ${r.uncovered.length} uncovered)`;
    if (r.kind === "FAIL") console.error(`\n  ✗ ${head}`);
    else console.error(`\n  ! ${head} — surface has no citations[] yet; treat as needs-tagging`);
    for (const u of r.uncovered.slice(0, 20)) {
      console.error(`     - "${u.token}" (${u.kind})`);
    }
    if (r.uncovered.length > 20) console.error(`     ... and ${r.uncovered.length - 20} more`);
  }

  console.error("");
  console.error(`citation coverage: ${strictPasses} strict pass · ${strictFails} strict FAIL · ${warnSurfaces} needs-tagging`);

  // Registered-source rule check. Print every other:* offender and fail.
  if (invalidSources.length > 0) {
    console.error("");
    console.error(`registered-source rule: ${invalidSources.length} citation(s) use a banned source type.`);
    console.error("Every source must be pipeline:<provider>:<key>, card:<id>, or derived. The other:<freeform> pattern is banned.");
    console.error("See editorial/review_protocol.md § Registered-source rule and editorial/writing-style.md § 4.1d.");
    for (const v of invalidSources.slice(0, 40)) {
      console.error(`   ✗ ${v.where}: "${v.phrase}" -> source: ${v.source}`);
    }
    if (invalidSources.length > 40) console.error(`   ... and ${invalidSources.length - 40} more`);
    console.error("");
    console.error("Build blocked. Promote each other:* source to a registered card in editorial/source_cards/registry.yaml, or replace with pipeline:* / derived.");
    process.exit(1);
  }

  // Tier-verification rule check. Print every tier violation and fail.
  if (tierViolations.length > 0) {
    console.error("");
    console.error(`tier-verification rule: ${tierViolations.length} citation(s) reference cards that have not closed the verification chain.`);
    console.error("Every card cited on the live site must be either Tier A (primary-verified), or Tier B/C with user_confirmed_at filled, or Mode 3 with user_approved_at.");
    console.error("See editorial/review_protocol.md § 'Tiered verification' and editorial/credible_secondaries.md.");
    for (const v of tierViolations.slice(0, 40)) {
      console.error(`   ✗ ${v.where}: "${v.phrase}" -> ${v.source} (${v.reason})`);
    }
    if (tierViolations.length > 40) console.error(`   ... and ${tierViolations.length - 40} more`);
    console.error("");
    console.error("Build blocked. Walk the verification queue at editorial/source_cards/audit/_pending.html and approve or reject each pending card.");
    process.exit(1);
  }

  if (strictFails > 0) {
    console.error("");
    console.error("Build blocked. Tag the failed surfaces' missing claims with citations[] entries or document an exemption.");
    process.exit(1);
  }

  if (warnSurfaces > 0) {
    console.error("");
    console.error("Heads up: the surfaces above have no citations[] yet. They don't block the build, but they're not under audit either. Tag them when you can.");
  }
  process.exit(0);
}

main();
