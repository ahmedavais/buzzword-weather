from datetime import UTC, datetime

import altair as alt
import pandas as pd

from buzzword_weather.periods import Period

RATE = "Mentions per 10,000 posts"
LEGEND_COLUMNS = 2
COLORBLIND_SAFE_COLORS = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9"]


def rates_chart(rates: dict[str, list[float]], periods: list[Period]) -> alt.Chart:
    return (
        alt.Chart(_points(rates, periods))
        .mark_line()
        .encode(
            x=alt.X("starts:T", title=None),
            y=alt.Y("rate:Q", title=RATE),
            color=alt.Color(
                "buzzword:N",
                sort=list(rates),
                scale=alt.Scale(domain=list(rates), range=COLORBLIND_SAFE_COLORS[: len(rates)]),
                legend=alt.Legend(orient="bottom", columns=LEGEND_COLUMNS),
                title=None,
            ),
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
