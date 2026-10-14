# Buzzword weather

Engineering buzzwords and their weather: how often Hacker News mentions each term over the last 2 years, the last
10 years or since 2007, and a forecast for each one from its last 24 months (calm, a front moving in, a storm
passing, clearing skies and more).

A toy from [ahmedavais.com](https://ahmedavais.com), built with Streamlit on the
[Hacker News search API by Algolia](https://hn.algolia.com/api).

## Run it

```bash
uv run streamlit run app.py
```

## Refresh the almanac

`almanac.json` records past mention counts for every buzzword in the catalog, so the app only searches Hacker News
for months and quarters newer than the almanac. Past counts don't change. To bring it up to date:

```bash
uv run python record_almanac.py
```

It searches only for counts the almanac lacks, one request at a time with a short pause.

## Test it

```bash
uv run pytest
```

`uv run pytest -m integration` also checks the real Hacker News search API. CI runs the offline tests on every pull
request and push to `main` (`.github/workflows/ci.yml`); Community Cloud deploys `main` on its own.

## How it's put together

- `buzzword_weather/periods.py`: complete months and quarters, leaving out the one in progress
- `buzzword_weather/spans.py`: the three spans of history a visitor can choose
- `buzzword_weather/catalog.py`: buzzwords by era, each with the phrase that finds it (SAFe searches for
  "scaled agile")
- `buzzword_weather/hacker_news.py`: mentions of a term per period, over `http_client.py`; both offer `create()`
  and `create_null()` so tests run without the network
- `buzzword_weather/almanac.py`, `recorder.py`: recorded counts, and filling in the missing ones
- `buzzword_weather/barometer.py`: mentions from the almanac, searching Hacker News only for what it lacks
- `buzzword_weather/forecast.py`: the weather of a term from its last 24 months against its busiest quarter since
  2007: clear skies, first clouds, a front moving in, a storm overhead, a storm passing, clearing skies, or a steady
  breeze
- `app.py`: the Streamlit page; it only renders
