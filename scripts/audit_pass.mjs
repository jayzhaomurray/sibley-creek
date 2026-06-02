#!/usr/bin/env node
// audit_pass.mjs -- Shape A audit: one model produced a file; the opposite audits it.
//
// Usage:
//   node scripts/audit_pass.mjs --by <claude|codex> --target <path> --task "<description>"
//
// Behavior:
//   1. Resolves auditor as opposite of --by.
//   2. Reads the target file and the canon context block.
//   3. Constructs an audit prompt and invokes the auditor CLI.
//   4. Writes findings to editorial/audit_findings/<basename>-by-<auditor>-<YYYY-MM-DD>.md.
//   5. Prints the findings path to stdout.

import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { buildCanonBlock, oppositeModel, findingsPath, repoRoot } from "./_lib/canon_brief.mjs";

// ---------------------------------------------------------------------------
// Arg parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = { by: null, target: null, task: null, debug: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--by") args.by = argv[++i];
    else if (argv[i] === "--target") args.target = argv[++i];
    else if (argv[i] === "--task") args.task = argv[++i];
    else if (argv[i] === "--debug") args.debug = true;
    else die(`Unknown argument: ${argv[i]}`);
  }
  if (!args.by) die("--by <claude|codex> is required");
  if (!args.target) die("--target <path> is required");
  if (!args.task) die("--task \"<description>\" is required");
  return args;
}

function die(msg) {
  process.stderr.write(`audit_pass: ${msg}\n`);
  process.exit(1);
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

  process.stderr.write(`audit_pass: invoking ${model} auditor...\n`);
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
    process.stderr.write(`audit_pass: ${model} exited with status ${result.status}\n`);
    if (result.stderr) process.stderr.write(result.stderr + "\n");
    process.exit(1);
  }
  return result.stdout;
}

// ---------------------------------------------------------------------------
// Prompt construction
// ---------------------------------------------------------------------------

function buildPrompt(canonBlock, leaderModel, auditorModel, task, targetRel, fileText) {
  return `You are auditing work produced by ${leaderModel} for the Sibley Creek Canadian macroeconomics publication.

## Project canon

${canonBlock}

## Task the leader (${leaderModel}) was given

${task}

## File under audit: ${targetRel}

${fileText}

## Your job

You are ${auditorModel}. Enumerate every problem you find with the artifact above, judged against the project canon and the stated task. Be thorough and concrete. Do not praise; only findings matter.

Group your findings by severity:

### BLOCKER
Problems that must be fixed before ship: incorrect data wiring, retired components resurrected, factual errors, voice canon failures that misrepresent the publication, broken builds.

### IMPORTANT
Significant issues that degrade quality: structural failures, missed parallel work, voice drift, missing provenance, soft canon violations.

### MINOR
Small issues: word choice, formatting, non-critical convention gaps.

For each finding state:
- Location (file, section, or line reference)
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

const targetAbs = path.isAbsolute(args.target)
  ? args.target
  : path.resolve(repoRoot, args.target);

if (!existsSync(targetAbs)) {
  die(`Target file not found: ${args.target}`);
}

const targetRel = path.relative(repoRoot, targetAbs).split(path.sep).join("/");
const fileText = await fs.readFile(targetAbs, "utf-8");
const canonBlock = await buildCanonBlock();

const prompt = buildPrompt(canonBlock, leader, auditor, args.task, targetRel, fileText);

const findingsContent = invokeAuditor(auditor, prompt, args.debug);

// Write findings file.
const outPath = findingsPath(args.target, auditor);
await fs.mkdir(path.dirname(outPath), { recursive: true });

const date = new Date().toISOString().slice(0, 10);
const header = [
  "---",
  `target: ${targetRel}`,
  `leader: ${leader}`,
  `auditor: ${auditor}`,
  `task: ${args.task}`,
  `date: ${date}`,
  "---",
  "",
].join("\n");

await fs.writeFile(outPath, header + findingsContent, "utf-8");

const outRel = path.relative(repoRoot, outPath).split(path.sep).join("/");
process.stderr.write(`audit_pass: findings written to ${outRel}\n`);
process.stdout.write(outPath + "\n");
