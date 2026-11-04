"""Adjusted US-market data with explicit errors, timestamps and demo provenance."""

import hashlib
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

import exchange_calendars as xcals
import numpy as np
import pandas as pd


class DataError(ValueError):
    """Data is unavailable or cannot be safely interpreted."""


@dataclass
class MarketData:
    symbol: str
    frame: pd.DataFrame
    source: str
    fetched_at: str
    currency: str = "USD"


def symbol(value):
    if not isinstance(value, str):
        raise DataError("Ticker must be text.")
    value = value.strip().upper()
    if not re.fullmatch(r"\^?[A-Z][A-Z0-9-]{0,9}", value):
        raise DataError("Enter a US ticker such as MSFT, AAPL, SPY or BRK-B.")
    return value


@lru_cache(maxsize=1)
def calendar():
    return xcals.get_calendar("XNYS")


def completed_sessions():
    today = pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
    sessions = calendar().sessions_in_range(today - pd.Timedelta(days=4500), today)
    while len(sessions) and calendar().session_close(sessions[-1]) > pd.Timestamp.now(tz="UTC"):
        sessions = sessions[:-1]
    return sessions


def future_sessions(last, count):
    start = pd.Timestamp(last).normalize() + pd.Timedelta(days=1)
    result = calendar().sessions_in_range(start, start + pd.Timedelta(days=count * 3 + 30))
    if len(result) < count:
        raise DataError("The exchange calendar does not cover the requested forecast.")
    return result[:count]


def normalize(frame, minimum=252):
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise DataError("The provider returned no price data.")
    required = ["Open", "Close", "Volume"]
    if any(column not in frame.columns for column in required):
        raise DataError("Price data must contain adjusted Open, Close and Volume.")
    result = frame[required].copy()
    index = pd.DatetimeIndex(result.index)
    if index.tz is not None:
        index = index.tz_localize(None)
    result.index = index.normalize()
    if result.index.hasnans:
        raise DataError("Missing trading dates found.")
    if result.index.has_duplicates:
        raise DataError("Duplicate trading dates found.")
    result = result.sort_index().astype(float)
    if len(result) < minimum:
        raise DataError(f"At least {minimum} completed trading sessions are required.")
    if not np.isfinite(result.to_numpy()).all():
        raise DataError("Missing or non-finite prices/volume found; data was not filled silently.")
    if (result[["Open", "Close"]] <= 0).any().any() or (result["Volume"] < 0).any():
        raise DataError("Prices must be positive and volume cannot be negative.")
    return result


def demo_data(ticker, period):
    ticker = symbol(ticker)
    count = {"2y": 504, "5y": 1260, "10y": 2520}[period]
    sessions = completed_sessions()[-2520:]
    seed = int.from_bytes(hashlib.sha256(ticker.encode()).digest()[:4], "big")
    market = np.random.default_rng(7).normal(0.0003, 0.009, len(sessions))
    rng = np.random.default_rng(seed)
    returns = (
        market if ticker == "SPY" else 0.8 * market + rng.normal(0.00015, 0.008, len(sessions))
    )
    close = 100 * np.exp(np.cumsum(returns))
    opening = np.r_[100, close[:-1]] * np.exp(rng.normal(0, 0.003, len(close)))
    frame = pd.DataFrame(
        {"Open": opening, "Close": close, "Volume": rng.integers(1_000_000, 8_000_000, len(close))},
        index=sessions,
    )
    return MarketData(
        ticker, normalize(frame.iloc[-count:]), "Synthetic demo (not real prices)", utc_now()
    )


def utc_now():
    return datetime.now(timezone.utc).isoformat()


_CACHE = {}


def get_prices(ticker, period="5y", mode="demo"):
    ticker = symbol(ticker)
    if period not in {"2y", "5y", "10y"} or mode not in {"demo", "live"}:
        raise DataError("Unsupported data period or source.")
    if mode == "demo":
        return demo_data(ticker, period)
    key = (ticker, period)
    cached = _CACHE.get(key)
    if cached and time.monotonic() - cached[0] < 900:
        data = cached[1]
        return MarketData(
            data.symbol, data.frame.copy(), data.source, data.fetched_at, data.currency
        )
    import yfinance as yf

    try:
        client = yf.Ticker(ticker)
        raw = client.history(period=period, auto_adjust=True, actions=False, raise_errors=True)
        metadata = client.get_history_metadata()
    except Exception as error:
        raise DataError(
            f"Yahoo Finance could not supply {ticker}. Retry or explicitly select demo data."
        ) from error
    currency = metadata.get("currency")
    exchange = metadata.get("exchangeName", "")
    if currency != "USD" or exchange not in {
        "NMS",
        "NYQ",
        "NGM",
        "NCM",
        "PCX",
        "ASE",
        "BTS",
        "BATS",
        "CBOE",
    }:
        raise DataError(
            f"{ticker}: this version supports USD-listed US shares and ETFs, not this market."
        )
    completed = completed_sessions()
    frame = normalize(raw)
    frame = frame.loc[frame.index <= completed[-1]]
    missing = calendar().sessions_in_range(frame.index[0], frame.index[-1]).difference(frame.index)
    if len(missing):
        raise DataError(f"{ticker}: {len(missing)} trading sessions are missing; analysis stopped.")
    frame = normalize(frame)
    data = MarketData(ticker, frame, "Yahoo Finance / adjusted prices", utc_now(), currency)
    if len(_CACHE) >= 24:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = (time.monotonic(), data)
    return MarketData(data.symbol, data.frame.copy(), data.source, data.fetched_at, data.currency)
