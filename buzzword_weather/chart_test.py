from buzzword_weather.chart import rates_chart
from buzzword_weather.periods import Month

AUGUST, SEPTEMBER = Month(2026, 8), Month(2026, 9)


def test_draws_a_line_for_each_buzzword_with_a_point_for_each_period():
    spec = rates_chart({"Agile": [3.0, 2.5], "Vibe coding": [20.0, 18.0]}, [AUGUST, SEPTEMBER]).to_dict()

    rows = next(iter(spec["datasets"].values()))
    assert spec["mark"]["type"] == "line"
    assert spec["encoding"]["color"]["field"] == "buzzword"
    assert [(row["buzzword"], row["rate"]) for row in rows] == [("Agile", 3.0), ("Agile", 2.5), ("Vibe coding", 20.0), ("Vibe coding", 18.0)]


def test_does_not_zoom_or_pan_so_scrolling_on_a_phone_scrolls_the_page():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert "params" not in spec


def test_titles_the_rate_axis_for_readers():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["y"]["title"] == "Mentions per 10,000 posts"


def test_lets_the_dates_speak_for_themselves():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["x"]["title"] is None


def test_lists_buzzwords_in_the_order_the_visitor_picked_them():
    spec = rates_chart({"Vibe coding": [20.0, 18.0], "Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["color"]["sort"] == ["Vibe coding", "Agile"]


def test_names_each_line_without_a_legend_title():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["color"]["title"] is None


def test_shows_the_buzzword_period_and_rate_on_hover_or_tap():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    rows = next(iter(spec["datasets"].values()))
    assert [tip["field"] for tip in spec["encoding"]["tooltip"]] == ["buzzword", "period", "rate"]
    assert [row["period"] for row in rows] == ["Aug 2026", "Sep 2026"]


def test_rounds_the_rate_on_hover_to_two_decimals_so_small_buzzwords_still_show():
    spec = rates_chart({"SAFe": [0.0574894363161, 0.02]}, [AUGUST, SEPTEMBER]).to_dict()

    rate_tip = spec["encoding"]["tooltip"][2]
    assert (rate_tip["format"], rate_tip["title"]) == (".2f", "Mentions per 10,000 posts")


def test_gives_each_buzzword_its_own_color_from_a_colorblind_safe_palette_in_order():
    spec = rates_chart({"Vibe coding": [20.0, 18.0], "Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["color"]["scale"]["range"] == ["#3987e5", "#d95926"]


def test_puts_the_legend_under_the_chart_so_phones_keep_the_full_width():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["color"]["legend"]["orient"] == "bottom"


def test_wraps_the_legend_into_two_columns_so_every_name_fits_on_a_phone():
    spec = rates_chart({"Agile": [3.0, 2.5]}, [AUGUST, SEPTEMBER]).to_dict()

    assert spec["encoding"]["color"]["legend"]["columns"] == 2
