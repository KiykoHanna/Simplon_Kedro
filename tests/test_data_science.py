
import numpy as np
import pandas as pd
import pytest

from atelier_spaceflights.pipelines.data_science.nodes import (
    evaluate_model,
    split_data,
    train_model,
)


def test_split_data_sizes_and_reproducibility():
    table = pd.DataFrame({
        "feature": range(20),
        "price": [value * 10.0 for value in range(20)],
    })
    options = {
        "features": ["feature"],
        "test_size": 0.2,
        "random_state": 3,
    }

    X_train, X_test, y_train, y_test = split_data(table, options)
    second_split = split_data(table, options)

    assert len(X_train) == 16
    assert len(X_test) == 4
    assert len(y_train) == 16
    assert len(y_test) == 4
    pd.testing.assert_frame_equal(X_test, second_split[1])


def test_split_data_raises_for_missing_feature():
    table = pd.DataFrame({"price": [100.0, 200.0]})
    options = {
        "features": ["unknown_feature"],
        "test_size": 0.5,
        "random_state": 3,
    }

    with pytest.raises(KeyError):
        split_data(table, options)


def test_train_model_learns_linear_relationship():
    X_train = pd.DataFrame({"feature": [1, 2, 3, 4]})
    y_train = pd.Series([10.0, 20.0, 30.0, 40.0])

    model = train_model(X_train, y_train)

    predictions = model.predict(pd.DataFrame({"feature": [5, 6]}))
    np.testing.assert_allclose(predictions, [50.0, 60.0])


def test_evaluate_model_returns_metrics_and_predictions():
    X_train = pd.DataFrame({"feature": [1, 2, 3, 4]})
    y_train = pd.Series([10.0, 20.0, 30.0, 40.0])
    model = train_model(X_train, y_train)

    X_test = pd.DataFrame({"feature": [5, 6]})
    y_test = pd.Series([50.0, 60.0])

    metrics, predictions = evaluate_model(model, X_test, y_test)

    assert metrics["mae"] == pytest.approx(0.0)
    assert metrics["r2"] == pytest.approx(1.0)
    assert metrics["n_test"] == 2
    assert list(predictions.columns) == ["actual", "prediction"]
    np.testing.assert_allclose(predictions["prediction"], [50.0, 60.0])
