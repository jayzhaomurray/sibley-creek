#!/usr/bin/env node
/*
 * pull_subscribers.mjs — fetches submissions from formsubmit.co's free API
 * and appends new ones to business/subscribers.md (dedup by email+timestamp).
 *
 * DESTINATION: jay@sibleycreek.ca (switched from jayzhaomurray@outlook.com
 * 2026-05-23). Forms now POST to the raw-email AJAX endpoint; formsubmit
 * will send an activation link to jay@sibleycreek.ca on the first submission.
 * Jay must click that link before subsequent submissions deliver.
 *
 * AFTER ACTIVATION — fetch the secure hash and lock it in:
 *   1. Get the new API key:  node scripts/pull_subscribers.mjs --get-apikey
 *      (emails the key to jay@sibleycreek.ca — check that inbox)
 *   2. Store it: echo "YOUR_KEY_HERE" > business/secrets/formsubmit_apikey.txt
 *   3. Get the secure hash from the formsubmit.co dashboard or activation email.
 *   4. Swap `jay@sibleycreek.ca` for the hash in every form action URL:
 *        src/pages/index.astro   (splash subscribe form)
 *        src/pages/subscribe.astro
 *        src/pages/contact.astro
 *
 * SETUP for a fresh destination (one time only):
 *   1. Run: node scripts/pull_subscribers.mjs --get-apikey
 *      This fires a GET to formsubmit.co which emails your API key to
 *      the FORM_EMAIL address below. Copy the key from that email.
 *   2. Store it in business/secrets/formsubmit_apikey.txt  (already gitignored)
 *      e.g.:  echo "YOUR_KEY_HERE" > business/secrets/formsubmit_apikey.txt
 *   3. Run normally: node scripts/pull_subscribers.mjs
 *
 * API limits (formsubmit.co free tier):
 *   - 30-day retention of submissions
 *   - 5 API calls per day
 *
 * Usage:
 *   node scripts/pull_subscribers.mjs             # pull and append new
 *   node scripts/pull_subscribers.mjs --dry-run   # print without writing
 *   node scripts/pull_subscribers.mjs --get-apikey
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const LOG_PATH = path.join(REPO_ROOT, "business", "subscribers.md");
const KEY_PATH = path.join(REPO_ROOT, "business", "secrets", "formsubmit_apikey.txt");
// The email address tied to the active formsubmit account.
// Updated 2026-05-23: switched from jayzhaomurray@outlook.com to jay@sibleycreek.ca.
// The old API key (business/secrets/formsubmit_apikey.txt) is bound to the OLD
// destination. Re-run --get-apikey after activation to get the new key.
const FORM_EMAIL = "jay@sibleycreek.ca";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readApiKey() {
  if (!fs.existsSync(KEY_PATH)) {
    console.error(`API key file not found: ${KEY_PATH}`);
    console.error(`Run:  node scripts/pull_subscribers.mjs --get-apikey`);
    console.error(`Then store the emailed key in that file.`);
    process.exit(1);
  }
  return fs.readFileSync(KEY_PATH, "utf-8").trim();
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} from ${url}`);
  return res.json();
}

function parseExistingLog(raw) {
  // Returns Set of "email|timestamp" strings already in the log.
  const seen = new Set();
  const lines = raw.split(/\r?\n/).filter((l) => !l.trimStart().startsWith("#"));
  const blocks = lines.join("\n").split(/\n\s*\n/).filter((b) => b.trim());
  for (const block of blocks) {
    const obj = {};
    for (const line of block.split(/\r?\n/)) {
      const m = line.match(/^(\w+)\s*:\s*(.*)/);
      if (m) obj[m[1].trim()] = m[2].trim();
    }
    if (obj.email && obj.timestamp) seen.add(`${obj.email.toLowerCase()}|${obj.timestamp}`);
  }
  return seen;
}

function submissionToBlock(sub) {
  // sub shape: { form_url, submitted_at: {date,...}, form_data: {email,name,...} }
  const ts = sub.submitted_at?.date ?? sub.submitted_at ?? "unknown";
  const data = sub.form_data ?? {};
  const email = (data.email || data.Email || "").trim();
  if (!email) return null;
  // Determine source from form_url heuristic.
  const url = (sub.form_url || "").toLowerCase();
  const source = url.includes("contact") ? "contact" : "subscribe";
  const msg = (data.message || data.Message || "").trim();
  let block = `timestamp: ${ts}\nemail:     ${email}\nsource:    ${source}`;
  if (msg) block += `\nmessage:   ${msg}`;
  return block;
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function getApiKey() {
  console.log(`Requesting API key for ${FORM_EMAIL} from formsubmit.co ...`);
  const url = `https://formsubmit.co/api/get-apikey/${encodeURIComponent(FORM_EMAIL)}`;
  const data = await fetchJson(url);
  console.log(`Response:`, JSON.stringify(data, null, 2));
  console.log(`\nCheck ${FORM_EMAIL} inbox for your API key.`);
  console.log(`NOTE: this key is for the NEW destination (jay@sibleycreek.ca).`);
  console.log(`Then: echo "YOUR_KEY" > business/secrets/formsubmit_apikey.txt`);
}

async function pullSubmissions(dryRun) {
  const apiKey = readApiKey();
  const url = `https://formsubmit.co/api/get-submissions/${apiKey}`;
  console.log(`Fetching submissions from formsubmit.co ...`);
  const data = await fetchJson(url);

  const submissions = data.submissions ?? data ?? [];
  if (!Array.isArray(submissions)) {
    console.error("Unexpected API response shape:", JSON.stringify(data, null, 2));
    process.exit(1);
  }
  console.log(`  ${submissions.length} total submission(s) returned by API (30-day window).`);

  const existing = fs.existsSync(LOG_PATH)
    ? parseExistingLog(fs.readFileSync(LOG_PATH, "utf-8"))
    : new Set();

  const newBlocks = [];
  for (const sub of submissions) {
    const block = submissionToBlock(sub);
    if (!block) continue;
    const ts = (sub.submitted_at?.date ?? sub.submitted_at ?? "").toString();
    const email = (sub.form_data?.email || sub.form_data?.Email || "").toLowerCase();
    const key = `${email}|${ts}`;
    if (!existing.has(key)) newBlocks.push(block);
  }

  if (newBlocks.length === 0) {
    console.log("No new submissions to append.");
    return;
  }

  console.log(`  ${newBlocks.length} new submission(s) to append.`);
  if (dryRun) {
    console.log("\n--- DRY RUN (nothing written) ---");
    for (const b of newBlocks) console.log("\n" + b);
    return;
  }

  // Ensure business/secrets exists
  fs.mkdirSync(path.dirname(KEY_PATH), { recursive: true });

  const append = "\n\n" + newBlocks.join("\n\n");
  fs.appendFileSync(LOG_PATH, append, "utf-8");
  console.log(`Appended ${newBlocks.length} new entry/entries to business/subscribers.md`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--get-apikey")) {
    await getApiKey();
  } else {
    await pullSubmissions(args.includes("--dry-run"));
  }
}

main().catch((err) => {
  console.error("FATAL:", err.message);
  process.exit(1);
});
