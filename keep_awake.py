import sys
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from buzzword_weather.waking import TRIES, awake_within_tries

APP_URL = "https://buzzword-weather.streamlit.app/"
APP_TITLE = "Buzzword weather"
WAKE_BUTTON_TEXT = "Yes, get this app back up"
WAKE_BUTTON_GRACE_MS = 15_000
TRY_TIMEOUT_MS = 60_000


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL)
        awake = awake_within_tries(lambda: shows_the_app(page), lambda: reload(page))
        print(f"visited {page.title()}" if awake else f"the app didn't come up after {TRIES} tries", flush=True)
        browser.close()
    if not awake:
        sys.exit(1)


def shows_the_app(page: Page) -> bool:
    try:
        wake_if_asleep(page)
        page.wait_for_function(f"document.title.startsWith('{APP_TITLE}')", timeout=TRY_TIMEOUT_MS)
        return True
    except PlaywrightError as error:
        print(f"not up yet: {error.message.splitlines()[0]}", flush=True)
        return False


def wake_if_asleep(page: Page) -> None:
    try:
        page.get_by_role("button", name=WAKE_BUTTON_TEXT).click(timeout=WAKE_BUTTON_GRACE_MS)
        print("the app was asleep, clicked the wake button", flush=True)
    except PlaywrightTimeoutError:
        pass


def reload(page: Page) -> None:
    print("reloading the app", flush=True)
    try:
        page.goto(f"{APP_URL}?reload={time.time_ns()}")
    except PlaywrightError as error:
        print(f"the reload failed, trying again: {error.message.splitlines()[0]}", flush=True)


if __name__ == "__main__":
    main()
