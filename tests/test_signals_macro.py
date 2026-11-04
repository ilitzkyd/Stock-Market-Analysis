import numpy as np
import pandas as pd
import pytest

from stocklab.macro import analyze_macro, correlate, monthly_returns
from stocklab.signals import analyze_signals, indicators


def signal_frame():
    close = np.full(80, 100.0)
    close[30] = 50
    opening = np.full(80, 100.0)
    opening[31], opening[32] = 80, 110
    return pd.DataFrame(
        {"Open": opening, "Close": close, "Volume": np.full(80, 1000)},
        index=pd.bdate_range("2024-01-02", periods=80),
    )


def test_signal_executes_after_detection_at_next_open():
    frame = signal_frame()
    result = analyze_signals(frame, 0)
    assert result["trades"][0]["date"] == frame.index[31].strftime("%Y-%m-%d")
    assert result["trades"][0]["price"] == 80
    assert result["trades"][1]["date"] == frame.index[32].strftime("%Y-%m-%d")
    assert result["trades"][1]["price"] == 110
    assert result["return_pct"] == pytest.approx(37.5)
    assert len(result["dates"]) == len(result["equity"]) == len(result["buy_hold"])


def test_costs_reduce_both_strategy_and_benchmark_returns():
    free = analyze_signals(signal_frame(), 0)
    costly = analyze_signals(signal_frame(), 25)
    assert costly["return_pct"] < free["return_pct"]
    assert costly["buy_hold_return_pct"] < free["buy_hold_return_pct"]


def test_flat_prices_have_neutral_rsi():
    frame = signal_frame()
    frame["Close"] = 100.0
    assert indicators(frame)["rsi"].iloc[-1] == 50
    assert analyze_signals(frame)["trade_count"] == 0


def test_macro_uses_completed_months_only():
    frame = pd.DataFrame(
        {"Close": np.arange(1, 401)}, index=pd.date_range("2023-01-01", periods=400)
    )
    returns = monthly_returns(frame, "2024-01-15")
    assert returns.index[-1] == pd.Timestamp("2023-12-31")


def test_macro_missing_key_is_explicit(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    result = analyze_macro(signal_frame(), "live", "2024-04-01")
    assert result["available"] is False
    assert "FRED_API_KEY" in result["note"]


def test_macro_correlations_count_only_paired_observations():
    index = pd.date_range("2020-01-31", periods=24, freq="ME")
    stock = pd.Series(np.arange(24) / 100, index=index)
    levels = pd.Series(np.cumsum(np.arange(24)), index=index)
    levels.iloc[5] = np.nan
    result = correlate(stock, levels, "diff")
    assert result["observations"] == 21
    assert result["correlation"] == pytest.approx(1.0)
