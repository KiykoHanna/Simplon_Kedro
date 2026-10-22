
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


def split_data(table: pd.DataFrame, options: dict):
    """Split the model input table into training and test datasets."""
    features = options["features"]
    clean_table = table.dropna(subset=features + ["price"])
    X = clean_table[features]
    y = clean_table["price"]

    return train_test_split(
        X,
        y,
        test_size=options["test_size"],
        random_state=options["random_state"],
    )


def train_model(X_train: pd.DataFrame, y_train: pd.Series):
    """Train a linear regression model."""
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    return regressor


def evaluate_model(regressor, X_test: pd.DataFrame, y_test: pd.Series):
    """Evaluate the model and return metrics and predictions."""
    predictions = regressor.predict(X_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
        "n_test": int(len(y_test)),
    }

    predictions_df = pd.DataFrame({
        "actual": y_test.to_numpy(),
        "prediction": predictions,
    })

    return metrics, predictions_df
