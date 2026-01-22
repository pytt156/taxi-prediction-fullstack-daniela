from __future__ import annotations

import pandas as pd
import joblib

from taxipred.common.constants import MODEL, TAXI_CSV_CLEANED


def load_model():
    """
    Load trained ML model.
    Intended to be called once at app startup.
    """
    return joblib.load(MODEL)


def load_training_data() -> pd.DataFrame:
    """
    Load cleaned training dataset.
    """
    return pd.read_csv(TAXI_CSV_CLEANED)


def compute_dataset_defaults(df: pd.DataFrame) -> dict:
    """
    Compute dataset-based default values used during inference
    when optional inputs are missing.
    """
    return {
        "base_fare": df["base_fare"].median(),
        "per_km_rate": df["per_km_rate"].median(),
        "per_minute_rate": df["per_minute_rate"].median(),
        "weather": df["weather"].mode().iloc[0],
        "traffic_conditions": df["traffic_conditions"].mode().iloc[0],
    }
