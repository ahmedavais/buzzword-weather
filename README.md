# Buzzword weather

Engineering buzzwords and their weather: how often Hacker News mentions each term over the last 2 years, the last
10 years or all time since Hacker News began in 2007, and a forecast for each one from its last 24 months (calm, a
front moving in, a storm passing, clearing skies and more).

Every count is shown as mentions per 10,000 posts, because Hacker News posts about 13 times as much now as in 2008.
In raw counts nearly every buzzword would look bigger today than it ever was.

A toy from [ahmedavais.com](https://ahmedavais.com), built with Streamlit on the
[Hacker News search API by Algolia](https://hn.algolia.com/api). It lives at
[buzzword-weather.streamlit.app](https://buzzword-weather.streamlit.app/).

## Run it

```bash
uv run streamlit run app.py
```

## Refresh the almanac

`almanac.json` records past mention counts for every buzzword in the catalog, and how many items Hacker News had
before each month at the edge of a period, so the app only asks Hacker News about months and quarters newer than the
almanac. Hacker News numbers every story and comment in order, so the newest item before a month tells how many came
before it, and the difference between two months is how many were posted in between. Past counts don't change. To
bring it up to date:

```bash
uv run python record_almanac.py
```

It searches only for counts the almanac lacks, one request at a time with a short pause. A GitHub Action
(`.github/workflows/refresh-almanac.yml`) does this on the 3rd of every month and commits the almanac when it
changed, which redeploys the app. Run it by hand from the Actions tab after adding buzzwords to the catalog.

## Lint it

```bash
uv run ruff check .
```

Ruff with bug-catching rules (`pyproject.toml`); lint only, no formatter.

## Test it

```bash
uv run pytest
```

`uv run pytest -m integration` also checks the real Hacker News search API. CI runs Ruff and the offline tests on every pull
request and push to `main` (`.github/workflows/ci.yml`); Community Cloud deploys `main` on its own.

## Deploy it

Community Cloud deploys `main` on its own, without restarting the app. Streamlit reloads changed modules only for a
visitor who had the page open when the files changed, so everyone else would keep running the old `buzzword_weather`
modules and cached objects next to the new `app.py`, and the app would crash. To prevent that, `app.py` starts every
run by comparing the version of the code on disk with the one in memory. When a deploy changed it, the app drops the
`buzzword_weather` modules and clears Streamlit's caches, so the new code loads clean. No reboot is needed after a
deploy.

## Keep it awake

Community Cloud puts an app to sleep after about 12 hours without visitors, and the next visitor waits through a
cold boot. A GitHub Action (`.github/workflows/keep-awake.yml`) visits the app every 6 hours in a headless browser
and clicks the wake button if the app fell asleep anyway. A plain HTTP request doesn't count as a visit. To visit
it by hand:

```bash
uv run --group keep-awake playwright install chromium
```

```bash
uv run --group keep-awake python keep_awake.py
```

## Sensors

`sensors/` holds tests that watch real data, not logic. They run with the rest of the tests in CI, and the refresh
Action runs them before it commits a new almanac:

- `almanac_coverage_test.py`: every catalog buzzword has every period up to the almanac's latest month, every month
  at the edge of those periods has its item count, and that month is at most two months old

## How it's put together

- `buzzword_weather/periods.py`: complete months and quarters, leaving out the one in progress
- `buzzword_weather/spans.py`: the three spans of history a visitor can choose
- `buzzword_weather/catalog.py`: buzzwords by era, each with the phrase that finds it (SAFe searches for
  "scaled agile")
- `buzzword_weather/hacker_news.py`: mentions of a term per period, and how many items were posted before a month,
  over `http_client.py`; both offer `create()` and `create_null()` so tests run without the network
- `buzzword_weather/almanac.py`, `recorder.py`: recorded counts, and filling in the missing ones
- `buzzword_weather/barometer.py`: mentions per 10,000 posts from the almanac, asking Hacker News only for what it
  lacks
- `buzzword_weather/forecast.py`: the weather of a term from its mentions per 10,000 posts in the last 24 months,
  against its busiest quarter ever: clear skies, first clouds, a front moving in, a storm overhead, a storm passing,
  clearing skies, or a steady breeze
- `buzzword_weather/defaults.py`: the starting buzzwords, picked from the curated `DEFAULT_POOL` in
  `catalog.py`: in pool order, at most two in one kind of weather, so the first view stays varied as the weather
  changes
- `buzzword_weather/code_version.py`: the version of the package's code, from its source files
- `app.py`: the Streamlit page; it reloads the code after a deploy, then only renders
- `keep_awake.py`: visits the deployed app so Community Cloud doesn't put it to sleep
