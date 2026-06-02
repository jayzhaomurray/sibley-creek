#!/usr/bin/env node
// audit_diff.mjs -- Shape C audit: audit a working git diff.
//
// Usage:
//   node scripts/audit_diff.mjs --by <claude|codex> --task "<description>"
//
// Behavior:
//   1. Resolves auditor as opposite of --by.
//   2. Runs `git diff --no-color` filtered to substantial paths from .audit-config.json.
//   3. If diff is empty, exits with a clear message.
//   4. Constructs audit prompt and invokes the auditor CLI.
//   5. Writes findings to editorial/audit_findings/working-diff-by-<auditor>-<YYYY-MM-DD>-<HHmm>.md.
//   6. Prints the findings path to stdout.

import fs from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { buildCanonBlock, oppositeModel, findingsPath, repoRoot } from "./_lib/canon_brief.mjs";

// ---------------------------------------------------------------------------
// Arg parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = { by: null, task: null, debug: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--by") args.by = argv[++i];
    else if (argv[i] === "--task") args.task = argv[++i];
    else if (argv[i] === "--debug") args.debug = true;
    else die(`Unknown argument: ${argv[i]}`);
  }
  if (!args.by) die("--by <claude|codex> is required");
  if (!args.task) die("--task \"<description>\" is required");
  return args;
}

function die(msg) {
  process.stderr.write(`audit_diff: ${msg}\n`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Load substantial paths from .audit-config.json (infra agent owns this file)
// ---------------------------------------------------------------------------

function loadSubstantialPaths() {
  const configPath = path.join(repoRoot, ".audit-config.json");
  if (!existsSync(configPath)) {
    process.stderr.write("audit_diff: .audit-config.json not found -- diffing all tracked files\n");
    return [];
  }
  try {
    const raw = readFileSync(configPath, "utf-8");
    const config = JSON.parse(raw);
    return Array.isArray(config.substantial_paths) ? config.substantial_paths : [];
  } catch (e) {
    process.stderr.write(`audit_diff: could not parse .audit-config.json: ${e.message} -- diffing all tracked files\n`);
    return [];
  }
}

// ---------------------------------------------------------------------------
// Run git diff
// ---------------------------------------------------------------------------

function runGitDiff(patterns) {
  // git diff --no-color [-- <pathspec>...]
  // We pass patterns as pathspecs after "--".
  const gitArgs = ["diff", "--no-color"];
  if (patterns.length > 0) {
    gitArgs.push("--");
    gitArgs.push(...patterns);
  }

  const result = spawnSync("git", gitArgs, {
    cwd: repoRoot,
    encoding: "utf-8",
    maxBuffer: 10 * 1024 * 1024,
  });

  if (result.error) {
    die(`git diff failed to launch: ${result.error.message}`);
  }
  if (result.status !== 0) {
    process.stderr.write(`audit_diff: git diff exited ${result.status}\n`);
    if (result.stderr) process.stderr.write(result.stderr + "\n");
    process.exit(1);
  }
  return result.stdout;
}

// ---------------------------------------------------------------------------
// Auditor invocation
// ---------------------------------------------------------------------------

// Codex non-interactive: "codex exec <PROMPT>" (verified against installed
// CLI 2026-05-28). Claude uses "claude --print" (proven pattern).
function invokeAuditor(model, prompt, debug) {
  let cmd, args;
  if (model === "claude") {
    cmd = "claude";
    args = ["--print", prompt];
  } else if (model === "codex") {
    cmd = "codex";
    args = ["exec", prompt];
  } else {
    die(`Unknown auditor model: ${model}`);
  }

  process.stderr.write(`audit_diff: invoking ${model} auditor...\n`);
  const result = spawnSync(cmd, args, {
    encoding: "utf-8",
    maxBuffer: 10 * 1024 * 1024,
  });

  if (debug) {
    process.stderr.write(`[debug] exit: ${result.status}\n`);
    if (result.stderr) process.stderr.write(`[debug] stderr: ${result.stderr}\n`);
  }

  if (result.error) {
    die(`Auditor CLI "${cmd}" could not be launched: ${result.error.message}\nIs ${model} installed and on PATH?`);
  }
  if (result.status !== 0) {
    process.stderr.write(`audit_diff: ${model} exited with status ${result.status}\n`);
    if (result.stderr) process.stderr.write(result.stderr + "\n");
    process.exit(1);
  }
  return result.stdout;
}

// ---------------------------------------------------------------------------
// Prompt construction
// ---------------------------------------------------------------------------

function buildPrompt(canonBlock, leaderModel, auditorModel, task, diff) {
  return `You are auditing a working git diff produced by ${leaderModel} for the Sibley Creek Canadian macroeconomics publication.

## Project canon

${canonBlock}

## Task the leader (${leaderModel}) was trying to accomplish

${task}

## Working diff

\`\`\`diff
${diff}
\`\`\`

## Your job

You are ${auditorModel}. Enumerate every problem you find in the changes above, judged against the project canon and the stated task. Be thorough and concrete. Do not praise; only findings matter.

Group your findings by severity:

### BLOCKER
Problems that must be fixed before ship: incorrect data wiring, retired components resurrected, factual errors, voice canon failures that misrepresent the publication, broken builds.

### IMPORTANT
Significant issues that degrade quality: structural failures, missed parallel work, voice drift, missing provenance, soft canon violations.

### MINOR
Small issues: word choice, formatting, non-critical convention gaps.

For each finding state:
- Location (file and line reference from the diff)
- What is wrong
- What the correct form should be

If a category has no findings, write "None."`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const args = parseArgs(process.argv.slice(2));
const leader = args.by;
let auditor;
try {
  auditor = oppositeModel(leader);
} catch (e) {
  die(e.message);
}

const patterns = loadSubstantialPaths();
process.stderr.write(
  patterns.length > 0
    ? `audit_diff: filtering diff to ${patterns.length} substantial path pattern(s)\n`
    : "audit_diff: no path filter applied\n"
);

const diff = runGitDiff(patterns);

if (!diff.trim()) {
  process.stderr.write("audit_diff: no changes in the working tree for the configured paths -- nothing to audit\n");
  process.exit(0);
}

const diffLines = diff.split("\n").length;
process.stderr.write(`audit_diff: diff is ${diffLines} lines\n`);

const canonBlock = await buildCanonBlock();
const prompt = buildPrompt(canonBlock, leader, auditor, args.task, diff);

const findingsContent = invokeAuditor(auditor, prompt, args.debug);

// Write findings file.
const outPath = findingsPath("working-diff", auditor);
await fs.mkdir(path.dirname(outPath), { recursive: true });

const date = new Date().toISOString().slice(0, 10);
const header = [
  "---",
  `shape: working-diff`,
  `leader: ${leader}`,
  `auditor: ${auditor}`,
  `task: ${args.task}`,
  `date: ${date}`,
  `diff_lines: ${diffLines}`,
  "---",
  "",
].join("\n");

await fs.writeFile(outPath, header + findingsContent, "utf-8");

const outRel = path.relative(repoRoot, outPath).split(path.sep).join("/");
process.stderr.write(`audit_diff: findings written to ${outRel}\n`);
process.stdout.write(outPath + "\n");
