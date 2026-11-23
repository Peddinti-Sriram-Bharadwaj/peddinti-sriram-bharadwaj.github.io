import yaml from "js-yaml";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const toDate = (d) => (d instanceof Date ? d : new Date(d));

export default function (cfg) {
  // Content data lives in src/_data/*.yaml
  cfg.addDataExtension("yaml,yml", (contents) => yaml.load(contents));

  // Static files are copied as-is
  cfg.addPassthroughCopy({ "src/assets": "assets" });
  cfg.addPassthroughCopy({ "src/assets/signature.png": "favicon.png" });

  // Essays and notes: every Markdown file in src/writing, newest first
  cfg.addCollection("writing", (api) =>
    api.getFilteredByGlob("src/writing/*.md").sort((a, b) => b.date - a.date)
  );

  // Date filters (UTC so a date never slips a day)
  cfg.addFilter("isoDate", (d) => toDate(d).toISOString().slice(0, 10));
  cfg.addFilter("shortDate", (d) => { d = toDate(d); return `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`; });
  cfg.addFilter("longDate", (d) => { d = toDate(d); return `${d.getUTCDate()} ${MONTHS_LONG[d.getUTCMonth()]} ${d.getUTCFullYear()}`; });
  // "2026-11" -> "Nov 2026"
  cfg.addFilter("monthYear", (s) => { const [y, m] = String(s).split("-"); return `${MONTHS[+m - 1]} ${y}`; });

  cfg.addFilter("where", (arr, key, val) => (arr || []).filter((x) => x[key] === val));
  cfg.addFilter("limit", (arr, n) => (arr || []).slice(0, n));
  cfg.addFilter("pad", (n, width = 2) => String(n).padStart(width, "0"));

  // Is this nav item the current section?
  cfg.addFilter("isCurrent", (itemUrl, pageUrl) =>
    itemUrl === "/" ? pageUrl === "/" : pageUrl === itemUrl || pageUrl.startsWith(itemUrl.replace(/\.html$/, "/"))
  );

  cfg.addGlobalData("year", () => new Date().getFullYear());

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
}
