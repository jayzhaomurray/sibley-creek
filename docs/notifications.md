# Sibley Creek Notification System -- Operator Reference (Phase 1)

Phase 1 is pure monitoring. No commits, no review UI. The system
detects three event types and fires email; a durable ledger records
every event for audit.

---

## Subject-line severity taxonomy

Every notification subject is prefixed with one of:

| severity        | prefix                        | meaning                                  |
|-----------------|-------------------------------|------------------------------------------|
| fyi             | [Sibley Creek Update]         | informational; no action expected        |
| review          | [Sibley Creek Review]         | inspect the section; spot-check charts   |
| alert           | [Sibley Creek Alert]          | something failed; check logs             |
| action_required | [Sibley Creek Action Required]| reserved for Phase 2+ escalations        |

---

## Event types

### failure
Fires when a pipeline entry point raises an unhandled exception.

- Severity: alert
- Dedupe window: 4 hours per (entry_point, exception_class)
- Dedupe key pattern: `failure:<entry_point>:<ExceptionClass>`
- Entry points monitored: `build_macro`, `build_financial`, `panel_data`

Note: GHA workflow failures (including build-gate check failures such as
check_panel_data_wired.mjs, check_tk_in_dist.mjs, check_sections_slug_alignment.mjs)
are caught by the `notify-on-failure` step in deploy.yml, which uses the
dawidd6/action-send-mail action. That step fires independently of the Python
notification substrate.

### new_vintage
Fires when a macro data series advances its asOfISO field in panel_data.

- Severity: review
- Dedupe window: 24 hours per (section, max asOfISO)
- Dedupe key pattern: `new_vintage:<section>:<asOfISO>`
- One notification per section per refresh cycle, batched across panels.
- Financial sections (markets, financial) are excluded.

### news_feed_update
Fires when new items appear in data/derived/news_feed_cache.json vs the
last git-committed version.

- Severity: fyi
- Dedupe window: 1 hour per refresh-timestamp bucket (minute-level)
- Dedupe key pattern: `news_feed:<YYYY-MM-DDTHH:MM>`

---

## Dedupe windows

| event_type       | window   |
|------------------|----------|
| failure          | 4 hours  |
| new_vintage      | 24 hours |
| news_feed_update | 1 hour   |

---

## Event ledger

Location: `data/derived/notification_events.json`

Append-only JSON array. Each record:

```json
{
  "id":           "evt_<8-char hex>",
  "timestamp":    "2026-05-28T14:32:00Z",
  "type":         "failure | new_vintage | news_feed_update",
  "severity":     "fyi | review | alert | action_required",
  "subject":      "[Sibley Creek Review] New inflation data is live (April 2026)",
  "body_preview": "first 200 chars of the email body",
  "dedupe_key":   "new_vintage:inflation:2026-04-01",
  "details":      { },
  "sent":         true,
  "dry_run":      false,
  "error":        null
}
```

---

## GitHub Secrets -- one-time setup required

Jay must configure these in the repository settings under
Settings > Secrets and variables > Actions > Repository secrets.

| Secret name  | Value                                          |
|--------------|------------------------------------------------|
| SMTP_HOST    | Your SMTP relay host (e.g. smtp.gmail.com)     |
| SMTP_PORT    | Port number (587 for STARTTLS, 465 for SSL)    |
| SMTP_USER    | SMTP login username                            |
| SMTP_PASS    | SMTP login password or app password            |
| SMTP_FROM    | Sending address (e.g. jayzhaomurray@gmail.com)      |

These are referenced by both the Python notification substrate
(pipeline/notifications/send.py) and the GHA deploy.yml workflow-failure
step (dawidd6/action-send-mail@v3).

---

## Silencing a noisy notification type

Set the environment variable (locally or in GHA):

    SIBLEY_NOTIFICATIONS_DISABLED_TYPES=failure,new_vintage

Comma-separated list of type strings. Silenced types are logged but not
sent and not recorded in the ledger.

For GHA: add the env var to the relevant step or job in deploy.yml or
the data-build workflows.

---

## Dry-run mode

    SIBLEY_NOTIFICATIONS_DRY_RUN=1

Writes email content to `data/derived/notification_dry_run.txt` instead
of sending. The ledger is still updated. Use this for local testing.
Never set SIBLEY_NOTIFICATIONS_DRY_RUN=0 in CI until SMTP secrets are
configured and you want to activate live sends.

---

## GHA workflow-failure email step

The deploy.yml build job includes a final step that runs only on failure:

```yaml
- name: Notify on build failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: ${{ secrets.SMTP_HOST }}
    server_port: ${{ secrets.SMTP_PORT }}
    username: ${{ secrets.SMTP_USER }}
    password: ${{ secrets.SMTP_PASS }}
    subject: "[Sibley Creek Alert] Deploy build failed (${{ github.workflow }})"
    to: jayzhaomurray@gmail.com
    from: ${{ secrets.SMTP_FROM }}
    body: |
      The Sibley Creek GitHub Actions deploy build failed.

      Workflow: ${{ github.workflow }}
      Run: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}

      This covers all build-gate check failures (check_panel_data_wired,
      check_tk_in_dist, check_sections_slug_alignment, Astro build errors,
      text overlap failures, etc.).
```

This step covers ALL build-gate failures (including the JS check scripts)
because any failing step in the `build` job causes if: failure() to trigger.
The Python notification substrate does not need separate wiring for the JS
build gates.
