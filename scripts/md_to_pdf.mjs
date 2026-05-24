// Generic markdown -> PDF renderer via Playwright (Chromium).
//
// Usage:  node scripts/md_to_pdf.mjs <input.md> <output.pdf>
//
// Renders the input markdown to a Sibley-Creek-styled HTML page, then
// uses Playwright's print-to-PDF to produce the output. Inline markdown
// parser is intentionally minimal — handles the subset of markdown used
// in onboarding/team docs (headings, paragraphs, lists, bold, italics,
// inline code, code fences, horizontal rules, links). For richer docs,
// swap in `marked` or `markdown-it`.

import { chromium } from "playwright";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const [, , inputArg, outputArg] = process.argv;
if (!inputArg || !outputArg) {
  console.error("usage: node scripts/md_to_pdf.mjs <input.md> <output.pdf>");
  process.exit(1);
}

const inputPath = resolve(process.cwd(), inputArg);
const outputPath = resolve(process.cwd(), outputArg);

const md = await readFile(inputPath, "utf8");

// --- minimal markdown -> HTML --------------------------------------------

function escapeHtml(s) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function inline(s) {
  // links [text](url)
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) => {
    return `<a href="${escapeHtml(url)}">${inline(text)}</a>`;
  });
  // bold **text** (must come before italic)
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  // italic *text* or _text_
  s = s.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>");
  // inline code `text`
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  return s;
}

function mdToHtml(src) {
  const lines = src.split(/\r?\n/);
  const out = [];
  let i = 0;
  let inList = false;

  function closeList() {
    if (inList) {
      out.push("</ol>");
      inList = false;
    }
  }

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed === "") {
      closeList();
      i++;
      continue;
    }

    if (trimmed === "---") {
      closeList();
      out.push("<hr>");
      i++;
      continue;
    }

    // headings
    const h = trimmed.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      closeList();
      const level = h[1].length;
      out.push(`<h${level}>${inline(escapeHtml(h[2]))}</h${level}>`);
      i++;
      continue;
    }

    // numbered list items
    const ol = trimmed.match(/^\d+\.\s+(.*)$/);
    if (ol) {
      if (!inList) {
        out.push('<ol>');
        inList = true;
      }
      // gather indented continuation lines (sublists, paragraphs)
      let item = ol[1];
      let j = i + 1;
      while (j < lines.length && /^\s{3,}\S/.test(lines[j])) {
        item += " " + lines[j].trim();
        j++;
      }
      out.push(`<li>${inline(escapeHtml(item))}</li>`);
      i = j;
      continue;
    }

    // bullet list items
    const ul = trimmed.match(/^[-*]\s+(.*)$/);
    if (ul) {
      if (!inList) {
        out.push('<ul>');
        inList = true;
      }
      out.push(`<li>${inline(escapeHtml(ul[1]))}</li>`);
      i++;
      continue;
    }

    // plain paragraph (collect consecutive non-empty lines)
    closeList();
    const para = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !lines[i].trim().startsWith("#") &&
      !lines[i].trim().startsWith("---") &&
      !/^\d+\.\s/.test(lines[i].trim()) &&
      !/^[-*]\s/.test(lines[i].trim())
    ) {
      para.push(lines[i].trim());
      i++;
    }
    out.push(`<p>${inline(escapeHtml(para.join(" ")))}</p>`);
  }

  closeList();
  return out.join("\n");
}

const body = mdToHtml(md);

const html = `<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<title>Sibley Creek</title>
<style>
  @page { size: Letter; margin: 0.75in 0.85in; }
  html { font-family: "Manrope", "Helvetica Neue", Helvetica, Arial, sans-serif; color: #000; }
  body { font-size: 11pt; line-height: 1.55; max-width: 100%; }
  h1 { font-size: 22pt; font-weight: 800; letter-spacing: -0.01em; line-height: 1.15; margin: 0 0 12pt; border-bottom: 1px solid #000; padding-bottom: 8pt; }
  h2 { font-size: 13pt; font-weight: 800; letter-spacing: -0.005em; margin: 18pt 0 6pt; }
  h3 { font-size: 11pt; font-weight: 700; margin: 12pt 0 4pt; text-transform: none; }
  p { margin: 0 0 8pt; }
  ol, ul { margin: 0 0 10pt 0; padding-left: 20pt; }
  li { margin-bottom: 4pt; }
  li > strong:first-child { font-weight: 700; }
  hr { border: 0; border-top: 1px solid #000; margin: 16pt 0; }
  code { font-family: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace; font-size: 10pt; background: #f3f3f3; padding: 1pt 4pt; border-radius: 2pt; }
  strong { font-weight: 700; }
  em { font-style: italic; }
  a { color: #000; text-decoration: underline; }
  /* Tight first-element margin so heading sits at top */
  h1:first-child { margin-top: 0; }
</style>
</head>
<body>
${body}
</body>
</html>`;

// --- render via Playwright -----------------------------------------------

const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.setContent(html, { waitUntil: "networkidle" });
await page.pdf({
  path: outputPath,
  format: "Letter",
  printBackground: true,
  margin: { top: "0.75in", bottom: "0.75in", left: "0.85in", right: "0.85in" },
});
await browser.close();

console.log(`wrote: ${outputPath}`);
