"""Smoke test: verify the Claude CLI subprocess path is wired up.

Not a pytest case -- a runnable script. Calls the cheapest model with a
trivially short prompt and asserts the reply contains a known token.

Run:
    python -m pipeline.blurbs.test_cli_subprocess
"""

from __future__ import annotations

import sys

from pipeline.blurbs.llm_client import available_paths, call_claude


SENTINEL = "pipeline operational"
SMOKE_PROMPT = f"Say '{SENTINEL}' and nothing else."
SMOKE_MODEL = "claude-haiku-4-5-20251001"


def main() -> int:
    paths = available_paths()
    print(f"available paths: {paths}", flush=True)
    if not paths["claude_cli"] and not paths["anthropic_api_key"]:
        print("FAIL: no Claude auth path available", file=sys.stderr)
        return 2

    print(f"calling {SMOKE_MODEL} via call_claude...", flush=True)
    try:
        out = call_claude(SMOKE_PROMPT, model=SMOKE_MODEL, timeout=60.0)
    except Exception as exc:
        print(f"FAIL: call_claude raised: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 1

    print(f"raw stdout: {out!r}", flush=True)
    if SENTINEL.lower() not in out.lower():
        print(f"FAIL: sentinel {SENTINEL!r} not found in reply", file=sys.stderr)
        return 1
    print("PASS: pipeline operational")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
