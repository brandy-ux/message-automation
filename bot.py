import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TARGET_URL = os.environ["TARGET_URL"]
SUBMISSION_LINK = os.environ["SUBMISSION_LINK"]

# Optional overrides. Leave these secrets unset unless the page needs a specific selector.
TEXTBOX_SELECTOR = os.getenv("TEXTBOX_SELECTOR", "").strip()
SUBMIT_SELECTOR = os.getenv("SUBMIT_SELECTOR", "").strip()

COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "1920"))
ACTION_TIMEOUT = 45_000


def first_visible(locator, timeout=ACTION_TIMEOUT):
    """Return the first visible element from a locator, or None."""
    try:
        count = locator.count()
    except Exception:
        return None

    for i in range(count):
        item = locator.nth(i)
        try:
            if item.is_visible(timeout=2_000):
                return item
        except Exception:
            pass

    try:
        locator.first.wait_for(state="visible", timeout=timeout)
        return locator.first
    except Exception:
        return None


def find_textbox(page):
    # If explicitly configured, try it first.
    selectors = []
    if TEXTBOX_SELECTOR:
        selectors.append(TEXTBOX_SELECTOR)

    # Common URL/link form controls.
    selectors += [
        "input[name='url']",
        "input[name='link']",
        "input[name='website']",
        "input[name='target']",
        "input[type='url']",
        "input[type='text']",
        "textarea[name='url']",
        "textarea",
        "[contenteditable='true']",
    ]

    for selector in selectors:
        try:
            loc = page.locator(selector)
            found = first_visible(loc)
            if found:
                print(f"Textbox found with selector: {selector}")
                return found
        except Exception as e:
            print(f"Selector skipped: {selector} ({e})")

    # Search inside iframes too.
    for frame in page.frames:
        if frame == page.main_frame:
            continue

        for selector in selectors:
            try:
                found = first_visible(frame.locator(selector), timeout=10_000)
                if found:
                    print(f"Textbox found inside iframe with selector: {selector}")
                    return found
            except Exception:
                pass

    return None


def find_submit(page):
    selectors = []
    if SUBMIT_SELECTOR:
        selectors.append(SUBMIT_SELECTOR)

    selectors += [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Submit')",
        "button:has-text('Send')",
        "button:has-text('Continue')",
        "button:has-text('Go')",
        "[role='button']:has-text('Submit')",
    ]

    for selector in selectors:
        try:
            loc = page.locator(selector)
            found = first_visible(loc)
            if found:
                print(f"Submit button found with selector: {selector}")
                return found
        except Exception as e:
            print(f"Submit selector skipped: {selector} ({e})")

    for frame in page.frames:
        if frame == page.main_frame:
            continue
        for selector in selectors:
            try:
                found = first_visible(frame.locator(selector), timeout=10_000)
                if found:
                    print(f"Submit button found inside iframe with selector: {selector}")
                    return found
            except Exception:
                pass

    return None


def save_diagnostics(page):
    try:
        page.screenshot(path="automation-error.png", full_page=True)
        print("Saved automation-error.png")
    except Exception as e:
        print(f"Could not save screenshot: {e}")

    try:
        with open("automation-error.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Saved automation-error.html")
    except Exception as e:
        print(f"Could not save HTML: {e}")

    try:
        inputs = page.locator("input, textarea, button, select").all()
        print(f"Detected {len(inputs)} form controls on the main page.")
        for i, el in enumerate(inputs[:30]):
            try:
                print(
                    f"  [{i}] tag={el.evaluate('(e) => e.tagName')} "
                    f"type={el.get_attribute('type')} "
                    f"name={el.get_attribute('name')} "
                    f"id={el.get_attribute('id')} "
                    f"placeholder={el.get_attribute('placeholder')} "
                    f"text={(el.inner_text() or '')[:80]}"
                )
            except Exception:
                pass
    except Exception:
        pass

    print("Frames:")
    for i, frame in enumerate(page.frames):
        print(f"  [{i}] {frame.url}")


def run():
    print("=" * 60)
    print("Starting browser automation")
    print("=" * 60)
    print(f"Target URL: {TARGET_URL}")
    print(f"Textbox selector override: {TEXTBOX_SELECTOR or '(auto-detect)'}")
    print(f"Submit selector override: {SUBMIT_SELECTOR or '(auto-detect)'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=False,
        )
        page = context.new_page()
        page.set_default_timeout(ACTION_TIMEOUT)
        page.set_default_navigation_timeout(60_000)

        try:
            print("Opening target page...")
            response = page.goto(
                TARGET_URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            print(f"Page loaded. HTTP status: {response.status if response else 'unknown'}")
            print(f"Current URL: {page.url}")

            # Give client-side JavaScript a little time to render the form.
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except PlaywrightTimeoutError:
                print("networkidle timed out; continuing because the page is already loaded.")

            page.wait_for_timeout(2_000)

            print("Looking for textbox...")
            textbox = find_textbox(page)

            if textbox is None:
                save_diagnostics(page)
                raise RuntimeError(
                    "Could not find a visible textbox. "
                    "Check automation-error.html/png and the page's actual form selector."
                )

            textbox.fill(SUBMISSION_LINK)
            print("Link entered successfully.")

            print("Looking for submit button...")
            submit_button = find_submit(page)

            if submit_button is None:
                save_diagnostics(page)
                raise RuntimeError(
                    "Could not find a visible submit button. "
                    "Check automation-error.html/png and the page's actual button selector."
                )

            submit_button.click()
            print("Form submitted.")

            # Allow redirects/toasts/result pages to appear.
            page.wait_for_timeout(5_000)
            print(f"After submission URL: {page.url}")
            print("Submission step completed.")

        except (PlaywrightTimeoutError, Exception) as e:
            print("=" * 60)
            print("AUTOMATION ERROR")
            print("=" * 60)
            print(str(e))
            print(f"Current URL: {page.url}")
            save_diagnostics(page)
            raise
        finally:
            context.close()
            browser.close()

    if COOLDOWN_SECONDS > 0:
        print(f"Starting {COOLDOWN_SECONDS // 60}-minute cooldown.")
        remaining = COOLDOWN_SECONDS
        while remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            print(f"Cooldown: {minutes}m {seconds}s remaining...")
            sleep_for = min(60, remaining)
            time.sleep(sleep_for)
            remaining -= sleep_for

        print("Cooldown finished.")


if __name__ == "__main__":
    run()
