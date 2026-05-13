#!/usr/bin/env node
/*
 * install_pre_commit_hook.mjs
 *
 * One-shot installer for the local pre-commit hook that runs the citation
 * coverage gate before any commit lands. The hook lives at
 * `.git/hooks/pre-commit` and exits non-zero if untagged claims are
 * detected, blocking the commit until the user adds citations.
 *
 * Why a local hook (not just CI):
 *   - Catches missing tags BEFORE the commit goes up, not after push.
 *   - The user types prose, runs `git commit`, the hook fails loudly with
 *     the exact uncovered tokens, the user adds citations, commits again.
 *   - Author-blind: applies to every commit, regardless of who authored.
 *
 * Usage:
 *   node scripts/install_pre_commit_hook.mjs
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const HOOK_PATH = path.join(repoRoot, ".git", "hooks", "pre-commit");

const HOOK_BODY = `#!/usr/bin/env sh
# Sibley Creek pre-commit gate — citation coverage.
#
# This hook runs the build-time citation gate locally so untagged claims
# get caught BEFORE the commit lands. If you see this hook fail, the
# script output names the exact uncovered tokens; add a citations[]
# entry (or, for research deep dives, an entry in
# editorial/source_cards/research/<slug>.yaml) covering each token and
# try the commit again.
#
# Per editorial/review_protocol.md "Authorship is not a gate exemption":
# this gate applies regardless of who typed the prose. User-typed and
# LLM-typed claims face the same coverage requirement.

set -e

cd "$(git rev-parse --show-toplevel)"

# Run only if the commit touches any prose surface the gate scans.
# Stays cheap on commits that don't touch reader-facing prose.
CHANGED=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '^(src/pages/.+\\.astro|src/data/sections\\.ts|editorial/published/.+\\.md|editorial/source_cards/research/.+\\.yaml|editorial/source_cards/registry\\.yaml|src/components/home/TitleStatement\\.astro)$' || true)

if [ -z "$CHANGED" ]; then
  # No reader-facing prose changes — skip the gate, let the commit pass.
  exit 0
fi

echo "[pre-commit] Reader-facing prose changed — running citation gate..."

if ! node scripts/check_citation_coverage.mjs; then
  echo ""
  echo "[pre-commit] Commit BLOCKED. Citation gate found uncovered claims."
  echo ""
  echo "Fix one of two ways:"
  echo "  1) Add citations[] / abstractCitations / tileLineCitations entries"
  echo "     covering the uncovered tokens listed above (or a sidecar YAML"
  echo "     entry for research deep dives)."
  echo "  2) If a claim genuinely can't be sourced, soften the prose to remove"
  echo "     the citable number/date and the gate will let it through."
  echo ""
  echo "If you need to commit despite this (one-off, only when justified),"
  echo "re-run with --no-verify. Use sparingly — the gate exists for a reason."
  exit 1
fi

exit 0
`;

if (!fs.existsSync(path.dirname(HOOK_PATH))) {
  console.error(`hooks directory not found at ${path.dirname(HOOK_PATH)}; is this a git repo?`);
  process.exit(2);
}

fs.writeFileSync(HOOK_PATH, HOOK_BODY, { encoding: "utf-8", mode: 0o755 });

// Make sure it's executable on Unix-y platforms.
try {
  fs.chmodSync(HOOK_PATH, 0o755);
} catch (e) {
  // Windows ignores chmod; that's fine — git for windows runs hooks via sh.
}

console.log(`installed pre-commit hook at ${path.relative(repoRoot, HOOK_PATH)}`);
console.log("");
console.log("Effect: any commit that touches a reader-facing prose file");
console.log("now runs scripts/check_citation_coverage.mjs first.");
console.log("Untagged citable claims block the commit until citations are added.");
