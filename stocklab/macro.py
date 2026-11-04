"""Descriptive monthly macro correlations; never used as forecasting features."""

import json
import os
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

SERIES = {
    "CPIAUCSL": ("Consumer prices", "pct"),
    "UNRATE": ("Unemployment", "diff"),
    "FEDFUNDS": ("Federal funds rate", "diff"),
    "INDPRO": ("Industrial production", "pct"),
}


def monthly_returns(frame, as_of):
    cutoff = pd.Timestamp(as_of)
    close = frame.loc[frame.index <= cutoff, "Close"].resample("ME").last()
    close = close.loc[close.index <= cutoff]
    return close.pct_change(fill_method=None).rename("stock_return")


def correlate(returns, level, transform):
    change = level.pct_change(fill_method=None) if transform == "pct" else level.diff()
    pairs = pd.concat([returns, change.rename("macro_change")], axis=1).dropna()
    count = len(pairs)
    if count < 12 or (pairs.std() == 0).any():
        return {
            "correlation": None,
            "observations": count,
            "status": "Insufficient variation or history",
        }
    return {
        "correlation": float(pairs.corr().iloc[0, 1]),
        "observations": count,
        "status": "Descriptive only",
    }


def analyze_macro(frame, mode, as_of=None):
    as_of = as_of or date.today().isoformat()
    try:
        vintage = date.fromisoformat(as_of)
    except (ValueError, TypeError) as error:
        raise ValueError("Macro vintage must be YYYY-MM-DD.") from error
    if vintage > date.today() or vintage < date(1900, 1, 1):
        raise ValueError("Macro vintage must be between 1900-01-01 and today.")
    returns = monthly_returns(frame, as_of)
    key = os.environ.get("FRED_API_KEY", "").strip()
    if mode == "live" and not key:
        return {
            "available": False,
            "rows": [],
            "as_of": as_of,
            "note": "Set FRED_API_KEY in the server environment to enable live macro analysis. No embedded key is used.",
        }
    rows = []
    for index, (series, (name, transform)) in enumerate(SERIES.items()):
        try:
            if mode == "demo":
                rng = np.random.default_rng(100 + index)
                level = pd.Series(
                    100 + np.cumsum(rng.normal(0.1, 0.5, len(returns))), index=returns.index
                )
            else:
                query = urlencode(
                    {
                        "api_key": key,
                        "file_type": "json",
                        "series_id": series,
                        "observation_start": frame.index[0].strftime("%Y-%m-%d"),
                        "observation_end": as_of,
                        "realtime_start": as_of,
                        "realtime_end": as_of,
                    }
                )
                with urlopen(
                    "https://api.stlouisfed.org/fred/series/observations?" + query, timeout=20
                ) as response:
                    observations = json.load(response)["observations"]
                values = {
                    item["date"]: float(item["value"])
                    for item in observations
                    if item["value"] != "."
                }
                level = pd.Series(values, dtype=float)
                level.index = pd.to_datetime(level.index).to_period("M").to_timestamp("M")
                level = level.loc[level.index <= pd.Timestamp(as_of)]
            row = correlate(returns, level, transform)
        except HTTPError as error:
            row = {"correlation": None, "observations": 0, "status": f"FRED HTTP {error.code}"}
        except (URLError, TimeoutError, KeyError, ValueError) as error:
            row = {
                "correlation": None,
                "observations": 0,
                "status": f"Series unavailable ({type(error).__name__})",
            }
        rows.append(
            {
                "series": series,
                "name": name,
                "transform": "Monthly % change"
                if transform == "pct"
                else "Monthly percentage-point change",
                **row,
            }
        )
    return {
        "available": any(row["correlation"] is not None for row in rows),
        "rows": rows,
        "as_of": as_of,
        "note": (
            "Synthetic economic series. " if mode == "demo" else f"FRED vintage as of {as_of}. "
        )
        + "Monthly stock returns versus economic changes, aligned to observation months. "
        "These are contemporaneous descriptive correlations, not release-date-aware predictors. "
        "Macro data is deliberately excluded from the forecasting models.",
    }
