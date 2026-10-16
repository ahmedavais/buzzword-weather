import logging
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from buzzword_weather.almanac import Almanac
from buzzword_weather.barometer import Barometer
from buzzword_weather.catalog import CATALOG, DEFAULT_POOL, search_phrase_for
from buzzword_weather.defaults import pick_defaults
from buzzword_weather.forecast import Weather, weather_of
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period
from buzzword_weather.spans import Span

MOST_TERMS = 7
CACHED_SERIES = 500
ALMANAC = Path(__file__).parent / "almanac.json"
CHART_HEIGHT = 180


@st.cache_resource
def barometer() -> Barometer:
    almanac = Almanac.from_json(ALMANAC.read_text()) if ALMANAC.exists() else Almanac()
    return Barometer(almanac, HackerNews.create())


@st.cache_data(max_entries=CACHED_SERIES, show_spinner=False)
def mentions_across(phrase: str, periods: tuple[Period, ...]) -> list[int]:
    return barometer().mentions(phrase, list(periods))


def weather_for(name: str) -> Weather:
    phrase = search_phrase_for(name)
    return weather_of(mentions_across(phrase, recent_months), mentions_across(phrase, all_quarters))


def starting_buzzwords() -> list[str]:
    try:
        return pick_defaults([(name, weather_for(name)) for name in DEFAULT_POOL], most=MOST_TERMS)
    except Exception:
        logging.getLogger(__name__).exception("Couldn't read the pool's weather; starting with the pool's first buzzwords")
        return DEFAULT_POOL[:MOST_TERMS]


recent_months = tuple(Span.LAST_2_YEARS.periods_before(date.today()))
all_quarters = tuple(Span.ALL_TIME.periods_before(date.today()))

st.set_page_config(page_title="Buzzword weather", page_icon="🌦️")
st.title("🌦️ Buzzword weather")
st.write("How often Hacker News talks about each engineering buzzword over the years, and the weather it's in now.")

terms = st.multiselect(
    "Buzzwords",
    options=[buzzword.name for buzzword in CATALOG],
    default=starting_buzzwords(),
    max_selections=MOST_TERMS,
    accept_new_options=True,
    placeholder="Pick or type a buzzword",
)

span = st.segmented_control("History", options=list(Span), format_func=lambda span: span.label, default=Span.LAST_2_YEARS)
span = span or Span.LAST_2_YEARS
periods = tuple(span.periods_before(date.today()))

if not terms:
    st.info("Pick a buzzword, or type your own, to see its weather.")
    st.stop()

try:
    with st.spinner("Reading the barometer…"):
        mentions = {term: mentions_across(search_phrase_for(term), periods) for term in terms}
        weathers = {term: weather_for(term) for term in terms}
except Exception:
    logging.getLogger(__name__).exception("Hacker News search failed")
    st.error("Hacker News search didn't answer just now. Try again in a minute.")
    st.stop()

period_starts = pd.to_datetime([period.starts_at for period in periods], unit="s")
for term, counts in mentions.items():
    weather = weathers[term]
    st.markdown(f"#### {weather.icon} {term}: {weather.forecast}")
    st.line_chart(pd.Series(counts, index=period_starts, name=term), y_label=f"Mentions a {span.step}", height=CHART_HEIGHT)

st.caption(
    f"Counts Hacker News stories and comments that use the exact phrase (SAFe searches for \"scaled agile\", SOA for "
    f"\"service oriented architecture\"), {periods[0].label} to {periods[-1].label}, "
    "through the Hacker News search by Algolia. The forecast reads the last two years month by month, against each "
    "buzzword's busiest quarter ever. The month or "
    "quarter in progress is left out. Hacker News talks for one corner "
    "of the industry, so treat it as one weather station. A toy from [ahmedavais.com](https://ahmedavais.com)."
)
