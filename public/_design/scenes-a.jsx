// scenes-a.jsx — heroes 01–04
// Each scene mounts an animation into an SVG/canvas via useEffect and tears
// it down on unmount. Hairlines, one red moment, no fills outside ink.

const { useRef, useEffect } = React;

const INK = '#0a0a0a';
const GREY = 'rgba(10,10,10,0.32)';
const GREY_FAINT = 'rgba(10,10,10,0.14)';
const RED = '#D7263D';

const CAPTION_STYLE = {
  fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
  fontSize: 9,
  letterSpacing: '0.22em',
  textTransform: 'uppercase',
  fill: INK,
};

function Caption({ x, y, anchor = 'start', dim = false, children }) {
  return (
    <text x={x} y={y} textAnchor={anchor}
      style={{ ...CAPTION_STYLE, fill: dim ? GREY : INK }}>
      {children}
    </text>
  );
}

// ─────────────────────────────────────────────────────────────
// 01 — ELEVATION FIELD
// Marching-squares contours over a slowly evolving sum-of-sines field.
// Red dot tracks the field maximum.
// ─────────────────────────────────────────────────────────────
function SceneElevation() {
  const groupRef = useRef(null);
  const peakRef = useRef(null);
  const W = 720, H = 500;

  useEffect(() => {
    const cols = 72, rows = 50;
    const cellW = W / cols, cellH = H / rows;
    const grid = new Float32Array((cols + 1) * (rows + 1));
    const NUM_LEVELS = 11;

    // Pre-allocate path elements — never recreate, just rewrite `d`.
    const ns = 'http://www.w3.org/2000/svg';
    const paths = [];
    for (let i = 0; i < NUM_LEVELS; i++) {
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('stroke', INK);
      p.setAttribute('stroke-width', i % 3 === 0 ? '1' : '0.7');
      p.setAttribute('stroke-opacity', i % 3 === 0 ? '0.9' : '0.55');
      p.setAttribute('fill', 'none');
      groupRef.current.appendChild(p);
      paths.push(p);
    }

    let raf;
    const t0 = performance.now();

    function frame(now) {
      const t = (now - t0) * 0.001;
      // Fill grid; track range and peak.
      let minV = Infinity, maxV = -Infinity;
      let peakI = 0, peakJ = 0;
      for (let j = 0; j <= rows; j++) {
        const v = j / rows;
        for (let i = 0; i <= cols; i++) {
          const u = i / cols;
          const f =
            Math.sin(u * 4.2 + t * 0.32) +
            Math.sin(v * 3.4 + t * 0.24) * 0.9 +
            Math.sin((u + v) * 5.0 - t * 0.18) * 0.6 +
            Math.cos(Math.hypot(u - 0.5, v - 0.42) * 7.0 + t * 0.14) * 0.55 +
            Math.sin(u * 8.0 - v * 3.0 + t * 0.21) * 0.35;
          grid[j * (cols + 1) + i] = f;
          if (f > maxV) { maxV = f; peakI = i; peakJ = j; }
          if (f < minV) minV = f;
        }
      }

      // Marching squares for each level.
      for (let n = 0; n < NUM_LEVELS; n++) {
        const level = minV + ((n + 0.5) / NUM_LEVELS) * (maxV - minV);
        let d = '';
        for (let j = 0; j < rows; j++) {
          for (let i = 0; i < cols; i++) {
            const a = grid[j * (cols + 1) + i];
            const b = grid[j * (cols + 1) + i + 1];
            const c = grid[(j + 1) * (cols + 1) + i + 1];
            const e = grid[(j + 1) * (cols + 1) + i];
            let idx = 0;
            if (a > level) idx |= 1;
            if (b > level) idx |= 2;
            if (c > level) idx |= 4;
            if (e > level) idx |= 8;
            if (idx === 0 || idx === 15) continue;
            const x = i * cellW, y = j * cellH;
            const ta = (level - a) / (b - a);
            const tb = (level - b) / (c - b);
            const tc = (level - e) / (c - e);
            const td = (level - a) / (e - a);
            const Ax = x + ta * cellW, Ay = y;
            const Bx = x + cellW,     By = y + tb * cellH;
            const Cx = x + tc * cellW, Cy = y + cellH;
            const Dx = x,              Dy = y + td * cellH;
            switch (idx) {
              case 1: case 14: d += `M${Ax.toFixed(1)} ${Ay.toFixed(1)}L${Dx.toFixed(1)} ${Dy.toFixed(1)}`; break;
              case 2: case 13: d += `M${Ax.toFixed(1)} ${Ay.toFixed(1)}L${Bx.toFixed(1)} ${By.toFixed(1)}`; break;
              case 3: case 12: d += `M${Dx.toFixed(1)} ${Dy.toFixed(1)}L${Bx.toFixed(1)} ${By.toFixed(1)}`; break;
              case 4: case 11: d += `M${Bx.toFixed(1)} ${By.toFixed(1)}L${Cx.toFixed(1)} ${Cy.toFixed(1)}`; break;
              case 5: d += `M${Ax.toFixed(1)} ${Ay.toFixed(1)}L${Dx.toFixed(1)} ${Dy.toFixed(1)}M${Bx.toFixed(1)} ${By.toFixed(1)}L${Cx.toFixed(1)} ${Cy.toFixed(1)}`; break;
              case 6: case 9: d += `M${Ax.toFixed(1)} ${Ay.toFixed(1)}L${Cx.toFixed(1)} ${Cy.toFixed(1)}`; break;
              case 7: case 8: d += `M${Dx.toFixed(1)} ${Dy.toFixed(1)}L${Cx.toFixed(1)} ${Cy.toFixed(1)}`; break;
              case 10: d += `M${Ax.toFixed(1)} ${Ay.toFixed(1)}L${Bx.toFixed(1)} ${By.toFixed(1)}M${Dx.toFixed(1)} ${Dy.toFixed(1)}L${Cx.toFixed(1)} ${Cy.toFixed(1)}`; break;
            }
          }
        }
        paths[n].setAttribute('d', d);
      }

      if (peakRef.current) {
        peakRef.current.setAttribute('cx', (peakI * cellW).toFixed(1));
        peakRef.current.setAttribute('cy', (peakJ * cellH).toFixed(1));
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <g ref={groupRef} />
      <circle ref={peakRef} r="2.5" fill={RED} />
      <Caption x={28} y={36}>01 · Elevation field</Caption>
      <Caption x={28} y={476} dim>Marching squares · 11 isolevels · peak ↗</Caption>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 02 — DRAINAGE BASIN
// A dendritic river network grown from an ocean outlet upstream.
// Each segment reveals in distance order via stroke-dashoffset.
// Loops every ~14s.
// ─────────────────────────────────────────────────────────────
function SceneWatershed() {
  const groupRef = useRef(null);
  const outletRef = useRef(null);
  const W = 720, H = 500;

  useEffect(() => {
    // Seeded RNG for a determinate (and good) tree every reload.
    let seed = 91247;
    const rand = () => (seed = (seed * 16807 + 19) % 2147483647) / 2147483647;

    const segs = [];
    function grow(x, y, ang, len, depth, t0, width) {
      const x2 = x + Math.cos(ang) * len;
      const y2 = y + Math.sin(ang) * len;
      if (x2 < 24 || x2 > W - 24 || y2 < 24 || y2 > H - 24) return;
      const dur = len * 0.035;
      segs.push({ x1: x, y1: y, x2, y2, t0, t1: t0 + dur, width });
      if (depth <= 0 || len < 7) return;
      const n = 1 + (rand() < 0.7 ? 1 : 0) + (rand() < 0.18 ? 1 : 0);
      const baseSpread = 0.55 + rand() * 0.25;
      for (let i = 0; i < n; i++) {
        const side = n === 1 ? (rand() < 0.5 ? -1 : 1) : (i === 0 ? -1 : (i === 1 ? 1 : (rand() - 0.5) * 1.8));
        const newAng = ang + side * baseSpread * (0.7 + rand() * 0.5);
        const newLen = len * (0.62 + rand() * 0.24);
        const delay = dur * (0.4 + rand() * 0.3);
        grow(x2, y2, newAng, newLen, depth - 1, t0 + delay, Math.max(0.4, width * 0.78));
      }
    }

    // Two trunk systems converging visually to one ocean outlet (right edge).
    const outX = W * 0.93, outY = H * 0.58;
    grow(outX, outY, Math.PI * 1.02, 95, 7, 0.0, 1.6);
    grow(outX, outY, Math.PI * 0.92, 75, 6, 0.4, 1.2);
    grow(outX, outY, Math.PI * 1.10, 65, 6, 0.7, 1.1);

    // Total duration → keep the reveal under ~9s.
    const total = segs.reduce((m, s) => Math.max(m, s.t1), 0);
    const reveal = 9.0;
    const speed = total / reveal;

    const ns = 'http://www.w3.org/2000/svg';
    segs.forEach(s => {
      const ln = document.createElementNS(ns, 'line');
      ln.setAttribute('x1', s.x1.toFixed(1));
      ln.setAttribute('y1', s.y1.toFixed(1));
      ln.setAttribute('x2', s.x2.toFixed(1));
      ln.setAttribute('y2', s.y2.toFixed(1));
      ln.setAttribute('stroke', INK);
      ln.setAttribute('stroke-width', s.width.toFixed(2));
      ln.setAttribute('stroke-linecap', 'round');
      const length = Math.hypot(s.x2 - s.x1, s.y2 - s.y1);
      ln.setAttribute('stroke-dasharray', length.toFixed(1));
      ln.setAttribute('stroke-dashoffset', length.toFixed(1));
      s._el = ln; s._len = length;
      groupRef.current.appendChild(ln);
    });

    let raf;
    const t0 = performance.now();
    const CYCLE = (reveal + 3.5) * 1000; // reveal + hold + fade
    function frame(now) {
      const elapsed = (now - t0) % CYCLE;
      const tSec = elapsed / 1000;
      // Fade-out over last 1.2s of the cycle.
      const fadeStart = CYCLE / 1000 - 1.2;
      const groupOpacity = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1.2) : 1;
      groupRef.current.setAttribute('opacity', groupOpacity.toFixed(3));
      if (outletRef.current) outletRef.current.setAttribute('opacity', groupOpacity.toFixed(3));

      for (const s of segs) {
        const local = (tSec * speed) - s.t0;
        const p = Math.max(0, Math.min(1, local / (s.t1 - s.t0)));
        s._el.setAttribute('stroke-dashoffset', (s._len * (1 - p)).toFixed(1));
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <g ref={groupRef} />
      <circle ref={outletRef} cx={W * 0.93} cy={H * 0.58} r="3.2" fill={RED} />
      {/* tiny tick suggesting coastline */}
      <line x1={W * 0.93 + 6} y1={H * 0.58 - 80} x2={W * 0.93 + 6} y2={H * 0.58 + 80} stroke={GREY_FAINT} strokeWidth="1" />
      <Caption x={28} y={36}>02 · Drainage basin</Caption>
      <Caption x={28} y={476} dim>Upstream trace · outlet to ocean ↘</Caption>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 03 — RAIL · MAREY SCHEDULE
// Time-distance graph (Tufte's favourite). Stations on Y, hours on X,
// diagonal trains. A vertical "now" cursor sweeps left→right; train dots
// mark each train's current position. One red corridor highlighted.
// ─────────────────────────────────────────────────────────────
function SceneMarey() {
  const dotsRef = useRef(null);
  const cursorRef = useRef(null);
  const labelRef = useRef(null);
  const W = 720, H = 500;

  // Layout
  const padL = 96, padR = 28, padT = 70, padB = 60;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  // Stations (Halifax → Vancouver, roughly weighted by rail distance).
  const stations = [
    { name: 'HALIFAX',   km: 0 },
    { name: 'MONTRÉAL',  km: 1346 },
    { name: 'TORONTO',   km: 1880 },
    { name: 'WINNIPEG',  km: 4040 },
    { name: 'SASKATOON', km: 4800 },
    { name: 'CALGARY',   km: 5450 },
    { name: 'VANCOUVER', km: 6050 },
  ];
  const kmMax = stations[stations.length - 1].km;
  const yFor = km => padT + (km / kmMax) * plotH;
  const xFor = hr => padL + (hr / 24) * plotW;

  // A small fixed schedule of trains. Each is one diagonal segment between
  // two stations, with a start hour and duration. tinted = highlighted route.
  const trains = [
    { a: 0, b: 6, t0:  1, dur: 22, dir: +1 }, // Halifax → Vancouver, slow freight
    { a: 6, b: 0, t0:  3, dur: 21, dir: -1 },
    { a: 0, b: 2, t0:  6, dur: 5,  dir: +1, hot: true }, // RED — Quebec corridor
    { a: 2, b: 0, t0: 14, dur: 5,  dir: -1, hot: true }, // RED return
    { a: 1, b: 3, t0:  4, dur: 9 },
    { a: 3, b: 1, t0: 10, dur: 9 },
    { a: 2, b: 5, t0:  7, dur: 11 },
    { a: 5, b: 2, t0:  9, dur: 11 },
    { a: 3, b: 6, t0: 12, dur: 7 },
    { a: 6, b: 3, t0:  5, dur: 8 },
    { a: 4, b: 6, t0: 15, dur: 4 },
    { a: 1, b: 2, t0:  8, dur: 2 },
    { a: 2, b: 1, t0: 18, dur: 2 },
  ];

  useEffect(() => {
    let raf;
    const t0 = performance.now();
    const CYCLE = 24000; // 24 seconds = 24 hours of schedule

    function frame(now) {
      const tHour = ((now - t0) % CYCLE) / CYCLE * 24;
      // Update cursor
      const cx = xFor(tHour);
      cursorRef.current.setAttribute('x1', cx);
      cursorRef.current.setAttribute('x2', cx);

      // Hour label
      const hh = Math.floor(tHour).toString().padStart(2, '0');
      const mm = Math.floor((tHour % 1) * 60).toString().padStart(2, '0');
      labelRef.current.textContent = `${hh}:${mm}`;
      labelRef.current.setAttribute('x', Math.min(W - padR - 32, cx + 8));

      // Update each train dot
      const g = dotsRef.current;
      while (g.firstChild) g.removeChild(g.firstChild);
      for (const tr of trains) {
        if (tHour < tr.t0 || tHour > tr.t0 + tr.dur) continue;
        const p = (tHour - tr.t0) / tr.dur;
        const kmA = stations[tr.a].km;
        const kmB = stations[tr.b].km;
        const cy = yFor(kmA + (kmB - kmA) * p);
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', cx);
        dot.setAttribute('cy', cy);
        dot.setAttribute('r', tr.hot ? '3' : '2.2');
        dot.setAttribute('fill', tr.hot ? RED : INK);
        g.appendChild(dot);
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, []);

  // Build static schedule lines + axes once via JSX.
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      {/* Hour grid */}
      {[0, 3, 6, 9, 12, 15, 18, 21, 24].map(h => (
        <g key={`h${h}`}>
          <line x1={xFor(h)} y1={padT} x2={xFor(h)} y2={padT + plotH} stroke={GREY_FAINT} strokeWidth="1" />
          <text x={xFor(h)} y={padT + plotH + 18} textAnchor="middle"
            style={{ ...CAPTION_STYLE, fill: GREY }}>{String(h).padStart(2,'0')}</text>
        </g>
      ))}
      {/* Station rows */}
      {stations.map((s, i) => (
        <g key={s.name}>
          <line x1={padL} y1={yFor(s.km)} x2={padL + plotW} y2={yFor(s.km)} stroke={GREY_FAINT} strokeWidth="1" />
          <text x={padL - 10} y={yFor(s.km) + 3} textAnchor="end"
            style={{ ...CAPTION_STYLE, fill: GREY, fontSize: 8.5 }}>{s.name}</text>
        </g>
      ))}
      {/* Schedule lines */}
      {trains.map((tr, i) => (
        <line key={i}
          x1={xFor(tr.t0)} y1={yFor(stations[tr.a].km)}
          x2={xFor(tr.t0 + tr.dur)} y2={yFor(stations[tr.b].km)}
          stroke={tr.hot ? RED : INK}
          strokeWidth={tr.hot ? '1.2' : '0.9'}
          strokeOpacity={tr.hot ? '0.9' : '0.7'} />
      ))}
      {/* Plot frame */}
      <rect x={padL} y={padT} width={plotW} height={plotH} fill="none" stroke={INK} strokeWidth="1" />
      {/* Sweep cursor */}
      <line ref={cursorRef} y1={padT} y2={padT + plotH} stroke={INK} strokeWidth="1" strokeDasharray="2 3" />
      <text ref={labelRef} y={padT - 8}
        style={{ ...CAPTION_STYLE, fill: INK }}>00:00</text>
      <g ref={dotsRef} />

      <Caption x={28} y={36}>03 · National rail · 24h schedule</Caption>
      <Caption x={padL} y={H - 16} dim>Time → · Distance ↓ · After Marey, 1885</Caption>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 04 — WIND · LIVE FLOW FIELD
// Vector-field of short streamlines. Base flow is westerly; mouse adds a
// rotational disturbance (low-pressure system). Lines redraw each frame.
// ─────────────────────────────────────────────────────────────
function SceneWind() {
  const svgRef = useRef(null);
  const W = 720, H = 500;

  useEffect(() => {
    const svg = svgRef.current;
    // Seed grid of streamline starts.
    const cols = 28, rows = 18;
    const stepX = W / cols, stepY = H / rows;

    let mouse = { x: W * 0.65, y: H * 0.45, active: false };

    const onMove = (e) => {
      const r = svg.getBoundingClientRect();
      mouse.x = (e.clientX - r.left) * (W / r.width);
      mouse.y = (e.clientY - r.top)  * (H / r.height);
      mouse.active = true;
    };
    const onLeave = () => { mouse.active = false; };
    svg.addEventListener('pointermove', onMove);
    svg.addEventListener('pointerleave', onLeave);

    // Pre-allocate one polyline per seed.
    const ns = 'http://www.w3.org/2000/svg';
    const g = document.createElementNS(ns, 'g');
    svg.appendChild(g);
    const lines = [];
    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols; i++) {
        const pl = document.createElementNS(ns, 'polyline');
        pl.setAttribute('fill', 'none');
        pl.setAttribute('stroke', INK);
        pl.setAttribute('stroke-width', '0.7');
        pl.setAttribute('stroke-opacity', '0.85');
        g.appendChild(pl);
        lines.push({ el: pl, sx: (i + 0.5) * stepX, sy: (j + 0.5) * stepY });
      }
    }
    // Endpoint markers — tiny "head" dots indicating direction.
    const heads = document.createElementNS(ns, 'g');
    svg.appendChild(heads);

    // Eased mouse so the field doesn't jitter on quick moves.
    let smoothed = { x: mouse.x, y: mouse.y, w: 0 };
    let raf;
    const t0 = performance.now();

    function field(x, y, t) {
      // Base westerly + slow vertical undulation.
      let vx = 1.0;
      let vy = 0.18 * Math.sin(x * 0.012 + t * 0.4) + 0.10 * Math.sin(y * 0.008 - t * 0.3);
      // Rotational disturbance around smoothed mouse position.
      if (smoothed.w > 0.01) {
        const dx = x - smoothed.x, dy = y - smoothed.y;
        const r2 = dx * dx + dy * dy + 6000;
        const k = 32000 / r2 * smoothed.w;
        // Counter-clockwise curl (cyclone in N. hemisphere)
        vx += -dy * k * 0.012;
        vy +=  dx * k * 0.012;
      }
      return [vx, vy];
    }

    function frame(now) {
      const t = (now - t0) * 0.001;
      // Smooth mouse activation
      const targetW = mouse.active ? 1 : 0;
      smoothed.w += (targetW - smoothed.w) * 0.06;
      smoothed.x += (mouse.x - smoothed.x) * 0.18;
      smoothed.y += (mouse.y - smoothed.y) * 0.18;

      // Clear heads
      while (heads.firstChild) heads.removeChild(heads.firstChild);

      for (const L of lines) {
        let x = L.sx, y = L.sy;
        const pts = [x.toFixed(1) + ',' + y.toFixed(1)];
        const STEPS = 9;
        const STEP_LEN = 4.5;
        for (let s = 0; s < STEPS; s++) {
          const [vx, vy] = field(x, y, t);
          const mag = Math.hypot(vx, vy) || 1;
          x += (vx / mag) * STEP_LEN;
          y += (vy / mag) * STEP_LEN;
          if (x < -10 || x > W + 10 || y < -10 || y > H + 10) break;
          pts.push(x.toFixed(1) + ',' + y.toFixed(1));
        }
        L.el.setAttribute('points', pts.join(' '));
      }

      // Red marker: the eye of the disturbance (only when mouse is in).
      if (smoothed.w > 0.05) {
        const eye = document.createElementNS(ns, 'circle');
        eye.setAttribute('cx', smoothed.x.toFixed(1));
        eye.setAttribute('cy', smoothed.y.toFixed(1));
        eye.setAttribute('r', '3');
        eye.setAttribute('fill', RED);
        eye.setAttribute('opacity', smoothed.w.toFixed(2));
        heads.appendChild(eye);
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      svg.removeEventListener('pointermove', onMove);
      svg.removeEventListener('pointerleave', onLeave);
      while (svg.firstChild && svg.firstChild !== svg.querySelector('text')) svg.removeChild(svg.firstChild);
    };
  }, []);

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe', cursor: 'crosshair' }}>
      <text x={28} y={36} style={{ ...CAPTION_STYLE, fill: INK }}>04 · Prevailing wind · interactive</text>
      <text x={28} y={476} style={{ ...CAPTION_STYLE, fill: GREY }}>Move pointer to seed a low ↻</text>
    </svg>
  );
}

window.SceneElevation = SceneElevation;
window.SceneWatershed = SceneWatershed;
window.SceneMarey = SceneMarey;
window.SceneWind = SceneWind;
