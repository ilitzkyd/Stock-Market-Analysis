"""Explicit price observations and a next-open illustrative strategy backtest."""

import numpy as np
import pandas as pd

from .forecast import dates


def indicators(frame):
    close = frame["Close"]
    mean = close.rolling(20).mean()
    deviation = close.rolling(20).std()
    change = close.diff()
    gain = change.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-change.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    rsi = rsi.mask((loss == 0) & (gain > 0), 100)
    rsi = rsi.mask((loss == 0) & (gain == 0), 50)
    return pd.DataFrame(
        {"mean": mean, "upper": mean + 2 * deviation, "lower": mean - 2 * deviation, "rsi": rsi},
        index=frame.index,
    )


def drawdown(equity):
    values = np.asarray(equity, dtype=float)
    return float(np.min(values / np.maximum.accumulate(values) - 1) * 100)


def analyze_signals(frame, cost_bps=10):
    if not isinstance(cost_bps, (int, float)) or not 0 <= cost_bps <= 100:
        raise ValueError("Trading cost must be between 0 and 100 basis points per side.")
    indicator = indicators(frame)
    desired, holding = [], 0
    for i, close in enumerate(frame["Close"]):
        if close < indicator["lower"].iloc[i]:
            holding = 1
        elif close >= indicator["mean"].iloc[i]:
            holding = 0
        desired.append(holding)
    cost = cost_bps / 10000
    opens = frame["Open"].to_numpy()
    equity, trades, position = [100.0], [], 0
    for i in range(1, len(frame) - 1):
        next_position = desired[i - 1]
        turnover = abs(next_position - position)
        if turnover:
            trades.append(
                {
                    "date": frame.index[i].strftime("%Y-%m-%d"),
                    "action": "Enter" if next_position else "Exit",
                    "price": float(opens[i]),
                    "reason": "Previous close signal / next open",
                }
            )
        growth = (1 - turnover * cost) * (1 + next_position * (opens[i + 1] / opens[i] - 1))
        equity.append(equity[-1] * growth)
        position = next_position
    if position:
        equity[-1] *= 1 - cost
        trades.append(
            {
                "date": frame.index[-1].strftime("%Y-%m-%d"),
                "action": "Exit",
                "price": float(opens[-1]),
                "reason": "End-of-test liquidation",
            }
        )
    benchmark = 100 * opens[1:] / opens[1] * (1 - cost)
    benchmark[-1] *= 1 - cost
    latest, close = indicator.iloc[-1], frame["Close"].iloc[-1]
    state = (
        "Above upper band"
        if close > latest["upper"]
        else ("Below lower band" if close < latest["lower"] else "Inside bands")
    )
    return {
        "rsi": float(latest["rsi"]),
        "band_state": state,
        "upper": float(latest["upper"]),
        "lower": float(latest["lower"]),
        "mean": float(latest["mean"]),
        "dates": dates(frame.index[1:]),
        "equity": equity,
        "buy_hold": benchmark,
        "return_pct": float((equity[-1] / 100 - 1) * 100),
        "buy_hold_return_pct": float((benchmark[-1] / 100 - 1) * 100),
        "max_drawdown_pct": drawdown(equity),
        "trades": trades[-100:],
        "trade_count": len(trades),
        "cost_bps": cost_bps,
        "rule": "Illustrative mean reversion: enter long after a close below the 20-session lower band; exit after a close at/above the mean. Execute next open; no leverage. Charge costs on both entry and exit, including final liquidation.",
        "note": "Historical simulation, not an out-of-sample strategy selection result. No recommendation or assumed execution guarantee.",
    }
