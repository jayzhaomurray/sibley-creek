// canon_brief.mjs -- shared helpers for audit scripts.
//
// Exports:
//   buildCanonBlock()    -> Promise<string>  packed context string for audit prompts
//   oppositeModel(by)    -> "claude" | "codex"
//   findingsPath(target, auditor, shape)  -> string  (absolute)

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export const repoRoot = path.resolve(__dirname, "..", "..");

// Files that make up the project canon context.
const CANON_FILES = [
  "CLAUDE.md",
  "editorial/dashboard_purpose.md",
  "editorial/writing-style.md",
  "editorial/review_protocol.md",
  "design/design-system.md",
];

export async function buildCanonBlock() {
  const parts = [];
  for (const rel of CANON_FILES) {
    const abs = path.join(repoRoot, rel);
    let text;
    try {
      text = await fs.readFile(abs, "utf-8");
    } catch {
      process.stderr.write(`canon_brief: warning -- could not read ${rel} (skipping)\n`);
      continue;
    }
    parts.push(`=== ${rel} ===\n${text}`);
  }
  return parts.join("\n\n");
}

export function oppositeModel(by) {
  if (by === "claude") return "codex";
  if (by === "codex") return "claude";
  throw new Error(`oppositeModel: unknown model "${by}" -- must be "claude" or "codex"`);
}

// Shape A: editorial/audit_findings/<basename>-by-<auditor>-<YYYY-MM-DD>.md
// Shape C: editorial/audit_findings/working-diff-by-<auditor>-<YYYY-MM-DD>-<HHmm>.md
export function findingsPath(targetFileOrShape, auditor) {
  const dir = path.join(repoRoot, "editorial", "audit_findings");
  const now = new Date();
  const date = now.toISOString().slice(0, 10);

  if (targetFileOrShape === "working-diff") {
    const hhmm = now.toISOString().slice(11, 16).replace(":", "");
    return path.join(dir, `working-diff-by-${auditor}-${date}-${hhmm}.md`);
  }

  const basename = path.basename(targetFileOrShape, path.extname(targetFileOrShape));
  return path.join(dir, `${basename}-by-${auditor}-${date}.md`);
}
