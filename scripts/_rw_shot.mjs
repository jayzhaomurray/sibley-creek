// Temp: build a local static server over dist/ and screenshot /recession-watch/.
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname } from "node:path";
import { chromium } from "playwright";

const DIST = join(process.cwd(), "dist");
const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript",
  ".css": "text/css", ".svg": "image/svg+xml", ".json": "application/json",
  ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
  ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg",
  ".ico": "image/x-icon", ".avif": "image/avif",
};

async function readFirst(candidates) {
  for (const c of candidates) {
    try {
      const s = await stat(c);
      if (s.isFile()) return c;
    } catch {}
  }
  return null;
}

const server = createServer(async (req, res) => {
  const raw = decodeURIComponent(req.url.split("?")[0]);
  const base = join(DIST, raw);
  const candidates = [
    base,
    join(base, "index.html"),
    base.replace(/\/$/, "") + ".html",
  ];
  const fp = await readFirst(candidates);
  if (!fp) { res.writeHead(404); res.end("404"); return; }
  const data = await readFile(fp);
  res.writeHead(200, { "content-type": TYPES[extname(fp)] || "application/octet-stream" });
  res.end(data);
});

await new Promise((r) => server.listen(0, r));
const port = server.address().port;

const browser = await chromium.launch();
const page = await (await browser.newContext({
  viewport: { width: 1280, height: 1700 }, deviceScaleFactor: 2,
})).newPage();
const resp = await page.goto(`http://localhost:${port}/recession-watch/`, { waitUntil: "networkidle" });
console.log("HTTP", resp.status());
const out = join(process.cwd(), "data", "derived", "rw_preview.png");
await page.screenshot({ path: out, fullPage: true });
await browser.close();
server.close();
console.log("saved", out);
