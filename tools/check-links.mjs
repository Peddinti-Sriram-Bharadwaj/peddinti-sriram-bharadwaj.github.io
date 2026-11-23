// Verifies every internal link, image and #anchor in the built site resolves.
// Usage: npm run check   (runs after a build; exits non-zero on any broken link)
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, dirname, resolve } from "node:path";

const ROOT = resolve("_site");
const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]));
const pages = walk(ROOT).filter((f) => f.endsWith(".html"));
const ids = new Map(pages.map((f) => [f, new Set([...readFileSync(f, "utf8").matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]))]));

let broken = 0, checked = 0;
for (const page of pages) {
  const html = readFileSync(page, "utf8");
  for (const [, ref] of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
    if (/^(https?:|mailto:|data:|\/\/)/.test(ref)) continue;
    checked++;
    const [path, hash] = ref.split("#");
    let target = path === "" ? page : path.startsWith("/") ? join(ROOT, path) : join(dirname(page), path);
    if (path.endsWith("/") || path === "") target = path === "" ? page : join(target, "index.html");
    const ok = existsSync(target) && (!hash || !target.endsWith(".html") || ids.get(target)?.has(hash));
    if (!ok) { broken++; console.error(`✗ ${page.replace(ROOT, "")} → ${ref}`); }
  }
}
console.log(`${checked} internal links checked across ${pages.length} pages, ${broken} broken.`);
process.exit(broken ? 1 : 0);
