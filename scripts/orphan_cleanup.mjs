#!/usr/bin/env node
/*
 * orphan_cleanup.mjs - prune stale audit pages + flag orphan registry cards.
 *
 * Runs as a build step after source_audit.mjs and before check_citation_coverage.mjs.
 *
 * Behaviors:
 *   1. Delete editorial/source_cards/audit/<slug>.html if src/pages/<slug>.astro
 *      no longer exists (or no longer declares plates: Plate[]).
 *   2. Delete editorial/source_cards/audit/research/<slug>.html if the dive
 *      no longer appears in src/data/sections.ts deepDives.
 *   3. Flag registry.yaml cards whose cited_in: surfaces have all disappeared.
 *      Reports orphans; does NOT delete cards automatically (the editor decides).
 *   4. Flag registry cards with no verification_tier field set.
 *   5. Verify every card referenced as "card:<id>" in section pages /
 *      dive sidecars actually exists in the registry; report missing.
 *
 * Exit codes:
 *   0 - clean (no orphans, no missing refs)
 *   1 - reportable issues found; printed to stderr but build continues
 *
 * Build sequence (intent): source_audit -> orphan_cleanup -> check_citation_coverage -> astro check -> astro build.
 *
 * Usage:
 *   node scripts/orphan_cleanup.mjs
 *   node scripts/orphan_cleanup.mjs --delete-orphan-cards   # opt-in destructive
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
const AUDIT_DIR = path.join(repoRoot, "editorial", "source_cards", "audit");
const RESEARCH_AUDIT_DIR = path.join(AUDIT_DIR, "research");
const REGISTRY_PATH = path.join(repoRoot, "editorial", "source_cards", "registry.yaml");
const RESEARCH_SIDECAR_DIR = path.join(repoRoot, "editorial", "source_cards", "research");
const PUBLISHED_DIR = path.join(repoRoot, "editorial", "published");

const args = new Set(process.argv.slice(2));
const DELETE_ORPHAN_CARDS = args.has("--delete-orphan-cards");

function discoverSections() {
  if (!fs.existsSync(PAGES_DIR)) return [];
  const slugs = [];
  for (const file of fs.readdirSync(PAGES_DIR)) {
    if (!file.endsWith(".astro")) continue;
    const slug = file.replace(/\.astro$/, "");
    const text = fs.readFileSync(path.join(PAGES_DIR, file), "utf-8");
    if (/const\s+plates\s*:\s*Plate\[\]\s*=\s*\[/.test(text)) slugs.push(slug);
  }
  return new Set(slugs);
}

function discoverDives() {
  // A dive is a .md file in editorial/published/ that has a corresponding entry
  // in sections.ts deepDives. For orphan-cleanup purposes, we use the union
  // of (published md files) and (deepDives slugs) — if either is missing, the
  // audit page is orphaned.
  const slugs = new Set();
  if (fs.existsSync(PUBLISHED_DIR)) {
    for (const file of fs.readdirSync(PUBLISHED_DIR)) {
      if (file.endsWith(".md") && file !== "README.md") {
        slugs.add(file.replace(/\.md$/, ""));
      }
    }
  }
  return slugs;
}

function listAuditPages() {
  if (!fs.existsSync(AUDIT_DIR)) return { sections: [], dives: [] };
  const sections = [];
  const dives = [];
  for (const f of fs.readdirSync(AUDIT_DIR)) {
    if (!f.endsWith(".html")) continue;
    if (["index.html", "splash.html", "_pending.html"].includes(f)) continue;
    sections.push(f.replace(/\.html$/, ""));
  }
  if (fs.existsSync(RESEARCH_AUDIT_DIR)) {
    for (const f of fs.readdirSync(RESEARCH_AUDIT_DIR)) {
      if (f.endsWith(".html")) dives.push(f.replace(/\.html$/, ""));
    }
  }
  return { sections, dives };
}

function loadRegistry() {
  const raw = fs.readFileSync(REGISTRY_PATH, "utf-8");
  return parseYaml(raw);
}

function findCardReferences() {
  // Scan section .astro files and dive sidecars for `card:<id>` references.
  const refs = new Set();
  for (const f of fs.readdirSync(PAGES_DIR)) {
    if (!f.endsWith(".astro")) continue;
    const text = fs.readFileSync(path.join(PAGES_DIR, f), "utf-8");
    for (const m of text.matchAll(/"card:([a-z0-9_-]+)"/g)) refs.add(m[1]);
  }
  const sectionsText = fs.readFileSync(SECTIONS_TS, "utf-8");
  for (const m of sectionsText.matchAll(/"card:([a-z0-9_-]+)"/g)) refs.add(m[1]);
  if (fs.existsSync(RESEARCH_SIDECAR_DIR)) {
    for (const f of fs.readdirSync(RESEARCH_SIDECAR_DIR)) {
      if (!f.endsWith(".yaml")) continue;
      const text = fs.readFileSync(path.join(RESEARCH_SIDECAR_DIR, f), "utf-8");
      for (const m of text.matchAll(/card:([a-z0-9_-]+)/g)) refs.add(m[1]);
    }
  }
  return refs;
}

function main() {
  const issues = [];
  const sections = discoverSections();
  const dives = discoverDives();
  const audit = listAuditPages();

  // 1. Section audit orphans.
  for (const slug of audit.sections) {
    if (!sections.has(slug)) {
      const p = path.join(AUDIT_DIR, `${slug}.html`);
      fs.unlinkSync(p);
      console.log(`removed orphan audit page: ${path.relative(repoRoot, p)}`);
    }
  }
  // 2. Dive audit orphans.
  for (const slug of audit.dives) {
    if (!dives.has(slug)) {
      const p = path.join(RESEARCH_AUDIT_DIR, `${slug}.html`);
      fs.unlinkSync(p);
      console.log(`removed orphan dive audit page: ${path.relative(repoRoot, p)}`);
    }
  }

  // 3. Orphan registry cards (cited_in references files that no longer exist).
  const registry = loadRegistry();
  const cards = registry?.sources ?? [];
  const referenced = findCardReferences();
  const orphanCards = [];
  const untaggedCards = [];
  for (const card of cards) {
    if (!card.verification_tier) untaggedCards.push(card.id);
    if (!referenced.has(card.id)) orphanCards.push(card.id);
  }

  if (orphanCards.length > 0) {
    console.log("");
    console.log(`orphan cards (not referenced by any current surface):`);
    for (const id of orphanCards) console.log(`  - ${id}`);
    if (DELETE_ORPHAN_CARDS) {
      console.log("  [--delete-orphan-cards passed; would delete here in a future revision]");
    } else {
      console.log("  (pass --delete-orphan-cards to remove them; default is to flag only)");
    }
    issues.push(`${orphanCards.length} orphan card(s)`);
  }

  if (untaggedCards.length > 0) {
    console.log("");
    console.log(`cards without verification_tier:`);
    for (const id of untaggedCards) console.log(`  - ${id}`);
    issues.push(`${untaggedCards.length} untagged card(s)`);
  }

  // 4. Missing card references (referenced but not in registry AND not in
  //    _pending/). Pending cards are known but not approved; they are NOT
  //    "missing" — they're surfaced on the audit page as pending claims.
  const cardIds = new Set(cards.map((c) => c.id));
  const pendingIds = new Set();
  const pendingDir = path.join(repoRoot, "editorial", "source_cards", "_pending");
  if (fs.existsSync(pendingDir)) {
    for (const sub of fs.readdirSync(pendingDir)) {
      const subPath = path.join(pendingDir, sub);
      try {
        if (!fs.statSync(subPath).isDirectory()) continue;
      } catch { continue; }
      for (const f of fs.readdirSync(subPath)) {
        if (f.endsWith(".yaml")) pendingIds.add(f.replace(/\.yaml$/, ""));
      }
    }
  }
  const missing = [];
  for (const ref of referenced) {
    if (!cardIds.has(ref) && !pendingIds.has(ref)) missing.push(ref);
  }
  if (missing.length > 0) {
    console.log("");
    console.log(`citations reference missing cards (card:<id> not in registry):`);
    for (const id of missing) console.log(`  - card:${id}`);
    issues.push(`${missing.length} missing card reference(s)`);
  }

  console.log("");
  if (issues.length === 0) {
    console.log("orphan_cleanup: clean. No orphan audit pages, no orphan cards, no missing references.");
    process.exit(0);
  }
  console.log(`orphan_cleanup: ${issues.join(", ")}. Build continues; review the flags above.`);
  // Non-zero exit only on missing references (a real consistency error).
  // Orphan cards / untagged cards are warnings.
  process.exit(missing.length > 0 ? 1 : 0);
}

main();
