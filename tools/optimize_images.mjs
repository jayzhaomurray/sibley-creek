/**
 * tools/optimize_images.mjs
 * One-shot image optimization for showcase and other public assets.
 *
 * Run from project root:
 *   node tools/optimize_images.mjs
 *
 * Strategy:
 *   PNGs  — sharp pngquant (lossy, quality 70-85) + advancedMask (spng/zlib)
 *           Chartbook PNGs are resized to 1120px wide (2x retina at 560px
 *           display width) before compression.
 *   JPG   — sharp mozjpeg at quality 80, max 1440px wide
 *
 * Files are optimized in-place (overwrite). Originals are NOT preserved here
 * because git history holds the prior version.
 */

import sharp from "sharp";
import { readFileSync, statSync, writeFileSync, existsSync } from "fs";
import { resolve } from "path";

const ROOT = new URL("..", import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1");

/**
 * Chartbook slugs — mirrors sections[] in src/data/sections.ts.
 * Update here when a new section is added.
 */
const CHARTBOOK_SLUGS = [
  "output",
  "inflation",
  "labour",
  "housing",
  "policy",
  "markets",
  "trade",
];

// ── Job list ────────────────────────────────────────────────────────────────

const jobs = [
  // ── Legacy splash showcase PNGs ─────────────────────────────────────────
  {
    src: "public/showcase/chart-research.png",
    type: "png",
  },
  {
    src: "public/showcase/dashboard.png",
    type: "png",
  },
  // ── Commentary PDF renders (~440px rendered width) ────────────────────
  {
    src: "public/showcase/commentary-cpi-april-2026-cover.png",
    type: "png",
  },
  {
    src: "public/showcase/commentary-cpi-april-2026-page2.png",
    type: "png",
  },
  // ── About page hero JPG — max 1440px, mozjpeg quality 80 ──────────────
  {
    src: "public/about/sleeping-giant.jpg",
    type: "jpg",
    maxWidth: 1440,
    quality: 80,
  },
];

// Add chartbook PNG jobs — resize to 1120px wide (2x retina at 560px display)
for (const slug of CHARTBOOK_SLUGS) {
  jobs.push({
    src: `public/showcase/chartbook-${slug}.png`,
    type: "png",
    resizeWidth: 1120,
  });
}

// ── Optimization helpers ───────────────────────────────────────────────────

async function optimizePng(filePath, resizeWidth) {
  const buf = readFileSync(filePath);
  const meta = await sharp(buf).metadata();

  let pipeline = sharp(buf);
  if (resizeWidth && meta.width > resizeWidth) {
    pipeline = pipeline.resize({ width: resizeWidth, withoutEnlargement: true });
  }

  const out = await pipeline
    .png({
      quality: 80,          // pngquant/imagequant lossy; 80 = good retina fidelity
      compressionLevel: 9,  // zlib max deflate on top
      effort: 10,           // libvips compression effort (0-10)
      palette: false,       // keep full colour (screenshots have gradients)
    })
    .toBuffer();

  // Re-read metadata after possible resize
  const outMeta = await sharp(out).metadata();
  return { out, width: outMeta.width, height: outMeta.height };
}

async function optimizeJpg(filePath, maxWidth = 1440, quality = 80) {
  const buf = readFileSync(filePath);
  const meta = await sharp(buf).metadata();

  let pipeline = sharp(buf);
  if (meta.width > maxWidth) {
    pipeline = pipeline.resize({ width: maxWidth, withoutEnlargement: true });
  }

  const out = await pipeline
    .jpeg({
      quality,
      mozjpeg: true,   // mozjpeg encoder (already bundled in sharp)
      chromaSubsampling: "4:2:0",
    })
    .toBuffer();

  return { out, width: meta.width, height: meta.height };
}

function verifyMagic(buf, type) {
  if (type === "png") {
    // PNG magic: 0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
    return (
      buf[0] === 0x89 &&
      buf[1] === 0x50 &&
      buf[2] === 0x4e &&
      buf[3] === 0x47
    );
  }
  if (type === "jpg") {
    // JFIF/EXIF: 0xFF 0xD8
    return buf[0] === 0xff && buf[1] === 0xd8;
  }
  return false;
}

// ── Main loop ─────────────────────────────────────────────────────────────

const results = [];

for (const job of jobs) {
  const abs = resolve(ROOT, job.src);

  if (!existsSync(abs)) {
    results.push({ file: job.src, status: "MISSING" });
    continue;
  }

  const before = statSync(abs).size;

  let out, width, height;
  try {
    if (job.type === "png") {
      ({ out, width, height } = await optimizePng(abs, job.resizeWidth));
    } else {
      ({ out, width, height } = await optimizeJpg(abs, job.maxWidth, job.quality));
    }
  } catch (err) {
    results.push({ file: job.src, status: "ERROR", error: err.message });
    continue;
  }

  if (!verifyMagic(out, job.type)) {
    results.push({ file: job.src, status: "INVALID_MAGIC" });
    continue;
  }

  const after = out.length;
  const pct = (((before - after) / before) * 100).toFixed(1);

  if (after >= before) {
    // Sharp produced a larger file — keep original.
    results.push({
      file: job.src,
      status: "SKIPPED_LARGER",
      before,
      after,
      dimensions: `${width}x${height}`,
    });
    continue;
  }

  writeFileSync(abs, out);
  results.push({
    file: job.src,
    status: "OK",
    before,
    after,
    reduction: `${pct}%`,
    dimensions: `${width}x${height}`,
  });
}

// ── Summary ──────────────────────────────────────────────────────────────
console.log("\nImage optimization results");
console.log("==========================");
for (const r of results) {
  if (r.status === "OK") {
    const kb = (n) => (n / 1024).toFixed(1) + " KB";
    console.log(
      `OK   ${r.file}\n     ${kb(r.before)} -> ${kb(r.after)} (${r.reduction} reduction)  [${r.dimensions}]`
    );
  } else if (r.status === "SKIPPED_LARGER") {
    const kb = (n) => (n / 1024).toFixed(1) + " KB";
    console.log(
      `SKIP ${r.file}  (sharp output ${kb(r.after)} >= original ${kb(r.before)}, kept original)  [${r.dimensions}]`
    );
  } else if (r.status === "MISSING") {
    console.log(`MISS ${r.file}  (file not found, skipped)`);
  } else if (r.status === "ERROR") {
    console.log(`ERR  ${r.file}  ${r.error}`);
  } else {
    console.log(`FAIL ${r.file}  ${r.status}`);
  }
}
