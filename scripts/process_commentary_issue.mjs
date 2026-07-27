#!/usr/bin/env node
/*
 * process_commentary_issue.mjs — turns a "Publish a data commentary" issue
 * form submission into a live commentaries[] entry.
 *
 * Reads the issue body from the ISSUE_BODY env var (set by
 * .github/workflows/publish-commentary.yml from the issue-opened event
 * payload), parses the issue-form fields, downloads the attached PDF,
 * saves it to public/research/commentaries/<slug>.pdf, and inserts a new
 * entry at the top of the `commentaries` array in src/data/sections.ts.
 *
 * Writes `slug=<slug>` to $GITHUB_OUTPUT so later workflow steps (the PDF
 * page-render step, the commit step, the comment step) know what to
 * operate on without re-parsing anything.
 *
 * Deliberately does NOT run any build/citation checks itself — the
 * workflow's own "Validate full build" step (`npm run build`) is the
 * single source of truth for whether this is safe to ship. This script's
 * only job is to turn form fields into files.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const SECTIONS_TS = path.join(repoRoot, "src", "data", "sections.ts");
const COMMENTARIES_DIR = path.join(repoRoot, "public", "research", "commentaries");

const SECTION_MAP = {
  output: "output",
  inflation: "inflation",
  labour: "labour",
  housing: "housing",
  monetary: "monetary",
  fiscal: "fiscal",
  trade: "trade",
};

const AUTHORS = {
  "thompson richards": { name: "Thompson Richards", title: "Economist", jsonLdId: "thompson-richards" },
  // "Jay Zhao-Murray" -> no author field written; the site defaults to Jay.
};

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

function setOutput(key, value) {
  const outFile = process.env.GITHUB_OUTPUT;
  if (!outFile) return;
  fs.appendFileSync(outFile, `${key}=${value}\n`);
}

// Issue forms render the body as "### <label>\n\n<value>\n\n### <next label>...".
function parseIssueForm(body) {
  const fields = {};
  const chunks = body.split(/\n(?=### )/);
  for (const chunk of chunks) {
    const match = chunk.match(/^### (.+?)\n\n([\s\S]*?)\s*$/);
    if (!match) continue;
    const label = match[1].trim();
    const value = match[2].trim();
    fields[label] = value === "_No response_" ? "" : value;
  }
  return fields;
}

function slugify(value) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function uniqueSlug(base, existingSlugs) {
  if (!existingSlugs.has(base)) return base;
  const letters = "bcdefghijklmnopqrstuvwxyz";
  for (const letter of letters) {
    const candidate = `${base}-${letter}`;
    if (!existingSlugs.has(candidate)) return candidate;
  }
  fail(`Could not find a free slug based on "${base}" — too many collisions.`);
}

function extractExistingSlugs(sectionsSrc) {
  const arrayStart = sectionsSrc.indexOf("export const commentaries: DataCommentary[] = [");
  if (arrayStart === -1) fail("Could not find the commentaries[] array in sections.ts.");
  const slugs = new Set();
  const re = /slug:\s*"([^"]+)"/g;
  let m;
  const arraySlice = sectionsSrc.slice(arrayStart);
  while ((m = re.exec(arraySlice))) slugs.add(m[1]);
  return { arrayStart, slugs };
}

function extractPdfUrl(pdfFieldValue) {
  const match = pdfFieldValue.match(/\((https:\/\/github\.com\/[^)\s]+)\)/);
  if (!match) fail("No PDF link found in the PDF field — did the file finish uploading before submitting?");
  return match[1];
}

async function downloadPdf(url, destPath) {
  const res = await fetch(url, { redirect: "follow" });
  if (!res.ok) fail(`Could not download the PDF (HTTP ${res.status}) from ${url}`);
  const buf = Buffer.from(await res.arrayBuffer());
  if (buf.length < 100) fail("Downloaded PDF is suspiciously small — check the attachment.");
  fs.mkdirSync(path.dirname(destPath), { recursive: true });
  fs.writeFileSync(destPath, buf);
}

function insertCommentaryEntry(sectionsSrc, arrayStart, entry) {
  // NOTE: naive indexOf("[", arrayStart) finds the wrong bracket here --
  // "DataCommentary[]" (the type annotation) has its own "[" before the
  // actual array literal's opening "[". Anchor on "= [" instead.
  const marker = "= [";
  const markerAt = sectionsSrc.indexOf(marker, arrayStart);
  if (markerAt === -1) fail("Could not find the commentaries array literal's opening bracket.");
  const insertAt = markerAt + marker.length;
  const before = sectionsSrc.slice(0, insertAt);
  const after = sectionsSrc.slice(insertAt);

  const lines = [`\n  {`, `    slug: ${JSON.stringify(entry.slug)},`, `    section: ${JSON.stringify(entry.section)},`, `    title: ${JSON.stringify(entry.title)},`, `    publishedAt: ${JSON.stringify(entry.date)},`, `    pdfPath: ${JSON.stringify(entry.pdfPath)},`, `    excerpt: ${JSON.stringify(entry.excerpt)},`];
  if (entry.author) {
    lines.push(`    author: {`);
    lines.push(`      name: ${JSON.stringify(entry.author.name)},`);
    lines.push(`      title: ${JSON.stringify(entry.author.title)},`);
    lines.push(`      jsonLdId: ${JSON.stringify(entry.author.jsonLdId)},`);
    lines.push(`    },`);
  }
  lines.push(`  },`);

  return before + lines.join("\n") + after;
}

async function main() {
  const body = process.env.ISSUE_BODY;
  if (!body) fail("ISSUE_BODY env var is not set.");

  const fields = parseIssueForm(body);

  const sectionLabel = (fields["Section"] || "").trim();
  const sectionSlug = SECTION_MAP[sectionLabel.toLowerCase()];
  if (!sectionSlug) fail(`Unrecognized section "${sectionLabel}".`);

  const title = (fields["Title"] || "").trim();
  if (!title) fail("Title is empty.");

  const date = (fields["Publish date"] || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) fail(`Date "${date}" is not in YYYY-MM-DD format.`);

  const excerpt = (fields["Excerpt"] || "").trim();
  if (!excerpt) fail("Excerpt is empty.");

  const bylineLabel = (fields["Byline"] || "").trim().toLowerCase();
  const author = AUTHORS[bylineLabel]; // undefined -> falls back to site default (Jay)

  const pdfField = fields["PDF"] || "";
  const pdfUrl = extractPdfUrl(pdfField);

  const sectionsSrc = fs.readFileSync(SECTIONS_TS, "utf8");
  const { arrayStart, slugs } = extractExistingSlugs(sectionsSrc);
  const slug = uniqueSlug(`${sectionSlug}-${date}`, slugs);

  const pdfDest = path.join(COMMENTARIES_DIR, `${slug}.pdf`);
  await downloadPdf(pdfUrl, pdfDest);

  const entry = {
    slug,
    section: sectionSlug,
    title,
    date,
    pdfPath: `/research/commentaries/${slug}.pdf`,
    excerpt,
    author,
  };

  const updatedSrc = insertCommentaryEntry(sectionsSrc, arrayStart, entry);
  fs.writeFileSync(SECTIONS_TS, updatedSrc);

  console.log(`[process] slug: ${slug}`);
  console.log(`[process] section: ${sectionSlug}`);
  console.log(`[process] title: ${title}`);
  setOutput("slug", slug);
}

main().catch((err) => fail(err.stack || String(err)));
