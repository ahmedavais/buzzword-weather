from datetime import UTC, datetime

import altair as alt
import pandas as pd

from buzzword_weather.periods import Period

RATE = "Mentions per 10,000 posts"


def rates_chart(rates: dict[str, list[float]], periods: list[Period]) -> alt.Chart:
    return (
        alt.Chart(_points(rates, periods))
        .mark_line()
        .encode(
            x=alt.X("starts:T", title=None),
            y=alt.Y("rate:Q", title=RATE),
            color=alt.Color("buzzword:N", sort=list(rates), title=None),
            tooltip=["buzzword:N", "period:N", alt.Tooltip("rate:Q", format=".2f", title=RATE)],
        )
    )


def _points(rates: dict[str, list[float]], periods: list[Period]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"buzzword": buzzword, "period": period.label, "starts": datetime.fromtimestamp(period.starts_at, UTC), "rate": rate}
            for buzzword, series in rates.items()
            for period, rate in zip(periods, series, strict=True)
        ]
    )
