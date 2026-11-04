"""Direct multi-horizon forecasts with training-only features and exact date alignment."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .data import future_sessions, normalize

HORIZON = 20
MODELS = ("Last price", "Log drift", "Random Forest")
FEATURES = (
    "Return 1d",
    "Return 5d",
    "Return 10d",
    "Return 20d",
    "Volatility 5d",
    "Volatility 20d",
    "Price / mean 5d",
    "Price / mean 20d",
    "Relative volume 20d",
)


def features(frame):
    """One vector at the observation cutoff; no future rows are available."""
    prices = frame["Close"].to_numpy()
    volume = frame["Volume"].to_numpy()
    if len(prices) < 21:
        raise ValueError("Features require at least 21 observations.")
    changes = np.diff(np.log(prices[-21:]))
    avg_volume = volume[-20:].mean()
    return np.array(
        [
            *[np.log(prices[-1] / prices[-1 - lag]) for lag in (1, 5, 10, 20)],
            changes[-5:].std(),
            changes.std(),
            prices[-1] / prices[-5:].mean() - 1,
            prices[-1] / prices[-20:].mean() - 1,
            volume[-1] / avg_volume - 1 if avg_volume > 0 else 0.0,
        ]
    )


class Forecaster:
    def __init__(self, name):
        if name not in MODELS:
            raise ValueError("Unknown forecasting model.")
        self.name = name
        self.history = None

    def fit(self, frame):
        self.history = normalize(frame, minimum=80)
        prices = self.history["Close"].to_numpy()
        self.last = prices[-1]
        if self.name == "Log drift":
            self.drift = np.diff(np.log(prices[-253:])).mean()
        elif self.name == "Random Forest":
            cutoffs = range(20, len(prices) - HORIZON)
            x = np.array([features(self.history.iloc[: t + 1]) for t in cutoffs])
            targets = np.array(
                [np.log(prices[t + 1 : t + HORIZON + 1] / prices[t]) for t in cutoffs]
            )
            self.model = RandomForestRegressor(
                n_estimators=160,
                max_depth=6,
                min_samples_leaf=8,
                max_features=0.8,
                random_state=42,
                n_jobs=1,
            )
            self.model.fit(x, targets)
        return self

    def predict(self):
        if self.history is None:
            raise ValueError("Fit the model before predicting.")
        if self.name == "Last price":
            return np.full(HORIZON, self.last)
        if self.name == "Log drift":
            return self.last * np.exp(self.drift * np.arange(1, HORIZON + 1))
        return self.last * np.exp(self.model.predict(features(self.history)[None, :])[0])


def metrics(actual, prediction):
    actual, prediction = np.asarray(actual), np.asarray(prediction)
    error = actual - prediction
    return {
        "mae": float(np.abs(error).mean()),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mape": float(np.mean(np.abs(error) / actual) * 100),
    }


def evaluate(frame):
    frame = normalize(frame)
    development = frame.iloc[:-HORIZON]
    test = frame.iloc[-HORIZON:]
    errors = {name: [] for name in MODELS}
    validation_pairs = {name: ([], []) for name in MODELS}
    for cutoff in range(len(development) - 5 * HORIZON, len(development), HORIZON):
        training = development.iloc[:cutoff]
        actual = development["Close"].iloc[cutoff : cutoff + HORIZON].to_numpy()
        for name in MODELS:
            prediction = Forecaster(name).fit(training).predict()
            # Relative errors make pooled bands less sensitive to changing price levels.
            errors[name].extend((actual - prediction) / training["Close"].iloc[-1])
            validation_pairs[name][0].extend(actual)
            validation_pairs[name][1].extend(prediction)
    validation = {name: metrics(*pair) for name, pair in validation_pairs.items()}
    winner = min(MODELS, key=lambda name: validation[name]["mape"])
    test_predictions = {name: Forecaster(name).fit(development).predict() for name in MODELS}
    test_metrics = {
        name: metrics(test["Close"], prediction) for name, prediction in test_predictions.items()
    }
    fitted = {name: Forecaster(name).fit(frame) for name in MODELS}
    predictions = {name: model.predict() for name, model in fitted.items()}
    bounds = {}
    for name in MODELS:
        quantiles = np.quantile(errors[name], [0.025, 0.10, 0.90, 0.975])
        bounds[name] = {
            "lower95": np.maximum(0, predictions[name] + quantiles[0] * frame["Close"].iloc[-1]),
            "lower80": np.maximum(0, predictions[name] + quantiles[1] * frame["Close"].iloc[-1]),
            "upper80": np.maximum(0, predictions[name] + quantiles[2] * frame["Close"].iloc[-1]),
            "upper95": np.maximum(0, predictions[name] + quantiles[3] * frame["Close"].iloc[-1]),
        }
    return {
        "winner": winner,
        "validation": validation,
        "test": test_metrics,
        "test_dates": dates(test.index),
        "test_actual": test["Close"].to_numpy(),
        "test_predictions": test_predictions,
        "dates": dates(future_sessions(frame.index[-1], HORIZON)),
        "predictions": predictions,
        "bounds": bounds,
        "features": FEATURES,
        "importance": fitted["Random Forest"].model.feature_importances_,
        "method": "Five chronological 20-session folds select the model; the last 20 sessions are held out. All models then refit on all history.",
        "band_note": "Empirical error bands pool relative errors across validation horizons. They are not calibrated coverage guarantees.",
    }


def dates(index):
    return pd.DatetimeIndex(index).strftime("%Y-%m-%d").tolist()
