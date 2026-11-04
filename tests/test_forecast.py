import numpy as np
import pandas as pd
import pytest

from stocklab.data import DataError, future_sessions, normalize
from stocklab.forecast import HORIZON, Forecaster, evaluate, features


@pytest.fixture
def frame():
    rng = np.random.default_rng(4)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, 300)))
    return pd.DataFrame(
        {"Open": close * 0.999, "Close": close, "Volume": np.full(300, 1000)},
        index=pd.bdate_range("2024-01-02", periods=300),
    )


def test_models_predict_positive_full_horizon(frame):
    for name in ("Last price", "Log drift", "Random Forest"):
        prediction = Forecaster(name).fit(frame).predict()
        assert prediction.shape == (HORIZON,)
        assert np.isfinite(prediction).all() and (prediction > 0).all()
    np.testing.assert_array_equal(
        Forecaster("Last price").fit(frame).predict(), np.full(20, frame["Close"].iloc[-1])
    )


def test_log_drift_recovers_exponential_trend(frame):
    frame["Close"] = 100 * np.exp(0.001 * np.arange(len(frame)))
    actual = Forecaster("Log drift").fit(frame).predict()
    np.testing.assert_allclose(actual, frame["Close"].iloc[-1] * np.exp(0.001 * np.arange(1, 21)))


def test_targets_are_inside_training_cutoff(frame, monkeypatch):
    class RecordingForest:
        def __init__(self, **kwargs):
            pass

        def fit(self, x, y):
            self.x, self.y = x, y

    monkeypatch.setattr("stocklab.forecast.RandomForestRegressor", RecordingForest)
    trained = Forecaster("Random Forest").fit(frame.iloc[:100])
    np.testing.assert_allclose(trained.model.x[0], features(frame.iloc[:21]))
    close = frame["Close"].to_numpy()
    np.testing.assert_allclose(trained.model.y[0], np.log(close[21:41] / close[20]))
    np.testing.assert_allclose(trained.model.y[-1], np.log(close[80:100] / close[79]))


def test_holdout_does_not_change_selection_or_validation(frame):
    before = evaluate(frame)
    changed = frame.copy()
    changed.iloc[-20:, changed.columns.get_loc("Close")] *= 1.5
    after = evaluate(changed)
    assert before["validation"] == after["validation"]
    assert before["winner"] == after["winner"]
    assert before["test"] != after["test"]
    assert before["test_dates"] == frame.index[-20:].strftime("%Y-%m-%d").tolist()
    np.testing.assert_array_equal(before["test_actual"], frame["Close"].iloc[-20:])


def test_forecasts_skip_exchange_holidays():
    assert future_sessions("2026-11-25", 3).strftime("%Y-%m-%d").tolist() == [
        "2026-11-27",
        "2026-11-30",
        "2026-12-01",
    ]


@pytest.mark.parametrize("problem", ["nan", "negative", "duplicate", "date", "short"])
def test_bad_histories_fail_explicitly(frame, problem):
    if problem == "nan":
        frame.iloc[4, 1] = np.nan
    elif problem == "negative":
        frame.iloc[4, 1] = -1
    elif problem == "duplicate":
        frame.index = [frame.index[0]] * len(frame)
    elif problem == "date":
        frame.index = [pd.NaT] + frame.index[1:].tolist()
    else:
        frame = frame.iloc[:20]
    with pytest.raises(DataError):
        normalize(frame)
