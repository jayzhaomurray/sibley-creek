#!/usr/bin/env node
/*
 * check_sources.mjs - source-currency probe.
 *
 * Reads editorial/source_cards/registry.yaml and, for each entry, fetches
 * the currency_probe_url. Surfaces entries where a newer vintage may exist
 * than what we have verified, and entries past their next_expected date.
 *
 * Usage:
 *   node scripts/check_sources.mjs              # human-readable to stdout
 *   node scripts/check_sources.mjs --report     # also writes a dated MD report
 *
 * Detection logic is intentionally conservative — the script flags
 * candidates rather than asserting. Human (or agent) review confirms.
 *
 * Two flag types:
 *   - PAST-DUE: the current date is past the entry's next_expected.
 *               Reliable signal regardless of probe content.
 *   - NEWER-VINTAGE-MAYBE: probe URL response contains a date or vintage
 *               token that appears NEWER than the entry's verified vintage.
 *               Imprecise; uses simple date-pattern matching. False positives
 *               are expected — treat as "look here," not "definitive."
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const REGISTRY = path.join(repoRoot, "editorial", "source_cards", "registry.yaml");

const writeReport = process.argv.includes("--report");

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function parseISO(d) {
  // yaml parser may give us a Date object or a string
  if (d instanceof Date) return d;
  if (typeof d === "string") return new Date(d);
  return null;
}

function daysBetween(a, b) {
  const ms = b.getTime() - a.getTime();
  return Math.round(ms / 86400000);
}

async function fetchText(url) {
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "sibley-creek-source-check/1.0" },
      redirect: "follow",
    });
    if (!res.ok) return { status: res.status, text: "" };
    const text = await res.text();
    return { status: res.status, text };
  } catch (err) {
    return { status: 0, text: "", error: String(err) };
  }
}

/**
 * Extract candidate vintage tokens from probe text. Looks for ISO dates
 * (YYYY-MM-DD), month-name + year, and 4-digit year tokens. Returns the
 * most-recent-looking token strings observed.
 */
function extractCandidateVintages(text) {
  const candidates = new Set();
  // ISO dates
  for (const m of text.matchAll(/\b(20\d{2})-(\d{2})-(\d{2})\b/g)) {
    candidates.add(m[0]);
  }
  // Month name + year
  for (const m of text.matchAll(/\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b/g)) {
    candidates.add(`${m[1]} ${m[2]}`);
  }
  return Array.from(candidates);
}

function entryReport(entry, today) {
  const flags = [];
  const nextExpected = parseISO(entry.next_expected);
  if (nextExpected && today >= nextExpected) {
    flags.push({
      kind: "PAST-DUE",
      msg: `next_expected ${entry.next_expected} has passed (today ${todayISO()}).`,
    });
  }
  return { flags };
}

async function probeEntry(entry) {
  if (!entry.currency_probe_url) return { probe: null };
  const { status, text, error } = await fetchText(entry.currency_probe_url);
  if (status !== 200) {
    return {
      probe: {
        status,
        error: error ?? null,
        candidates: [],
        newerHints: [],
      },
    };
  }
  const candidates = extractCandidateVintages(text);
  // newerHints: very rough — look for ISO dates AFTER the entry's verified_at
  const verifiedAt = parseISO(entry.verified_at);
  const newerHints = candidates.filter((c) => {
    if (!/\d{4}-\d{2}-\d{2}/.test(c)) return false;
    const d = new Date(c);
    return verifiedAt && d > verifiedAt;
  });
  return {
    probe: {
      status,
      candidates: candidates.slice(0, 20),
      newerHints: newerHints.slice(0, 10),
    },
  };
}

async function main() {
  if (!fs.existsSync(REGISTRY)) {
    console.error(`registry not found: ${REGISTRY}`);
    process.exit(2);
  }
  const raw = fs.readFileSync(REGISTRY, "utf-8");
  const reg = parseYaml(raw);
  const sources = reg?.sources ?? [];
  if (!Array.isArray(sources) || sources.length === 0) {
    console.error("registry has no sources[]");
    process.exit(2);
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const lines = [];
  lines.push(`# Source-currency report - ${todayISO()}`);
  lines.push("");
  lines.push(`Checked ${sources.length} sources.`);
  lines.push("");

  let pastDueCount = 0;
  let newerHintCount = 0;

  for (const entry of sources) {
    const { flags } = entryReport(entry, today);
    const { probe } = await probeEntry(entry);
    const newerHints = probe?.newerHints ?? [];
    if (flags.some((f) => f.kind === "PAST-DUE")) pastDueCount++;
    if (newerHints.length > 0) newerHintCount++;

    lines.push(`## ${entry.id}`);
    lines.push("");
    lines.push(`- **Title:** ${entry.title}`);
    lines.push(`- **Vintage:** ${entry.vintage_label}`);
    lines.push(`- **Verified at:** ${entry.verified_at}`);
    lines.push(`- **Next expected:** ${entry.next_expected} (${entry.cadence})`);
    if (probe) {
      lines.push(`- **Probe status:** ${probe.status}`);
    } else {
      lines.push(`- **Probe status:** no probe URL`);
    }
    if (flags.length > 0) {
      for (const f of flags) lines.push(`- **${f.kind}:** ${f.msg}`);
    }
    if (newerHints.length > 0) {
      lines.push(`- **NEWER-VINTAGE-MAYBE:** probe text contains date(s) after verified_at: ${newerHints.join(", ")}`);
    }
    if (flags.length === 0 && newerHints.length === 0) {
      lines.push(`- **Status:** OK (no flags)`);
    }
    lines.push("");
  }

  lines.push("---");
  lines.push("");
  lines.push(`**Summary:** ${pastDueCount} past-due | ${newerHintCount} newer-vintage hints | ${sources.length - pastDueCount - newerHintCount} ok-ish.`);
  lines.push("");
  lines.push("PAST-DUE entries should be re-verified by hand or by dispatching researcher with WebFetch to confirm and update the registry.");
  lines.push("NEWER-VINTAGE-MAYBE flags are imprecise; a researcher pass should confirm whether the new date is actually a new publication or just a listing-page artifact.");

  const out = lines.join("\n") + "\n";
  console.log(out);

  if (writeReport) {
    const reportDir = path.join(repoRoot, "editorial", "source_cards");
    const reportPath = path.join(reportDir, `report-${todayISO()}.md`);
    fs.writeFileSync(reportPath, out, "utf-8");
    console.error(`wrote ${path.relative(repoRoot, reportPath)}`);
  }

  // Exit code: 0 if nothing past-due, 1 if anything past-due (CI-friendly).
  process.exit(pastDueCount > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error("check_sources failed:", err);
  process.exit(2);
});
