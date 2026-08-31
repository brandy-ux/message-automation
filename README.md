# GitHub Form Automation

Playwright-based browser automation for authorized form testing and repetitive workflows.

## GitHub Secrets

Add these under:
Repository → Settings → Secrets and variables → Actions

- `TARGET_URL` — page to open
- `SUBMISSION_LINK` — link to enter
- `TEXTBOX_SELECTOR` — textbox CSS selector
- `SUBMIT_SELECTOR` — submit button CSS selector

Example selectors:

```text
input[name="url"]
button[type="submit"]
```

## Run

Go to Actions → Form Automation → Run workflow.

The automation opens the target page, enters the configured link, submits the form, then waits approximately 32 minutes.

Never hard-code passwords, API keys, cookies, or session tokens. Use GitHub Secrets for sensitive values.
