import logging
import sys
from datetime import date
from pathlib import Path

import streamlit as st

from buzzword_weather.code_version import code_version

CODE = Path(__file__).parent / "buzzword_weather"


@st.cache_resource
def code_in_memory() -> dict[str, str]:
    return {}


def forget_loaded(package: str) -> None:
    for name in [name for name in sys.modules if name == package or name.startswith(f"{package}.")]:
        del sys.modules[name]


def reload_code_after_a_deploy() -> None:
    deployed = code_version(CODE)
    if code_in_memory().get("version") != deployed:
        forget_loaded(CODE.name)
        st.cache_data.clear()
        st.cache_resource.clear()
        code_in_memory()["version"] = deployed


reload_code_after_a_deploy()

from buzzword_weather.almanac import Almanac
from buzzword_weather.barometer import Barometer
from buzzword_weather.catalog import CATALOG, DEFAULT_POOL, search_phrase_for
from buzzword_weather.chart import MOST_LINES, rates_chart
from buzzword_weather.defaults import pick_defaults
from buzzword_weather.forecast import Weather, weather_of
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period
from buzzword_weather.spans import Span

CACHED_SERIES = 500
ALMANAC = Path(__file__).parent / "almanac.json"


@st.cache_resource
def barometer() -> Barometer:
    almanac = Almanac.from_json(ALMANAC.read_text()) if ALMANAC.exists() else Almanac()
    return Barometer(almanac, HackerNews.create())


@st.cache_data(max_entries=CACHED_SERIES, show_spinner=False)
def mention_rates_across(phrase: str, periods: tuple[Period, ...]) -> list[float]:
    return barometer().mention_rates(phrase, list(periods))


def weather_for(name: str) -> Weather:
    phrase = search_phrase_for(name)
    return weather_of(mention_rates_across(phrase, recent_months), mention_rates_across(phrase, all_quarters))


def starting_buzzwords() -> list[str]:
    try:
        return pick_defaults([(name, weather_for(name)) for name in DEFAULT_POOL], most=MOST_LINES)
    except Exception:
        logging.getLogger(__name__).exception("Couldn't read the pool's weather; starting with the pool's first buzzwords")
        return DEFAULT_POOL[:MOST_LINES]


recent_months = tuple(Span.LAST_2_YEARS.periods_before(date.today()))
all_quarters = tuple(Span.ALL_TIME.periods_before(date.today()))

st.set_page_config(page_title="Buzzword weather", page_icon="🌦️")
st.title("🌦️ Buzzword weather")
st.write("How often Hacker News talks about each engineering buzzword over the years, and the weather it's in now.")

terms = st.multiselect(
    "Buzzwords",
    options=[buzzword.name for buzzword in CATALOG],
    default=starting_buzzwords(),
    max_selections=MOST_LINES,
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
        mention_rates = {term: mention_rates_across(search_phrase_for(term), periods) for term in terms}
        weathers = {term: weather_for(term) for term in terms}
except Exception:
    logging.getLogger(__name__).exception("Hacker News search failed")
    st.error("Hacker News search didn't answer just now. Try again in a minute.")
    st.stop()

st.markdown("  \n".join(f"{weathers[term].icon} {term}: {weathers[term].forecast}" for term in terms))
st.altair_chart(rates_chart(mention_rates, list(periods)), width="stretch")

st.caption(
    f"Counts Hacker News stories and comments that use the exact phrase (SAFe searches for \"scaled agile\", SOA for "
    f"\"service oriented architecture\"), {periods[0].label} to {periods[-1].label}, through the Hacker News search "
    f"by Algolia. Each {span.step} shows mentions per 10,000 posts, so a busier Hacker News doesn't make every "
    "buzzword look bigger. The forecast reads the last two years month by month, against each buzzword's busiest "
    "quarter ever. The month or quarter in progress is left out. Hacker News talks for one corner of the industry, "
    "so treat it as one weather station. A toy from [ahmedavais.com](https://ahmedavais.com)."
)
