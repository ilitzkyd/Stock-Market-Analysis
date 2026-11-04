# Stock Research Lab

A local, interactive stock-research app with transparent model comparisons, exact
trading-date evaluation, benchmark comparisons, macro context, and explicit
trading-rule simulations. This replaces the original exploratory notebooks.

**Research software, not investment advice. No trades are placed.**

## Run

Requires Python 3.11 or later. From this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m stocklab.server
```

Open **http://127.0.0.1:8766** in your browser. On Windows, you can also run:

```powershell
.\Start-StockLab.ps1
```

The launcher installs dependencies on first use, waits for the server to become
ready, and opens the browser. Close the server's terminal to stop it. On macOS or
Linux, use `.venv/bin/python` instead of the Windows Python path above.

The app starts in **Synthetic demo** mode. To use real observations, select
**Live / Yahoo Finance** and click **Run analysis**. Provider errors are displayed;
live failures never silently become synthetic data.

## Views

| View | What it shows |
| --- | --- |
| Overview | Adjusted prices, normalized performance against a benchmark, volatility, drawdown, and rolling return correlation |
| Forecast | Last-price, log-drift, and Random Forest comparisons; validation/test scores; 5, 10, or 20 future trading sessions; empirical error bands |
| Signals | RSI and Bollinger observations; a fully specified mean-reversion rule; next-open executions, per-side costs, equity curves, and trade ledger |
| Macro | Monthly stock returns versus economic changes, paired sample counts, and an optional FRED vintage date |

Charts support pointer inspection and keyboard arrow navigation. Export the
forecast as CSV or the active chart as PNG. Light/dark themes and narrow screens
are supported. There are no third-party browser scripts.

## Data and market scope

- USD-listed US shares and ETFs; default asset `MSFT`, benchmark `SPY`.
- Historical windows: two, five, or ten years; at least 252 completed sessions.
- Yahoo Finance data via `yfinance`, with `auto_adjust=True` for both open and close.
- The US NYSE session calendar supplies common US equity holidays and future
  trading sessions. In-progress sessions are excluded.
- Duplicate dates, missing trading sessions, invalid prices, and missing volume
  are rejected explicitly. No outliers are removed or missing prices filled.
- Live prices and model results are cached in memory for approximately 15 minutes.
  The displayed source, fetched-at timestamp, and last observation date identify
  exactly what is being shown. The quote is not a real-time execution price.
- Synthetic histories are reproducible and consistent across window choices.
- The HTTP server binds only to loopback. It is a local app, not a public hosting
  solution. Use the provider's applicable terms and licensing for your use case.

## Forecast methodology

1. Reserve the final **20 observed sessions** as an untouched test period.
2. Before that test, evaluate **five non-overlapping, chronological 20-session
   folds**, expanding the training history before each fold.
3. Choose the model with the lowest pooled validation MAPE, never test performance.
4. Fit that model on pre-test history and evaluate on the exact test-session dates.
   MAE, RMSE, and MAPE are retained for all three models.
5. Refit all models on the complete history for the final outlook.

All models forecast 20 sessions. The UI's 5/10/20 selector displays a prefix of
that forecast; the evaluation scores always refer to the full 20-session horizon.

### Models

- **Last price:** an unchanged-price baseline.
- **Log drift:** extrapolates mean daily log returns from up to the last 252
  intervals of the training window.
- **Random Forest:** directly predicts a vector of 20 future log returns using
  trailing 1/5/10/20-session returns, 5/20-session volatility, price-to-moving-mean
  ratios, and relative volume. Every target falls within its training fold.
  All features use only observations available at the forecast origin.

No future actual prices, macro values, fundamentals, or fabricated future
features are fed into these models. Random Forest is not assumed to outperform
the simpler baselines.

Bands use empirical quantiles of validation errors normalized by each fold's
origin price, scaled to the current price. They pool errors across horizons and
are **not guaranteed or formally calibrated prediction intervals**. Bands can
be asymmetric and need not contain the point forecast. Lower prices are bounded
at zero. Parameter, regime, and model-selection uncertainty are not fully represented.

## Signal simulation

The demonstration strategy enters long after a close below the 20-session mean
minus two rolling standard deviations; it exits after a close at or above that
mean. Orders execute at the **following session's adjusted open**.

The simulation starts at 100, uses either full long exposure or cash, compounds
open-to-open returns, charges user-selected costs on every entry and exit, and
liquidates any final position at the last observed open. The buy-and-hold
comparison uses the same asset, open-price period, and entry/exit costs.

This is a historical rule illustration, not an out-of-sample trading-system
selection experiment. Cash interest, taxes, borrowing, market impact beyond the
chosen flat costs, and execution constraints are not modeled. RSI and band
observations are not automatic buy/sell recommendations.

## FRED macro data

The default demo uses explicitly synthetic macro series. Live macro analysis
requires your own FRED key in the server environment:

```powershell
$env:FRED_API_KEY = "your-new-key"
.\.venv\Scripts\python.exe -m stocklab.server
```

If a server is already running, stop and restart it after setting the variable.
`.env.example` documents the variable; `.env` files are ignored by Git and are
not automatically loaded. Never put a key into notebook source.

The selected vintage is passed as both `realtime_start` and `realtime_end`.
Prices and indicators are restricted to completed months on or before that date.
CPI and industrial production use monthly percentage changes; unemployment and
the policy rate use monthly percentage-point changes. Each correlation reports
its paired observation count.

These are **descriptive contemporaneous correlations aligned to observation
months**, not release-date-aware predictors. Macro data is deliberately excluded
from model training. A full macro-predictive backtest would require vintage and
availability alignment at every historical decision time. A single vintage
snapshot does not accomplish that.

## Development

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```

Unit tests run offline. They cover target boundaries, unchanged validation under
holdout mutations, exact test dates, exchange holidays, missing data, next-open
execution, costs, neutral RSI, monthly alignment, missing FRED configuration, and
the prohibition on silent live-to-demo fallback. GitHub Actions runs these checks.

For browser checks, start the app first, then:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[browser]"
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tests\browser_smoke.py
```

Add `--live` to test Yahoo Finance as well. Set `STOCKLAB_BROWSER_PATH` to use an
installed browser executable instead of Playwright's bundled Chromium. Screenshots
are saved under the Git-ignored `artifacts/` directory.

## Source layout

```text
stocklab/
  data.py       Provider, market calendar, validation, demo data, cache
  forecast.py   Baselines, Random Forest, chronological evaluation
  signals.py    Indicators and explicit next-open simulation
  macro.py      Descriptive FRED/demo correlations
  service.py    Analysis composition
  server.py     Local HTTP API
  index.html    Self-contained interactive dashboard
tests/          Offline tests and optional browser smoke check
```

## Migration from the notebooks

Removed the duplicated exploratory notebooks and generated chart artifacts,
including code containing a hard-coded FRED credential. Old material remains in
Git history; **removing a key from the current files does not revoke it or remove
it from history. Revoke/rotate that old key before using live FRED access.**

The old Prophet experiments, raw-price correlation rankings, and arbitrary
"Strong buy" point system are not carried forward. They are replaced by reusable
modules, explicit baseline comparisons, time-aligned evaluation, return-based
correlations, documented simulations, and automated checks.
