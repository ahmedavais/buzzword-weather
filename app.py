from datetime import date

import pandas as pd
import streamlit as st

from buzzword_weather.forecast import weather_of
from buzzword_weather.hacker_news import HackerNews
from buzzword_weather.periods import Month, complete_months_before

STARTING_TERMS = ["vibe coding", "harness engineering", "loop engineering", "ralph loop", "platform engineering"]
MORE_TERMS = ["devops", "microservices", "scrum", "context engineering", "prompt engineering", "agentic"]
MONTHS_SHOWN = 24
MOST_TERMS = 6
ONE_DAY_SECONDS = 24 * 60 * 60
CHART_HEIGHT = 180


@st.cache_data(ttl=ONE_DAY_SECONDS, show_spinner=False)
def monthly_mentions(term: str, months: tuple[Month, ...]) -> list[int]:
    return HackerNews.create().mentions_by_period(term, list(months))


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

months = tuple(complete_months_before(date.today(), MONTHS_SHOWN))

if not terms:
    st.info("Pick a buzzword, or type your own, to see its weather.")
    st.stop()

try:
    with st.spinner("Reading the barometer…"):
        mentions = {term: monthly_mentions(term.lower().strip(), months) for term in terms}
except Exception:
    st.error("Hacker News search didn't answer just now. Try again in a minute.")
    st.stop()

month_starts = pd.to_datetime([f"{month.year}-{month.month:02d}-01" for month in months])
for term, counts in mentions.items():
    weather = weather_of(counts)
    st.markdown(f"#### {weather.icon} {term}: {weather.forecast}")
    st.line_chart(pd.Series(counts, index=month_starts, name=term), y_label="Mentions a month", height=CHART_HEIGHT)

st.caption(
    f"Counts Hacker News stories and comments that use the exact phrase, {months[0].label} to {months[-1].label}, "
    "through the Hacker News search by Algolia. The month in progress is left out. Hacker News talks for one corner "
    "of the industry, so treat it as one weather station. A toy from [ahmedavais.com](https://ahmedavais.com)."
)
