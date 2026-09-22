/**
 * Render every poster to PNG at its native Figma size.
 *
 *   npm run export            → export/*.png            (1×, the size Figma shows)
 *   npm run export -- --2x    → export/*@2x.png         (retina master)
 *   npm run export -- --only 05
 *
 * Chromium screenshots the .poster element itself, so nothing around it —
 * page background, scrollbars — ever ends up in the file.
 */
import { chromium } from "playwright";
import { mkdir, readdir } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join, resolve } from "node:path";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(root, "export");

const args = process.argv.slice(2);
const scale = args.includes("--2x") ? 2 : 1;
const only = args.includes("--only") ? args[args.indexOf("--only") + 1] : null;

const pages = (await readdir(join(root, "posters")))
  .filter((f) => f.endsWith(".html"))
  .filter((f) => !only || f.startsWith(only))
  .sort();

if (!pages.length) {
  console.error(only ? `No poster starts with "${only}".` : "No posters found.");
  process.exit(1);
}

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({ deviceScaleFactor: scale });
const page = await context.newPage();

for (const file of pages) {
  await page.goto(pathToFileURL(join(root, "posters", file)).href, { waitUntil: "load" });
  // Webfonts and the background plate both have to be in before we shoot.
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() =>
    Promise.all([...document.images].filter((i) => !i.complete).map((i) => i.decode().catch(() => {})))
  );

  const el = page.locator(".poster");
  const box = await el.boundingBox();
  await page.setViewportSize({ width: Math.ceil(box.width), height: Math.ceil(box.height) });

  const name = file.replace(/\.html$/, "") + (scale === 2 ? "@2x" : "") + ".png";
  await el.screenshot({ path: join(outDir, name) });
  console.log(`${name}  ${box.width * scale} × ${box.height * scale}`);
}

await browser.close();
console.log(`\nWritten to ${outDir}`);
