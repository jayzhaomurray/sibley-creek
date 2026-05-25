#!/usr/bin/env node
/*
 * pull_subscribers.mjs — fetches submissions from formsubmit.co's free API
 * and appends new entries to business/recipients/recipients.yaml (dedup by email).
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

// Output paths — recipients.yaml is the master file; sync.log is the audit trail.
const RECIPIENTS_PATH = path.join(REPO_ROOT, "business", "recipients", "recipients.yaml");
const SYNC_LOG_PATH = path.join(REPO_ROOT, "business", "recipients", "sync.log");
const KEY_PATH = path.join(REPO_ROOT, "business", "secrets", "formsubmit_apikey.txt");

// The email address tied to the active formsubmit account.
// Updated 2026-05-23: switched from jayzhaomurray@outlook.com to jay@sibleycreek.ca.
// The old API key is bound to the OLD destination. Re-run --get-apikey after
// activation to get the new key.
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

/**
 * Read recipients.yaml and return a Set of known emails (lowercase).
 * We only dedup on email — not on timestamp — because the master file
 * stores one canonical entry per person, not one per submission.
 */
function readKnownEmails() {
  if (!fs.existsSync(RECIPIENTS_PATH)) return new Set();
  const raw = fs.readFileSync(RECIPIENTS_PATH, "utf-8");
  const seen = new Set();
  // Simple line-by-line scan. Each entry in recipients.yaml starts with
  // "- email: foo@example.com" (list item prefix). We match both the
  // list-item form ("- email:") and any indented form ("  email:") to be
  // resilient to minor formatting variations.
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^(?:-\s+|[\s]+)email:\s*([^\s#]+)/);
    if (m) seen.add(m[1].trim().toLowerCase());
  }
  return seen;
}

/**
 * Convert one formsubmit API submission into a YAML entry block (as a string).
 * Returns null if the submission has no usable email address.
 */
function submissionToYamlEntry(sub) {
  // sub shape: { form_url, submitted_at: {date,...}, form_data: {email,name,...} }
  const data = sub.form_data ?? {};
  const email = (data.email || data.Email || "").trim().toLowerCase();
  if (!email) return null;

  const ts = sub.submitted_at?.date ?? sub.submitted_at ?? "unknown";
  // Determine added date: prefer the submission date (YYYY-MM-DD prefix).
  const added = typeof ts === "string" ? ts.slice(0, 10) : new Date().toISOString().slice(0, 10);

  // Name from form data: may not be present on the subscribe form.
  const rawName = (data.name || data.Name || "").trim();
  const nameEntry = rawName ? rawName : "# name not provided";

  // Source: heuristic on form_url.
  const url = (sub.form_url || "").toLowerCase();
  const source = url.includes("contact") ? "subscribe_form" : "subscribe_form";
  // Both contact and subscribe forms land as subscribe_form here. The category
  // is always subscriber because only subscribers submit forms; journalists
  // are manually added.
  const category = "subscriber";

  const msg = (data.message || data.Message || "").trim();

  // Build the YAML entry as a literal string block. This is intentional:
  // we need append-only writes to a file that already has hand-annotated
  // entries, and a full YAML round-trip would destroy comments + formatting.
  const lines = [
    `- email: ${email}`,
    `  name: ${nameEntry}`,
    `  category: ${category}`,
    `  tier: null`,
    `  source: ${source}`,
    `  outlet: ""`,
    `  beat: ""`,
    `  added: ${added}`,
    `  active: true`,
    `  notes: ${msg ? JSON.stringify(msg) : "\"\""}`,
  ];

  return lines.join("\n");
}

/**
 * Write one line to sync.log.
 * Format: ISO-timestamp  source=formsubmit  fetched=N  new=N  dupes=N  [dry_run]
 */
function appendSyncLog(fetched, newCount, dupes, dryRun) {
  const ts = new Date().toISOString();
  const dryTag = dryRun ? "  [dry_run]" : "";
  const line = `${ts}  source=formsubmit  fetched=${fetched}  new=${newCount}  dupes=${dupes}${dryTag}\n`;
  fs.appendFileSync(SYNC_LOG_PATH, line, "utf-8");
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

  // Build the set of emails already in recipients.yaml.
  const knownEmails = readKnownEmails();

  const newEntries = [];
  let dupeCount = 0;

  for (const sub of submissions) {
    const entry = submissionToYamlEntry(sub);
    if (!entry) continue;
    // Extract the email from the entry string for dedup check.
    const emailMatch = entry.match(/^- email:\s*(.+)$/m);
    if (!emailMatch) continue;
    const email = emailMatch[1].trim().toLowerCase();

    if (knownEmails.has(email)) {
      dupeCount++;
    } else {
      newEntries.push(entry);
      knownEmails.add(email); // prevent intra-batch dupes
    }
  }

  const fetched = submissions.length;
  const newCount = newEntries.length;

  console.log(`  ${newCount} new, ${dupeCount} already known.`);

  if (newEntries.length === 0) {
    console.log("No new entries to append.");
    appendSyncLog(fetched, 0, dupeCount, dryRun);
    return;
  }

  if (dryRun) {
    console.log("\n--- DRY RUN (nothing written) ---");
    for (const e of newEntries) {
      console.log("\n" + e);
    }
    appendSyncLog(fetched, newCount, dupeCount, true);
    console.log(`\n[DRY RUN] ${newCount} entry/entries would be appended to recipients.yaml.`);
    return;
  }

  // Ensure the recipients directory exists (should already, but be safe).
  fs.mkdirSync(path.dirname(RECIPIENTS_PATH), { recursive: true });

  // Append new entries. Each entry is separated by a blank line.
  const append = "\n\n" + newEntries.join("\n\n") + "\n";
  fs.appendFileSync(RECIPIENTS_PATH, append, "utf-8");
  appendSyncLog(fetched, newCount, dupeCount, false);

  console.log(`Appended ${newCount} new entry/entries to business/recipients/recipients.yaml`);
  console.log(`Sync logged to business/recipients/sync.log`);
}

// ---------------------------------------------------------------------------
// Deprecated-file notice
// ---------------------------------------------------------------------------

function checkDeprecated() {
  const deprecated = path.join(REPO_ROOT, "business", "subscribers.md");
  if (fs.existsSync(deprecated)) {
    console.warn(
      `NOTE: business/subscribers.md still exists (renamed to business/_deprecated_subscribers.md).`
    );
    console.warn(
      `      It is no longer written to. Delete it once you have confirmed the migration.`
    );
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  checkDeprecated();
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
