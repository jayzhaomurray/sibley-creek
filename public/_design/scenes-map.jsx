// scenes-map.jsx — Map iterations on the drainage-basin direction.
// 5 scenes (A–E) sharing a hand-tuned Canada geography in 720×500 space.

const { useRef: useMRef, useEffect: useMEffect } = React;

const M_INK   = '#0a0a0a';
const M_GREY  = 'rgba(10,10,10,0.55)';
const M_MID   = 'rgba(10,10,10,0.32)';
const M_FAINT = 'rgba(10,10,10,0.12)';
const M_RED   = '#D7263D';
const M_CAP   = {
  fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
  fontSize: 9,
  letterSpacing: '0.22em',
  textTransform: 'uppercase',
  fill: M_INK,
};

// ═════════════════════════════════════════════════════════
// CANADA GEOGRAPHY — pixel coordinates in a 720×500 frame.
// Hand-tuned to read as Canada without literal GIS accuracy.
// ═════════════════════════════════════════════════════════

// Outer perimeter, clockwise from NW Yukon.
const CA_OUTLINE = [
  [50,100],[140,88],[240,75],[360,70],[480,70],
  [560,85],[620,115],[640,155],[680,200],[685,270],
  [695,320],[680,340],[650,355],[625,380],[605,380],
  [575,365],[555,380],[530,360],[495,375],[460,385],
  [420,400],[360,405],[280,395],[180,395],[80,395],
  [55,385],[40,330],[30,240],[35,175],[42,130],[50,100],
];
// Hudson Bay inner outline (separate polygon).
const HUDSON = [
  [470,175],[510,165],[550,195],[560,235],
  [530,275],[490,290],[450,285],[440,240],
  [450,200],[470,175],
];

const CITIES = [
  { id:'van', name:'VANCOUVER',  x: 90, y:355, tier:1 },
  { id:'vic', name:'VICTORIA',   x: 70, y:370, tier:3 },
  { id:'wh',  name:'WHITEHORSE', x: 75, y:148, tier:3 },
  { id:'yk',  name:'YELLOWKNIFE',x:200, y:198, tier:3 },
  { id:'iqa', name:'IQALUIT',    x:540, y:175, tier:3 },
  { id:'edm', name:'EDMONTON',   x:195, y:305, tier:2 },
  { id:'cal', name:'CALGARY',    x:200, y:325, tier:1 },
  { id:'sas', name:'SASKATOON',  x:260, y:305, tier:3 },
  { id:'reg', name:'REGINA',     x:275, y:330, tier:3 },
  { id:'win', name:'WINNIPEG',   x:340, y:340, tier:2 },
  { id:'tbk', name:'THUNDER BAY',x:415, y:355, tier:3 },
  { id:'sud', name:'SUDBURY',    x:485, y:360, tier:3 },
  { id:'tor', name:'TORONTO',    x:495, y:385, tier:1 },
  { id:'ott', name:'OTTAWA',     x:525, y:370, tier:2 },
  { id:'mtl', name:'MONTRÉAL',   x:545, y:365, tier:1 },
  { id:'qc',  name:'QUÉBEC',     x:575, y:350, tier:3 },
  { id:'hfx', name:'HALIFAX',    x:610, y:382, tier:2 },
  { id:'sjn', name:"ST. JOHN'S", x:680, y:355, tier:3 },
];
const CITY = Object.fromEntries(CITIES.map(c => [c.id, c]));

const RAIL_TRUNK   = ['van','cal','sas','win','tbk','sud','tor','mtl','hfx'];
const RAIL_BRANCH  = [
  ['cal','edm'], ['win','reg'], ['tor','ott'], ['mtl','qc'],
  ['qc','hfx'], ['hfx','sjn'], ['edm','yk'], ['wh','yk'],
];

const RIVERS = [
  // St. Lawrence: Toronto → Montreal → Quebec → Gulf
  [[495,385],[525,375],[545,365],[575,350],[610,345],[650,345]],
  // Mackenzie: Yellowknife → Beaufort Sea
  [[200,198],[195,160],[180,120],[185, 90]],
  // Yukon
  [[ 75,148],[ 50,130],[ 30,100]],
  // Fraser: Calgary → Vancouver (rough)
  [[200,325],[170,340],[140,355],[100,360],[ 90,355]],
  // Saskatchewan
  [[200,325],[260,305],[340,340]],
];

// ── tiny shared utilities ─────────────────────────────────
function pathD(pts, closed) {
  let d = '';
  for (let i = 0; i < pts.length; i++) d += (i ? 'L' : 'M') + pts[i][0] + ' ' + pts[i][1];
  return closed ? d + 'Z' : d;
}
function ss(t) { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); }
function tierR(t) { return t === 1 ? 3.4 : t === 2 ? 2.4 : 1.7; }
const NS = 'http://www.w3.org/2000/svg';

// ═════════════════════════════════════════════════════════
// A · WATERSHED MAP
// Multiple dendritic trees grow inland from real Canadian river mouths.
// Faint coastline strokes on first as a backdrop.
// ═════════════════════════════════════════════════════════
function SceneMapWatershed() {
  const groupRef  = useMRef(null);
  const coastRef  = useMRef(null);
  const hudsonRef = useMRef(null);
  const dotRef    = useMRef(null);
  const ringRef   = useMRef(null);

  useMEffect(() => {
    let seed = 20251;
    const rand = () => (seed = (seed * 16807 + 19) % 2147483647) / 2147483647;

    // [x, y, inland-angle, trunk length, depth, time offset]
    const outlets = [
      { x: 650, y: 345, ang: Math.PI * 1.00, len: 90,  depth: 6, t0: 0.0 }, // St. Lawrence
      { x: 545, y: 265, ang: Math.PI * 0.55, len: 70,  depth: 6, t0: 0.6 }, // Hudson Bay west
      { x: 475, y: 285, ang: Math.PI * 0.40, len: 60,  depth: 6, t0: 1.1 }, // Hudson Bay south
      { x: 185, y:  95, ang: Math.PI * 0.50, len: 110, depth: 6, t0: 0.3 }, // Mackenzie / Beaufort
      { x:  40, y: 320, ang: Math.PI * 1.85, len: 80,  depth: 5, t0: 1.6 }, // Pacific / Fraser
    ];

    const segs = [];
    function grow(x, y, ang, len, depth, t0, width) {
      const x2 = x + Math.cos(ang) * len;
      const y2 = y + Math.sin(ang) * len;
      if (x2 < 20 || x2 > 700 || y2 < 60 || y2 > 470) return;
      const dur = len * 0.035;
      segs.push({ x1: x, y1: y, x2, y2, t0, t1: t0 + dur, width });
      if (depth <= 0 || len < 7) return;
      const n = 1 + (rand() < 0.7 ? 1 : 0) + (rand() < 0.18 ? 1 : 0);
      const spread = 0.45 + rand() * 0.25;
      for (let i = 0; i < n; i++) {
        const side = n === 1 ? (rand() < 0.5 ? -1 : 1) : (i === 0 ? -1 : (i === 1 ? 1 : (rand() - 0.5) * 1.8));
        const newAng = ang + side * spread * (0.7 + rand() * 0.5);
        const newLen = len * (0.62 + rand() * 0.24);
        const delay  = dur * (0.4 + rand() * 0.3);
        grow(x2, y2, newAng, newLen, depth - 1, t0 + delay, Math.max(0.4, width * 0.78));
      }
    }
    outlets.forEach(o => grow(o.x, o.y, o.ang, o.len, o.depth, o.t0, 1.4));

    const total  = segs.reduce((m, s) => Math.max(m, s.t1), 0);
    const reveal = 8.5;
    const speed  = total / reveal;

    segs.forEach(s => {
      const ln = document.createElementNS(NS, 'line');
      ln.setAttribute('x1', s.x1.toFixed(1));
      ln.setAttribute('y1', s.y1.toFixed(1));
      ln.setAttribute('x2', s.x2.toFixed(1));
      ln.setAttribute('y2', s.y2.toFixed(1));
      ln.setAttribute('stroke', M_INK);
      ln.setAttribute('stroke-width', s.width.toFixed(2));
      ln.setAttribute('stroke-linecap', 'round');
      const L = Math.hypot(s.x2 - s.x1, s.y2 - s.y1);
      ln.setAttribute('stroke-dasharray', L.toFixed(1));
      ln.setAttribute('stroke-dashoffset', L.toFixed(1));
      s._el = ln; s._len = L;
      groupRef.current.appendChild(ln);
    });

    const coastL  = coastRef.current.getTotalLength();
    const hudsonL = hudsonRef.current.getTotalLength();
    coastRef.current.setAttribute('stroke-dasharray', coastL);
    hudsonRef.current.setAttribute('stroke-dasharray', hudsonL);

    let raf;
    const t0 = performance.now();
    const CYCLE = 13000;
    function frame(now) {
      const tSec = ((now - t0) % CYCLE) / 1000;
      const fadeStart = CYCLE / 1000 - 1.2;
      const g = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1.2) : 1;

      const coastP  = ss(tSec / 1.8);
      const hudsonP = ss((tSec - 1) / 1.8);
      coastRef.current.setAttribute('stroke-dashoffset',  (coastL  * (1 - coastP)).toFixed(1));
      hudsonRef.current.setAttribute('stroke-dashoffset', (hudsonL * (1 - hudsonP)).toFixed(1));

      const watT = tSec - 1.5;
      for (const s of segs) {
        const local = watT * speed - s.t0;
        const p = Math.max(0, Math.min(1, local / (s.t1 - s.t0)));
        s._el.setAttribute('stroke-dashoffset', (s._len * (1 - p)).toFixed(1));
      }

      groupRef.current.setAttribute('opacity', g.toFixed(3));
      coastRef.current.setAttribute('opacity',  g.toFixed(3));
      hudsonRef.current.setAttribute('opacity', g.toFixed(3));
      // Red outlet — gentle pulse
      const pulse = 0.5 + 0.5 * Math.sin(tSec * 1.6);
      dotRef.current.setAttribute('opacity', g.toFixed(3));
      ringRef.current.setAttribute('r', (5 + pulse * 4).toFixed(2));
      ringRef.current.setAttribute('opacity', ((0.35 - pulse * 0.3) * g).toFixed(3));

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (groupRef.current) groupRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox="0 0 720 500" width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <path ref={coastRef}  d={pathD(CA_OUTLINE, true)} fill="none" stroke={M_MID} strokeWidth="1" />
      <path ref={hudsonRef} d={pathD(HUDSON, true)}     fill="none" stroke={M_FAINT} strokeWidth="1" />
      <g ref={groupRef} />
      <circle ref={ringRef} cx={650} cy={345} r="5" fill="none" stroke={M_RED} strokeWidth="0.8" />
      <circle ref={dotRef}  cx={650} cy={345} r="3"  fill={M_RED} />
      <text x={28} y={36}  style={{ ...M_CAP, fill: M_INK }}>A · Drainage basin · five outlets</text>
      <text x={28} y={476} style={{ ...M_CAP, fill: M_MID }}>Gulf of St. Lawrence · Hudson · Beaufort · Pacific</text>
    </svg>
  );
}

// ═════════════════════════════════════════════════════════
// B · TRANSCONTINENTAL
// Single rail trunk grows Halifax → Vancouver. Cities snap on as the line
// reaches them. After Vancouver, branches sprout to secondary cities.
// ═════════════════════════════════════════════════════════
function SceneMapRail() {
  const coastRef    = useMRef(null);
  const hudsonRef   = useMRef(null);
  const citiesRef   = useMRef(null);
  const trunkRef    = useMRef(null);
  const branchesRef = useMRef(null);
  const redRingRef  = useMRef(null);
  const redDotRef   = useMRef(null);

  // Trunk in EAST→WEST order so the line starts in Halifax.
  const trunkSeq = [...RAIL_TRUNK].reverse();
  const trunkPts = trunkSeq.map(id => [CITY[id].x, CITY[id].y]);
  // Cumulative arc lengths between consecutive nodes (for city-arrival timing).
  const segLens = [];
  let trunkTotal = 0;
  for (let i = 1; i < trunkPts.length; i++) {
    const L = Math.hypot(trunkPts[i][0] - trunkPts[i-1][0], trunkPts[i][1] - trunkPts[i-1][1]);
    segLens.push(L); trunkTotal += L;
  }
  const cityArriveT = [0];
  let acc = 0;
  for (let i = 0; i < segLens.length; i++) { acc += segLens[i]; cityArriveT.push(acc / trunkTotal); }
  // map trunkSeq[i] → arrival time in [0,1]

  useMEffect(() => {
    // Coastline
    const coastL  = coastRef.current.getTotalLength();
    const hudsonL = hudsonRef.current.getTotalLength();
    coastRef.current.setAttribute('stroke-dasharray',  coastL);
    hudsonRef.current.setAttribute('stroke-dasharray', hudsonL);
    // Trunk
    trunkRef.current.setAttribute('d', pathD(trunkPts, false));
    const trunkL = trunkRef.current.getTotalLength();
    trunkRef.current.setAttribute('stroke-dasharray',  trunkL);
    trunkRef.current.setAttribute('stroke-dashoffset', trunkL);
    // Branches
    const branches = [];
    RAIL_BRANCH.forEach(([a, b]) => {
      const A = CITY[a], B = CITY[b];
      const ln = document.createElementNS(NS, 'line');
      ln.setAttribute('x1', A.x); ln.setAttribute('y1', A.y);
      ln.setAttribute('x2', B.x); ln.setAttribute('y2', B.y);
      ln.setAttribute('stroke', M_INK);
      ln.setAttribute('stroke-width', '0.9');
      ln.setAttribute('stroke-linecap', 'round');
      const L = Math.hypot(B.x - A.x, B.y - A.y);
      ln.setAttribute('stroke-dasharray', L);
      ln.setAttribute('stroke-dashoffset', L);
      branchesRef.current.appendChild(ln);
      branches.push({ el: ln, L });
    });

    // City dots — set initial opacity 0, then per-frame fade by arrival.
    const cityNodes = Array.from(citiesRef.current.children);
    cityNodes.forEach(n => n.setAttribute('opacity', '0'));

    let raf;
    const t0 = performance.now();
    const CYCLE = 14000;
    function frame(now) {
      const tSec = ((now - t0) % CYCLE) / 1000;
      const fadeStart = CYCLE / 1000 - 1;
      const g = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1) : 1;

      // Coast 0–1.8s, hudson 0.6–2.4s
      const coastP  = ss(tSec / 1.8);
      const hudsonP = ss((tSec - 0.6) / 1.8);
      coastRef.current.setAttribute('stroke-dashoffset',  (coastL  * (1 - coastP)).toFixed(1));
      hudsonRef.current.setAttribute('stroke-dashoffset', (hudsonL * (1 - hudsonP)).toFixed(1));

      // Trunk draws 2 → 9s (7s)
      const trunkP = ss((tSec - 2) / 7);
      trunkRef.current.setAttribute('stroke-dashoffset', (trunkL * (1 - trunkP)).toFixed(1));

      // Cities along trunk light up as the line passes them.
      cityNodes.forEach((node) => {
        const cid = node.getAttribute('data-city');
        const idx = trunkSeq.indexOf(cid);
        let op = 0;
        if (idx >= 0) {
          // along trunk
          const arrive = cityArriveT[idx];
          op = ss((trunkP - arrive) / 0.05 + 0.5);
        } else {
          // not on trunk — fades in after trunk completes
          op = ss((tSec - 9.5) / 1.2);
        }
        node.setAttribute('opacity', (op * g).toFixed(2));
      });

      // Branches reveal 9.2–11.5s, in order
      branches.forEach((b, i) => {
        const start = 9.2 + i * 0.20;
        const p = ss((tSec - start) / 1.0);
        b.el.setAttribute('stroke-dashoffset', (b.L * (1 - p)).toFixed(1));
      });

      // Apply global fade
      coastRef.current.setAttribute('opacity',     (coastP  * g).toFixed(2));
      hudsonRef.current.setAttribute('opacity',    (hudsonP * g).toFixed(2));
      trunkRef.current.setAttribute('opacity',     g.toFixed(2));
      branchesRef.current.setAttribute('opacity',  g.toFixed(2));

      // Red ring at Vancouver — arrives at trunk completion (~9s)
      const redP = ss((tSec - 8.8) / 0.8);
      const pulse = 0.5 + 0.5 * Math.sin((tSec - 8.8) * 2.4);
      redRingRef.current.setAttribute('opacity', ((0.35 - pulse * 0.3) * redP * g).toFixed(2));
      redRingRef.current.setAttribute('r', (5 + pulse * 4).toFixed(2));
      redDotRef.current.setAttribute('opacity',  (redP * g).toFixed(2));

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (branchesRef.current) branchesRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox="0 0 720 500" width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <path ref={coastRef}  d={pathD(CA_OUTLINE, true)} fill="none" stroke={M_MID}   strokeWidth="1" />
      <path ref={hudsonRef} d={pathD(HUDSON, true)}     fill="none" stroke={M_FAINT} strokeWidth="1" />
      <g ref={citiesRef}>
        {CITIES.map(c => (
          <circle key={c.id} data-city={c.id} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK} opacity="0" />
        ))}
      </g>
      <g ref={branchesRef} />
      <path ref={trunkRef} d="" fill="none" stroke={M_INK} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <circle ref={redRingRef} cx={CITY.van.x} cy={CITY.van.y} r="5" fill="none" stroke={M_RED} strokeWidth="0.9" opacity="0" />
      <circle ref={redDotRef}  cx={CITY.van.x} cy={CITY.van.y} r="3"  fill={M_RED} opacity="0" />
      <text x={28} y={36}  style={{ ...M_CAP, fill: M_INK }}>B · Transcontinental · Halifax → Vancouver</text>
      <text x={28} y={476} style={{ ...M_CAP, fill: M_MID }}>Trunk first · then branches · 14 s loop</text>
    </svg>
  );
}
// ═════════════════════════════════════════════════════════
// C · CITY TRIANGULATION
// Cities appear as dots; nearest-neighbour edges grow into a mesh.
// The country's shape emerges from the network alone — coastline arrives
// last as the envelope.
// ═════════════════════════════════════════════════════════
function SceneMapTriangulation() {
  const dotsRef   = useMRef(null);
  const edgesRef  = useMRef(null);
  const coastRef  = useMRef(null);
  const redRef    = useMRef(null);

  // Precompute K-nearest-neighbour edge list once.
  const K = 4;
  const edges = [];
  const seen = new Set();
  for (let i = 0; i < CITIES.length; i++) {
    const a = CITIES[i];
    const dists = CITIES
      .map((b, j) => ({ d: j === i ? Infinity : Math.hypot(a.x - b.x, a.y - b.y), j }))
      .sort((x, y) => x.d - y.d);
    for (let k = 0; k < K; k++) {
      const j = dists[k].j;
      const key = i < j ? `${i}-${j}` : `${j}-${i}`;
      if (!seen.has(key)) { seen.add(key); edges.push({ i, j, d: dists[k].d }); }
    }
  }
  edges.sort((a, b) => a.d - b.d);

  useMEffect(() => {
    // City fade-in order (random by seeded shuffle for determinism)
    let seed = 5318;
    const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const order = CITIES.map((_, i) => i);
    for (let i = order.length - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [order[i], order[j]] = [order[j], order[i]];
    }

    // Set up edges
    edges.forEach(e => {
      const A = CITIES[e.i], B = CITIES[e.j];
      const ln = document.createElementNS(NS, 'line');
      ln.setAttribute('x1', A.x); ln.setAttribute('y1', A.y);
      ln.setAttribute('x2', B.x); ln.setAttribute('y2', B.y);
      ln.setAttribute('stroke', M_INK);
      ln.setAttribute('stroke-width', '0.8');
      ln.setAttribute('stroke-opacity', '0.75');
      const L = Math.hypot(B.x - A.x, B.y - A.y);
      ln.setAttribute('stroke-dasharray', L);
      ln.setAttribute('stroke-dashoffset', L);
      e._el = ln; e._L = L;
      edgesRef.current.appendChild(ln);
    });
    const coastL = coastRef.current.getTotalLength();
    coastRef.current.setAttribute('stroke-dasharray', coastL);
    coastRef.current.setAttribute('stroke-dashoffset', coastL);

    const dotNodes = Array.from(dotsRef.current.children);
    dotNodes.forEach(n => n.setAttribute('opacity', '0'));

    let raf;
    const t0 = performance.now();
    const CYCLE = 12000;
    function frame(now) {
      const tSec = ((now - t0) % CYCLE) / 1000;
      const fadeStart = CYCLE / 1000 - 1.0;
      const g = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1.0) : 1;

      // Cities appear 0–2.5s in shuffled order.
      dotNodes.forEach(n => {
        const i = parseInt(n.getAttribute('data-i'), 10);
        const rank = order.indexOf(i);
        const start = 0 + rank * (2.5 / dotNodes.length);
        const p = ss((tSec - start) / 0.4);
        n.setAttribute('opacity', (p * g).toFixed(2));
      });

      // Edges reveal 3.0–8.0s, shortest first.
      edges.forEach((e, i) => {
        const start = 3.0 + i * (5.0 / edges.length);
        const p = ss((tSec - start) / 0.7);
        e._el.setAttribute('stroke-dashoffset', (e._L * (1 - p)).toFixed(1));
        e._el.setAttribute('stroke-opacity', (0.65 * p * g).toFixed(2));
      });

      // Coast appears 8–10s as envelope.
      const coastP = ss((tSec - 8) / 2);
      coastRef.current.setAttribute('stroke-dashoffset', (coastL * (1 - coastP)).toFixed(1));
      coastRef.current.setAttribute('opacity', (coastP * 0.7 * g).toFixed(2));

      // Red moment: Winnipeg as the "centre of gravity" of the mesh.
      const redP = ss((tSec - 2.4) / 0.5);
      redRef.current.setAttribute('opacity', (redP * g).toFixed(2));

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); if (edgesRef.current) edgesRef.current.innerHTML = ''; };
  }, []);

  return (
    <svg viewBox="0 0 720 500" width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <path ref={coastRef} d={pathD(CA_OUTLINE, true)} fill="none" stroke={M_MID} strokeWidth="1" opacity="0" />
      <g ref={edgesRef} />
      <g ref={dotsRef}>
        {CITIES.map((c, i) => (
          <circle key={c.id} data-i={i} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK} opacity="0" />
        ))}
      </g>
      <circle ref={redRef} cx={CITY.win.x} cy={CITY.win.y} r="4.4" fill="none" stroke={M_RED} strokeWidth="1.4" opacity="0" />
      <text x={28} y={36}  style={{ ...M_CAP, fill: M_INK }}>C · Cities · network triangulation</text>
      <text x={28} y={476} style={{ ...M_CAP, fill: M_MID }}>Each city → 4 nearest · envelope last</text>
    </svg>
  );
}

// ═════════════════════════════════════════════════════════
// D · SKELETON → FLESH
// Sequential additive build. Pure reveal — every layer arrives in order.
// 0–2.5  coastline
// 2.5–4   Hudson Bay
// 4–6     rivers
// 6–7.5   cities
// 7.5–10  rail trunk
// 10–11.5 branches
// 11.5–14 hold
// 14–15   fade
// ═════════════════════════════════════════════════════════
function SceneMapSkeleton() {
  const coastRef    = useMRef(null);
  const hudsonRef   = useMRef(null);
  const riversRef   = useMRef(null);
  const citiesRef   = useMRef(null);
  const trunkRef    = useMRef(null);
  const branchesRef = useMRef(null);
  const ottRedRef   = useMRef(null);

  useMEffect(() => {
    const coastL  = coastRef.current.getTotalLength();
    const hudsonL = hudsonRef.current.getTotalLength();
    coastRef.current.setAttribute('stroke-dasharray',  coastL);
    coastRef.current.setAttribute('stroke-dashoffset', coastL);
    hudsonRef.current.setAttribute('stroke-dasharray', hudsonL);
    hudsonRef.current.setAttribute('stroke-dashoffset',hudsonL);

    // Rivers
    const rivers = [];
    RIVERS.forEach(pts => {
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', pathD(pts, false));
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', M_INK);
      p.setAttribute('stroke-width', '0.9');
      p.setAttribute('stroke-opacity', '0.65');
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-linejoin','round');
      riversRef.current.appendChild(p);
      const L = p.getTotalLength();
      p.setAttribute('stroke-dasharray', L);
      p.setAttribute('stroke-dashoffset', L);
      rivers.push({ el: p, L });
    });

    // Trunk
    const trunkPts = RAIL_TRUNK.map(id => [CITY[id].x, CITY[id].y]);
    trunkRef.current.setAttribute('d', pathD(trunkPts, false));
    const trunkL = trunkRef.current.getTotalLength();
    trunkRef.current.setAttribute('stroke-dasharray',  trunkL);
    trunkRef.current.setAttribute('stroke-dashoffset', trunkL);

    // Branches
    const branches = [];
    RAIL_BRANCH.forEach(([a, b]) => {
      const A = CITY[a], B = CITY[b];
      const ln = document.createElementNS(NS, 'line');
      ln.setAttribute('x1', A.x); ln.setAttribute('y1', A.y);
      ln.setAttribute('x2', B.x); ln.setAttribute('y2', B.y);
      ln.setAttribute('stroke', M_INK);
      ln.setAttribute('stroke-width', '0.85');
      ln.setAttribute('stroke-linecap', 'round');
      const L = Math.hypot(B.x - A.x, B.y - A.y);
      ln.setAttribute('stroke-dasharray', L);
      ln.setAttribute('stroke-dashoffset', L);
      branchesRef.current.appendChild(ln);
      branches.push({ el: ln, L });
    });

    const dotNodes = Array.from(citiesRef.current.children);
    dotNodes.forEach(n => n.setAttribute('opacity', '0'));

    let raf;
    const t0 = performance.now();
    const CYCLE = 15000;
    function frame(now) {
      const tSec = ((now - t0) % CYCLE) / 1000;
      const fadeStart = CYCLE / 1000 - 1;
      const g = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1) : 1;

      const coastP  = ss(tSec / 2.5);
      const hudsonP = ss((tSec - 2.5) / 1.5);
      coastRef.current.setAttribute('stroke-dashoffset',  (coastL  * (1 - coastP)).toFixed(1));
      hudsonRef.current.setAttribute('stroke-dashoffset', (hudsonL * (1 - hudsonP)).toFixed(1));

      // Rivers 4–6, sequential
      rivers.forEach((r, i) => {
        const start = 4 + i * (2 / rivers.length);
        const p = ss((tSec - start) / 1.0);
        r.el.setAttribute('stroke-dashoffset', (r.L * (1 - p)).toFixed(1));
      });

      // Cities 6–7.5, sequential
      dotNodes.forEach((n, i) => {
        const start = 6 + i * (1.5 / dotNodes.length);
        const p = ss((tSec - start) / 0.4);
        n.setAttribute('opacity', (p * g).toFixed(2));
      });

      // Trunk 7.5–10
      const trunkP = ss((tSec - 7.5) / 2.5);
      trunkRef.current.setAttribute('stroke-dashoffset', (trunkL * (1 - trunkP)).toFixed(1));

      // Branches 10–11.5
      branches.forEach((b, i) => {
        const start = 10 + i * (1.5 / branches.length);
        const p = ss((tSec - start) / 0.6);
        b.el.setAttribute('stroke-dashoffset', (b.L * (1 - p)).toFixed(1));
      });

      // Apply globals
      coastRef.current.setAttribute('opacity',    (coastP  * g).toFixed(2));
      hudsonRef.current.setAttribute('opacity',   (hudsonP * g).toFixed(2));
      riversRef.current.setAttribute('opacity',   g.toFixed(2));
      trunkRef.current.setAttribute('opacity',    g.toFixed(2));
      branchesRef.current.setAttribute('opacity', g.toFixed(2));

      // Red ring on Ottawa appears at hold start (capital)
      const redP = ss((tSec - 11.5) / 0.6);
      const pulse = 0.5 + 0.5 * Math.sin((tSec - 11.5) * 2);
      ottRedRef.current.setAttribute('opacity', ((0.4 - pulse * 0.3) * redP * g).toFixed(2));
      ottRedRef.current.setAttribute('r', (4.5 + pulse * 3).toFixed(2));

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      if (riversRef.current) riversRef.current.innerHTML = '';
      if (branchesRef.current) branchesRef.current.innerHTML = '';
    };
  }, []);

  return (
    <svg viewBox="0 0 720 500" width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <path ref={coastRef}  d={pathD(CA_OUTLINE, true)} fill="none" stroke={M_INK}   strokeWidth="1.1" opacity="0" />
      <path ref={hudsonRef} d={pathD(HUDSON, true)}     fill="none" stroke={M_MID}   strokeWidth="0.9" opacity="0" />
      <g ref={riversRef} opacity="0" />
      <g ref={citiesRef}>
        {CITIES.map(c => <circle key={c.id} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK} opacity="0" />)}
      </g>
      <path ref={trunkRef} d="" fill="none" stroke={M_INK} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
      <g ref={branchesRef} />
      <circle ref={ottRedRef} cx={CITY.ott.x} cy={CITY.ott.y} r="4.5" fill="none" stroke={M_RED} strokeWidth="1.2" opacity="0" />
      <text x={28} y={36}  style={{ ...M_CAP, fill: M_INK }}>D · Skeleton → flesh</text>
      <text x={28} y={476} style={{ ...M_CAP, fill: M_MID }}>Coast · Hudson · rivers · cities · rail · branches</text>
    </svg>
  );
}

// ═════════════════════════════════════════════════════════
// E · KNOW WHAT TO IGNORE
// Map fades in fully detailed, then layers peel away in reverse priority
// until only the essentials remain — a nod to the brand tagline.
// 0–1.2   fade in everything
// 1.2–2.4 hold full
// 2.4–6.5 progressive deletion
// 6.5–9   hold essentials (one red trunk edge)
// 9–10    fade
// ═════════════════════════════════════════════════════════
function SceneMapIgnore() {
  const coastRef    = useMRef(null);
  const hudsonRef   = useMRef(null);
  const riversRef   = useMRef(null);
  const branchesRef = useMRef(null);
  const tinyRef     = useMRef(null);   // tier-3 cities
  const midRef      = useMRef(null);   // tier-2 cities
  const majorRef    = useMRef(null);   // tier-1 cities
  const trunkRef    = useMRef(null);
  const trunkRedRef = useMRef(null);

  useMEffect(() => {
    const coastL  = coastRef.current.getTotalLength();
    const hudsonL = hudsonRef.current.getTotalLength();

    // Rivers
    const rivers = [];
    RIVERS.forEach(pts => {
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', pathD(pts, false));
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', M_INK);
      p.setAttribute('stroke-width', '0.85');
      p.setAttribute('stroke-opacity', '0.6');
      p.setAttribute('stroke-linecap','round');
      riversRef.current.appendChild(p);
      rivers.push(p);
    });

    // Trunk (full)
    const trunkPts = RAIL_TRUNK.map(id => [CITY[id].x, CITY[id].y]);
    const fullD = pathD(trunkPts, false);
    trunkRef.current.setAttribute('d', fullD);
    // Red sub-trunk: Toronto–Montreal corridor (the essentials)
    trunkRedRef.current.setAttribute('d', pathD([[CITY.tor.x, CITY.tor.y], [CITY.mtl.x, CITY.mtl.y]], false));

    // Branches (full)
    RAIL_BRANCH.forEach(([a, b]) => {
      const A = CITY[a], B = CITY[b];
      const ln = document.createElementNS(NS, 'line');
      ln.setAttribute('x1', A.x); ln.setAttribute('y1', A.y);
      ln.setAttribute('x2', B.x); ln.setAttribute('y2', B.y);
      ln.setAttribute('stroke', M_INK);
      ln.setAttribute('stroke-width', '0.85');
      ln.setAttribute('stroke-linecap','round');
      branchesRef.current.appendChild(ln);
    });

    let raf;
    const t0 = performance.now();
    const CYCLE = 10000;
    function frame(now) {
      const tSec = ((now - t0) % CYCLE) / 1000;
      const fadeStart = CYCLE / 1000 - 1;
      const g = tSec > fadeStart ? Math.max(0, 1 - (tSec - fadeStart) / 1) : 1;

      // Fade-in 0–1.2s for every layer except the red.
      const fIn = ss(tSec / 1.2);

      // Removal schedule. Each layer fades from full→0 over its own window.
      const decay = (start, dur) => 1 - ss((tSec - start) / dur);

      const branchesOp = decay(2.4, 0.9);
      const riversOp   = decay(3.4, 0.9);
      const hudsonOp   = decay(4.2, 0.7);
      const tinyOp     = decay(4.6, 0.9);
      const midOp      = decay(5.5, 0.9);
      const trunkOp    = decay(6.2, 0.6); // dims, not gone
      // Coast stays (light grey backdrop)
      const coastBaseOp = 1;

      coastRef.current.setAttribute('opacity',    (coastBaseOp * fIn * g).toFixed(2));
      hudsonRef.current.setAttribute('opacity',   (hudsonOp * fIn * g).toFixed(2));
      riversRef.current.setAttribute('opacity',   (riversOp * fIn * g).toFixed(2));
      branchesRef.current.setAttribute('opacity', (branchesOp * fIn * g).toFixed(2));
      tinyRef.current.setAttribute('opacity',     (tinyOp * fIn * g).toFixed(2));
      midRef.current.setAttribute('opacity',      (midOp * fIn * g).toFixed(2));
      majorRef.current.setAttribute('opacity',    (fIn * g).toFixed(2));
      // Main trunk dims to faint, red corridor appears
      const trunkBase = Math.max(0.15, trunkOp);
      trunkRef.current.setAttribute('opacity', (trunkBase * fIn * g).toFixed(2));
      const redP = ss((tSec - 6.4) / 0.6);
      trunkRedRef.current.setAttribute('opacity', (redP * g).toFixed(2));

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      if (riversRef.current) riversRef.current.innerHTML = '';
      if (branchesRef.current) branchesRef.current.innerHTML = '';
    };
  }, []);

  const tier1Cities = CITIES.filter(c => c.tier === 1);
  const tier2Cities = CITIES.filter(c => c.tier === 2);
  const tier3Cities = CITIES.filter(c => c.tier === 3);

  return (
    <svg viewBox="0 0 720 500" width="100%" height="100%" style={{ display: 'block', background: '#fefefe' }}>
      <path ref={coastRef}  d={pathD(CA_OUTLINE, true)} fill="none" stroke={M_MID}   strokeWidth="1" />
      <path ref={hudsonRef} d={pathD(HUDSON, true)}     fill="none" stroke={M_MID}   strokeWidth="0.9" />
      <g ref={riversRef}    opacity="0" />
      <g ref={branchesRef}  opacity="0" />
      <path ref={trunkRef}  d="" fill="none" stroke={M_INK} strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round" />
      <path ref={trunkRedRef} d="" fill="none" stroke={M_RED} strokeWidth="1.8" strokeLinecap="round" opacity="0" />
      <g ref={tinyRef}  opacity="0">{tier3Cities.map(c => <circle key={c.id} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK}/>)}</g>
      <g ref={midRef}   opacity="0">{tier2Cities.map(c => <circle key={c.id} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK}/>)}</g>
      <g ref={majorRef} opacity="0">{tier1Cities.map(c => <circle key={c.id} cx={c.x} cy={c.y} r={tierR(c.tier)} fill={M_INK}/>)}</g>
      <text x={28} y={36}  style={{ ...M_CAP, fill: M_INK }}>E · Seeing clearly · know what to ignore</text>
      <text x={28} y={476} style={{ ...M_CAP, fill: M_MID }}>Every layer falls away · the corridor remains</text>
    </svg>
  );
}

window.SceneMapWatershed      = SceneMapWatershed;
window.SceneMapRail           = SceneMapRail;
window.SceneMapTriangulation  = SceneMapTriangulation;
window.SceneMapSkeleton       = SceneMapSkeleton;
window.SceneMapIgnore         = SceneMapIgnore;
