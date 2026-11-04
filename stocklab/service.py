"""Compose analysis panels without mixing sample and live observations."""

import time
from datetime import date
from functools import lru_cache

import numpy as np
import pandas as pd

from .data import get_prices, symbol
from .forecast import dates, evaluate
from .macro import analyze_macro
from .signals import analyze_signals, drawdown


def parse_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object.")
    ticker = symbol(payload.get("ticker", "MSFT"))
    benchmark = symbol(payload.get("benchmark", "SPY"))
    mode, period = payload.get("mode", "demo"), payload.get("period", "5y")
    if mode not in {"live", "demo"} or period not in {"2y", "5y", "10y"}:
        raise ValueError("Invalid source or period.")
    cost = payload.get("cost_bps", 10)
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= cost <= 100:
        raise ValueError("Costs must be a number from 0 to 100 basis points.")
    return ticker, benchmark, mode, period, cost


@lru_cache(maxsize=8)
def forecast_cached(ticker, period, mode, bucket):
    market = get_prices(ticker, period, mode)
    return market, evaluate(market.frame)


def analyze(payload):
    ticker, benchmark, mode, period, cost = parse_request(payload)
    data, forecast = forecast_cached(ticker, period, mode, int(time.monotonic() // 900))
    comparison = get_prices(benchmark, period, mode)
    frame = data.frame
    pair = pd.concat(
        [frame["Close"].rename("asset"), comparison.frame["Close"].rename("benchmark")], axis=1
    ).dropna()
    if len(pair) < 252:
        raise ValueError("The asset and benchmark do not share 252 trading sessions.")
    returns = pair.pct_change(fill_method=None).dropna()
    correlation = returns["asset"].corr(returns["benchmark"])
    rolling = returns["asset"].rolling(63).corr(returns["benchmark"])
    close = frame["Close"]
    overview = {
        "last": float(close.iloc[-1]),
        "return_pct": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "annualized_volatility_pct": float(
            close.pct_change(fill_method=None).dropna().std() * np.sqrt(252) * 100
        ),
        "max_drawdown_pct": drawdown(close.to_numpy()),
        "benchmark_correlation": float(correlation) if pd.notna(correlation) else None,
        "comparison_dates": dates(pair.index),
        "asset_normalized": (100 * pair["asset"] / pair["asset"].iloc[0]).to_numpy(),
        "benchmark_normalized": (100 * pair["benchmark"] / pair["benchmark"].iloc[0]).to_numpy(),
        "rolling_dates": dates(rolling.dropna().index),
        "rolling_correlation": rolling.dropna().to_numpy(),
    }
    return {
        "ticker": ticker,
        "benchmark": benchmark,
        "mode": mode,
        "period": period,
        "source": data.source,
        "currency": data.currency,
        "fetched_at": data.fetched_at,
        "as_of": frame.index[-1].strftime("%Y-%m-%d"),
        "macro_default_vintage": date.today().isoformat(),
        "observations": len(frame),
        "history_dates": dates(frame.index),
        "history_close": close.to_numpy(),
        "overview": overview,
        "forecast": forecast,
        "signals": analyze_signals(frame, cost),
    }


def macro(payload):
    ticker, _, mode, period, _ = parse_request(payload)
    return analyze_macro(get_prices(ticker, period, mode).frame, mode, payload.get("as_of"))
