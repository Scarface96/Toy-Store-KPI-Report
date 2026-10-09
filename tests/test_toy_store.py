import numpy as np
import pandas as pd
import pytest

from analysis import data, forecast


@pytest.fixture(scope="module")
def sales():
    return data.load_sales()


def test_prices_parse_from_dollar_strings():
    p = data.load_products()
    assert p["price"].dtype == float
    assert (p["price"] > p["cost"]).all(), "every product should sell above cost"


def test_totals_match_the_power_bi_report(sales):
    t = data.totals(sales)
    assert t["orders"] == 829_262
    assert abs(t["revenue"] - 14_444_572.35) < 1
    assert abs(t["profit"] - 4_014_029) < 1


def test_every_calendar_day_has_sales(sales):
    assert data.check_calendar(sales)["days_without_sales"] == 0


def test_like_for_like_uses_the_same_months(sales):
    lfl = data.like_for_like(sales)
    assert lfl.attrs["months"] == 9
    jan_sep_2022 = sales[(sales["year"] == 2022) & (sales["Date"].dt.month <= 9)]["revenue"].sum()
    assert abs(lfl.loc[0, "revenue_2022"] - jan_sep_2022) < 1e-6


def test_abc_classes_cover_all_profit(sales):
    p = data.abc(sales)
    assert abs(p["share"].sum() - 1) < 1e-9
    assert list(p["class"].unique()) == ["A", "B", "C"]
    assert p["cumulative_share"].is_monotonic_increasing


def test_seasonal_naive_on_a_known_series():
    idx = pd.date_range("2022-01-01", periods=15, freq="MS")
    s = pd.Series(np.arange(15, dtype=float) + 100, index=idx)
    f = forecast.seasonal_naive(s, horizon=2, window=3)
    # last 3 months (112,113,114) vs a year earlier (100,101,102): growth = 339/303 - 1
    g = 339 / 303 - 1
    assert f.index[0] == pd.Timestamp("2023-04-01")
    assert abs(f.iloc[0] - 103 * (1 + g)) < 1e-9


def test_forecast_picks_lowest_backtest_error(sales):
    f = forecast.forecast(data.monthly(sales))
    assert f["best"] == min(f["errors"], key=f["errors"].get)
    assert len(f["forecast"]) == 3
    assert (f["low"] <= f["forecast"]).all() and (f["forecast"] <= f["high"]).all()
