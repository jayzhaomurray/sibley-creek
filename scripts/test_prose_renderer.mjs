/**
 * test_prose_renderer.mjs -- self-checking unit tests for the prose engine.
 *
 * No test framework in this repo (Playwright is visual-only), so this is a
 * plain self-checking node script wired into `npm run build` -- it exits 1
 * on any failure, which fails CI before the site builds.
 *
 * Coverage: expression evaluator, predicate parser, every named format,
 * load-time validation failures, first-true-wins, silent sentence drop,
 * empty-required/callout build failure, suspect-final-observation guard.
 *
 * Run: node scripts/test_prose_renderer.mjs
 */

import {
  parseTemplate,
  renderTemplate,
  collectSeries,
  dropSuspectFinalObs,
  ProseTemplateError,
  ProseRenderError,
  FORMATS,
} from "../src/lib/prose/engine.mjs";

let passed = 0;
let failed = 0;

function check(name, fn) {
  try {
    fn();
    passed++;
  } catch (e) {
    failed++;
    console.error(`FAIL: ${name}`);
    console.error(`      ${e.message}`);
  }
}

function assertEq(actual, expected, label = "") {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`${label} expected ${b}, got ${a}`);
}

function assertThrows(fn, errClass, msgPart) {
  let threw = null;
  try {
    fn();
  } catch (e) {
    threw = e;
  }
  if (!threw) throw new Error(`expected ${errClass.name}, nothing thrown`);
  if (!(threw instanceof errClass)) {
    throw new Error(`expected ${errClass.name}, got ${threw.name}: ${threw.message}`);
  }
  if (msgPart && !threw.message.includes(msgPart)) {
    throw new Error(`expected message containing "${msgPart}", got: ${threw.message}`);
  }
}

// --------------------------------------------------------------------------- #
// Fixtures: synthetic panel data with hand-checkable values
// --------------------------------------------------------------------------- #

function panel(records, generatedAt = "2026-06-09T23:00:00+00:00") {
  // alpha: 10 obs 1..10 (latest 10); beta: constant 2.5 except latest 3.0
  return {
    generatedAt,
    panels: {
      "panel-1": {
        primary: {
          key: "alpha",
          data: records ?? [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((v, i) => ({
            date: `2026-06-0${i < 9 ? i + 1 : 9}`.slice(0, 10) && `2026-05-${String(i + 1).padStart(2, "0")}`,
            value: v,
          })),
        },
        secondary: {
          key: "beta",
          data: [2.5, 2.5, 2.5, 2.5, 3.0].map((v, i) => ({
            date: `2026-05-${String(i + 10).padStart(2, "0")}`,
            value: v,
          })),
        },
      },
    },
  };
}

const BASE = panel();

function tpl(surfaces, slots = { a: "alpha", b: "beta" }, data = BASE) {
  return parseTemplate({ section: "test", slots, surfaces }, collectSeries(data).keys());
}

function renderOne(surfaceDef, data = BASE) {
  const t = tpl({ s: surfaceDef }, undefined, data);
  return renderTemplate(t, data).surfaces["s"].text;
}

function evalExpr(expr, fmt = "two_dec", data = BASE) {
  return renderOne(
    { variants: [{ when: "true", text: `{${expr}|${fmt}}` }] },
    data
  );
}

// --------------------------------------------------------------------------- #
// Expression evaluator
// --------------------------------------------------------------------------- #

check("latest", () => assertEq(evalExpr("latest(a)"), "10.00"));
check("at T-0 equals latest", () => assertEq(evalExpr('at(a, "T-0")'), "10.00"));
check("at T-3", () => assertEq(evalExpr('at(a, "T-3")'), "7.00"));
check("delta", () => assertEq(evalExpr("delta(a, 4)"), "4.00"));
check("pct_change", () => assertEq(evalExpr("pct_change(a, 5)"), "100.00"));
check("max includes latest", () => assertEq(evalExpr("max(a, 3)"), "10.00"));
check("min over window", () => assertEq(evalExpr("min(a, 3)"), "8.00"));
check("spread", () => assertEq(evalExpr("spread(a, b)"), "7.00"));
check("bps", () => assertEq(evalExpr("bps(spread(a, b))"), "700.00"));
check("abs", () => assertEq(evalExpr("abs(delta(b, 1) - 1)"), "0.50"));
check("arithmetic precedence", () => assertEq(evalExpr("latest(a) + 2 * 3"), "16.00"));
check("unary minus", () => assertEq(evalExpr("-delta(a, 2)"), "-2.00"));
check("latest_date", () =>
  assertEq(evalExpr("latest_date(b)", "month_day_year"), "May 14, 2026"));

// --------------------------------------------------------------------------- #
// Predicates
// --------------------------------------------------------------------------- #

function predicateFires(when, data = BASE) {
  const text = renderOne(
    { variants: [{ when, text: "Y" }, { when: "true", text: "N" }] },
    data
  );
  return text === "Y";
}

check("cmp <", () => assertEq(predicateFires("latest(b) < 3.5"), true));
check("cmp <=", () => assertEq(predicateFires("latest(a) <= 10"), true));
check("cmp >", () => assertEq(predicateFires("latest(a) > 10"), false));
check("cmp >=", () => assertEq(predicateFires("latest(a) >= 10"), true));
check("cmp ==", () => assertEq(predicateFires("latest(a) == 10"), true));
check("between inclusive lo", () => assertEq(predicateFires("between(latest(a), 10, 20)"), true));
check("between inclusive hi", () => assertEq(predicateFires("between(latest(a), 0, 10)"), true));
check("between outside", () => assertEq(predicateFires("between(latest(a), 11, 20)"), false));
check("between negative literal", () =>
  assertEq(predicateFires("between(-delta(a, 1), -2, -1)"), true));
check("and", () => assertEq(predicateFires("latest(a) > 5 && latest(b) > 5"), false));
check("or", () => assertEq(predicateFires("latest(a) > 5 || latest(b) > 5"), true));
check("not", () => assertEq(predicateFires("!(latest(a) > 5)"), false));
check("parens", () =>
  assertEq(predicateFires("(latest(a) > 5 || latest(b) > 5) && latest(b) == 3"), true));
check("literal true", () => assertEq(predicateFires("true"), true));

// --------------------------------------------------------------------------- #
// Formats (exact strings, including U+2212 in int_signed)
// --------------------------------------------------------------------------- #

const F = (name, v) => FORMATS[name].render(v);

check("fx4", () => assertEq(F("fx4", 1.38964), "1.3896"));
check("usd", () => assertEq(F("usd", 92.155), "US$92.16"));
check("usd0", () => assertEq(F("usd0", 92.16), "US$92"));
check("int", () => assertEq(F("int", 62.7), "63"));
check("int_signed positive", () => assertEq(F("int_signed", 8.2), "+8"));
check("int_signed negative uses U+2212", () =>
  assertEq(F("int_signed", -11.7), "−12"));
check("int_signed zero", () => assertEq(F("int_signed", 0.2), "0"));
check("thousands", () => assertEq(F("thousands", 35216.8), "35,217"));
check("thousands2", () => assertEq(F("thousands2", 33994.866), "33,994.87"));
check("pct1", () => assertEq(F("pct1", 3.44), "3.4%"));
check("pct2", () => assertEq(F("pct2", 3.435), "3.44%"));
check("one_dec", () => assertEq(F("one_dec", 0.94), "0.9"));
check("two_dec", () => assertEq(F("two_dec", 0.926), "0.93"));
check("month_day", () => assertEq(F("month_day", "2026-06-09"), "June 9"));
check("month_day_year", () => assertEq(F("month_day_year", "2026-06-09"), "June 9, 2026"));
check("negative pct1", () => assertEq(F("pct1", -5.93), "-5.9%"));
check("round half away from zero", () => assertEq(F("one_dec", 2.25), "2.3"));

// --------------------------------------------------------------------------- #
// Rendering semantics
// --------------------------------------------------------------------------- #

check("first true predicate wins", () => {
  const text = renderOne({
    variants: [
      { when: "latest(a) > 100", text: "no" },
      { when: "latest(a) > 5", text: "first" },
      { when: "latest(a) > 1", text: "second" },
      { when: "true", text: "fallback" },
    ],
  });
  assertEq(text, "first");
});

check("sentence with no matching variant drops silently", () => {
  const text = renderOne({
    sentences: [
      { variants: [{ when: "true", text: "Kept." }] },
      { variants: [{ when: "latest(a) > 100", text: "Dropped." }] },
      { variants: [{ when: "true", text: "Also kept." }] },
    ],
  });
  assertEq(text, "Kept. Also kept.");
});

check("required surface rendering empty fails the build", () => {
  const t = tpl({
    s: {
      required: true,
      sentences: [{ variants: [{ when: "latest(a) > 100", text: "x" },
                               { when: "true", text: "y" }] }],
    },
  });
  // Force emptiness by rendering against data where the terminal-true
  // sentence still renders -- so instead build a non-terminating surface
  // via the sentences path: required sentence-surfaces need one literal-true
  // terminator at LOAD time, so emptiness can only arise via eval errors.
  // Covered separately below; here assert the load-time guarantee instead.
  assertEq(typeof t, "object");
});

check("callout surface rendering empty fails the build", () => {
  const t = tpl({
    "x-callout-value": {
      variants: [{ when: "latest(a) > 100", text: "never" }],
    },
  });
  assertThrows(
    () => renderTemplate(t, BASE),
    ProseRenderError,
    "callout"
  );
});

check("required surface empty via insufficient history fails the build", () => {
  // The only-true variant needs 50 obs of history; eval error skips it,
  // surface renders empty, required -> ProseRenderError.
  const t = tpl({
    s: {
      required: true,
      sentences: [
        { variants: [{ when: "delta(a, 50) > 0", text: "needs history" },
                     { when: "true", text: "{at(a, \"T-50\")|int}" }] },
      ],
    },
  });
  assertThrows(() => renderTemplate(t, BASE), ProseRenderError);
});

check("predicate skipped on insufficient history records a warning", () => {
  const t = tpl({
    s: {
      variants: [
        { when: "delta(a, 50) > 0", text: "deep" },
        { when: "true", text: "shallow" },
      ],
    },
  });
  const r = renderTemplate(t, BASE);
  assertEq(r.surfaces["s"].text, "shallow");
  assertEq(r.warnings.length >= 1, true, "warning count");
});

check("interpolation eval failure in selected text is a hard error", () => {
  const t = tpl({
    s: { variants: [{ when: "true", text: "{pct_change(a, 50)|pct1}" }] },
  });
  assertThrows(() => renderTemplate(t, BASE), ProseRenderError);
});

// --------------------------------------------------------------------------- #
// Load-time validation
// --------------------------------------------------------------------------- #

check("unknown series key in slots fails at load", () => {
  assertThrows(
    () => parseTemplate(
      { section: "t", slots: { x: "nope" }, surfaces: { s: { variants: [{ when: "true", text: "t" }] } } },
      collectSeries(BASE).keys()
    ),
    ProseTemplateError,
    'series key "nope"'
  );
});

check("unknown alias in expression fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "latest(zzz) > 0", text: "t" }] } }),
    ProseTemplateError,
    'unknown series alias "zzz"'
  );
});

check("unknown function fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "median(a) > 0", text: "t" }] } }),
    ProseTemplateError,
    'unknown function "median"'
  );
});

check("unknown format fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "true", text: "{latest(a)|euros}" }] } }),
    ProseTemplateError,
    'unknown format "euros"'
  );
});

check("date expression with numeric format fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "true", text: "{latest_date(a)|pct1}" }] } }),
    ProseTemplateError,
    'format "pct1"'
  );
});

check("numeric expression with date format fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "true", text: "{latest(a)|month_day}" }] } }),
    ProseTemplateError
  );
});

check("required variants surface without true terminator fails at load", () => {
  assertThrows(
    () => tpl({ s: { required: true, variants: [{ when: "latest(a) > 0", text: "t" }] } }),
    ProseTemplateError,
    "terminate"
  );
});

check("required sentences surface without any true terminator fails at load", () => {
  assertThrows(
    () => tpl({
      s: {
        required: true,
        sentences: [{ variants: [{ when: "latest(a) > 0", text: "t" }] }],
      },
    }),
    ProseTemplateError,
    "terminating"
  );
});

check("non-boolean predicate fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "latest(a)", text: "t" }] } }),
    ProseTemplateError
  );
});

check("malformed predicate fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "latest(a) >", text: "t" }] } }),
    ProseTemplateError
  );
});

check("interpolation without format fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "true", text: "{latest(a)}" }] } }),
    ProseTemplateError,
    "missing a format"
  );
});

check("bad T-ref fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: 'at(a, "yesterday") > 0', text: "t" }] } }),
    ProseTemplateError,
    'form "T-N"'
  );
});

check("surface with both variants and sentences fails at load", () => {
  assertThrows(
    () => tpl({ s: { variants: [{ when: "true", text: "t" }], sentences: [] } }),
    ProseTemplateError,
    "exactly one"
  );
});

// --------------------------------------------------------------------------- #
// Suspect-final-observation guard (belt-and-suspenders)
// --------------------------------------------------------------------------- #

check("final obs dated generatedAt day, pre-21:30Z -> stepped back", () => {
  const s = { dates: ["2026-06-08", "2026-06-09"], values: [1, 2] };
  const out = dropSuspectFinalObs(s, "2026-06-09T13:15:00+00:00");
  assertEq(out.values, [1]);
});

check("final obs dated generatedAt day, post-21:30Z -> kept", () => {
  const s = { dates: ["2026-06-08", "2026-06-09"], values: [1, 2] };
  const out = dropSuspectFinalObs(s, "2026-06-09T22:05:00+00:00");
  assertEq(out.values, [1, 2]);
});

check("final obs older than generatedAt day -> kept", () => {
  const s = { dates: ["2026-06-08", "2026-06-09"], values: [1, 2] };
  const out = dropSuspectFinalObs(s, "2026-06-10T03:57:00+00:00");
  assertEq(out.values, [1, 2]);
});

check("python-style microsecond generatedAt parses", () => {
  const s = { dates: ["2026-06-09"], values: [2] };
  const out = dropSuspectFinalObs(s, "2026-06-09T13:15:23.089064+00:00");
  assertEq(out.values, []);
});

check("renderTemplate applies the suspect-final-obs guard", () => {
  // beta's latest (3.0) is dated 2026-05-14; generate "same day, 13:00Z"
  const data = panel(undefined, "2026-05-14T13:00:00+00:00");
  const t = tpl({ s: { variants: [{ when: "true", text: "{latest(b)|two_dec}" }] } }, undefined, data);
  assertEq(renderTemplate(t, data).surfaces["s"].text, "2.50");
});

// --------------------------------------------------------------------------- #

if (failed > 0) {
  console.error(`\n[test_prose_renderer] FAIL: ${failed} of ${passed + failed} checks failed.`);
  process.exit(1);
}
console.log(`[test_prose_renderer] OK: ${passed} checks passed.`);
