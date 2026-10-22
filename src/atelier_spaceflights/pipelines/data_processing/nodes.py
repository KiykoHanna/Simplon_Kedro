
import pandas as pd


def _convert_indicators(series: pd.Series) -> pd.Series:
    """Convert t/f indicators to boolean values."""
    values = series.dropna().astype(str).str.strip().str.lower()
    invalid = ~values.isin(["t", "f"])
    if invalid.any():
        raise ValueError(
            f"Unexpected indicator values: {values[invalid].unique().tolist()}"
        )
    return series.map({"t": True, "f": False})


def preprocess_companies(companies: pd.DataFrame) -> pd.DataFrame:
    """Convert company ratings and approval indicators."""
    companies = companies.copy()
    companies["company_rating"] = (
        companies["company_rating"].str.rstrip("%").astype(float) / 100
    )
    companies["iata_approved"] = _convert_indicators(
        companies["iata_approved"]
    )
    return companies


def preprocess_shuttles(shuttles: pd.DataFrame) -> pd.DataFrame:
    """Convert prices and completion indicators."""
    shuttles = shuttles.copy()
    shuttles["price"] = (
        shuttles["price"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    for column in ["d_check_complete", "moon_clearance_complete"]:
        shuttles[column] = _convert_indicators(shuttles[column])
    return shuttles


def create_model_input_table(
    shuttles: pd.DataFrame,
    companies: pd.DataFrame,
    reviews: pd.DataFrame,
) -> pd.DataFrame:
    """Join shuttle, company, and review data for model training."""
    reviews = reviews.rename(
        columns={"shuttle_id": "id", "review_scores_rating": "review_score"}
    )

    model_input_table = shuttles.merge(
        reviews,
        on="id",
        how="left",
        validate="one_to_one",
    )

    companies = companies.rename(columns={"id": "company_id"})
    model_input_table = model_input_table.merge(
        companies,
        on="company_id",
        how="left",
        validate="many_to_one",
        suffixes=("", "_company"),
    )

    required_columns = [
        "passenger_capacity",
        "company_rating",
        "review_score",
        "price",
    ]
    model_input_table = model_input_table.dropna(
        subset=required_columns
    )

    return model_input_table.reset_index(drop=True)
