// The tear-off pad: shows Voyager 1's distance; every TEAR_EVERY ms the top slip rips
// away along a ragged edge and falls, revealing the new number on the slip beneath.
import { voyagerFromEarthKm } from "./voyager.js";

const TEAR_EVERY = 8000;
const C_KM_S = 299_792.458;

const pad = document.querySelector(".voyager");
if (pad) {
  const sheet = pad.querySelector("[data-sheet]");
  const num = pad.querySelector("[data-num]");
  const note = pad.querySelector("[data-note]");
  const group = (n) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const calm = matchMedia("(prefers-reduced-motion: reduce)");

  const render = () => {
    const km = voyagerFromEarthKm();
    num.textContent = group(km);
    const s = km / C_KM_S, h = Math.floor(s / 3600), m = Math.round((s % 3600) / 60);
    note.textContent = `its signal takes ${h} h ${m} min to reach us`;
    pad.setAttribute("aria-label", `Voyager 1 is ${group(km)} kilometres from Earth`);
  };

  // a ragged tear line across the top of the slip, as a clip-path polygon
  const raggedTop = () => {
    const pts = []; let y = 6;
    for (let x = 0; x <= 100; x += 2 + Math.random() * 3) {
      y = Math.max(1.5, Math.min(11, y + (Math.random() - .5) * 4.5));
      pts.push(`${x.toFixed(1)}% ${y.toFixed(1)}%`);
    }
    pts.push(`100% ${y.toFixed(1)}%`, "100% 100%", "0% 100%");
    return `polygon(${pts.join(",")})`;
  };

  // a sketchy sepia border, re-drawn by hand for every slip
  const frame = () => {
    const line = (x0, y0, x1, y1) => {
      const n = 7, p = [];
      for (let i = 0; i <= n; i++) {
        const t = i / n, j = () => (Math.random() - .5) * 1.4;
        p.push(`${(x0 + (x1 - x0) * t + j()).toFixed(1)},${(y0 + (y1 - y0) * t + j()).toFixed(1)}`);
      }
      return `M${p.join(" L")}`;
    };
    const o = () => (Math.random() - .5) * 3;
    let d = "";
    for (let pass = 0; pass < 2; pass++) {
      d += line(4 + o(), 5 + o(), 236 + o(), 4 + o()) + line(236 + o(), 3 + o(), 237 + o(), 116 + o())
         + line(238 + o(), 115 + o(), 5 + o(), 116 + o()) + line(4 + o(), 117 + o(), 5 + o(), 4 + o());
    }
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 120" preserveAspectRatio="none">
      <path d="${d}" fill="none" stroke="#6b3518" stroke-opacity=".55" stroke-width="1" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>`;
    return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
  };

  // the stubs left on the pad: an irregular torn fringe, new after every tear
  const stub = pad.querySelector(".pad-stub");
  const roughStub = () => {
    if (!stub) return;
    const pts = ["0 0", "100% 0"]; let x = 100;
    while (x > 0) {
      const y = 25 + Math.random() * 75;
      pts.push(`${x.toFixed(1)}% ${y.toFixed(0)}%`);
      x -= 1.5 + Math.random() * 7;
    }
    pts.push(`0 ${(30 + Math.random() * 60).toFixed(0)}%`);
    stub.style.clipPath = `polygon(${pts.join(",")})`;
  };

  const tear = () => {
    if (document.hidden) return;
    if (calm.matches) { render(); return; }
    const old = sheet.cloneNode(true);
    old.removeAttribute("data-sheet");
    old.className = "pad-falling";
    old.style.clipPath = raggedTop();
    old.style.setProperty("--drift", `${10 + Math.random() * 40}px`);
    old.style.setProperty("--spin", `${18 + Math.random() * 22}deg`);
    const flap = document.createElement("span"); flap.className = "pad-flap"; old.appendChild(flap);
    sheet.parentNode.appendChild(old);
    sheet.style.setProperty("--frame", frame());                     // a fresh slip, its own border
    setTimeout(roughStub, 650);                                      // once it has torn free, a new stub remains
    render();                                                        // the slip underneath has the new number
    old.addEventListener("animationend", () => old.remove(), { once: true });
  };

  sheet.style.setProperty("--frame", frame());
  roughStub();
  render();
  setInterval(tear, TEAR_EVERY);
}
