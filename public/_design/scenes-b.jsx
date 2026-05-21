// scenes-b.jsx — heroes 05–08
const { useRef: useRefB, useEffect: useEffectB } = React;

const INK_B = '#0a0a0a';
const GREY_B = 'rgba(10,10,10,0.32)';
const GREY_B_FAINT = 'rgba(10,10,10,0.14)';
const RED_B = '#D7263D';

const CAPTION_B = {
  fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
  fontSize: 9,
  letterSpacing: '0.22em',
  textTransform: 'uppercase',
  fill: INK_B,
};

// ─────────────────────────────────────────────────────────────
// 05 — AURORA · 65°N
// Stack of phase-shifted hairlines, each a sum of three slow sines.
// Curtain effect from drifting amplitudes. Faint vertical "rays" suggest
// the magnetic-field structure.
// ─────────────────────────────────────────────────────────────
function SceneAurora() {
  const groupRef = useRefB(null);
  const raysRef = useRefB(null);
  const W = 720, H = 500;

  useEffectB(() => {
    const ns = 'http://www.w3.org/2000/svg';
    const N_LINES = 28;
    const top = 60, bottom = 360;
    const lines = [];
    for (let i = 0; i < N_LINES; i++) {
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('stroke', INK_B);
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke-width', '0.7');
      p.setAttribute('stroke-opacity', String(0.16 + 0.55 * (i / N_LINES)));
      groupRef.current.appendChild(p);
      const baseY = top + (i / (N_LINES - 1)) * (bottom - top);
      lines.push({
        el: p, baseY,
        freq1: 0.005 + Math.random() * 0.003,
        freq2: 0.009 + Math.random() * 0.004,
        freq3: 0.018 + Math.random() * 0.006,
        amp1: 18 + Math.random() * 10,
        amp2: 8 + Math.random() * 6,
        amp3: 3 + Math.random() * 3,
        phase: Math.random() * Math.PI * 2,
        speed: 0.05 + Math.random() * 0.08,
      });
    }

    // Faint vertical rays — sparsely populated.
    const N_RAYS = 9;
    const rays = [];
    for (let i = 0; i < N_RAYS; i++) {
      const ln = document.createElementNS(ns, 'line');
      ln.setAttribute('stroke', INK_B);
      ln.setAttribute('stroke-width', '0.6');
      ln.setAttribute('stroke-opacity', '0.10');
      raysRef.current.appendChild(ln);
      rays.push({ el: ln, x: 40 + Math.random() * (W - 80), drift: (Math.random() - 0.5) * 0.4 });
    }

    let raf;
    const t0 = performance.now();
    function frame(now) {
      const t = (now - t0) * 0.001;
      // Curtains
      for (const L of lines) {
        let d = '';
        const STEP = 4;
        for (let x = 0; x <= W; x += STEP) {
          const y = L.baseY
            + Math.sin(x * L.freq1 + t * L.speed + L.phase) * L.amp1
            + Math.sin(x * L.freq2 - t * L.speed * 1.4 + L.phase * 1.7) * L.amp2
            + Math.sin(x * L.freq3 + t * L.speed * 0.6) * L.amp3;
          d += (x === 0 ? 'M' : 'L') + x + ' ' + y.toFixed(2);
        }
        L.el.setAttribute('d', d);
      }
      // Rays follow the upper curtain envelope
      for (const r of rays) {
        const sway = Math.sin(t * 0.3 + r.x * 0.01) * 12;
        const yTop = top - 30 + sway;
        const yBot = bottom + 20 + sway * 0.4;
        r.el.setAttribute('x1', (r.x + r.drift * t * 4).toFixed(1));
        r.el.setAttribute('y1', yTop.toFixed(1));
        r.el.setAttribute('x2', (r.x + r.drift * t * 4 + sway * 0.3).toFixed(1));
        r.el.setAttribute('y2', yBot.toFixed(1));
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; if (raysRef.current) raysRef.current.innerHTML=''; };
  }, []);

  // Horizon line + single red tick at "magnetic north"
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <g ref={raysRef} />
      <g ref={groupRef} />
      {/* horizon */}
      <line x1={28} y1={H - 84} x2={W - 28} y2={H - 84} stroke={INK_B} strokeWidth="1" />
      <text x={28} y={36} style={{ ...CAPTION_B, fill: INK_B }}>05 · Aurora · 65°N</text>
      <text x={28} y={H - 84 - 8} style={{ ...CAPTION_B, fill: GREY_B }}>Horizon</text>
      {/* compass tick — magnetic north, the red moment */}
      <line x1={W * 0.74} y1={H - 84 - 6} x2={W * 0.74} y2={H - 84 + 6} stroke={RED_B} strokeWidth="1.5" />
      <text x={W * 0.74 + 8} y={H - 84 - 8} style={{ ...CAPTION_B, fill: RED_B }}>N (mag.)</text>
      <text x={28} y={H - 22} style={{ ...CAPTION_B, fill: GREY_B }}>Kp index · live · curtain form</text>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 06 — STAR TRAILS · POLARIS
// Stars at random (r, θ₀) revolve slowly around centre. Each is a tiny
// trailing arc — long-exposure feel. Polaris is the red point at centre.
// ─────────────────────────────────────────────────────────────
function SceneStarTrails() {
  const groupRef = useRefB(null);
  const W = 720, H = 500;

  useEffectB(() => {
    const cx = W / 2, cy = H / 2 + 30;
    const ns = 'http://www.w3.org/2000/svg';

    let seed = 4711;
    const rand = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;

    const stars = [];
    // Distribute stars in concentric annuli, with a few brighter ones.
    for (let i = 0; i < 180; i++) {
      const r = 26 + rand() * 320;
      const theta0 = rand() * Math.PI * 2;
      const arcSpan = 0.06 + (r / 400) * 0.18 + rand() * 0.04;
      const bright = rand() < 0.18;
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('stroke', INK_B);
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke-width', bright ? '1.1' : '0.6');
      p.setAttribute('stroke-opacity', bright ? '0.9' : '0.45');
      p.setAttribute('stroke-linecap', 'round');
      groupRef.current.appendChild(p);
      stars.push({ el: p, r, theta0, arcSpan, bright });
    }

    function arcPath(r, t0, t1) {
      const x0 = cx + r * Math.cos(t0), y0 = cy + r * Math.sin(t0);
      const x1 = cx + r * Math.cos(t1), y1 = cy + r * Math.sin(t1);
      const large = Math.abs(t1 - t0) > Math.PI ? 1 : 0;
      const sweep = t1 > t0 ? 1 : 0;
      return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 ${large} ${sweep} ${x1.toFixed(1)} ${y1.toFixed(1)}`;
    }

    let raf;
    const t0 = performance.now();
    const OMEGA = 0.05; // rad/s — quarter revolution per ~31s

    function frame(now) {
      const t = (now - t0) * 0.001;
      for (const s of stars) {
        const head = s.theta0 + OMEGA * t;
        const tail = head - s.arcSpan;
        // Skip stars fully outside the canvas bounding circle.
        if (s.r * Math.SQRT2 < 999) {
          s.el.setAttribute('d', arcPath(s.r, tail, head));
        }
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      {/* horizon tick line at bottom */}
      <line x1={28} y1={H - 36} x2={W - 28} y2={H - 36} stroke={INK_B} strokeWidth="1" />
      <g ref={groupRef} />
      {/* Polaris — the red moment, dead-centre */}
      <circle cx={W / 2} cy={H / 2 + 30} r="2.6" fill={RED_B} />
      <text x={W / 2 + 8} y={H / 2 + 27} style={{ ...CAPTION_B, fill: RED_B }}>Polaris</text>
      <text x={28} y={36} style={{ ...CAPTION_B, fill: INK_B }}>06 · Star trails</text>
      <text x={28} y={H - 16} style={{ ...CAPTION_B, fill: GREY_B }}>Long exposure · 64°N looking N</text>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 07 — DAYLIGHT · 55°N
// Polar plot: radius = daylight hours per day across a year (curve, slow
// continuous loop). A sweep hand pointing to "today" rotates one revolution
// per ~36s. Single red tick at winter solstice.
// ─────────────────────────────────────────────────────────────
function SceneDaylight() {
  const handRef = useRefB(null);
  const dotRef = useRefB(null);
  const dayLabelRef = useRefB(null);
  const W = 720, H = 500;

  // Build static daylight curve once.
  const cx = W / 2 - 40, cy = H / 2 + 6;
  const Rmin = 70, Rmax = 200;
  const LAT = 55 * Math.PI / 180;
  // Day-length approximation: D(n) = 24/π · acos(-tan(lat)·tan(δ))
  // with δ = 23.44° · sin(2π·(n+10)/365)
  function daylight(n) {
    const decl = 23.44 * Math.PI / 180 * Math.sin(2 * Math.PI * (n - 81) / 365);
    const ratio = -Math.tan(LAT) * Math.tan(decl);
    const cl = Math.max(-1, Math.min(1, ratio));
    return 24 / Math.PI * Math.acos(cl);
  }

  const days = 366;
  const points = [];
  for (let n = 0; n < days; n++) {
    const dl = daylight(n); // hours, 0..24
    const r = Rmin + (dl / 24) * (Rmax - Rmin);
    const theta = -Math.PI / 2 + (n / days) * 2 * Math.PI;
    points.push({ x: cx + r * Math.cos(theta), y: cy + r * Math.sin(theta), r, theta, dl });
  }
  const curveD = points.map((p, i) => (i ? 'L' : 'M') + p.x.toFixed(1) + ' ' + p.y.toFixed(1)).join('') + 'Z';

  // Day-of-year of solstices/equinoxes (approx).
  const markers = [
    { day: 80,  label: 'EQX' },   // vernal
    { day: 172, label: 'SOL' },   // summer solstice
    { day: 266, label: 'EQX' },   // autumnal
    { day: 355, label: 'SOL', red: true }, // WINTER solstice — red moment
  ];

  useEffectB(() => {
    let raf;
    const t0 = performance.now();
    const CYCLE = 36000;
    function frame(now) {
      const tDay = ((now - t0) % CYCLE) / CYCLE * days;
      const idx = Math.floor(tDay) % days;
      const p = points[idx];
      const theta = p.theta;
      const r = p.r;
      // Hand from centre to current radius
      handRef.current.setAttribute('x2', (cx + r * Math.cos(theta)).toFixed(1));
      handRef.current.setAttribute('y2', (cy + r * Math.sin(theta)).toFixed(1));
      dotRef.current.setAttribute('cx', (cx + r * Math.cos(theta)).toFixed(1));
      dotRef.current.setAttribute('cy', (cy + r * Math.sin(theta)).toFixed(1));
      // Label day length
      dayLabelRef.current.textContent = p.dl.toFixed(2).padStart(5, '0') + ' h';
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, []);

  // Generate month tick marks
  const monthTicks = [];
  const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
  const monthStart = [0,31,59,90,120,151,181,212,243,273,304,334];
  for (let m = 0; m < 12; m++) {
    const theta = -Math.PI / 2 + (monthStart[m] / days) * 2 * Math.PI;
    monthTicks.push({ theta, label: months[m] });
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      {/* Radial axis ticks every 6 h */}
      {[6, 12, 18, 24].map(h => {
        const r = Rmin + (h / 24) * (Rmax - Rmin);
        return (
          <g key={h}>
            <circle cx={cx} cy={cy} r={r} fill="none" stroke={GREY_B_FAINT} strokeWidth="1" />
            <text x={cx + 4} y={cy - r + 3} style={{ ...CAPTION_B, fill: GREY_B, fontSize: 8 }}>{h}h</text>
          </g>
        );
      })}
      {/* Month spokes */}
      {monthTicks.map((m, i) => {
        const x1 = cx + Rmin * Math.cos(m.theta);
        const y1 = cy + Rmin * Math.sin(m.theta);
        const x2 = cx + (Rmax + 14) * Math.cos(m.theta);
        const y2 = cy + (Rmax + 14) * Math.sin(m.theta);
        const tx = cx + (Rmax + 24) * Math.cos(m.theta);
        const ty = cy + (Rmax + 24) * Math.sin(m.theta);
        return (
          <g key={i}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={GREY_B_FAINT} strokeWidth="1" />
            <text x={tx} y={ty + 3} textAnchor="middle" style={{ ...CAPTION_B, fill: GREY_B, fontSize: 8 }}>{m.label}</text>
          </g>
        );
      })}
      {/* Daylight curve */}
      <path d={curveD} stroke={INK_B} strokeWidth="1.1" fill="none" />
      {/* Solstice/equinox markers */}
      {markers.map((m, i) => {
        const p = points[m.day];
        return (
          <g key={i}>
            <line x1={cx + (Rmax + 4) * Math.cos(p.theta)}
                  y1={cy + (Rmax + 4) * Math.sin(p.theta)}
                  x2={cx + (Rmax + 12) * Math.cos(p.theta)}
                  y2={cy + (Rmax + 12) * Math.sin(p.theta)}
                  stroke={m.red ? RED_B : INK_B} strokeWidth={m.red ? '1.8' : '1'} />
          </g>
        );
      })}
      {/* Sweep hand (centre → current day on curve) */}
      <line ref={handRef} x1={cx} y1={cy} stroke={INK_B} strokeWidth="1" />
      <circle ref={dotRef} r="2.2" fill={INK_B} />
      <circle cx={cx} cy={cy} r="2" fill={INK_B} />

      <text x={28} y={36} style={{ ...CAPTION_B, fill: INK_B }}>07 · Daylight · 55°N</text>
      <text x={28} y={H - 16} style={{ ...CAPTION_B, fill: GREY_B }}>Hours of sun per day · annual loop</text>
      {/* Right-side readout */}
      <text x={W - 28} y={64} textAnchor="end" style={{ ...CAPTION_B, fill: GREY_B }}>Today</text>
      <text ref={dayLabelRef} x={W - 28} y={88} textAnchor="end" style={{ fontFamily:'"Helvetica Neue",Helvetica,Arial,sans-serif', fontSize: 22, fontWeight: 300, fill: INK_B, letterSpacing: '-0.01em' }}>—</text>
      <text x={W - 28} y={H - 60} textAnchor="end" style={{ ...CAPTION_B, fill: RED_B }}>Winter solstice</text>
      <text x={W - 28} y={H - 44} textAnchor="end" style={{ ...CAPTION_B, fill: GREY_B }}>Dec 21 · 7.04 h</text>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// 08 — 49°N · POPULATION STIPPLE
// Dense stipple of dots above a red horizontal line (49th parallel),
// thinning northward, very sparse south of the line. Each dot has its own
// slow opacity sine, giving the field a faint, continuous shimmer.
// ─────────────────────────────────────────────────────────────
function SceneParallel() {
  const groupRef = useRefB(null);
  const W = 720, H = 500;

  useEffectB(() => {
    let seed = 88991;
    const rand = () => (seed = (seed * 1103515245 + 12345) % 2147483647) / 2147483647;
    const ns = 'http://www.w3.org/2000/svg';

    // 49th parallel line — about 72% down the canvas.
    const yParallel = H * 0.72;

    // Density profile: a long-tail above the parallel (most Canadians live
    // within ~300 km of the border), very sparse below.
    function densityAt(y) {
      if (y >= yParallel) {
        // Below parallel (south): nearly zero. Tiny scatter representing
        // border-straddle / Detroit-Windsor type density.
        return Math.exp(-(y - yParallel) * 0.04) * 0.04;
      }
      const d = yParallel - y; // px above parallel
      // Peak just above the line (~30 px above), exponential falloff with
      // distance northward.
      return Math.exp(-Math.pow((d - 30) / 110, 2)) * 1.0;
    }

    // Pre-place dots by rejection sampling.
    const dots = [];
    const TARGET = 900;
    let tries = 0;
    while (dots.length < TARGET && tries < TARGET * 12) {
      tries++;
      const x = 24 + rand() * (W - 48);
      const y = 64 + rand() * (H - 96);
      const dens = densityAt(y);
      if (rand() < dens) {
        const sz = 0.6 + rand() * 0.8;
        const c = document.createElementNS(ns, 'circle');
        c.setAttribute('cx', x.toFixed(1));
        c.setAttribute('cy', y.toFixed(1));
        c.setAttribute('r', sz.toFixed(2));
        c.setAttribute('fill', INK_B);
        groupRef.current.appendChild(c);
        dots.push({
          el: c,
          baseOp: 0.55 + rand() * 0.45,
          freq: 0.4 + rand() * 0.8,
          phase: rand() * Math.PI * 2,
        });
      }
    }

    let raf;
    const t0 = performance.now();
    function frame(now) {
      const t = (now - t0) * 0.001;
      for (const d of dots) {
        const o = d.baseOp * (0.55 + 0.45 * Math.sin(t * d.freq + d.phase));
        d.el.setAttribute('opacity', o.toFixed(2));
      }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; };
  }, []);

  const yParallel = H * 0.72;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <g ref={groupRef} />
      {/* the parallel — the single red edge */}
      <line x1={0} y1={yParallel} x2={W} y2={yParallel} stroke={RED_B} strokeWidth="1.2" />
      <text x={28} y={36} style={{ ...CAPTION_B, fill: INK_B }}>08 · 49th parallel</text>
      <text x={W - 28} y={yParallel - 8} textAnchor="end" style={{ ...CAPTION_B, fill: RED_B }}>49°00′ N</text>
      <text x={28} y={yParallel + 18} style={{ ...CAPTION_B, fill: GREY_B }}>US border</text>
      <text x={28} y={H - 16} style={{ ...CAPTION_B, fill: GREY_B }}>One dot ≈ population density · 2021</text>
    </svg>
  );
}

window.SceneAurora = SceneAurora;
window.SceneStarTrails = SceneStarTrails;
window.SceneDaylight = SceneDaylight;
window.SceneParallel = SceneParallel;
