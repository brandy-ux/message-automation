# GitHub Form Automation — Fixed

This version fixes the original failure where Playwright waited 30 seconds for:

`input[name='url']`

and the element was not visible.

## What changed

- The textbox selector is no longer forced to `input[name='url']`.
- The bot tries several common URL/link selectors automatically.
- It waits for client-side JavaScript rendering.
- It checks if the form is inside an iframe.
- It auto-detects common submit buttons.
- It produces `automation-error.png` and `automation-error.html` when detection fails.
- GitHub Actions uploads those diagnostics as an artifact when the job fails.
- Playwright is installed with `python -m playwright install --with-deps chromium`.

## Required GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions → Secrets

Required:

- `TARGET_URL` — page to open
- `SUBMISSION_LINK` — value to enter into the form

### Important

Delete these old repository secrets if you created them:

- `TEXTBOX_SELECTOR`
- `SUBMIT_SELECTOR`

The fixed bot auto-detects them. Keeping an incorrect `TEXTBOX_SELECTOR` can make the bot try the wrong element first.

If auto-detection still cannot find the controls, you can add the correct selectors back as secrets.

## Run

Go to:

Actions → Form Automation → Run workflow

If it fails again, open the failed run and download:

`automation-diagnostics`

The HTML and screenshot will show what the target page actually rendered in GitHub Actions.
