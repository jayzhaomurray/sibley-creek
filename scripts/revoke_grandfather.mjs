#!/usr/bin/env node
/*
 * revoke_grandfather.mjs - one-time correction.
 *
 * Moves every Tier B card with `grandfathered: true` out of the live
 * registry.yaml and into editorial/source_cards/_pending/<surface-slug>/<id>.yaml,
 * stripping the false user_confirmed_at + user_confirmed_by + grandfathered
 * fields. The user has not actually walked these cards; the grandfather act
 * was a backfill shortcut that has been retracted.
 *
 * Also moves the 4 published research dives from editorial/published/ back
 * to editorial/drafts/_holding/, since their citation chains include Tier B
 * cards that have not been user-verified. The dives drop back to draft
 * status (publishedPath stripped in sections.ts) and the live /research/<slug>/
 * routes will stop building until each dive's pending cards are walked.
 *
 * Run once: node scripts/revoke_grandfather.mjs
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const REGISTRY = path.join(repoRoot, "editorial", "source_cards", "registry.yaml");
const PENDING_DIR = path.join(repoRoot, "editorial", "source_cards", "_pending");
const PUBLISHED_DIR = path.join(repoRoot, "editorial", "published");
const HOLDING_DIR = path.join(repoRoot, "editorial", "drafts", "_holding");
const SECTIONS_TS = path.join(repoRoot, "src", "data", "sections.ts");

function surfaceSlugFromCitedIn(citedIn) {
  // Pick the first entry, derive a surface slug.
  // Examples:
  //   "editorial/source_cards/research/mortgage-renewal-wall.yaml" -> "mortgage-renewal-wall"
  //   "src/pages/policy.astro (plate-4)" -> "policy"
  //   "src/data/sections.ts (inflation.blurb.body)" -> "inflation"
  //   "editorial/published/us-tariff-repricing.md" -> "us-tariff-repricing"
  if (!citedIn?.length) return "_unattributed";
  const first = citedIn[0];
  let m;
  if ((m = first.match(/editorial\/source_cards\/research\/([^./]+)/))) return m[1];
  if ((m = first.match(/editorial\/published\/([^./]+)/))) return m[1];
  if ((m = first.match(/editorial\/drafts\/_holding\/([^./]+)/))) return m[1];
  if ((m = first.match(/src\/pages\/([^./]+)/))) return m[1];
  if ((m = first.match(/src\/data\/sections\.ts\s*\(([a-z-]+)\./i))) return m[1];
  if ((m = first.match(/src\/components\/charts\/([a-z-]+)\//))) return m[1];
  return "_unattributed";
}

function splitCards(yaml) {
  const lines = yaml.split("\n");
  const cards = [];
  let preamble = [];
  let current = null;
  for (const line of lines) {
    if (/^  - id:/.test(line)) {
      if (current) cards.push(current);
      current = { lines: [line] };
    } else if (current) {
      current.lines.push(line);
    } else {
      preamble.push(line);
    }
  }
  if (current) cards.push(current);
  return { preamble: preamble.join("\n"), cards };
}

function isGrandfathered(cardLines) {
  return cardLines.some((l) => /^\s*grandfathered:\s*true\b/.test(l));
}

function parseCardBlock(cardLines) {
  // Extract the fields we care about (id, cited_in) via regex; avoid YAML
  // parse, which trips on some embedded characters in excerpts.
  const text = cardLines.join("\n");
  const idMatch = text.match(/^\s*-?\s*id:\s*(.+?)\s*$/m);
  const id = idMatch ? idMatch[1].trim() : null;
  if (!id) return null;
  // cited_in: is a YAML list block. Grab each "- \"...\"" entry under it.
  const cited_in = [];
  const citedStart = text.match(/^(\s*)cited_in:\s*$/m);
  if (citedStart) {
    const indent = citedStart[1].length;
    const after = text.slice(citedStart.index + citedStart[0].length);
    const lines = after.split("\n");
    for (const l of lines) {
      if (l.trim() === "") continue; // skip blank lines inside the block header
      const m = l.match(/^(\s*)- ["']?(.+?)["']?\s*$/);
      if (!m) break;
      if (m[1].length <= indent) break; // de-indented; out of the cited_in block
      cited_in.push(m[2]);
    }
  }
  return { id, cited_in };
}

function stripFields(cardLines) {
  const drop = new Set(["grandfathered", "user_confirmed_at", "user_confirmed_by"]);
  return cardLines.filter((l) => {
    const m = l.match(/^\s+([a-z_]+)\s*:/);
    return !m || !drop.has(m[1]);
  });
}

function writePendingCard(slug, id, cardLines) {
  const dir = path.join(PENDING_DIR, slug);
  fs.mkdirSync(dir, { recursive: true });
  const out = path.join(dir, `${id}.yaml`);
  // Convert from "- id: <id>" indented at 2 to "id: <id>" at 0 indent (root key per pending schema).
  const stripped = stripFields(cardLines);
  const flat = stripped.map((l, i) => {
    if (i === 0) return l.replace(/^  - /, "");
    return l.replace(/^    /, "");
  });
  // Add status field at end.
  flat.push("status: pending_user");
  fs.writeFileSync(out, flat.join("\n") + "\n", "utf-8");
  return out;
}

function rewriteSectionsRemovePublishedPath(diveSlugs) {
  let text = fs.readFileSync(SECTIONS_TS, "utf-8");
  // For each dive slug, strip publishedPath: "..." line from its block.
  // Pattern: slug: "<slug>", ... publishedPath: "editorial/published/<slug>.md",
  for (const slug of diveSlugs) {
    const slugRe = new RegExp(`(slug:\\s*"${slug}",[\\s\\S]*?)publishedPath:\\s*"[^"]+",?\\n`, "m");
    text = text.replace(slugRe, "$1");
    // Also bump status to draft if it was shipped.
    const statusRe = new RegExp(`(slug:\\s*"${slug}",[\\s\\S]*?)status:\\s*"shipped"`, "m");
    text = text.replace(statusRe, '$1status: "drafted"');
  }
  fs.writeFileSync(SECTIONS_TS, text, "utf-8");
}

function main() {
  const raw = fs.readFileSync(REGISTRY, "utf-8");
  const { preamble, cards } = splitCards(raw);

  const movedCards = [];
  const keptCards = [];
  for (const card of cards) {
    if (isGrandfathered(card.lines)) {
      const parsed = parseCardBlock(card.lines);
      if (!parsed?.id) {
        console.error(`malformed grandfathered card (skipping):\n${card.lines.slice(0, 3).join("\n")}`);
        keptCards.push(card);
        continue;
      }
      const slug = surfaceSlugFromCitedIn(parsed.cited_in);
      const outPath = writePendingCard(slug, parsed.id, card.lines);
      movedCards.push({ id: parsed.id, slug, outPath });
      console.log(`moved ${parsed.id} -> ${path.relative(repoRoot, outPath)}`);
    } else {
      keptCards.push(card);
    }
  }

  // Rewrite the registry without the moved cards.
  const out = preamble + "\n" + keptCards.map((c) => c.lines.join("\n")).join("\n");
  fs.writeFileSync(REGISTRY, out, "utf-8");
  console.log(`\nremoved ${movedCards.length} grandfathered card(s) from registry.yaml.`);
  console.log(`registry.yaml now contains ${keptCards.length} cards.`);

  // Move the 4 published dives back to drafts/_holding/.
  const DIVES = ["mortgage-renewal-wall", "boc-fed-divergence", "per-capita-output", "us-tariff-repricing"];
  fs.mkdirSync(HOLDING_DIR, { recursive: true });
  const movedDives = [];
  for (const slug of DIVES) {
    const src = path.join(PUBLISHED_DIR, `${slug}.md`);
    const dst = path.join(HOLDING_DIR, `${slug}.md`);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dst);
      fs.unlinkSync(src);
      movedDives.push(slug);
      console.log(`moved dive: editorial/published/${slug}.md -> editorial/drafts/_holding/${slug}.md`);
    }
  }

  // Strip publishedPath from each dive in sections.ts so /research/<slug>/ stops building.
  rewriteSectionsRemovePublishedPath(movedDives);
  console.log(`\nstripped publishedPath from ${movedDives.length} deepDive entries in sections.ts.`);

  // Summarize.
  console.log("");
  console.log("Next steps:");
  console.log("  1. Run `npm run build` — expect it to FAIL on any section page or sidecar");
  console.log("     that cites a now-pending card. That's the disciplined outcome.");
  console.log("  2. Open editorial/source_cards/audit/index.html to see the verification queue");
  console.log("     populated with the pending cards organized by surface.");
  console.log("  3. Walk each draft's verification view, approve or reject each card,");
  console.log("     export decisions to clipboard, paste into PowerShell.");
  console.log("  4. As cards approve, the build will eventually go green again.");
  console.log("  5. To re-promote a dive once all its claims are approved: add publishedPath");
  console.log("     back to sections.ts and copy the holding draft to editorial/published/.");
}

main();
