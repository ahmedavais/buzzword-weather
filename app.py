from datetime import date

import pandas as pd
import streamlit as st

from buzzword_weather.forecast import weather_of
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Period
from buzzword_weather.spans import Span

STARTING_TERMS = ["vibe coding", "harness engineering", "loop engineering", "ralph loop", "platform engineering"]
MORE_TERMS = ["devops", "microservices", "scrum", "context engineering", "prompt engineering", "agentic"]
MOST_TERMS = 7
CACHED_COUNTS = 50_000
CHART_HEIGHT = 180


@st.cache_data(max_entries=CACHED_COUNTS, show_spinner=False)
def mentions_in(term: str, period: Period) -> int:
    return HackerNews.create().mentions(term, period)


def mentions_across(term: str, periods: list[Period]) -> list[int]:
    return [mentions_in(term, period) for period in periods]


st.set_page_config(page_title="Buzzword weather", page_icon="🌦️")
st.title("🌦️ Buzzword weather")
st.write("How often Hacker News talks about each engineering buzzword, month by month, and the weather it's in now.")

terms = st.multiselect(
    "Buzzwords",
    options=STARTING_TERMS + MORE_TERMS,
    default=STARTING_TERMS,
    max_selections=MOST_TERMS,
    accept_new_options=True,
    placeholder="Pick or type a buzzword",
)

span = st.segmented_control("History", options=list(Span), format_func=lambda span: span.label, default=Span.LAST_2_YEARS)
span = span or Span.LAST_2_YEARS
periods = span.periods_before(date.today())
recent_months = Span.LAST_2_YEARS.periods_before(date.today())

if not terms:
    st.info("Pick a buzzword, or type your own, to see its weather.")
    st.stop()

try:
    with st.spinner("Reading the barometer…"):
        mentions = {term: mentions_across(term.lower().strip(), periods) for term in terms}
        weathers = {term: weather_of(mentions_across(term.lower().strip(), recent_months)) for term in terms}
except Exception:
    st.error("Hacker News search didn't answer just now. Try again in a minute.")
    st.stop()

period_starts = pd.to_datetime([period.starts_at for period in periods], unit="s")
for term, counts in mentions.items():
    weather = weathers[term]
    st.markdown(f"#### {weather.icon} {term}: {weather.forecast}")
    st.line_chart(pd.Series(counts, index=period_starts, name=term), y_label=f"Mentions a {span.step}", height=CHART_HEIGHT)

st.caption(
    f"Counts Hacker News stories and comments that use the exact phrase, {periods[0].label} to {periods[-1].label}, "
    "through the Hacker News search by Algolia. The forecast reads the last two years, month by month. The month or "
    "quarter in progress is left out. Hacker News talks for one corner "
    "of the industry, so treat it as one weather station. A toy from [ahmedavais.com](https://ahmedavais.com)."
)
