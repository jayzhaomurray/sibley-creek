# Audit hook setup

The pre-push hook at `.githooks/pre-push` blocks pushes that touch substantial
paths (defined in `.audit-config.json`) without a matching audit-findings file
committed in the same push range.

## Enable the hook (run once per clone)

```sh
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

On Windows under Git Bash, `chmod` sets the executable bit correctly.
Under PowerShell you do not need to run `chmod`; Git Bash handles it.

## Skipping the check

If an audit is genuinely not warranted for a given push:

```sh
git push --no-verify
```

Use sparingly. The hook exists as an enforcement floor, not a speed bump.

## Configuration

Edit `.audit-config.json` at the repo root to add or remove paths.
The `substantial_extensions_in_pipeline` and `model_filename_patterns` fields
are documented there as future extensions; they are not enforced in v1.
