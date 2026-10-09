"""A transparent revenue forecast for the months after the data ends.

Method: "growth-adjusted seasonal naive". Next month's revenue = the same month
last year x the year-on-year growth rate of the most recent months. It keeps the
seasonal shape (December spikes) and only needs one year of history, which is all
this dataset has for October-December.

It's compared with Holt's linear trend (no seasonality) in a backtest on the
last months of known data, so the page can say how far off each method tends to be.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _series(monthly: pd.DataFrame) -> pd.Series:
    return monthly.set_index("month")["revenue"].asfreq("MS")


def yoy_growth(series: pd.Series, end: pd.Timestamp, window: int = 3) -> float:
    """Growth of the `window` months up to `end` versus the same months a year earlier."""
    recent = series.loc[:end].tail(window)
    prior = series.reindex(recent.index - pd.DateOffset(years=1))
    return recent.sum() / prior.sum() - 1


def seasonal_naive(series: pd.Series, horizon: int, window: int = 3) -> pd.Series:
    end = series.index.max()
    g = yoy_growth(series, end, window)
    idx = pd.date_range(end + pd.DateOffset(months=1), periods=horizon, freq="MS")
    base = series.reindex(idx - pd.DateOffset(years=1)).to_numpy()
    return pd.Series(base * (1 + g), index=idx)


def holt(series: pd.Series, horizon: int) -> pd.Series:
    fit = ExponentialSmoothing(series, trend="add", damped_trend=True, initialization_method="estimated").fit()
    return fit.forecast(horizon)


def backtest(series: pd.Series, test_months: int = 6, window: int = 3) -> pd.DataFrame:
    """One-step-ahead forecasts for each of the last `test_months` months."""
    rows = []
    for i in range(test_months, 0, -1):
        train = series.iloc[:-i]
        actual = series.iloc[-i]
        when = series.index[-i]
        rows.append({
            "month": when,
            "actual": actual,
            "seasonal_naive": seasonal_naive(train, 1, window).iloc[0],
            "holt": holt(train, 1).iloc[0],
        })
    t = pd.DataFrame(rows)
    t["blend"] = (t["seasonal_naive"] + t["holt"]) / 2
    for m in METHODS:
        t[f"{m}_error"] = (t[m] - t["actual"]) / t["actual"]
    return t


METHODS = {
    "seasonal_naive": "Same month last year x recent growth",
    "holt": "Damped trend (Holt), no seasonality",
    "blend": "Average of the two",
}


def mape(errors: pd.Series) -> float:
    return float(np.mean(np.abs(errors)))


def forecast(monthly: pd.DataFrame, horizon: int = 3) -> dict:
    """Forecast with every method, then pick the one with the lowest backtest error."""
    s = _series(monthly)
    bt = backtest(s)
    errors = {m: mape(bt[f"{m}_error"]) for m in METHODS}
    sn, h = seasonal_naive(s, horizon), holt(s, horizon)
    paths = {"seasonal_naive": sn, "holt": h, "blend": (sn + h) / 2}
    best = min(errors, key=errors.get)
    point = paths[best]
    band = max(errors[best], 0.02)  # +/- the chosen method's typical backtest error
    return {
        "history": s,
        "paths": paths,
        "best": best,
        "forecast": point,
        "low": point * (1 - band),
        "high": point * (1 + band),
        "errors": errors,
        "growth": yoy_growth(s, s.index.max()),
        "backtest": bt,
    }
