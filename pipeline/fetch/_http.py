"""HTTP client factory + retry policy shared by every source.

One place to set timeouts, retries, and the User-Agent. Adapters in the
per-source modules call get_client() / post_json() and don't need to know
the retry policy.

Retry policy:
    - Network errors and 5xx responses retry up to 4 times.
    - 429 (rate-limit) retries with exponential backoff up to 60s.
    - 4xx other than 429 fails immediately - those are caller bugs
      (wrong vector ID, invalid series key) and silent retry would hide them.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
USER_AGENT = "macro-research-department/0.1 (+https://github.com/jayzhaomurray/macro-research-department)"


def _should_retry(exc: BaseException) -> bool:
    """Retry on network errors and 5xx / 429. Fail fast on other 4xx."""
    if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout,
                        httpx.PoolTimeout, httpx.RemoteProtocolError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or 500 <= status < 600
    return False


def _log_retry(state: RetryCallState) -> None:
    if state.outcome and state.outcome.failed:
        exc = state.outcome.exception()
        logger.warning(
            "retry attempt=%d sleeping=%.1fs exc=%s",
            state.attempt_number,
            state.next_action.sleep if state.next_action else 0.0,
            exc,
        )


_retry_policy = retry(
    retry=retry_if_exception(_should_retry),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1.5, min=1, max=60),
    before_sleep=_log_retry,
    reraise=True,
)


def get_client(**kwargs: Any) -> httpx.Client:
    """Return a configured httpx.Client. Callers must use it in a `with` block."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    headers.update(kwargs.pop("headers", {}) or {})
    return httpx.Client(
        timeout=kwargs.pop("timeout", DEFAULT_TIMEOUT),
        headers=headers,
        follow_redirects=True,
        **kwargs,
    )


@_retry_policy
def get_json(client: httpx.Client, url: str, *, params: Optional[dict] = None) -> Any:
    """GET <url> -> parsed JSON. Raises for status before returning."""
    r = client.get(url, params=params)
    r.raise_for_status()
    return r.json()


@_retry_policy
def post_json(client: httpx.Client, url: str, *, json_body: Any) -> Any:
    """POST <url> with a JSON body -> parsed JSON. Raises for status before returning."""
    r = client.post(url, json=json_body)
    r.raise_for_status()
    return r.json()


@_retry_policy
def get_bytes(client: httpx.Client, url: str, *, params: Optional[dict] = None) -> httpx.Response:
    """GET <url> -> raw Response (do not raise_for_status; caller inspects status).

    Used for binary probing loops (e.g. CBA PDF discovery) where 404 is an
    expected probe result, not an error. Network errors and 5xx still retry
    via the shared policy; 404 returns immediately so the caller can move on.
    """
    r = client.get(url, params=params)
    if 500 <= r.status_code < 600:
        r.raise_for_status()  # triggers retry via _should_retry
    return r


@_retry_policy
def get_text(client: httpx.Client, url: str, *, params: Optional[dict] = None) -> str:
    """GET <url> -> response body as text. Raises for status before returning.

    Used for CSV / TSV bulk-download sources (Indeed Hiring Lab, future BIS
    bulk CSVs, etc.) where the response is plain text rather than JSON. Honors
    the same retry policy as get_json.
    """
    r = client.get(url, params=params)
    r.raise_for_status()
    return r.text
