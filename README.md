# Buzzword weather

Engineering buzzwords and their weather: a current forecast for each selected term, plus its Hacker News history over
the last 2 years, the last 10 years or all time since Hacker News began in 2007. The forecast reads each term's last
24 months as calm, a front moving in, a storm passing, clearing skies and more.

Above the forecast, "This week on HN" names the words Hacker News story titles used far more than usual last week:
up to 10 words and two-word phrases at twice their rate over the 12 weeks before or more, each with its heat (warm,
heatwave, wildfire, or a new front for a word under 3 stories in each of those 12 weeks) and a few of the titles that used it.

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

## Record the weekly words

`weekly_words.json` records, for each of the last 13 finished weeks (Monday to Sunday, UTC), how many story titles
Hacker News had, how many of them used each word or two-word phrase that at least 3 stories used, and that week's
risers with up to 3 example titles. Common English words, "Show HN" and the like, bracketed tags, numbers, money
amounts, CVE ids and the words of a story's own site are left out. A word whose stories are mostly the stories of a
word ranked above it is skipped, so one news story takes one row. Risers are ranked as each week is recorded; after
changing how they're ranked, empty `weekly_words.json` and run the Action to record the weeks again. Story titles come from the Hacker News search in 6-hour slices, and a slice
holding more stories than one answer returns is halved until none are lost. To record the weeks the file lacks:

```bash
uv run python record_weekly_words.py
```

A GitHub Action (`.github/workflows/record-weekly-words.yml`) does this every Monday: it checks the real Hacker News
search with the integration tests, records, runs the tests and commits the file, which redeploys the app. Then it
looks for words that rose in at least 3 of the last 4 weeks and aren't in the catalog, and opens a pull request for
each that adds it to the catalog in the "rising" era (`find_candidates.py`, `add_candidate.py`). A word whose pull
request was closed is never proposed again. GitHub doesn't run CI on pull requests the Action opens, so the Action
runs the tests itself before opening one; push a commit to a candidate's branch to run CI on it.

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
- `weekly_words_test.py`: the weekly words reach the week before last, every week counted at least 2,000 titles, and
  no common word or number ever ranked; skipped while the record is empty, until the backfill is due on 16 Nov 2026

## How it's put together

- `buzzword_weather/periods.py`: complete months, quarters and ISO weeks, leaving out the one in progress
- `buzzword_weather/spans.py`: the three spans of history a visitor can choose
- `buzzword_weather/catalog.py`: buzzwords by era, each with the phrase that finds it (SAFe searches for
  "scaled agile")
- `buzzword_weather/hacker_news.py`: mentions of a term per period, and how many items were posted before a month,
  and the stories posted in a window, over `http_client.py`; both offer `create()` and `create_null()` so tests run without the network
- `buzzword_weather/almanac.py`, `recorder.py`: recorded counts, and filling in the missing ones
- `buzzword_weather/barometer.py`: mentions per 10,000 posts from the almanac, asking Hacker News only for what it
  lacks
- `buzzword_weather/forecast.py`: the weather of a term from its mentions per 10,000 posts in the last 24 months,
  against its busiest quarter ever: clear skies, first clouds, a front moving in, a storm overhead, a storm passing,
  clearing skies, or a steady breeze
- `buzzword_weather/defaults.py`: the starting buzzwords, picked from the curated `DEFAULT_POOL` in
  `catalog.py`: in pool order, at most two in one kind of weather, so the first view stays varied as the weather
  changes
- `buzzword_weather/chart.py`: one buzzword's history chart, with no zoom or pan so scrolling past it on a phone
  scrolls the page; hovering or tapping shows the nearest period
- `buzzword_weather/forecast_card.py`: the current weather card for a buzzword
- `buzzword_weather/titles.py`: the words and two-word phrases of a story title, without the noise
- `buzzword_weather/weekly_words.py`, `week_recorder.py`: the weekly record, and filling in the missing weeks
- `buzzword_weather/rising.py`: a week's risers against the 12 weeks before, and their heat
- `buzzword_weather/this_week.py`: the rows of "This week on HN"
- `buzzword_weather/story_link.py`: a link to a story's discussion, with its title escaped so it can't break the link,
  mention anyone on GitHub or link an issue
- `buzzword_weather/candidates.py`: words that keep rising, proposed for the catalog
- `buzzword_weather/code_version.py`: the version of the package's code, from its source files
- `app.py`: the Streamlit page; it reloads the code after a deploy, then only renders
- `keep_awake.py`: visits the deployed app so Community Cloud doesn't put it to sleep
