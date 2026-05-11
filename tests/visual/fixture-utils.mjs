/*
 * fixture-utils.mjs - Fixture overlay + restore for the visual harness.
 *
 * Why a separate Node script instead of bash/PowerShell?
 * ------------------------------------------------------
 * - Cross-platform: Windows + ubuntu-latest CI both run this without
 *   shell-flavor-of-the-week branching.
 * - Atomic semantics: each operation either completes or restores cleanly.
 *   Bash one-liners with cp + mv would leak partial state on Ctrl-C.
 * - Works in npm scripts without extra deps.
 *
 * Subcommands
 * -----------
 *   freeze   Copy data/site/ -> data/fixtures/site/. One-shot, run by hand
 *            once panel visuals are stable and the live data is the
 *            canonical fixture.
 *
 *   overlay  Save data/site/ -> .fixture-backup/site.bak/ (rollback copy),
 *            then copy data/fixtures/site/ -> data/site/. Idempotent: if
 *            .fixture-backup/site.bak/ already exists, refuses to overwrite
 *            (signals an unclean prior run).
 *
 *   restore  Copy .fixture-backup/site.bak/ -> data/site/ (then remove
 *            the backup). Always run at the end of a test pass (success or
 *            failure) so the working copy is left in pre-test state.
 *
 * Exit codes
 * ----------
 *   0   success
 *   1   bad invocation or missing fixture corpus
 *   2   unclean state (e.g. overlay called while a prior backup exists)
 */
import { existsSync, mkdirSync, rmSync, cpSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..", "..");

const SITE_DIR = resolve(ROOT, "data", "site");
const FIXTURE_DIR = resolve(ROOT, "data", "fixtures", "site");
// IMPORTANT: BACKUP_DIR must NOT live under playwright.config.ts `outputDir`
// (tests/visual/.test-results/). Playwright clears that directory on test
// start; placing the backup there would wipe it before any test runs and a
// mid-test crash would leave data/site/ populated with fixture content
// permanently. Sibling dir, outside the swept tree.
const BACKUP_DIR = resolve(ROOT, "tests", "visual", ".fixture-backup", "site.bak");

function die(msg, code = 1) {
  // eslint-disable-next-line no-console
  console.error(`[fixture-utils] ${msg}`);
  process.exit(code);
}

function info(msg) {
  // eslint-disable-next-line no-console
  console.log(`[fixture-utils] ${msg}`);
}

function freeze() {
  if (!existsSync(SITE_DIR)) {
    die(
      `data/site/ does not exist. Run the pipeline first: ` +
        `python -m pipeline.build`,
    );
  }
  mkdirSync(dirname(FIXTURE_DIR), { recursive: true });
  if (existsSync(FIXTURE_DIR)) {
    rmSync(FIXTURE_DIR, { recursive: true, force: true });
  }
  cpSync(SITE_DIR, FIXTURE_DIR, { recursive: true });
  info(`Froze data/site/ -> data/fixtures/site/`);
}

function overlay() {
  if (!existsSync(FIXTURE_DIR)) {
    die(
      `No fixture corpus at data/fixtures/site/. Run ` +
        `\`npm run test:visual:freeze\` first (once visuals are stable).`,
    );
  }
  if (existsSync(BACKUP_DIR)) {
    die(
      `Backup already exists at tests/visual/.fixture-backup/site.bak/. ` +
        `A prior visual run likely crashed before restore. ` +
        `Inspect it, then either re-apply via \`npm run test:visual:restore\` ` +
        `or delete it manually if you are sure.`,
      2,
    );
  }
  mkdirSync(dirname(BACKUP_DIR), { recursive: true });

  // Save current data/site/ (if any) so we can restore on exit.
  if (existsSync(SITE_DIR)) {
    cpSync(SITE_DIR, BACKUP_DIR, { recursive: true });
    rmSync(SITE_DIR, { recursive: true, force: true });
  } else {
    // Marker so restore knows the original state was "no data/site/".
    mkdirSync(BACKUP_DIR, { recursive: true });
  }
  cpSync(FIXTURE_DIR, SITE_DIR, { recursive: true });
  info(`Overlaid data/fixtures/site/ -> data/site/ (backup saved)`);
}

function restore() {
  if (!existsSync(BACKUP_DIR)) {
    info(`No backup to restore. Skipping.`);
    return;
  }
  if (existsSync(SITE_DIR)) {
    rmSync(SITE_DIR, { recursive: true, force: true });
  }
  // If BACKUP_DIR is empty (marker state), original had no data/site/.
  let isEmpty = true;
  try {
    isEmpty = readdirSync(BACKUP_DIR).length === 0;
  } catch {
    isEmpty = true;
  }
  if (!isEmpty) {
    // renameSync across directories on Windows throws EPERM when the source
    // is a non-empty directory tree (different volumes / file handles).
    // cpSync + rmSync is the cross-platform pattern that works on both
    // Windows and POSIX runners.
    cpSync(BACKUP_DIR, SITE_DIR, { recursive: true, force: true });
    rmSync(BACKUP_DIR, { recursive: true, force: true });
  } else {
    rmSync(BACKUP_DIR, { recursive: true, force: true });
  }
  info(`Restored data/site/ from backup`);
}

const cmd = process.argv[2];
switch (cmd) {
  case "freeze":
    freeze();
    break;
  case "overlay":
    overlay();
    break;
  case "restore":
    restore();
    break;
  default:
    die(
      `Usage: node tests/visual/fixture-utils.mjs <freeze|overlay|restore>`,
    );
}
