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
    // written digit by digit: each a little tilted and off the line, as a hand writes
    num.innerHTML = [...group(km)].map((ch) => {
      const r = (Math.random() - .5) * 7, y = (Math.random() - .5) * 2.6;
      return `<span style="transform:translateY(${y.toFixed(1)}px) rotate(${r.toFixed(1)}deg)">${ch}</span>`;
    }).join("");
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

  // The tear, driven by the Web Animations API so every phase is explicit:
  //  1. the top-right corner rips and curls up        (0 – 0.5 s)
  //  2. the rip runs left along the top edge; the slip
  //     swings down from its last hold at the top-left (0.5 – 1.1 s)
  //  3. it tears free and falls under gravity, tumbling, until it is off the screen
  const tear = () => {
    if (document.hidden) return;
    if (calm.matches) { render(); return; }
    const old = sheet.cloneNode(true);
    old.removeAttribute("data-sheet");
    old.className = "pad-falling";
    old.style.clipPath = raggedTop();
    const flap = document.createElement("span"); flap.className = "pad-flap"; old.appendChild(flap);
    sheet.parentNode.appendChild(old);
    sheet.style.setProperty("--frame", frame());                     // a fresh slip, its own border
    render();                                                        // the slip underneath has the new number

    const fixed = getComputedStyle(pad).position === "fixed";
    const top = old.getBoundingClientRect().top;
    const fallTo = fixed ? innerHeight - top + 160 : 320;            // off the screen, or a short drop inline
    const drift = 25 + Math.random() * 45, spinEnd = 32 + Math.random() * 26;
    const T1 = 500, T2 = 1100, FALL = 1500;                         // ms
    const total = T2 + FALL;
    const frames = [
      { offset: 0, transform: "rotate(0deg)" },
      { offset: T1 / total * .45, transform: "rotate(1.5deg)" },
      { offset: T1 / total, transform: "rotate(5deg) translateY(1px)" },
      { offset: (T1 + (T2 - T1) * .6) / total, transform: "rotate(11deg) translateY(3px)" },
      { offset: T2 / total, transform: "rotate(14deg) translateY(5px)" },
    ];
    for (let k = 1; k <= 14; k++) {                                   // free fall: y = ½ g t²
      const f = k / 14, t = T2 + FALL * f;
      const y = 5 + fallTo * f * f, x = drift * f, r = 14 + (spinEnd - 14) * f, tilt = 34 * f;
      frames.push({ offset: t / total, transform: `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) rotate(${r.toFixed(1)}deg) rotateX(${tilt.toFixed(1)}deg)` });
    }
    old.animate(frames, { duration: total, easing: "linear", fill: "forwards" }).finished.then(() => old.remove());
    flap.animate([
      { transform: "scale(0)" },
      { transform: "scale(1.15) rotate(-4deg)", offset: T1 / total },
      { transform: "scale(1.5) rotate(-10deg)", offset: T2 / total },
      { transform: "scale(1.7) rotate(-16deg)" },
    ], { duration: total, fill: "forwards", easing: "ease-out" });
    setTimeout(roughStub, T2);                                       // once it has torn free, a new stub remains
  };

  sheet.style.setProperty("--frame", frame());
  roughStub();
  render();
  setInterval(tear, TEAR_EVERY);
}
