/**
 * check_reader_copy_leakage.mjs
 *
 * Post-build guard: fail loudly if any reader-facing page in dist/ contains
 * LLM / implementation / internal-process vocabulary in reader-visible text.
 *
 * Background
 * ----------
 * Builder agents repeatedly paraphrase their specs into placeholder prose,
 * leaking implementation vocabulary (CSS values, process phases, agent jargon)
 * onto live pages. This script is the terminal gate: if the banned vocabulary
 * survives into dist/, the build fails with a precise report.
 *
 * What it scans
 * -------------
 * Reader-visible text only. Before matching, each HTML file is stripped of:
 *   - <script>...</script> blocks (JS source, JSON islands)
 *   - <style>...</style>  blocks (CSS rules contain 1px, opacity, stroke, etc.)
 *   - HTML comments  <!-- ... -->
 *   - aria-hidden="true" subtrees (content hidden from screen-reader users)
 *   - HTML attribute values (href, class, data-*, aria-label, etc.) —
 *     only text node content between tags is evaluated
 *
 * Text extraction is deliberate but lightweight: we collapse the stripped HTML
 * to its text nodes by removing all remaining tags, leaving the readable prose.
 * This is intentionally imperfect for deeply-nested edge cases but is precise
 * enough for the categories of leakage we're guarding against, and avoids a
 * heavy dependency (cheerio / jsdom) for a CI gate.
 *
 * Exclusions
 * ----------
 * Same as check_tk_in_dist.mjs:
 *   - dist/og-preview/
 *   - dist/chart-alternatives/
 *   - dist/chart-archive/
 *
 * False-positive discipline
 * -------------------------
 * Every banned term was tested against the built good pages (inflation, labour,
 * output, trade, monetary, housing, markets, splash, about, research) before
 * shipping. "pipeline" and "slot" and "dispatch" are NOT banned — they appear
 * in legitimate editorial and reader copy. When in doubt, exclude a term; a
 * gate that false-fails good copy is worse than one that misses a borderline
 * case. The writer + three-gate review handles nuance; this catches the blatant
 * leaks.
 *
 * Verified proof of detection
 * ---------------------------
 * The /recession-watch/ methodology zone (as built in the initial Phase A
 * scaffold) contains confirmed leaks: "auto-zoom", "the information",
 * "1px" and "0.28" inside <code> text nodes, and "Phase A" in prose.
 * Run against that built page, this script flags all of them.
 */

import { readdirSync, readFileSync } from "fs";
import { join, relative } from "path";

const DIST_DIR = new URL("../dist", import.meta.url).pathname.replace(
  /^\/([A-Za-z]:)/,
  "$1"
);

// ============================================================
// BANNED_READER_LEAKAGE — extend this array as new tic patterns emerge.
//
// Each entry is:
//   { pattern: RegExp, label: string, note: string }
//
// Rules for adding:
//   - Patterns must NOT match inside <style>, <script>, or HTML attributes
//     (the extractor below strips those before matching).
//   - Test every new term against all existing good pages before adding.
//   - When uncertain about false positives, leave the term out.
// ============================================================
const BANNED_READER_LEAKAGE = [

  // ------------------------------------------------------------------
  // CSS / SVG implementation vocabulary leaking into prose
  // These are visual-spec values that have no place in reader sentences.
  // ------------------------------------------------------------------
  {
    pattern: /\bauto-zoom\b/i,
    label: "auto-zoom",
    note: "CSS/spec term. Reader copy should name the behaviour ('fixed axis'), not the implementation.",
  },
  {
    // "1px stroke" / "hairline 0.5px" in prose. NOT matched inside
    // <style> (stripped) or SVG attribute values (stripped).
    // \b[0-9]+(?:\.[0-9]+)?px\b catches "1px", "0.5px", "-6px" etc.
    // Legit econ prose never contains CSS measurement tokens.
    pattern: /\b\d+(?:\.\d+)?px\b/,
    label: "CSS px measurement",
    note: "CSS measurement token in prose. Remove or reframe (e.g. 'thin line').",
  },
  {
    // Bare decimal that follows the word "opacity" — catches "0.28 opacity"
    // or "opacity 0.28" as spec-value leakage. Does not catch standalone
    // decimals like "0.28 percentage points" (econ vocab) because those
    // won't have "opacity" nearby. We match the word "opacity" followed
    // within 10 chars by a decimal, OR a decimal followed within 10 chars
    // by "opacity".
    pattern: /opacity\s+[0-9]+\.[0-9]+|[0-9]+\.[0-9]+\s+opacity/i,
    label: "opacity decimal value",
    note: "Opacity spec value in reader prose. Remove — reader copy doesn't specify rendering.",
  },
  {
    pattern: /\bstroke-opacity\b/i,
    label: "stroke-opacity",
    note: "SVG attribute name in reader prose.",
  },
  {
    pattern: /\bhairline\b/i,
    label: "hairline",
    note: "Graphic-design term. Reader copy says 'thin line' or 'rule'.",
  },
  {
    // "aspect-ratio" in prose. Common in spec writing; no place in reader copy.
    pattern: /\baspect-ratio\b/i,
    label: "aspect-ratio",
    note: "CSS property name in reader prose.",
  },
  {
    // viewBox only appears in SVG attributes; if it leaks into text nodes it's
    // a templating error.
    pattern: /\bviewBox\b/,
    label: "viewBox",
    note: "SVG attribute in reader text node — templating error.",
  },

  // ------------------------------------------------------------------
  // Process / agent / LLM vocabulary
  // These are project-internal terms that have no business in reader copy.
  // ------------------------------------------------------------------
  {
    // "Phase A", "Phase B", "Phase C" — capital letter after Phase.
    // Does NOT match "expansion phase", "late phase", "phase of the cycle"
    // (bare lowercase "phase" + common econ words).
    pattern: /\bPhase\s+[A-Z]\b/,
    label: "Phase X (process phase label)",
    note: "Process-phase label from implementation spec. Rewrite without the label.",
  },
  {
    pattern: /\bscaffold\b/i,
    label: "scaffold",
    note: "Implementation term. Not reader vocabulary.",
  },
  {
    // "TODO" — only in caps to avoid false-positives on legitimate prose
    // containing "to do". We do NOT use /i here.
    pattern: /\bTODO\b/,
    label: "TODO",
    note: "Developer annotation in reader-visible text.",
  },
  {
    // "TK" as a placeholder — same precision rules as check_tk_in_dist.mjs
    // but here we look in extracted text nodes only (no attribute check needed —
    // the TK gate already covers that).
    pattern: /\bTK\b/,
    label: "TK placeholder",
    note: "Placeholder text survived into rendered copy.",
  },
  {
    pattern: /\bsubagent\b/i,
    label: "subagent",
    note: "Agent-system jargon. Not reader vocabulary.",
  },
  {
    // \bLLM\b — not a reader-facing acronym.
    pattern: /\bLLM\b/,
    label: "LLM",
    note: "Agent-system jargon in reader copy.",
  },
  {
    // "redline" as a process term. Not the colour or a financial term.
    // This is safe because "redline" in Canadian econ prose is uncommon
    // (the verb "redline" in housing/mortgage discrimination context is
    // more common than the noun, but "redline" as a verb is also not
    // standard economics vocabulary on this publication).
    pattern: /\bredline\b/i,
    label: "redline",
    note: "Review-process term. Not reader vocabulary.",
  },
  {
    // "pending writer" as a multi-word slot label.
    pattern: /pending\s+writer/i,
    label: "pending writer",
    note: "Workflow placeholder label in reader copy.",
  },
  {
    // Guillemet markers used as slot delimiters in spec prose.
    pattern: /[‹›]/,
    label: "guillemet slot marker (‹ or ›)",
    note: "Spec slot delimiter in reader copy.",
  },
  {
    // "spec" as a standalone noun ("the spec", "per spec", "see spec").
    // Careful: "specification" and "specific" must NOT match.
    // We match: word-boundary "spec" word-boundary, not inside longer words.
    // "prospect" / "aspect" / "inspector" all have "spec" mid-word, so
    // \bspec\b is sufficient — those have other word chars on both sides.
    // Risk: "spec" in legitimate econ copy ("Fed spec" is not a thing;
    // "off-spec" is not a thing here). Confidence: high.
    pattern: /\bspec\b/i,
    label: "spec (implementation spec reference)",
    note: "Internal implementation reference. Not reader vocabulary.",
  },
  {
    // "the information" as the spec tic "X is the information" —
    // framing where the gap/delta/signal is called "the information".
    // Exact phrase, case-insensitive. Risk: "the information" is common
    // English, BUT in this publishing context the phrase is exclusively
    // a spec tic. If a false positive appears, tighten to
    // "is the information" or "carries the information".
    // DECISION: include the bare phrase; the false-positive risk in
    // macro-economics prose is low (economists say "signal" or "the data").
    pattern: /\bthe\s+information\b/i,
    label: "the information (spec tic)",
    note: "Spec framing tic. Rewrite: 'the signal', 'the data', or restructure.",
  },

  // ------------------------------------------------------------------
  // "placeholder" in visible text (not in aria-label, which is stripped)
  // ------------------------------------------------------------------
  {
    // "placeholder" as visible text. aria-label="... placeholder" is an
    // attribute and is stripped before matching.
    pattern: /\bplaceholder\b/i,
    label: "placeholder",
    note: "Placeholder label in reader-visible text.",
  },
];

// ============================================================
// HTML -> reader-text extractor
// Strips non-reader content before pattern matching.
// ============================================================

/**
 * extractReaderText(html)
 *
 * Returns a string containing only the text that a human would read on the
 * page — stripped of scripts, styles, comments, and HTML tags (but NOT the
 * text inside them).
 *
 * Steps:
 *   1. Remove <!-- ... --> HTML comments (may span lines).
 *   2. Remove <script ...>...</script> blocks.
 *   3. Remove <style ...>...</style> blocks.
 *   4. Remove aria-hidden="true" subtrees.
 *      These are marked as invisible to AT and are excluded from reader copy.
 *      We use a simple regex that removes the element and its content up to
 *      the matching close tag for known void/structural elements. For the
 *      purposes of this gate, aria-hidden subtrees are `<... aria-hidden="true"
 *      ...>...</element>` where we strip the whole block.
 *   5. Remove all remaining HTML tags (attributes included) — leaves text nodes.
 *   6. Decode common HTML entities so &amp; doesn't mask "and".
 *
 * Limitations: this is not a full DOM parser. It is intentionally
 * conservative — it may leave a small amount of attribute-derived text
 * (e.g., from malformed HTML). The categories of leakage we're catching
 * (prose tics, CSS values in sentences) are not affected by this.
 */
function extractReaderText(html) {
  let text = html;

  // 1. HTML comments
  text = text.replace(/<!--[\s\S]*?-->/g, " ");

  // 2. <script> blocks (including type="application/json" and astro islands)
  text = text.replace(/<script[\s\S]*?<\/script>/gi, " ");

  // 3. <style> blocks
  text = text.replace(/<style[\s\S]*?<\/style>/gi, " ");

  // 4. aria-hidden="true" subtrees.
  // Strategy: replace the content of any element carrying aria-hidden="true"
  // with a space. We handle one nesting level, which covers 99% of practical
  // cases (nav dropdowns, decorative icons, separator divs).
  // We do NOT try to parse nested aria-hidden trees — this is intentional.
  // Unmatched close tags left behind are harmless (stripped in step 5).
  text = text.replace(/<[^>]+aria-hidden="true"[^>]*>[\s\S]*?<\/[a-zA-Z]+>/g, " ");

  // 5. Remove all remaining HTML tags (and their attribute content).
  // This is the key step: attribute values like aria-label="... placeholder"
  // are dropped here because they are inside the tag delimiters.
  text = text.replace(/<[^>]*>/g, " ");

  // 6. HTML entity decoding (enough for our purposes)
  text = text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&#\d+;/g, " ")
    .replace(/&[a-z]+;/g, " ");

  return text;
}

// ============================================================
// Walk dist/ and collect all HTML files
// ============================================================

const SKIP_SUBDIRS = new Set([
  "og-preview",
  "chart-alternatives",
  "chart-archive",
]);

function* walkHtml(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_SUBDIRS.has(entry.name)) continue;
      yield* walkHtml(full);
    } else if (entry.isFile() && entry.name.endsWith(".html")) {
      yield full;
    }
  }
}

// ============================================================
// Main scan
// ============================================================

let totalViolations = 0;
let totalFiles = 0;

for (const htmlPath of walkHtml(DIST_DIR)) {
  totalFiles++;
  const rel = relative(DIST_DIR, htmlPath);
  const raw = readFileSync(htmlPath, "utf-8");
  const text = extractReaderText(raw);
  const lines = text.split("\n");

  const fileViolations = [];

  for (const { pattern, label, note } of BANNED_READER_LEAKAGE) {
    if (!pattern.test(text)) continue;

    // Find every line containing the match for precise reporting
    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        const excerpt = lines[i].trim().replace(/\s+/g, " ").slice(0, 140);
        fileViolations.push({ label, note, line: i + 1, excerpt });
      }
    }
  }

  if (fileViolations.length > 0) {
    totalViolations += fileViolations.length;
    console.error(`\nLEAKAGE in dist/${rel}:`);
    for (const v of fileViolations) {
      console.error(`  [${v.label}] line ~${v.line}: ${v.excerpt}`);
      console.error(`    Fix: ${v.note}`);
    }
  }
}

if (totalViolations > 0) {
  console.error(
    `\n[check_reader_copy_leakage] FAIL: ${totalViolations} leakage violation(s) ` +
    `across ${totalFiles} HTML file(s).`
  );
  console.error(
    "Root-cause: an agent paraphrased a spec, LLM-drafted placeholder prose " +
    "survived the review gates, or implementation vocabulary was left in a " +
    "methodology/about section. Fix the source .astro file and rebuild."
  );
  process.exit(1);
}

console.log(
  `[check_reader_copy_leakage] OK: no leakage vocabulary in ${totalFiles} HTML file(s).`
);
