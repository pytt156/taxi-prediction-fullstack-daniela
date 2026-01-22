from __future__ import annotations

import joblib
import pandas as pd

from taxipred.common.constants import MODEL, TAXI_CSV_CLEANED


def load_model():
    """Load the trained model artifact from disk."""
    return joblib.load(MODEL)


def load_training_data() -> pd.DataFrame:
    """Load the cleaned training dataset used for computing defaults and stats endpoints."""
    return pd.read_csv(TAXI_CSV_CLEANED)


def compute_dataset_defaults(df: pd.DataFrame) -> dict:
    """Compute fallback values used when optional inference inputs are missing."""
    return {
        "base_fare": df["base_fare"].median(),
        "per_km_rate": df["per_km_rate"].median(),
        "per_minute_rate": df["per_minute_rate"].median(),
        "weather": df["weather"].mode().iloc[0],
        "traffic_conditions": df["traffic_conditions"].mode().iloc[0],
    }
