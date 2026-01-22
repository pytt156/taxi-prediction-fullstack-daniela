from __future__ import annotations

import pandas as pd


def apply_dataset_defaults(input_data: dict, defaults: dict) -> dict:
    for key, value in defaults.items():
        if input_data.get(key) is None:
            input_data[key] = value
    return input_data


def predict_with_model(model, input_data: dict) -> float:
    input_df = pd.DataFrame([input_data])
    return float(model.predict(input_df)[0])
