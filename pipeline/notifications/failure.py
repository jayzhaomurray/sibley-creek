"""Pipeline failure notification helper.

Wraps a pipeline entry point's main() in try/except; on unhandled exception
fires a failure notification with traceback summary and re-raises.

Usage in an entry-point module
-------------------------------
    from pipeline.notifications.failure import notify_on_failure

    if __name__ == "__main__":
        import sys
        with notify_on_failure("build_financial"):
            sys.exit(main())

Or as a decorator around a callable:
    result = notify_on_failure("build_macro").run(main)

Dedupe key: failure:<entry_point>:<ExceptionClass>
Window: 4 hours (DEFAULT_WINDOWS["failure"] in dedupe.py).

Body format follows the standard WHAT HAPPENED / VISITORS / TODO / DETAILS
template; DETAILS includes the entry point, exception class, and first 1000
chars of the traceback.
"""

from __future__ import annotations

import logging
import traceback
from contextlib import contextmanager
from typing import Optional

from pipeline.notifications.send import send_notification

logger = logging.getLogger("pipeline.notifications.failure")

_BODY_TEMPLATE = """\
WHAT HAPPENED
The {entry_point} pipeline step raised an unhandled exception and exited
non-zero. The most recent build may be incomplete or stale.

WHAT VISITORS SEE
The site will continue to serve the last successfully-built version.
No data was corrupted. The failure affects the freshness of data only.

WHAT TO DO
Check the pipeline run log (GitHub Actions or local terminal) for the
full traceback. The exception class and a brief excerpt are in DETAILS
below. Fix the underlying cause and re-run the pipeline.

DETAILS
entry_point: {entry_point}
exception_class: {exc_class}
exception_message: {exc_message}

traceback_excerpt (first 1000 chars):
{traceback_excerpt}
"""


@contextmanager
def notify_on_failure(entry_point: str):
    """Context manager: wrap a block; on exception, fire notification and re-raise.

    Example:
        with notify_on_failure("build_financial"):
            main()
    """
    try:
        yield
    except SystemExit as exc:
        # SystemExit(0) = clean exit; do not notify.
        # SystemExit(non-zero) = pipeline reported failures via sys.exit(1).
        # We treat non-zero SystemExit as a pipeline failure.
        if exc.code and int(exc.code) != 0:
            _fire(entry_point, exc)
        raise
    except Exception as exc:  # noqa: BLE001
        _fire(entry_point, exc)
        raise


def _fire(entry_point: str, exc: BaseException) -> None:
    exc_class = type(exc).__name__
    exc_message = str(exc)[:300]
    tb = traceback.format_exc()[:1000]
    dedupe_key = f"failure:{entry_point}:{exc_class}"

    body = _BODY_TEMPLATE.format(
        entry_point=entry_point,
        exc_class=exc_class,
        exc_message=exc_message,
        traceback_excerpt=tb,
    )

    try:
        send_notification(
            event_type="failure",
            severity="alert",
            subject=f"{entry_point} pipeline step failed ({exc_class})",
            body=body,
            dedupe_key=dedupe_key,
            details={
                "entry_point": entry_point,
                "exception_class": exc_class,
                "exception_message": exc_message,
                "traceback_excerpt": tb,
            },
        )
    except Exception as notify_exc:  # noqa: BLE001
        # Never let the notification mechanism swallow or mask the original error.
        logger.error(
            "failure notification itself failed (original exc still re-raised): %s",
            notify_exc,
        )
