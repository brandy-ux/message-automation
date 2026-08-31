import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TARGET_URL = os.environ["TARGET_URL"]
SUBMISSION_LINK = os.environ["SUBMISSION_LINK"]

TEXTBOX_SELECTOR = os.getenv("TEXTBOX_SELECTOR", "input[type='text']")
SUBMIT_SELECTOR = os.getenv("SUBMIT_SELECTOR", "button[type='submit']")

COOLDOWN_SECONDS = 32 * 60


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        try:
            print(f"Opening: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60_000)

            textbox = page.locator(TEXTBOX_SELECTOR).first
            textbox.wait_for(state="visible", timeout=30_000)
            textbox.fill(SUBMISSION_LINK)
            print("Link entered successfully.")

            submit_button = page.locator(SUBMIT_SELECTOR).first
            submit_button.wait_for(state="visible", timeout=30_000)
            submit_button.click()
            print("Form submitted.")

            page.wait_for_timeout(5_000)
            print("Submission completed.")

        except PlaywrightTimeoutError as e:
            print(f"Timed out while interacting with the page: {e}")
            raise
        finally:
            browser.close()

    print("Starting 32-minute cooldown.")
    for remaining in range(COOLDOWN_SECONDS, 0, -60):
        minutes = remaining // 60
        print(f"Cooldown: approximately {minutes} minutes remaining...")
        time.sleep(min(60, remaining))

    print("Cooldown finished.")


if __name__ == "__main__":
    run()
