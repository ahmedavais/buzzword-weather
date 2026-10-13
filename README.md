# Buzzword weather

Engineering buzzwords and their weather: how often Hacker News mentions each term, month by month, and a forecast
for each one (calm, a front moving in, a storm passing, or a steady breeze).

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

- `buzzword_weather/months.py`: the complete months to count, leaving out the month in progress
- `buzzword_weather/hacker_news.py`: mentions of a term per month, over `http_client.py`; both offer `create()`
  and `create_null()` so tests run without the network
- `buzzword_weather/forecast.py`: the weather of a term from its monthly mentions
- `app.py`: the Streamlit page; it only renders
