
import pandas as pd
import pytest

from atelier_spaceflights.pipelines.data_processing.nodes import (
    _convert_indicators,
    create_model_input_table,
    preprocess_companies,
    preprocess_shuttles,
)


def test_convert_indicators():
    result = _convert_indicators(pd.Series(["t", "f"]))
    assert result.tolist() == [True, False]


def test_convert_indicators_rejects_invalid_value():
    with pytest.raises(ValueError, match="Unexpected indicator values"):
        _convert_indicators(pd.Series(["t", "unknown"]))


def test_preprocess_companies():
    companies = pd.DataFrame({
        "company_rating": ["85%", "100%"],
        "iata_approved": ["t", "f"],
    })
    result = preprocess_companies(companies)

    assert result["company_rating"].tolist() == [0.85, 1.0]
    assert result["iata_approved"].tolist() == [True, False]
    assert companies["company_rating"].tolist() == ["85%", "100%"]


def test_preprocess_shuttles():
    shuttles = pd.DataFrame({
        "price": ["$1,200.50", "$900.0"],
        "d_check_complete": ["t", "f"],
        "moon_clearance_complete": ["f", "t"],
    })
    result = preprocess_shuttles(shuttles)

    assert result["price"].tolist() == [1200.5, 900.0]
    assert result["d_check_complete"].tolist() == [True, False]
    assert result["moon_clearance_complete"].tolist() == [False, True]
    assert shuttles["price"].tolist() == ["$1,200.50", "$900.0"]



def test_create_model_input_table():
    shuttles = pd.DataFrame({
        "id": [1, 2],
        "company_id": [10, 20],
        "passenger_capacity": [100, 200],
        "price": [1200.0, 1500.0],
    })
    companies = pd.DataFrame({
        "id": [10, 20],
        "company_rating": [0.85, 0.95],
        "company_location": ["France", "USA"],
        "total_fleet_count": [5, 8],
        "iata_approved": [True, False],
    })
    reviews = pd.DataFrame({
        "shuttle_id": [1, 2],
        "review_scores_rating": [4.5, 4.8],
        "review_scores_comfort": [4.0, 4.5],
        "review_scores_amenities": [4.1, 4.6],
        "review_scores_trip": [4.2, 4.7],
        "review_scores_crew": [4.3, 4.8],
        "review_scores_location": [4.4, 4.9],
        "review_scores_price": [4.0, 4.5],
        "number_of_reviews": [10, 20],
        "reviews_per_month": [1.0, 2.0],
    })

    result = create_model_input_table(shuttles, companies, reviews)

    assert len(result) == 2
    assert result["id"].tolist() == [1, 2]
    assert result["company_rating"].tolist() == [0.85, 0.95]
    assert result["review_score"].tolist() == [4.5, 4.8]
    assert result["price"].tolist() == [1200.0, 1500.0]


def test_create_model_input_table_drops_missing_values():
    shuttles = pd.DataFrame({
        "id": [1, 2],
        "company_id": [10, 20],
        "passenger_capacity": [100, 200],
        "price": [1200.0, 1500.0],
    })
    companies = pd.DataFrame({
        "id": [10, 20],
        "company_rating": [0.85, None],
        "company_location": ["France", "USA"],
        "total_fleet_count": [5, 8],
        "iata_approved": [True, False],
    })
    reviews = pd.DataFrame({
        "shuttle_id": [1, 2],
        "review_scores_rating": [4.5, 4.8],
        "review_scores_comfort": [4.0, 4.5],
        "review_scores_amenities": [4.1, 4.6],
        "review_scores_trip": [4.2, 4.7],
        "review_scores_crew": [4.3, 4.8],
        "review_scores_location": [4.4, 4.9],
        "review_scores_price": [4.0, 4.5],
        "number_of_reviews": [10, 20],
        "reviews_per_month": [1.0, 2.0],
    })

    result = create_model_input_table(shuttles, companies, reviews)

    assert len(result) == 1
    assert result["id"].tolist() == [1]


def test_create_model_input_table_rejects_duplicate_reviews():
    shuttles = pd.DataFrame({
        "id": [1],
        "company_id": [10],
        "passenger_capacity": [100],
        "price": [1200.0],
    })
    companies = pd.DataFrame({
        "id": [10],
        "company_rating": [0.85],
        "company_location": ["France"],
        "total_fleet_count": [5],
        "iata_approved": [True],
    })
    reviews = pd.DataFrame({
        "shuttle_id": [1, 1],
        "review_scores_rating": [4.5, 4.6],
    })

    with pytest.raises(pd.errors.MergeError):
        create_model_input_table(shuttles, companies, reviews)
