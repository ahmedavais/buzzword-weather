# Buzzword weather

Engineering buzzwords and their weather: how often Hacker News mentions each term over the last 2 years, the last
10 years or since 2007, and a forecast for each one from its last 24 months (calm, a front moving in, a storm
passing, or a steady breeze).

A toy from [ahmedavais.com](https://ahmedavais.com), built with Streamlit on the
[Hacker News search API by Algolia](https://hn.algolia.com/api).

## Run it

```bash
uv run streamlit run app.py
```

## Test it

```bash
uv run pytest
```

`uv run pytest -m integration` also checks the real Hacker News search API.

## How it's put together

- `buzzword_weather/periods.py`: complete months and quarters, leaving out the one in progress
- `buzzword_weather/spans.py`: the three spans of history a visitor can choose
- `buzzword_weather/catalog.py`: buzzwords by era, each with the phrase that finds it (SAFe searches for
  "scaled agile")
- `buzzword_weather/hacker_news.py`: mentions of a term per period, over `http_client.py`; both offer `create()`
  and `create_null()` so tests run without the network
- `buzzword_weather/forecast.py`: the weather of a term from its monthly mentions
- `app.py`: the Streamlit page; it only renders
