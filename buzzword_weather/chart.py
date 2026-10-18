from datetime import UTC, datetime

import altair as alt
import pandas as pd

from buzzword_weather.periods import Period

RATE = "Mentions per 10,000 posts"
LEGEND_COLUMNS = 2
HOVER_POINT_SIZE = 64
GUIDE_COLOR = "#8a8984"
COLORBLIND_SAFE_COLORS = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9"]


def rates_chart(rates: dict[str, list[float]], periods: list[Period]) -> alt.LayerChart:
    nearest = alt.selection_point(nearest=True, on="pointerover", fields=["starts"], empty=False)
    buzzwords = _buzzwords_over_time(rates, periods)
    return alt.layer(buzzwords.mark_line(), _guide(buzzwords, nearest), _hover_points(buzzwords, nearest))


def _buzzwords_over_time(rates: dict[str, list[float]], periods: list[Period]) -> alt.Chart:
    return alt.Chart(_points(rates, periods)).encode(
        x=alt.X("starts:T", title=None),
        y=alt.Y("rate:Q", title=RATE),
        color=alt.Color(
            "buzzword:N",
            sort=list(rates),
            scale=alt.Scale(domain=list(rates), range=COLORBLIND_SAFE_COLORS[: len(rates)]),
            legend=alt.Legend(orient="bottom", columns=LEGEND_COLUMNS),
            title=None,
        ),
    )


def _guide(buzzwords: alt.Chart, nearest: alt.Parameter) -> alt.Chart:
    return alt.Chart(buzzwords.data).mark_rule(color=GUIDE_COLOR).encode(x="starts:T").transform_filter(nearest)


def _hover_points(buzzwords: alt.Chart, nearest: alt.Parameter) -> alt.Chart:
    return (
        buzzwords.mark_point(filled=True, size=HOVER_POINT_SIZE)
        .encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
            tooltip=["buzzword:N", "period:N", alt.Tooltip("rate:Q", format=".2f", title=RATE)],
        )
        .add_params(nearest)
    )


def _points(rates: dict[str, list[float]], periods: list[Period]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"buzzword": buzzword, "period": period.label, "starts": datetime.fromtimestamp(period.starts_at, UTC), "rate": rate}
            for buzzword, series in rates.items()
            for period, rate in zip(periods, series, strict=True)
        ]
    )
