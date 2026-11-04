import pandas as pd
import pytest

from stocklab.data import DataError, demo_data, get_prices, symbol
from stocklab.service import parse_request


def test_demo_history_is_consistent_across_windows():
    short, long = demo_data("MSFT", "2y"), demo_data("MSFT", "5y")
    pd.testing.assert_frame_equal(short.frame, long.frame.loc[short.frame.index])
    assert "Synthetic" in short.source


@pytest.mark.parametrize("value", ["../MSFT", "", "BTC-USD.", None, "AAPL;ls"])
def test_invalid_symbols(value):
    with pytest.raises(DataError):
        symbol(value)


def test_invalid_config():
    with pytest.raises(ValueError):
        parse_request({"cost_bps": float("nan")})
    with pytest.raises(ValueError):
        parse_request({"cost_bps": True})
    with pytest.raises(ValueError):
        parse_request({"period": "forever"})


def test_live_failure_never_becomes_demo(monkeypatch):
    class FailedTicker:
        def __init__(self, ticker):
            pass

        def history(self, **kwargs):
            raise RuntimeError("Provider unavailable")

    monkeypatch.setattr("yfinance.Ticker", FailedTicker)
    with pytest.raises(DataError, match="Yahoo Finance"):
        get_prices("FAIL", "2y", "live")
