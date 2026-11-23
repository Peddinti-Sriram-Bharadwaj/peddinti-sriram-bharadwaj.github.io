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
    const pts = []; let y = 7;
    for (let x = 0; x <= 100; x += 2.5 + Math.random() * 3) {
      y = Math.max(2, Math.min(14, y + (Math.random() - .5) * 5));
      pts.push(`${x.toFixed(1)}% ${y.toFixed(1)}%`);
    }
    pts.push(`100% ${y.toFixed(1)}%`, "100% 100%", "0% 100%");
    return `polygon(${pts.join(",")})`;
  };

  const tear = () => {
    if (document.hidden) return;
    if (calm.matches) { render(); return; }
    const old = sheet.cloneNode(true);
    old.removeAttribute("data-sheet");
    old.classList.add("pad-falling");
    old.style.clipPath = raggedTop();
    old.style.setProperty("--drift", `${(Math.random() * 2 - 1) * 26}px`);
    old.style.setProperty("--spin", `${(Math.random() < .5 ? -1 : 1) * (10 + Math.random() * 16)}deg`);
    sheet.parentNode.appendChild(old);
    render();                                                        // the slip underneath has the new number
    old.addEventListener("animationend", () => old.remove(), { once: true });
  };

  render();
  setInterval(tear, TEAR_EVERY);
}
