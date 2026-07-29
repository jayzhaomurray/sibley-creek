#!/usr/bin/env node
/*
 * revert_commentary.mjs — removes one commentary published via the
 * "Publish a data commentary" issue form.
 *
 * Triggered by checking the "Revert this publish" box in the bot's own
 * success comment (.github/workflows/revert-commentary.yml listens for
 * that comment being edited). Reads the slug out of the hidden
 * `<!-- commentary-slug: <slug> --%>` marker in COMMENT_BODY, deletes the
 * matching entry from the `commentaries` array in src/data/sections.ts,
 * and deletes the associated PDF + preview images.
 *
 * Safe to run twice: if the slug is already gone (already reverted, or
 * never existed), this exits cleanly rather than failing loudly --
 * checking the box a second time shouldn't look like a crash.
 *
 * Deliberately does NOT run any build/citation checks itself -- same
 * division of labour as process_commentary_issue.mjs: the workflow's own
 * "Validate full build" step is the single source of truth for whether
 * the result is safe to ship.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const SECTIONS_TS = path.join(repoRoot, "src", "data", "sections.ts");
const COMMENTARIES_DIR = path.join(repoRoot, "public", "research", "commentaries");
const SHOWCASE_DIR = path.join(repoRoot, "public", "showcase");

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

function setOutput(key, value) {
  const outFile = process.env.GITHUB_OUTPUT;
  if (!outFile) return;
  fs.appendFileSync(outFile, `${key}=${value}\n`);
}

function extractSlug(commentBody) {
  const match = commentBody.match(/<!--\s*commentary-slug:\s*([a-z0-9-]+)\s*-->/i);
  if (!match) fail("Could not find the commentary-slug marker in the comment -- was this comment edited by hand?");
  return match[1];
}

// Removes the one top-level entry (a "  {\n ... \n  },\n" block, 2-space
// indent) whose body contains the target slug. Non-greedy matching means
// it stops at the FIRST "\n  },\n" it finds -- entries never contain that
// exact 2-space-indented closer internally, only nested objects/arrays
// (author, coverage) do, and those close at 4-space indent ("    },\n"),
// so this can't accidentally stop early inside a nested block.
function removeEntry(sectionsSrc, slug) {
  const entryPattern = /  \{[\s\S]*?\n  \},\n/g;
  let match;
  while ((match = entryPattern.exec(sectionsSrc))) {
    if (match[0].includes(`slug: "${slug}"`)) {
      return sectionsSrc.slice(0, match.index) + sectionsSrc.slice(match.index + match[0].length);
    }
  }
  return null; // not found
}

function deleteIfExists(filePath) {
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    console.log(`[revert] deleted ${filePath}`);
  } else {
    console.log(`[revert] already absent: ${filePath}`);
  }
}

function main() {
  const commentBody = process.env.COMMENT_BODY;
  if (!commentBody) fail("COMMENT_BODY env var is not set.");

  const slug = extractSlug(commentBody);
  console.log(`[revert] slug: ${slug}`);

  const sectionsSrc = fs.readFileSync(SECTIONS_TS, "utf8");
  const updatedSrc = removeEntry(sectionsSrc, slug);

  if (updatedSrc === null) {
    console.log(`[revert] "${slug}" is not in the commentaries list -- already reverted, or never there. Nothing to do.`);
    setOutput("slug", slug);
    setOutput("found", "false");
    return;
  }

  fs.writeFileSync(SECTIONS_TS, updatedSrc);

  deleteIfExists(path.join(COMMENTARIES_DIR, `${slug}.pdf`));
  deleteIfExists(path.join(SHOWCASE_DIR, `commentary-${slug}-cover.png`));
  deleteIfExists(path.join(SHOWCASE_DIR, `commentary-${slug}-page2.png`));

  setOutput("slug", slug);
  setOutput("found", "true");
}

main();
