"""Claude dispatch: CLI subprocess (subscription) primary, SDK fallback.

Single entry point for every LLM call in `pipeline/blurbs/`. Two auth
paths:

- `claude --print` subprocess (Claude Code subscription path; requires
  the `claude` CLI installed and authed locally -- see `claude
  setup-token`). Non-interactive, returns once and exits.
- `anthropic.Anthropic().messages.create` (paid API; requires
  `ANTHROPIC_API_KEY`). Used as a fallback so the pipeline COULD run in
  CI on a runner without the CLI.

Resolution order:

1. `CLAUDE_AUTH_MODE=cli` -> force CLI subprocess.
2. `CLAUDE_AUTH_MODE=api` -> force SDK; raises if `ANTHROPIC_API_KEY` unset.
3. Default (unset): prefer CLI if `claude` is on PATH; fall back to SDK
   if `ANTHROPIC_API_KEY` is set; otherwise raise.

The default favours the subscription path so blurb generation runs against
the user's existing Max subscription rather than incurring API charges.

Ported from `C:\\Users\\jayzh\\Documents\\boc-tracker\\analyze.py`
(boc-tracker's `call_claude` pattern, lines ~1680-1760). The key fact:
the prompt is passed on STDIN, not argv, because real prompts exceed
Windows' ~32KB CreateProcess argv limit.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger("pipeline.blurbs.llm_client")


# Default per-call wall-clock budget. Claude calls with framework prompts
# can run 30-60s; 120s gives a comfortable margin without hanging the
# pipeline forever.
DEFAULT_TIMEOUT_S = 120.0


class LLMDispatchError(RuntimeError):
    """Raised when no Claude auth path is usable or the call fails."""


def call_claude(
    prompt: str,
    model: str = "claude-opus-4-7",
    system: Optional[str] = None,
    max_tokens: int = 4096,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> str:
    """Dispatch one Claude call. Returns trimmed assistant text.

    Args:
      prompt: the user message.
      model: model pin (e.g. `claude-opus-4-7`, `claude-sonnet-4-7`,
        `claude-haiku-4-5-20251001`). Required on both paths.
      system: optional system prompt; folded into the user message on the
        CLI path via `--append-system-prompt` flag.
      max_tokens: max output tokens. SDK only -- the CLI does not expose
        this; prompts must self-limit via sentence-count instructions.
      timeout: wall-clock budget per call (seconds).

    Raises:
      LLMDispatchError: if no auth path is available, or the chosen path
        fails with a non-recoverable error.
    """
    mode = os.environ.get("CLAUDE_AUTH_MODE", "").strip().lower()

    if mode == "cli":
        return _call_cli(prompt, model, system=system, timeout=timeout)
    if mode == "api":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise LLMDispatchError(
                "CLAUDE_AUTH_MODE=api but ANTHROPIC_API_KEY is unset."
            )
        return _call_api(
            prompt, model, system=system,
            max_tokens=max_tokens, timeout=timeout,
        )

    # Default resolution: prefer CLI if available, then fall back to SDK.
    if shutil.which("claude"):
        try:
            return _call_cli(prompt, model, system=system, timeout=timeout)
        except LLMDispatchError as exc:
            if os.environ.get("ANTHROPIC_API_KEY"):
                logger.warning(
                    "claude CLI failed (%s); falling back to ANTHROPIC_API_KEY", exc
                )
                return _call_api(
                    prompt, model, system=system,
                    max_tokens=max_tokens, timeout=timeout,
                )
            raise
    if os.environ.get("ANTHROPIC_API_KEY"):
        return _call_api(
            prompt, model, system=system,
            max_tokens=max_tokens, timeout=timeout,
        )
    raise LLMDispatchError(
        "No Claude auth path available. Either install Claude Code (so the "
        "`claude` CLI is on PATH) or set ANTHROPIC_API_KEY. To force a "
        "specific path, set CLAUDE_AUTH_MODE=cli or CLAUDE_AUTH_MODE=api."
    )


# ---------------------------------------------------------------------------
# CLI subprocess path (primary)
# ---------------------------------------------------------------------------

def _call_cli(
    prompt: str,
    model: str,
    system: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> str:
    """Call Claude via the `claude --print` subprocess.

    The prompt is fed on STDIN -- argv has a Windows ~32KB CreateProcess
    limit and our framework prompts exceed that. `--print` is the
    non-interactive flag (returns once, exits).
    """
    argv = ["claude", "--print", "--model", model]
    if system:
        argv.extend(["--append-system-prompt", system])

    try:
        result = subprocess.run(
            argv,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise LLMDispatchError(
            f"`claude` CLI not found on PATH: {exc}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise LLMDispatchError(
            f"`claude --print` timed out after {timeout}s (model={model})"
        ) from exc

    if result.returncode != 0:
        stderr_snippet = (result.stderr or "")[:500]
        raise LLMDispatchError(
            f"`claude --print` exited with code {result.returncode} "
            f"(model={model}). stderr: {stderr_snippet}"
        )
    return (result.stdout or "").strip()


# ---------------------------------------------------------------------------
# Anthropic SDK fallback path
# ---------------------------------------------------------------------------

def _call_api(
    prompt: str,
    model: str,
    system: Optional[str] = None,
    max_tokens: int = 4096,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> str:
    """Call Claude via the Anthropic SDK. Requires `pip install anthropic`."""
    try:
        import anthropic
    except ImportError as exc:
        raise LLMDispatchError(
            "anthropic package not installed; `pip install anthropic` "
            "or use the CLI path."
        ) from exc

    client = anthropic.Anthropic(timeout=timeout)
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    try:
        response = client.messages.create(**kwargs)
    except Exception as exc:
        raise LLMDispatchError(
            f"Anthropic SDK call failed (model={model}): "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    # response.content is a list of content blocks; take the first text block.
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            return text.strip()
    raise LLMDispatchError(
        f"Anthropic SDK returned no text content (model={model})"
    )


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def available_paths() -> dict:
    """Return a dict describing which auth paths are usable right now.

    Useful for the smoke test and for pipeline-startup logging.
    """
    return {
        "claude_cli": shutil.which("claude"),
        "anthropic_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "claude_auth_mode": os.environ.get("CLAUDE_AUTH_MODE", "") or None,
    }
