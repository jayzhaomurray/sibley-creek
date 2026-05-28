"""Small Google Calendar CLI for local personal automation.

Initial setup:
  1. Enable Google Calendar API in a Google Cloud project.
  2. Create an OAuth client ID for a Desktop app.
  3. Download the JSON to work/secrets/google_calendar_credentials.json.
  4. Run: .venv\\Scripts\\python.exe tools\\google_calendar.py auth

Secrets and tokens live under work/secrets/ by default, which is ignored.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SECRET_DIR = ROOT / "work" / "secrets"
DEFAULT_CREDENTIALS = DEFAULT_SECRET_DIR / "google_calendar_credentials.json"
DEFAULT_TOKEN = DEFAULT_SECRET_DIR / "google_calendar_token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
DEFAULT_TIMEZONE = "America/Toronto"


def _path_from_env(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser().resolve() if value else default


def credentials_path() -> Path:
    return _path_from_env("GOOGLE_CALENDAR_CREDENTIALS", DEFAULT_CREDENTIALS)


def token_path() -> Path:
    return _path_from_env("GOOGLE_CALENDAR_TOKEN", DEFAULT_TOKEN)


def load_credentials(interactive: bool) -> Credentials:
    creds_file = credentials_path()
    token_file = token_path()
    creds: Credentials | None = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not interactive:
            raise SystemExit(
                "Calendar auth is not set up. Run: "
                ".venv\\Scripts\\python.exe tools\\google_calendar.py auth"
            )
        if not creds_file.exists():
            raise SystemExit(
                f"Missing OAuth client file: {creds_file}\n"
                "Download a Google Cloud OAuth Desktop client JSON there first."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
        creds = flow.run_local_server(port=0)

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def service(interactive: bool = False) -> Any:
    creds = load_credentials(interactive=interactive)
    return build("calendar", "v3", credentials=creds)


def parse_dt(value: str, timezone: str) -> dict[str, str]:
    """Return a Calendar API date/dateTime object."""
    if len(value) == 10:
        dt.date.fromisoformat(value)
        return {"date": value}

    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return {"dateTime": parsed.isoformat(timespec="seconds"), "timeZone": timezone}
    return {"dateTime": parsed.isoformat(timespec="seconds")}


def rfc3339_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def cmd_auth(_args: argparse.Namespace) -> None:
    load_credentials(interactive=True)
    print(f"Calendar token written to {token_path()}")


def cmd_calendars(args: argparse.Namespace) -> None:
    items = service().calendarList().list().execute().get("items", [])
    if args.json:
        print_json(items)
        return
    for cal in items:
        primary = " primary" if cal.get("primary") else ""
        access = cal.get("accessRole", "?")
        print(f"{cal['id']}\t{access}{primary}\t{cal.get('summary', '')}")


def cmd_upcoming(args: argparse.Namespace) -> None:
    now = dt.datetime.now(dt.UTC)
    end = now + dt.timedelta(days=args.days)
    events = (
        service()
        .events()
        .list(
            calendarId=args.calendar,
            timeMin=now.isoformat().replace("+00:00", "Z"),
            timeMax=end.isoformat().replace("+00:00", "Z"),
            maxResults=args.limit,
            singleEvents=True,
            orderBy="startTime",
            q=args.query,
        )
        .execute()
        .get("items", [])
    )
    if args.json:
        print_json(events)
        return
    for event in events:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        event_id = event.get("id", "")
        summary = event.get("summary", "(no title)")
        print(f"{start}\t{event_id}\t{summary}")


def event_body_from_args(args: argparse.Namespace, patch: bool = False) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if args.title is not None:
        body["summary"] = args.title
    if args.location is not None:
        body["location"] = args.location
    if args.description is not None:
        body["description"] = args.description
    if args.start is not None:
        body["start"] = parse_dt(args.start, args.timezone)
    if args.end is not None:
        body["end"] = parse_dt(args.end, args.timezone)
    if args.attendee:
        body["attendees"] = [{"email": email} for email in args.attendee]
    if getattr(args, "meet", False):
        body["conferenceData"] = {
            "createRequest": {
                "requestId": f"codex-{dt.datetime.now(dt.UTC).strftime('%Y%m%d%H%M%S')}"
            }
        }

    if not patch and ("start" not in body or "end" not in body):
        raise SystemExit("--start and --end are required when creating an event")
    return body


def cmd_create(args: argparse.Namespace) -> None:
    request = (
        service()
        .events()
        .insert(
            calendarId=args.calendar,
            body=event_body_from_args(args),
            conferenceDataVersion=1 if args.meet else 0,
            sendUpdates=args.send_updates,
        )
    )
    event = request.execute()
    print_json(
        {
            "id": event.get("id"),
            "summary": event.get("summary"),
            "htmlLink": event.get("htmlLink"),
            "start": event.get("start"),
            "end": event.get("end"),
        }
    )


def cmd_patch(args: argparse.Namespace) -> None:
    body = event_body_from_args(args, patch=True)
    if not body:
        raise SystemExit("No changes supplied.")
    event = (
        service()
        .events()
        .patch(
            calendarId=args.calendar,
            eventId=args.event_id,
            body=body,
            conferenceDataVersion=1 if args.meet else 0,
            sendUpdates=args.send_updates,
        )
        .execute()
    )
    print_json(
        {
            "id": event.get("id"),
            "summary": event.get("summary"),
            "htmlLink": event.get("htmlLink"),
            "start": event.get("start"),
            "end": event.get("end"),
        }
    )


def cmd_delete(args: argparse.Namespace) -> None:
    service().events().delete(
        calendarId=args.calendar,
        eventId=args.event_id,
        sendUpdates=args.send_updates,
    ).execute()
    print(f"Deleted {args.event_id}")


def add_event_args(parser: argparse.ArgumentParser, require_title: bool) -> None:
    parser.add_argument("--calendar", default="primary")
    parser.add_argument("--title", required=require_title)
    parser.add_argument("--start", help="ISO date or datetime, e.g. 2026-05-27T14:00")
    parser.add_argument("--end", help="ISO date or datetime, e.g. 2026-05-27T14:30")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--location")
    parser.add_argument("--description")
    parser.add_argument("--attendee", action="append", default=[])
    parser.add_argument("--meet", action="store_true", help="Create a Google Meet link")
    parser.add_argument(
        "--send-updates",
        choices=["all", "externalOnly", "none"],
        default="none",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Google Calendar local CLI")
    sub = parser.add_subparsers(required=True)

    auth = sub.add_parser("auth", help="Run the OAuth browser flow")
    auth.set_defaults(func=cmd_auth)

    calendars = sub.add_parser("calendars", help="List available calendars")
    calendars.add_argument("--json", action="store_true")
    calendars.set_defaults(func=cmd_calendars)

    upcoming = sub.add_parser("upcoming", help="List upcoming events")
    upcoming.add_argument("--calendar", default="primary")
    upcoming.add_argument("--days", type=int, default=14)
    upcoming.add_argument("--limit", type=int, default=20)
    upcoming.add_argument("--query")
    upcoming.add_argument("--json", action="store_true")
    upcoming.set_defaults(func=cmd_upcoming)

    create = sub.add_parser("create", help="Create an event")
    add_event_args(create, require_title=True)
    create.set_defaults(func=cmd_create)

    patch = sub.add_parser("patch", help="Patch an existing event")
    patch.add_argument("event_id")
    add_event_args(patch, require_title=False)
    patch.set_defaults(func=cmd_patch)

    delete = sub.add_parser("delete", help="Delete an event")
    delete.add_argument("event_id")
    delete.add_argument("--calendar", default="primary")
    delete.add_argument(
        "--send-updates",
        choices=["all", "externalOnly", "none"],
        default="none",
    )
    delete.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
