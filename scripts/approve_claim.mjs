#!/usr/bin/env node
/*
 * approve_claim.mjs - promote a pending card to the live registry.
 *
 * Usage:
 *   node scripts/approve_claim.mjs <draft-slug>:<claim-id>
 *   node scripts/approve_claim.mjs <draft-slug>:<claim-id> --user <handle>
 *
 * Steps:
 *   1. Read editorial/source_cards/_pending/<draft-slug>/<claim-id>.yaml
 *   2. Fill user_confirmed_at: today's date, user_confirmed_by: <handle>
 *   3. Append the card YAML to editorial/source_cards/registry.yaml
 *   4. Delete the pending YAML
 *   5. Run splice pass to replace [CLAIM-PENDING:<id>] in
 *      editorial/drafts/_holding/<draft-slug>.md with approved claim text
 *
 * If the placeholder doesn't appear in the holding draft, splice is a no-op
 * (some claims are referenced from sidecars only — that's fine).
 *
 * The npm wrapper passes the args through unchanged.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";
import { spawnSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const PENDING_DIR = path.join(repoRoot, "editorial", "source_cards", "_pending");
const HOLDING_DIR = path.join(repoRoot, "editorial", "drafts", "_holding");
const REGISTRY = path.join(repoRoot, "editorial", "source_cards", "registry.yaml");

function parseArgs() {
  const args = process.argv.slice(2);
  let target = null;
  let user = "jzm";
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--user" && i + 1 < args.length) {
      user = args[++i];
    } else if (!target) {
      target = args[i];
    }
  }
  if (!target || !target.includes(":")) {
    console.error("Usage: node scripts/approve_claim.mjs <draft-slug>:<claim-id> [--user <handle>]");
    process.exit(2);
  }
  const [draftSlug, claimId] = target.split(":");
  return { draftSlug, claimId, user };
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function spliceDraft(draftSlug, claimId, claimText) {
  const draftPath = path.join(HOLDING_DIR, `${draftSlug}.md`);
  if (!fs.existsSync(draftPath)) {
    return { spliced: false, reason: "no holding draft" };
  }
  const before = fs.readFileSync(draftPath, "utf-8");
  const placeholder = `[CLAIM-PENDING:${claimId}]`;
  if (!before.includes(placeholder)) {
    return { spliced: false, reason: "placeholder not found in draft" };
  }
  const after = before.split(placeholder).join(claimText);
  fs.writeFileSync(draftPath, after, "utf-8");
  return { spliced: true };
}

function main() {
  const { draftSlug, claimId, user } = parseArgs();
  const pendingPath = path.join(PENDING_DIR, draftSlug, `${claimId}.yaml`);
  if (!fs.existsSync(pendingPath)) {
    console.error(`pending card not found: ${path.relative(repoRoot, pendingPath)}`);
    process.exit(1);
  }

  const raw = fs.readFileSync(pendingPath, "utf-8");
  const card = parseYaml(raw);
  if (!card?.id) {
    console.error(`pending card YAML is malformed (missing id field): ${pendingPath}`);
    process.exit(1);
  }

  // Fill approval fields.
  const approvedAt = today();
  const isMode3 = card.mode === 3;
  if (isMode3) {
    card.user_approved_at = approvedAt;
    card.user_approved_by = user;
  } else {
    card.user_confirmed_at = approvedAt;
    card.user_confirmed_by = user;
  }
  delete card.status;
  delete card.proposed_claim;
  delete card.proposed_surface;

  // Re-emit YAML manually with stable key order matching the registry style.
  const indent = "    ";
  const lines = [];
  lines.push(`  - id: ${card.id}`);
  if (card.title) lines.push(`${indent}title: ${JSON.stringify(card.title)}`);
  if (card.url) lines.push(`${indent}url: ${JSON.stringify(card.url)}`);
  if (card.anchor) lines.push(`${indent}anchor: ${JSON.stringify(card.anchor)}`);
  if (card.excerpt) lines.push(`${indent}excerpt: ${JSON.stringify(card.excerpt)}`);
  if (card.currency_probe_url) lines.push(`${indent}currency_probe_url: ${JSON.stringify(card.currency_probe_url)}`);
  if (card.verified_value !== undefined) {
    lines.push(`${indent}verified_value:`);
    if (card.verified_value === null) {
      lines.push(`${indent}  null`);
    } else {
      for (const [k, v] of Object.entries(card.verified_value)) {
        lines.push(`${indent}  ${k}: ${JSON.stringify(v)}`);
      }
    }
  }
  if (card.verified_at) lines.push(`${indent}verified_at: ${approvedAt}`);
  if (card.vintage_label) lines.push(`${indent}vintage_label: ${JSON.stringify(card.vintage_label)}`);
  if (card.next_expected !== undefined && card.next_expected !== null) lines.push(`${indent}next_expected: ${JSON.stringify(card.next_expected)}`);
  if (card.cadence) lines.push(`${indent}cadence: ${JSON.stringify(card.cadence)}`);
  if (card.cited_in?.length) {
    lines.push(`${indent}cited_in:`);
    for (const c of card.cited_in) lines.push(`${indent}  - ${JSON.stringify(c)}`);
  }
  if (card.notes) lines.push(`${indent}notes: ${JSON.stringify(card.notes)}`);
  if (card.verification_tier) lines.push(`${indent}verification_tier: ${JSON.stringify(card.verification_tier)}`);
  if (isMode3) {
    lines.push(`${indent}mode: 3`);
    lines.push(`${indent}user_approved_at: ${JSON.stringify(card.user_approved_at)}`);
    lines.push(`${indent}user_approved_by: ${JSON.stringify(card.user_approved_by)}`);
    if (card.frame_test_check) lines.push(`${indent}frame_test_check: ${JSON.stringify(card.frame_test_check)}`);
  } else {
    if (card.user_confirmed_at) lines.push(`${indent}user_confirmed_at: ${JSON.stringify(card.user_confirmed_at)}`);
    if (card.user_confirmed_by) lines.push(`${indent}user_confirmed_by: ${JSON.stringify(card.user_confirmed_by)}`);
  }
  if (card.triangulation?.length) {
    lines.push(`${indent}triangulation:`);
    for (const sec of card.triangulation) {
      lines.push(`${indent}  - source: ${JSON.stringify(sec.source || "")}`);
      if (sec.url) lines.push(`${indent}    url: ${JSON.stringify(sec.url)}`);
      if (sec.excerpt) lines.push(`${indent}    excerpt: ${JSON.stringify(sec.excerpt)}`);
      if (sec.credibility) lines.push(`${indent}    credibility: ${JSON.stringify(sec.credibility)}`);
    }
  }

  const cardYaml = "\n" + lines.join("\n") + "\n";

  // Append to registry.yaml.
  fs.appendFileSync(REGISTRY, cardYaml, "utf-8");
  console.log(`appended ${card.id} to registry.yaml (Tier ${card.verification_tier}, approved ${approvedAt} by ${user})`);

  // Delete the pending YAML.
  fs.unlinkSync(pendingPath);
  console.log(`removed pending card: ${path.relative(repoRoot, pendingPath)}`);

  // Splice the draft if the placeholder exists and we have approved-claim text.
  // The card's `proposed_claim` field was used as the splice text (loaded before
  // the field was deleted above) — pass that into spliceDraft.
  const claimText = parseYaml(raw)?.proposed_claim || card.excerpt || "";
  if (claimText) {
    const result = spliceDraft(draftSlug, card.id, claimText);
    if (result.spliced) {
      console.log(`spliced approved claim into editorial/drafts/_holding/${draftSlug}.md`);
    } else {
      console.log(`splice skipped: ${result.reason}`);
    }
  } else {
    console.log(`splice skipped: no proposed_claim text on card`);
  }

  console.log("");
  console.log(`approve-claim complete: ${draftSlug}:${claimId}.`);

  // Auto-regenerate audit pages so the verification queue reflects the new
  // state immediately. Without this, the queue at audit/index.html shows
  // stale counts until the user manually re-runs source_audit.
  console.log(`regenerating audit pages...`);
  const result = spawnSync("node", ["scripts/source_audit.mjs"], {
    cwd: repoRoot,
    stdio: "inherit",
  });
  if (result.status !== 0) {
    console.error(`source_audit regen exited with code ${result.status} — audit pages may be stale.`);
    process.exit(result.status || 1);
  }
}

main();
