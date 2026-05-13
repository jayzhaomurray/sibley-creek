#!/usr/bin/env node
/*
 * reject_claim.mjs - delete a pending card and mark the draft placeholder as cut.
 *
 * Usage:
 *   node scripts/reject_claim.mjs <draft-slug>:<claim-id>
 *   node scripts/reject_claim.mjs <draft-slug>:<claim-id> --reason "<short rationale>"
 *
 * Steps:
 *   1. Delete editorial/source_cards/_pending/<draft-slug>/<claim-id>.yaml
 *   2. Replace [CLAIM-PENDING:<claim-id>] in
 *      editorial/drafts/_holding/<draft-slug>.md with
 *      [CLAIM CUT: <reason or "no rationale provided">]
 *   3. Append a rejection log entry to
 *      editorial/source_cards/_pending/_rejection-log.md
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const PENDING_DIR = path.join(repoRoot, "editorial", "source_cards", "_pending");
const HOLDING_DIR = path.join(repoRoot, "editorial", "drafts", "_holding");
const REJECTION_LOG = path.join(PENDING_DIR, "_rejection-log.md");

function parseArgs() {
  const args = process.argv.slice(2);
  let target = null;
  let reason = "no rationale provided";
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--reason" && i + 1 < args.length) {
      reason = args[++i];
    } else if (!target) {
      target = args[i];
    }
  }
  if (!target || !target.includes(":")) {
    console.error("Usage: node scripts/reject_claim.mjs <draft-slug>:<claim-id> [--reason \"<rationale>\"]");
    process.exit(2);
  }
  const [draftSlug, claimId] = target.split(":");
  return { draftSlug, claimId, reason };
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function logRejection(draftSlug, claimId, reason) {
  const header = fs.existsSync(REJECTION_LOG)
    ? ""
    : "# Rejection log\n\nClaims rejected by user during verification triage. Each entry: date, draft, claim, reason.\n\n";
  const entry = `- ${today()} · ${draftSlug}:${claimId} · ${reason}\n`;
  fs.appendFileSync(REJECTION_LOG, header + entry, "utf-8");
}

function main() {
  const { draftSlug, claimId, reason } = parseArgs();
  const pendingPath = path.join(PENDING_DIR, draftSlug, `${claimId}.yaml`);
  if (!fs.existsSync(pendingPath)) {
    console.error(`pending card not found: ${path.relative(repoRoot, pendingPath)}`);
    process.exit(1);
  }

  fs.unlinkSync(pendingPath);
  console.log(`deleted pending card: ${path.relative(repoRoot, pendingPath)}`);

  const draftPath = path.join(HOLDING_DIR, `${draftSlug}.md`);
  if (fs.existsSync(draftPath)) {
    const before = fs.readFileSync(draftPath, "utf-8");
    const placeholder = `[CLAIM-PENDING:${claimId}]`;
    if (before.includes(placeholder)) {
      const after = before.split(placeholder).join(`[CLAIM CUT: ${reason}]`);
      fs.writeFileSync(draftPath, after, "utf-8");
      console.log(`marked draft placeholder as cut: ${path.relative(repoRoot, draftPath)}`);
    } else {
      console.log(`placeholder not found in draft (no splice needed)`);
    }
  }

  logRejection(draftSlug, claimId, reason);
  console.log(`logged rejection: ${path.relative(repoRoot, REJECTION_LOG)}`);

  console.log("");
  console.log(`reject-claim complete: ${draftSlug}:${claimId}.`);

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
