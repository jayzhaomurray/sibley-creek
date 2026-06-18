/**
 * engine.mjs -- deterministic prose-template renderer (mechanical markets
 * prose, ratified 2026-06-09).
 *
 * Why this exists
 * ---------------
 * Hand-written markets prose went four weeks stale against daily charts and
 * shipped false claims ("oil still over $100" at $92). Reader-facing markets
 * text is therefore a FUNCTION OF THE DATA: templates authored once by the
 * writer (through the three review gates), bound to panel_data series and
 * re-rendered deterministically on every build. No LLM in the daily loop.
 *
 * Structural guarantees
 * ---------------------
 * 1. A sentence whose variant predicates all evaluate false DROPS silently --
 *    the template can never assert a claim the data does not currently
 *    support.
 * 2. A `required: true` surface, or any `-callout-` surface, that renders
 *    empty FAILS THE BUILD -- silence on a load-bearing slot is as bad as a
 *    false claim.
 * 3. All template parsing/validation happens at LOAD time with clear
 *    messages: unknown series alias, unparseable predicate or interpolation,
 *    unknown format name, missing `when: "true"` terminator on a required
 *    surface. A bad template never half-renders.
 * 4. The final observation of a series is treated as suspect (stepped back
 *    one row) when its date equals the panel's generatedAt date and
 *    generatedAt is before 21:30 UTC -- belt-and-suspenders on top of the
 *    pipeline-side intraday-partial guard in pipeline/fetch/yahoo.py.
 *
 * Consumers
 * ---------
 * - Astro frontmatter (build time) via src/lib/prose/index.ts
 * - scripts/render_prose.mjs (render-dump tool for review gates/debugging)
 * - scripts/test_prose_renderer.mjs (self-checking unit tests, run in CI)
 *
 * This file is plain ESM JavaScript (not TS) because it is shared verbatim
 * between the Vite/Astro world and bare `node scripts/*.mjs` -- no
 * transpile step on either side. Types live in engine.d.mts.
 *
 * DSL contract (FIXED -- extend only additively; the writer authors against
 * exactly this):
 *   Expressions: latest(s), at(s, "T-N"), delta(s, N), pct_change(s, N),
 *     max(s, N), min(s, N), spread(a, b), bps(x), abs(x), latest_date(s).
 *     N is in observations (trading days; 5 ~ 1w, 21 ~ 1m).
 *     max/min cover the last N observations INCLUDING the latest.
 *   Predicates: < <= > >= == between expressions and numeric literals,
 *     between(x, lo, hi) inclusive, && || !, parens, literal true.
 *   Interpolation: {expr|fmt} with the named formats in FORMATS below.
 *   Evaluation: variants in order, first TRUE predicate wins.
 *   (Additive extension in this implementation: arithmetic + - * / and
 *   unary minus inside expressions; numeric literals may be negative.)
 */

// --------------------------------------------------------------------------- #
// Errors
// --------------------------------------------------------------------------- #

export class ProseTemplateError extends Error {
  constructor(message) {
    super(`[prose-template] ${message}`);
    this.name = "ProseTemplateError";
  }
}

export class ProseRenderError extends Error {
  constructor(message) {
    super(`[prose-render] ${message}`);
    this.name = "ProseRenderError";
  }
}

/** Internal: data unavailable for an expression (insufficient history,
 *  zero denominator). In a predicate this skips the variant (with a
 *  warning); in interpolation text it escalates to ProseRenderError. */
class EvalUnavailableError extends Error {}

// --------------------------------------------------------------------------- #
// Tokenizer
// --------------------------------------------------------------------------- #

const TWO_CHAR_OPS = ["<=", ">=", "==", "&&", "||"];
const ONE_CHAR_OPS = ["<", ">", "!", "(", ")", ",", "+", "-", "*", "/"];

function tokenize(src) {
  const tokens = [];
  let i = 0;
  while (i < src.length) {
    const ch = src[i];
    if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
      i++;
      continue;
    }
    const two = src.slice(i, i + 2);
    if (TWO_CHAR_OPS.includes(two)) {
      tokens.push({ type: "op", value: two, pos: i });
      i += 2;
      continue;
    }
    if (ONE_CHAR_OPS.includes(ch)) {
      tokens.push({ type: "op", value: ch, pos: i });
      i += 1;
      continue;
    }
    if (ch === '"' || ch === "'") {
      const quote = ch;
      let j = i + 1;
      while (j < src.length && src[j] !== quote) j++;
      if (j >= src.length) {
        throw new ProseTemplateError(`unterminated string literal in "${src}"`);
      }
      tokens.push({ type: "str", value: src.slice(i + 1, j), pos: i });
      i = j + 1;
      continue;
    }
    if (/[0-9]/.test(ch) || (ch === "." && /[0-9]/.test(src[i + 1] ?? ""))) {
      const m = src.slice(i).match(/^[0-9]*\.?[0-9]+/);
      tokens.push({ type: "num", value: parseFloat(m[0]), pos: i });
      i += m[0].length;
      continue;
    }
    if (/[A-Za-z_]/.test(ch)) {
      const m = src.slice(i).match(/^[A-Za-z_][A-Za-z0-9_]*/);
      tokens.push({ type: "ident", value: m[0], pos: i });
      i += m[0].length;
      continue;
    }
    throw new ProseTemplateError(`unexpected character "${ch}" at position ${i} in "${src}"`);
  }
  tokens.push({ type: "eof", value: null, pos: src.length });
  return tokens;
}

// --------------------------------------------------------------------------- #
// Parser (recursive descent)
// --------------------------------------------------------------------------- #

const FUNCTIONS = {
  latest:      { args: ["series"], returns: "num" },
  at:          { args: ["series", "tref"], returns: "num" },
  delta:       { args: ["series", "numlit"], returns: "num" },
  pct_change:  { args: ["series", "numlit"], returns: "num" },
  max:         { args: ["series", "numlit"], returns: "num" },
  min:         { args: ["series", "numlit"], returns: "num" },
  spread:      { args: ["series", "series"], returns: "num" },
  bps:         { args: ["num"], returns: "num" },
  abs:         { args: ["num"], returns: "num" },
  between:     { args: ["num", "numlit", "numlit"], returns: "bool" },
  latest_date: { args: ["series"], returns: "date" },
};

function parseExpression(src) {
  const tokens = tokenize(src);
  let pos = 0;
  const peek = () => tokens[pos];
  const next = () => tokens[pos++];
  const expectOp = (v) => {
    const t = next();
    if (t.type !== "op" || t.value !== v) {
      throw new ProseTemplateError(`expected "${v}" at position ${t.pos} in "${src}"`);
    }
  };

  function parseOr() {
    let left = parseAnd();
    while (peek().type === "op" && peek().value === "||") {
      next();
      left = { t: "or", l: left, r: parseAnd() };
    }
    return left;
  }
  function parseAnd() {
    let left = parseNot();
    while (peek().type === "op" && peek().value === "&&") {
      next();
      left = { t: "and", l: left, r: parseNot() };
    }
    return left;
  }
  function parseNot() {
    if (peek().type === "op" && peek().value === "!") {
      next();
      return { t: "not", e: parseNot() };
    }
    return parseCmp();
  }
  function parseCmp() {
    const left = parseAdd();
    const t = peek();
    if (t.type === "op" && ["<", "<=", ">", ">=", "=="].includes(t.value)) {
      next();
      return { t: "cmp", op: t.value, l: left, r: parseAdd() };
    }
    return left;
  }
  function parseAdd() {
    let left = parseMul();
    while (peek().type === "op" && (peek().value === "+" || peek().value === "-")) {
      const op = next().value;
      left = { t: "arith", op, l: left, r: parseMul() };
    }
    return left;
  }
  function parseMul() {
    let left = parseUnary();
    while (peek().type === "op" && (peek().value === "*" || peek().value === "/")) {
      const op = next().value;
      left = { t: "arith", op, l: left, r: parseUnary() };
    }
    return left;
  }
  function parseUnary() {
    if (peek().type === "op" && peek().value === "-") {
      next();
      return { t: "neg", e: parseUnary() };
    }
    return parsePrimary();
  }
  function parsePrimary() {
    const t = next();
    if (t.type === "num") return { t: "num", v: t.value };
    if (t.type === "str") return { t: "str", v: t.value };
    if (t.type === "ident") {
      if (t.value === "true") return { t: "bool", v: true };
      if (t.value === "false") return { t: "bool", v: false };
      if (peek().type === "op" && peek().value === "(") {
        next(); // consume "("
        const args = [];
        if (!(peek().type === "op" && peek().value === ")")) {
          args.push(parseOr());
          while (peek().type === "op" && peek().value === ",") {
            next();
            args.push(parseOr());
          }
        }
        expectOp(")");
        return { t: "call", name: t.value, args };
      }
      return { t: "series", alias: t.value };
    }
    if (t.type === "op" && t.value === "(") {
      const inner = parseOr();
      expectOp(")");
      return inner;
    }
    throw new ProseTemplateError(
      `unexpected token "${t.value ?? "end of input"}" at position ${t.pos} in "${src}"`
    );
  }

  const ast = parseOr();
  if (peek().type !== "eof") {
    throw new ProseTemplateError(
      `trailing input after expression at position ${peek().pos} in "${src}"`
    );
  }
  return ast;
}

// --------------------------------------------------------------------------- #
// Static type check (load time)
// --------------------------------------------------------------------------- #

function isNumLiteral(node) {
  return node.t === "num" || (node.t === "neg" && node.e.t === "num");
}

/** Returns "num" | "bool" | "date". Throws ProseTemplateError on any misuse. */
function typecheck(node, slotAliases, src) {
  const fail = (msg) => {
    throw new ProseTemplateError(`${msg} in "${src}"`);
  };
  switch (node.t) {
    case "num":
      return "num";
    case "bool":
      return "bool";
    case "str":
      fail("string literal only allowed as the second argument of at()");
      break;
    case "series":
      fail(
        `bare series reference "${node.alias}" -- series may only appear inside a function, e.g. latest(${node.alias})`
      );
      break;
    case "call": {
      const spec = FUNCTIONS[node.name];
      if (!spec) fail(`unknown function "${node.name}"`);
      if (node.args.length !== spec.args.length) {
        fail(`${node.name}() takes ${spec.args.length} argument(s), got ${node.args.length}`);
      }
      spec.args.forEach((kind, i) => {
        const arg = node.args[i];
        if (kind === "series") {
          if (arg.t !== "series") {
            fail(`argument ${i + 1} of ${node.name}() must be a series alias`);
          }
          if (!slotAliases.has(arg.alias)) {
            fail(
              `unknown series alias "${arg.alias}" (declared slots: ${[...slotAliases].join(", ")})`
            );
          }
        } else if (kind === "tref") {
          if (arg.t !== "str" || !/^T-\d+$/.test(arg.v)) {
            fail(`argument ${i + 1} of ${node.name}() must be a string of the form "T-N"`);
          }
        } else if (kind === "numlit") {
          if (!isNumLiteral(arg)) {
            fail(`argument ${i + 1} of ${node.name}() must be a numeric literal`);
          }
        } else {
          // "num": any numeric expression
          if (typecheck(arg, slotAliases, src) !== "num") {
            fail(`argument ${i + 1} of ${node.name}() must be numeric`);
          }
        }
      });
      return spec.returns;
    }
    case "not":
      if (typecheck(node.e, slotAliases, src) !== "bool") fail("! requires a boolean operand");
      return "bool";
    case "and":
    case "or":
      if (
        typecheck(node.l, slotAliases, src) !== "bool" ||
        typecheck(node.r, slotAliases, src) !== "bool"
      ) {
        fail(`${node.t === "and" ? "&&" : "||"} requires boolean operands`);
      }
      return "bool";
    case "cmp":
      if (
        typecheck(node.l, slotAliases, src) !== "num" ||
        typecheck(node.r, slotAliases, src) !== "num"
      ) {
        fail(`comparison "${node.op}" requires numeric operands`);
      }
      return "bool";
    case "arith":
      if (
        typecheck(node.l, slotAliases, src) !== "num" ||
        typecheck(node.r, slotAliases, src) !== "num"
      ) {
        fail(`arithmetic "${node.op}" requires numeric operands`);
      }
      return "num";
    case "neg":
      if (typecheck(node.e, slotAliases, src) !== "num") fail("unary minus requires a numeric operand");
      return "num";
    default:
      fail(`internal: unknown AST node "${node.t}"`);
  }
}

function isLiteralTrue(ast) {
  return ast.t === "bool" && ast.v === true;
}

// --------------------------------------------------------------------------- #
// Evaluator
// --------------------------------------------------------------------------- #

function numLiteralValue(node) {
  return node.t === "neg" ? -node.e.v : node.v;
}

function seriesObs(ctx, alias) {
  const s = ctx.series.get(alias);
  if (!s) throw new ProseRenderError(`internal: series alias "${alias}" missing from context`);
  if (s.values.length === 0) {
    throw new EvalUnavailableError(`series "${alias}" has no completed observations`);
  }
  return s;
}

function obsAt(ctx, alias, back) {
  const s = seriesObs(ctx, alias);
  const idx = s.values.length - 1 - back;
  if (idx < 0) {
    throw new EvalUnavailableError(
      `series "${alias}": needs ${back + 1} observations, has ${s.values.length}`
    );
  }
  return s.values[idx];
}

function finite(v, what) {
  if (!Number.isFinite(v)) {
    throw new EvalUnavailableError(`${what} produced a non-finite value`);
  }
  return v;
}

function evalNode(node, ctx) {
  switch (node.t) {
    case "num":
      return node.v;
    case "bool":
      return node.v;
    case "call": {
      const a = node.args;
      switch (node.name) {
        case "latest":
          return obsAt(ctx, a[0].alias, 0);
        case "at": {
          const back = parseInt(a[1].v.slice(2), 10);
          return obsAt(ctx, a[0].alias, back);
        }
        case "delta": {
          const n = numLiteralValue(a[1]);
          return obsAt(ctx, a[0].alias, 0) - obsAt(ctx, a[0].alias, n);
        }
        case "pct_change": {
          const n = numLiteralValue(a[1]);
          const base = obsAt(ctx, a[0].alias, n);
          return finite(100 * (obsAt(ctx, a[0].alias, 0) / base - 1), "pct_change");
        }
        case "max":
        case "min": {
          const n = numLiteralValue(a[1]);
          const s = seriesObs(ctx, a[0].alias);
          if (n < 1 || n > s.values.length) {
            throw new EvalUnavailableError(
              `${node.name}("${a[0].alias}", ${n}): needs ${n} observations, has ${s.values.length}`
            );
          }
          const window = s.values.slice(s.values.length - n);
          return node.name === "max" ? Math.max(...window) : Math.min(...window);
        }
        case "spread":
          return obsAt(ctx, a[0].alias, 0) - obsAt(ctx, a[1].alias, 0);
        case "bps":
          return evalNode(a[0], ctx) * 100;
        case "abs":
          return Math.abs(evalNode(a[0], ctx));
        case "between": {
          const x = evalNode(a[0], ctx);
          return x >= numLiteralValue(a[1]) && x <= numLiteralValue(a[2]);
        }
        case "latest_date": {
          const s = seriesObs(ctx, a[0].alias);
          return s.dates[s.dates.length - 1];
        }
        default:
          throw new ProseRenderError(`internal: unknown function "${node.name}"`);
      }
    }
    case "not":
      return !evalNode(node.e, ctx);
    case "and":
      return evalNode(node.l, ctx) && evalNode(node.r, ctx);
    case "or":
      return evalNode(node.l, ctx) || evalNode(node.r, ctx);
    case "cmp": {
      const l = evalNode(node.l, ctx);
      const r = evalNode(node.r, ctx);
      switch (node.op) {
        case "<": return l < r;
        case "<=": return l <= r;
        case ">": return l > r;
        case ">=": return l >= r;
        case "==": return l === r;
        default: throw new ProseRenderError(`internal: unknown comparison "${node.op}"`);
      }
    }
    case "arith": {
      const l = evalNode(node.l, ctx);
      const r = evalNode(node.r, ctx);
      let v;
      switch (node.op) {
        case "+": v = l + r; break;
        case "-": v = l - r; break;
        case "*": v = l * r; break;
        case "/": v = l / r; break;
        default: throw new ProseRenderError(`internal: unknown operator "${node.op}"`);
      }
      return finite(v, `"${node.op}"`);
    }
    case "neg":
      return -evalNode(node.e, ctx);
    default:
      throw new ProseRenderError(`internal: unknown AST node "${node.t}"`);
  }
}

// --------------------------------------------------------------------------- #
// Formats
// --------------------------------------------------------------------------- #

const MINUS = "−"; // U+2212 MINUS SIGN (canon for signed deltas)
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** Round half away from zero (avoids toFixed's float artifacts). */
function roundTo(v, d) {
  const f = 10 ** d;
  return (Math.sign(v) || 1) * Math.round(Math.abs(v) * f) / f;
}

function fixedStr(v, d) {
  const r = roundTo(v, d);
  const s = Math.abs(r).toFixed(d);
  return (r < 0 ? "-" : "") + s;
}

function groupedStr(v, d) {
  const r = roundTo(v, d);
  const [intPart, fracPart] = Math.abs(r).toFixed(d).split(".");
  const g = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return (r < 0 ? "-" : "") + g + (fracPart ? "." + fracPart : "");
}

function parseISODate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso));
  if (!m) throw new ProseRenderError(`latest_date returned a non-ISO date "${iso}"`);
  return { y: parseInt(m[1], 10), m: parseInt(m[2], 10), d: parseInt(m[3], 10) };
}

export const FORMATS = {
  fx4:        { kind: "num", render: (v) => fixedStr(v, 4) },
  usd:        { kind: "num", render: (v) => (roundTo(v, 2) < 0 ? "-" : "") + "US$" + Math.abs(roundTo(v, 2)).toFixed(2) },
  usd0:       { kind: "num", render: (v) => (roundTo(v, 0) < 0 ? "-" : "") + "US$" + Math.abs(roundTo(v, 0)).toFixed(0) },
  cadb:       { kind: "num", render: (v) => (roundTo(v, 1) < 0 ? "-" : "") + "$" + Math.abs(roundTo(v, 1)).toFixed(1) + "B" },
  cadb_from_m:{ kind: "num", render: (v) => FORMATS.cadb.render(v / 1000) },
  int:        { kind: "num", render: (v) => fixedStr(v, 0) },
  int_signed: {
    kind: "num",
    render: (v) => {
      const r = roundTo(v, 0);
      if (r > 0) return "+" + r.toFixed(0);
      if (r < 0) return MINUS + Math.abs(r).toFixed(0);
      return "0";
    },
  },
  thousands:  { kind: "num", render: (v) => groupedStr(v, 0) },
  thousands2: { kind: "num", render: (v) => groupedStr(v, 2) },
  pct1:       { kind: "num", render: (v) => fixedStr(v, 1) + "%" },
  pct2:       { kind: "num", render: (v) => fixedStr(v, 2) + "%" },
  one_dec:    { kind: "num", render: (v) => fixedStr(v, 1) },
  two_dec:    { kind: "num", render: (v) => fixedStr(v, 2) },
  month_day: {
    kind: "date",
    render: (iso) => {
      const { m, d } = parseISODate(iso);
      return `${MONTHS[m - 1]} ${d}`;
    },
  },
  month_day_year: {
    kind: "date",
    render: (iso) => {
      const { y, m, d } = parseISODate(iso);
      return `${MONTHS[m - 1]} ${d}, ${y}`;
    },
  },
};

// --------------------------------------------------------------------------- #
// Text interpolation
// --------------------------------------------------------------------------- #

/** Split template text into parts at load time:
 *  [{ kind: "lit", text }, { kind: "expr", src, ast, type, format }] */
function compileText(text, slotAliases, where) {
  const parts = [];
  const re = /\{([^{}]+)\}/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push({ kind: "lit", text: text.slice(last, m.index) });
    const inner = m[1];
    const bar = inner.lastIndexOf("|");
    if (bar < 0) {
      throw new ProseTemplateError(
        `${where}: interpolation "{${inner}}" is missing a format -- use {expr|fmt}`
      );
    }
    const exprSrc = inner.slice(0, bar).trim();
    const fmtName = inner.slice(bar + 1).trim();
    const fmt = FORMATS[fmtName];
    if (!fmt) {
      throw new ProseTemplateError(
        `${where}: unknown format "${fmtName}" (known: ${Object.keys(FORMATS).join(", ")})`
      );
    }
    let ast;
    let type;
    try {
      ast = parseExpression(exprSrc);
      type = typecheck(ast, slotAliases, exprSrc);
    } catch (e) {
      throw new ProseTemplateError(`${where}: ${e.message}`);
    }
    if (type === "bool") {
      throw new ProseTemplateError(
        `${where}: "{${inner}}" is a boolean expression; only numeric or date expressions can be interpolated`
      );
    }
    if (type !== fmt.kind) {
      throw new ProseTemplateError(
        `${where}: format "${fmtName}" expects a ${fmt.kind} expression but "${exprSrc}" is ${type}`
      );
    }
    parts.push({ kind: "expr", src: exprSrc, ast, format: fmtName });
    last = re.lastIndex;
  }
  if (last < text.length) parts.push({ kind: "lit", text: text.slice(last) });
  return parts;
}

function renderText(compiled, ctx, where) {
  let out = "";
  for (const part of compiled) {
    if (part.kind === "lit") {
      out += part.text;
      continue;
    }
    let v;
    try {
      v = evalNode(part.ast, ctx);
    } catch (e) {
      // In selected text, data unavailability is a hard failure: we must
      // never ship half a sentence.
      throw new ProseRenderError(`${where}: "{${part.src}|${part.format}}" failed: ${e.message}`);
    }
    out += FORMATS[part.format].render(v);
  }
  return out;
}

// --------------------------------------------------------------------------- #
// Template parsing + validation (load time)
// --------------------------------------------------------------------------- #

function compileVariants(rawVariants, slotAliases, where) {
  if (!Array.isArray(rawVariants) || rawVariants.length === 0) {
    throw new ProseTemplateError(`${where}: "variants" must be a non-empty list`);
  }
  return rawVariants.map((rv, i) => {
    const vWhere = `${where} variant[${i}]`;
    if (typeof rv !== "object" || rv === null || typeof rv.when !== "string" || typeof rv.text !== "string") {
      throw new ProseTemplateError(`${vWhere}: each variant needs string fields "when" and "text"`);
    }
    let whenAst;
    try {
      whenAst = parseExpression(rv.when);
      const t = typecheck(whenAst, slotAliases, rv.when);
      if (t !== "bool") {
        throw new ProseTemplateError(`predicate must be boolean, got ${t}`);
      }
    } catch (e) {
      throw new ProseTemplateError(`${vWhere}: ${e.message}`);
    }
    return {
      when: rv.when,
      whenAst,
      text: rv.text,
      compiled: compileText(rv.text, slotAliases, vWhere),
    };
  });
}

function hasLiteralTrueTerminator(variants) {
  return isLiteralTrue(variants[variants.length - 1].whenAst);
}

/**
 * Parse + validate a template against the set of series keys actually
 * present in the panel data. Throws ProseTemplateError on any problem.
 *
 * @param raw           parsed YAML object
 * @param availableSeriesKeys  Set/array of panel_data series keys
 */
export function parseTemplate(raw, availableSeriesKeys) {
  const available = new Set(availableSeriesKeys);
  if (typeof raw !== "object" || raw === null) {
    throw new ProseTemplateError("template root must be a mapping");
  }
  if (typeof raw.section !== "string" || !raw.section) {
    throw new ProseTemplateError('template needs a string "section" field');
  }
  if (typeof raw.slots !== "object" || raw.slots === null || Object.keys(raw.slots).length === 0) {
    throw new ProseTemplateError('template needs a non-empty "slots" mapping (alias -> series key)');
  }
  const slots = {};
  for (const [alias, key] of Object.entries(raw.slots)) {
    if (typeof key !== "string") {
      throw new ProseTemplateError(`slot "${alias}": series key must be a string`);
    }
    if (!available.has(key)) {
      throw new ProseTemplateError(
        `slot "${alias}": series key "${key}" not found in panel data ` +
        `(available: ${[...available].sort().join(", ")})`
      );
    }
    slots[alias] = key;
  }
  const slotAliases = new Set(Object.keys(slots));

  if (typeof raw.surfaces !== "object" || raw.surfaces === null || Object.keys(raw.surfaces).length === 0) {
    throw new ProseTemplateError('template needs a non-empty "surfaces" mapping');
  }

  const surfaces = {};
  for (const [id, rawSurface] of Object.entries(raw.surfaces)) {
    const where = `surface "${id}"`;
    if (typeof rawSurface !== "object" || rawSurface === null) {
      throw new ProseTemplateError(`${where}: must be a mapping`);
    }
    const required = rawSurface.required === true;
    const hasVariants = "variants" in rawSurface;
    const hasSentences = "sentences" in rawSurface;
    if (hasVariants === hasSentences) {
      throw new ProseTemplateError(`${where}: needs exactly one of "variants" or "sentences"`);
    }

    if (hasVariants) {
      const variants = compileVariants(rawSurface.variants, slotAliases, where);
      if (required && !hasLiteralTrueTerminator(variants)) {
        throw new ProseTemplateError(
          `${where}: required surfaces must terminate in a 'when: "true"' variant ` +
          `(otherwise the build can fail at render time on an unforeseen data state)`
        );
      }
      surfaces[id] = { id, required, kind: "variants", variants };
    } else {
      if (!Array.isArray(rawSurface.sentences) || rawSurface.sentences.length === 0) {
        throw new ProseTemplateError(`${where}: "sentences" must be a non-empty list`);
      }
      const sentences = rawSurface.sentences.map((s, i) => {
        if (typeof s !== "object" || s === null || !("variants" in s)) {
          throw new ProseTemplateError(`${where} sentence[${i}]: needs a "variants" list`);
        }
        return compileVariants(s.variants, slotAliases, `${where} sentence[${i}]`);
      });
      if (required && !sentences.some(hasLiteralTrueTerminator)) {
        throw new ProseTemplateError(
          `${where}: required prose surfaces need at least one sentence terminating in ` +
          `a 'when: "true"' variant so the surface can never render empty`
        );
      }
      surfaces[id] = { id, required, kind: "sentences", sentences };
    }
  }

  return { section: raw.section, slots, surfaces };
}

// --------------------------------------------------------------------------- #
// Series context (render time)
// --------------------------------------------------------------------------- #

/** Collect every slot (primary/secondary/tertiary/extras) across all panels
 *  into key -> { dates, values }, keeping only non-null numeric values. */
export function collectSeries(panelData) {
  const out = new Map();
  for (const panel of Object.values(panelData.panels ?? {})) {
    const slots = [panel.primary, panel.secondary, panel.tertiary, ...(panel.extras ?? [])];
    for (const slot of slots) {
      if (!slot || !slot.key || !Array.isArray(slot.data)) continue;
      if (out.has(slot.key)) continue; // first occurrence wins; duplicates are identical reads
      const dates = [];
      const values = [];
      for (const rec of slot.data) {
        if (typeof rec.value === "number" && Number.isFinite(rec.value)) {
          dates.push(rec.date);
          values.push(rec.value);
        }
      }
      out.set(slot.key, { dates, values });
    }
  }
  return out;
}

// Same completed-close convention as pipeline/fetch/yahoo.py.
const COMPLETED_CLOSE_UTC_HOUR = 21;
const COMPLETED_CLOSE_UTC_MINUTE = 30;

/** Belt-and-suspenders: if the final observation is dated the same UTC day
 *  the panel was generated AND generation happened before 21:30 UTC, the
 *  observation may be an intraday snapshot -- step back one row. */
export function dropSuspectFinalObs(series, generatedAtISO) {
  if (!generatedAtISO || series.values.length === 0) return series;
  // Trim sub-second precision Python emits 6 digits of; JS Date wants <= 3.
  const gen = new Date(String(generatedAtISO).replace(/\.\d+/, ""));
  if (Number.isNaN(gen.getTime())) return series;
  const lastDate = series.dates[series.dates.length - 1];
  const genDateUTC = `${gen.getUTCFullYear()}-${String(gen.getUTCMonth() + 1).padStart(2, "0")}-${String(gen.getUTCDate()).padStart(2, "0")}`;
  if (String(lastDate).slice(0, 10) !== genDateUTC) return series;
  const threshold = Date.UTC(
    gen.getUTCFullYear(), gen.getUTCMonth(), gen.getUTCDate(),
    COMPLETED_CLOSE_UTC_HOUR, COMPLETED_CLOSE_UTC_MINUTE
  );
  if (gen.getTime() >= threshold) return series;
  return {
    dates: series.dates.slice(0, -1),
    values: series.values.slice(0, -1),
  };
}

// --------------------------------------------------------------------------- #
// Renderer (render time)
// --------------------------------------------------------------------------- #

function renderFromVariants(variants, ctx, where, warnings) {
  for (let i = 0; i < variants.length; i++) {
    const v = variants[i];
    let matched;
    try {
      matched = evalNode(v.whenAst, ctx);
    } catch (e) {
      if (e instanceof EvalUnavailableError) {
        warnings.push(`${where} variant[${i}] predicate "${v.when}" skipped: ${e.message}`);
        continue;
      }
      throw e;
    }
    if (matched) {
      return {
        variantIndex: i,
        predicate: v.when,
        text: renderText(v.compiled, ctx, `${where} variant[${i}]`),
      };
    }
  }
  return null;
}

/**
 * Render a parsed template against panel data.
 * Throws ProseRenderError when a required surface or a callout field
 * renders empty.
 */
export function renderTemplate(template, panelData) {
  const all = collectSeries(panelData);
  const generatedAt = panelData.generatedAt ?? null;
  const ctx = { series: new Map() };
  for (const [alias, key] of Object.entries(template.slots)) {
    const s = all.get(key);
    if (!s) {
      // parseTemplate validated against this panelData's keys, but defend
      // anyway -- the caller may re-render against a different file.
      throw new ProseRenderError(`slot "${alias}": series "${key}" not present in panel data`);
    }
    ctx.series.set(alias, dropSuspectFinalObs(s, generatedAt));
  }

  const warnings = [];
  const surfaces = {};

  for (const surface of Object.values(template.surfaces)) {
    const where = `surface "${surface.id}"`;
    let text = "";
    const parts = [];

    if (surface.kind === "variants") {
      const hit = renderFromVariants(surface.variants, ctx, where, warnings);
      if (hit) {
        text = hit.text;
        parts.push({ sentenceIndex: null, variantIndex: hit.variantIndex, predicate: hit.predicate, text: hit.text });
      }
    } else {
      const rendered = [];
      surface.sentences.forEach((variants, si) => {
        const hit = renderFromVariants(variants, ctx, `${where} sentence[${si}]`, warnings);
        if (hit) {
          rendered.push(hit.text);
          parts.push({ sentenceIndex: si, variantIndex: hit.variantIndex, predicate: hit.predicate, text: hit.text });
        }
        // No hit: the sentence DROPS silently -- the structural guarantee
        // against asserting claims the data no longer supports.
      });
      text = rendered.join(" ");
    }

    const isCallout = surface.id.includes("-callout-");
    if ((surface.required || isCallout) && text.trim() === "") {
      throw new ProseRenderError(
        `${where} rendered empty but is ${surface.required ? "required" : "a callout field"} -- ` +
        `no variant predicate matched the current data state`
      );
    }

    surfaces[surface.id] = { id: surface.id, required: surface.required, text, parts };
  }

  return {
    section: template.section,
    generatedAt,
    surfaces,
    warnings,
  };
}
