// Voyager 1's distance from Earth, computed in the browser.
//
// Voyager: heliocentric state from NASA/JPL Horizons (target -31, ecliptic J2000, km and km/s)
// at 2026-01-01 00:00 TDB. It coasts in a straight line now (the Sun's pull changes its speed
// by well under a metre per second per year), so position = r0 + v·t.
// Earth: the low-precision solar formula from the Astronomical Almanac (error ~0.01°),
// precessed to J2000. Together they match Horizons' geocentric distance to about 0.01%.
// To refresh the epoch, query Horizons for COMMAND=-31, CENTER=500@10, VECTORS, ECLIPTIC.

export const VOYAGER = {
  epochMs: Date.UTC(2026, 0, 1) - 69_000,              // TDB → UTC (≈69 s)
  r: [-4.762659739242758e9, -2.014761457045306e10, 1.457753551876435e10],
  v: [-2.072816913981589, -1.361111711012975e1, 9.834684958533998],
};

const AU = 149_597_870.7, DEG = Math.PI / 180;

export function earthHelio(ms) {
  const n = ms / 86_400_000 + 2440587.5 - 2451545.0;   // days since J2000
  const g = (357.528 + 0.9856003 * n) * DEG;
  const L = 280.460 + 0.9856474 * n;
  const lamDate = L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g);
  const lam = (lamDate - 1.396971 * n / 36525) * DEG;  // precess from date back to J2000
  const R = (1.00014 - 0.01671 * Math.cos(g) - 0.00014 * Math.cos(2 * g)) * AU;
  return [-R * Math.cos(lam), -R * Math.sin(lam), 0];  // Earth = −(Sun as seen from Earth)
}

export function voyagerFromEarthKm(ms = Date.now()) {
  const t = (ms - VOYAGER.epochMs) / 1000;
  const e = earthHelio(ms);
  const d = VOYAGER.r.map((r, i) => r + VOYAGER.v[i] * t - e[i]);
  return Math.hypot(...d);
}
