### `bot.py`

```python
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TARGET_URL = os.environ["TARGET_URL"]
SUBMISSION_LINK = os.environ["SUBMISSION_LINK"]

TEXTBOX_SELECTOR = os.getenv(
    "TEXTBOX_SELECTOR",
    "input[name='url']"
)

SUBMIT_SELECTOR = os.getenv(
    "SUBMIT_SELECTOR",
    "button[type='submit']"
)

COOLDOWN_SECONDS = 32 * 60


def run():
    print("=" * 60)
    print("Starting browser automation")
    print("=" * 60)

    print(f"Target URL: {TARGET_URL}")
    print(f"Textbox selector: {TEXTBOX_SELECTOR}")
    print(f"Submit selector: {SUBMIT_SELECTOR}")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = browser.new_page(
            viewport={
                "width": 1280,
                "height": 900,
            }
        )

        try:
            print("\nOpening target page...")

            page.goto(
                TARGET_URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            print("Page loaded.")
            print(f"Current URL: {page.url}")

            print("\nLooking for textbox...")
            print(f"Selector: {TEXTBOX_SELECTOR}")

            textbox = page.locator(
                TEXTBOX_SELECTOR
            ).first

            textbox.wait_for(
                state="visible",
                timeout=30_000,
            )

            print("Textbox found.")

            textbox.fill(
                SUBMISSION_LINK
            )

            print("Link entered successfully.")

            print("\nLooking for submit button...")
            print(f"Selector: {SUBMIT_SELECTOR}")

            submit_button = page.locator(
                SUBMIT_SELECTOR
            ).first

            submit_button.wait_for(
                state="visible",
                timeout=30_000,
            )

            print("Submit button found.")

            submit_button.click()

            print("Form submitted.")

            page.wait_for_timeout(5_000)

            print("Submission processing finished.")

        except PlaywrightTimeoutError as error:

            print("\n" + "=" * 60)
            print("PLAYWRIGHT TIMEOUT")
            print("=" * 60)

            print(f"Textbox selector: {TEXTBOX_SELECTOR}")
            print(f"Submit selector: {SUBMIT_SELECTOR}")
            print(f"Current URL: {page.url}")

            # Save a screenshot for debugging.
            try:
                page.screenshot(
                    path="automation-error.png",
                    full_page=True
                )
                print("Saved automation-error.png")
            except Exception as screenshot_error:
                print(
                    f"Could not save screenshot: "
                    f"{screenshot_error}"
                )

            # Save page HTML for debugging.
            try:
                with open(
                    "automation-error.html",
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(page.content())

                print("Saved automation-error.html")

            except Exception as html_error:
                print(
                    f"Could not save HTML: {html_error}"
                )

            raise error

        finally:
            browser.close()

    print("\nStarting 32-minute cooldown...")

    remaining = COOLDOWN_SECONDS

    while remaining > 0:

        minutes = remaining // 60
        seconds = remaining % 60

        print(
            f"Cooldown remaining: "
            f"{minutes:02d}:{seconds:02d}"
        )

        time.sleep(
            min(60, remaining)
        )

        remaining -= 60

    print("\nCooldown finished.")


if __name__ == "__main__":
    run()
```
