/*
 * run-visual.mjs - Top-level orchestrator for `npm run test:visual`.
 *
 * Sequence:
 *   1. Overlay fixtures (data/fixtures/site/ -> data/site/, with backup).
 *   2. Run `playwright test` (passing any extra CLI args through, e.g.
 *      `--update-snapshots` for baseline regen).
 *   3. Restore data/site/ from backup, ALWAYS -- even on test failure or
 *      Ctrl-C. This is the main reason we wrap Playwright in a
 *      Node script rather than chaining shell commands.
 *
 * The Playwright config's `webServer` step handles `astro build` and
 * `astro preview` itself, so this script does not need to invoke them.
 *
 * Exit code propagates from `playwright test`. Restore failures log a
 * loud warning but do NOT mask a Playwright test failure.
 */
import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..", "..");
const FIXTURE_UTILS = resolve(__dirname, "fixture-utils.mjs");

function runNode(args, opts = {}) {
  return new Promise((resolveP, rejectP) => {
    const child = spawn(process.execPath, args, {
      cwd: ROOT,
      stdio: "inherit",
      ...opts,
    });
    child.on("error", rejectP);
    child.on("exit", (code, signal) => {
      if (signal) {
        rejectP(new Error(`child killed by signal ${signal}`));
        return;
      }
      resolveP(code ?? 0);
    });
  });
}

function runNpx(args) {
  // npx is a .cmd on Windows; use shell:true so PATH lookups behave.
  return new Promise((resolveP, rejectP) => {
    const child = spawn("npx", args, {
      cwd: ROOT,
      stdio: "inherit",
      shell: true,
    });
    child.on("error", rejectP);
    child.on("exit", (code, signal) => {
      if (signal) {
        rejectP(new Error(`child killed by signal ${signal}`));
        return;
      }
      resolveP(code ?? 0);
    });
  });
}

async function safeRestore() {
  try {
    await runNode([FIXTURE_UTILS, "restore"]);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(
      `[run-visual] WARNING: fixture restore failed: ${err?.message || err}. ` +
        `Run \`npm run test:visual:restore\` manually to recover.`,
    );
  }
}

async function main() {
  const passthrough = process.argv.slice(2);

  // 1. Overlay. If this fails (missing fixture corpus), bail BEFORE we
  //    have any backup state to leak.
  const overlayCode = await runNode([FIXTURE_UTILS, "overlay"]);
  if (overlayCode !== 0) {
    process.exit(overlayCode);
  }

  // 2. Hand off to Playwright. Restore-on-exit is the central piece.
  let testCode = 1;
  try {
    testCode = await runNpx(["playwright", "test", ...passthrough]);
  } finally {
    await safeRestore();
  }
  process.exit(testCode);
}

// Trap SIGINT so a Ctrl-C still triggers the restore.
let shuttingDown = false;
async function onSignal(sig) {
  if (shuttingDown) return;
  shuttingDown = true;
  // eslint-disable-next-line no-console
  console.error(`[run-visual] got ${sig}; restoring fixtures and exiting...`);
  await safeRestore();
  process.exit(130);
}
process.on("SIGINT", () => onSignal("SIGINT"));
process.on("SIGTERM", () => onSignal("SIGTERM"));

main().catch(async (err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  await safeRestore();
  process.exit(1);
});
