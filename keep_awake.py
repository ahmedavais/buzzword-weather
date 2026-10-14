from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

APP_URL = "https://buzzword-weather.streamlit.app/"
APP_TITLE = "Buzzword weather"
WAKE_BUTTON_TEXT = "Yes, get this app back up"
WAKE_BUTTON_GRACE_MS = 15_000
WAKE_UP_TIMEOUT_MS = 180_000


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL)
        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        try:
            wake_button.click(timeout=WAKE_BUTTON_GRACE_MS)
            print("the app was asleep, woke it up", flush=True)
        except PlaywrightTimeoutError:
            print("the app was awake", flush=True)
        page.wait_for_function(f"document.title.startsWith('{APP_TITLE}')", timeout=WAKE_UP_TIMEOUT_MS)
        print(f"visited {page.title()}", flush=True)
        browser.close()


if __name__ == "__main__":
    main()
