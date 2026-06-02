#!/usr/bin/env node
// cross_audit.mjs -- Shape B: both models take independent passes; one referees.
//
// Usage:
//   node scripts/cross_audit.mjs "<task description>"
//
// Behavior:
//   1. Slugifies the task into a kebab-case task-slug (max 50 chars).
//   2. Creates claude-ref/cross_audit/<task-slug>/ and writes spec.md.
//   3. Fires Claude and Codex in parallel; each writes its pass to the dir.
//   4. Prompts the user to choose a referee model.
//   5. Fires the referee with both passes; writes synthesis.md.
//   6. Prints all output paths to stdout.

import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import * as readline from "node:readline";
import { buildCanonBlock, repoRoot } from "./_lib/canon_brief.mjs";

// ---------------------------------------------------------------------------
// Arg parsing
// ---------------------------------------------------------------------------

const taskArg = process.argv[2];
if (!taskArg || taskArg.startsWith("--")) {
  process.stderr.write("Usage: node scripts/cross_audit.mjs \"<task description>\"\n");
  process.exit(1);
}

const debug = process.argv.includes("--debug");

// ---------------------------------------------------------------------------
// Slug helper
// ---------------------------------------------------------------------------

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 50);
}

// ---------------------------------------------------------------------------
// Spawn a model and capture its stdout to a file
// ---------------------------------------------------------------------------

function runModel(model, prompt, outFile) {
  return new Promise((resolve, reject) => {
    let cmd, args;
    // Codex non-interactive: "codex exec <PROMPT>" (verified 2026-05-28).
    if (model === "claude") {
      cmd = "claude";
      args = ["--print", prompt];
    } else {
      cmd = "codex";
      args = ["exec", prompt];
    }

    process.stderr.write(`cross_audit: starting ${model} pass...\n`);

    const child = spawn(cmd, args, { encoding: "utf-8" });
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (d) => { stdout += d; });
    child.stderr.on("data", (d) => { stderr += d; });

    child.on("error", (err) => {
      reject(new Error(`${model} CLI could not be launched: ${err.message}`));
    });

    child.on("close", (code) => {
      if (debug && stderr) process.stderr.write(`[debug] ${model} stderr: ${stderr}\n`);
      if (code !== 0) {
        reject(new Error(`${model} exited ${code}${stderr ? ": " + stderr.trim() : ""}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Interactive referee prompt
// ---------------------------------------------------------------------------

function askReferee() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stderr });
    rl.question("Which model should referee the synthesis? [claude/codex]: ", (answer) => {
      rl.close();
      const trimmed = answer.trim().toLowerCase();
      if (trimmed === "claude" || trimmed === "codex") {
        resolve(trimmed);
      } else {
        process.stderr.write("cross_audit: invalid choice -- skipping referee\n");
        resolve(null);
      }
    });
    rl.on("close", () => resolve(null));
  });
}

// ---------------------------------------------------------------------------
// Prompt builders
// ---------------------------------------------------------------------------

function buildPassPrompt(model, canonBlock, task) {
  return `You are ${model}, taking an independent pass on a task for the Sibley Creek Canadian macroeconomics publication. Do NOT look at what any other model produced. Produce your best independent work.

## Project canon

${canonBlock}

## Task

${task}

Produce a complete, self-contained response. Label the top of your output: "## ${model.charAt(0).toUpperCase() + model.slice(1)} pass"`;
}

function buildRefereePrompt(refereeModel, canonBlock, task, claudePass, codexPass) {
  return `You are ${refereeModel}, refereeing two independent model passes on a task for the Sibley Creek Canadian macroeconomics publication.

## Project canon

${canonBlock}

## Task

${task}

## Claude pass

${claudePass}

## Codex pass

${codexPass}

## Your job

Produce a synthesis that:
1. Identifies where the two passes agree (take that as signal).
2. Identifies where they disagree and rules on the correct answer with justification.
3. Flags anything both models got wrong that you can identify from first principles.
4. Produces a final recommended artifact or set of recommendations, clearly labelled.

Label your output: "## Referee synthesis (by ${refereeModel})"`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const taskSlug = slugify(taskArg);
const workDir = path.join(repoRoot, "claude-ref", "cross_audit", taskSlug);

await fs.mkdir(workDir, { recursive: true });
process.stderr.write(`cross_audit: working dir: claude-ref/cross_audit/${taskSlug}/\n`);

// Write spec.
const specPath = path.join(workDir, "spec.md");
await fs.writeFile(
  specPath,
  `# Cross-audit spec\n\n## Task\n\n${taskArg}\n\n---\n_Generated by cross_audit.mjs. Both models receive this spec independently._\n`,
  "utf-8"
);

const canonBlock = await buildCanonBlock();
const claudePrompt = buildPassPrompt("claude", canonBlock, taskArg);
const codexPrompt = buildPassPrompt("codex", canonBlock, taskArg);

// Run both passes in parallel; write .err on failure.
const claudePassPath = path.join(workDir, "claude-pass.md");
const codexPassPath = path.join(workDir, "codex-pass.md");

const [claudeResult, codexResult] = await Promise.allSettled([
  runModel("claude", claudePrompt, claudePassPath),
  runModel("codex", codexPrompt, codexPassPath),
]);

let claudeText = null;
let codexText = null;

if (claudeResult.status === "fulfilled") {
  claudeText = claudeResult.value;
  await fs.writeFile(claudePassPath, claudeText, "utf-8");
  process.stderr.write("cross_audit: claude pass complete\n");
} else {
  const errPath = claudePassPath.replace(".md", ".err");
  await fs.writeFile(errPath, claudeResult.reason.message, "utf-8");
  process.stderr.write(`cross_audit: claude pass FAILED -- error written to claude-pass.err\n`);
  process.stderr.write(`  ${claudeResult.reason.message}\n`);
}

if (codexResult.status === "fulfilled") {
  codexText = codexResult.value;
  await fs.writeFile(codexPassPath, codexText, "utf-8");
  process.stderr.write("cross_audit: codex pass complete\n");
} else {
  const errPath = codexPassPath.replace(".md", ".err");
  await fs.writeFile(errPath, codexResult.reason.message, "utf-8");
  process.stderr.write(`cross_audit: codex pass FAILED -- error written to codex-pass.err\n`);
  process.stderr.write(`  ${codexResult.reason.message}\n`);
}

// Referee.
const synthesisPath = path.join(workDir, "synthesis.md");

if (!claudeText && !codexText) {
  process.stderr.write("cross_audit: both passes failed -- cannot referee; synthesis skipped\n");
} else {
  const referee = await askReferee();

  if (!referee) {
    process.stderr.write("cross_audit: no referee chosen -- synthesis pending\n");
    process.stderr.write(`  Re-run with a working pass and choose a referee to complete synthesis.\n`);
  } else {
    const passA = claudeText || "[Claude pass failed -- see claude-pass.err]";
    const passB = codexText || "[Codex pass failed -- see codex-pass.err]";
    const refereePrompt = buildRefereePrompt(referee, canonBlock, taskArg, passA, passB);

    process.stderr.write(`cross_audit: invoking ${referee} as referee...\n`);
    try {
      const synthesis = await runModel(referee, refereePrompt, synthesisPath);
      await fs.writeFile(synthesisPath, synthesis, "utf-8");
      process.stderr.write("cross_audit: synthesis complete\n");
    } catch (e) {
      const errPath = synthesisPath.replace(".md", ".err");
      await fs.writeFile(errPath, e.message, "utf-8");
      process.stderr.write(`cross_audit: referee failed -- error written to synthesis.err\n`);
    }
  }
}

// Print all paths to stdout.
process.stdout.write(specPath + "\n");
process.stdout.write(claudePassPath + "\n");
process.stdout.write(codexPassPath + "\n");
process.stdout.write(synthesisPath + "\n");
