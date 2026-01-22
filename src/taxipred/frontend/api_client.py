from __future__ import annotations

import os
import requests
import streamlit as st

AUTO = "(auto)"


def get_api_base() -> str:
    """Return API base URL from session state or environment variable."""
    return st.session_state.get(
        "api_base_url",
        os.getenv("TAXIPRED_API_URL", "http://localhost:8000"),
    ).rstrip("/")


def build_prediction_payload(
    *,
    trip_distance_km: float,
    passenger_count: int,
    time_of_day: str,
    day_of_week: str,
    traffic_conditions: str,
    weather: str,
    base_fare: float,
    per_km_rate: float,
    per_minute_rate: float,
) -> dict:
    """
    Build the JSON payload expected by the FastAPI `/predict` endpoint.

    Note:
        UI "Now/Today" and "(auto)" selections are translated to omitted fields
        so the backend can apply defaults.
    """
    payload = {
        "trip_distance_km": float(trip_distance_km),
        "passenger_count": int(passenger_count),
        "time_of_day": None if time_of_day == "Now" else time_of_day,
        "day_of_week": None if day_of_week == "Today" else day_of_week,
        "traffic_conditions": None
        if traffic_conditions == AUTO
        else traffic_conditions,
        "weather": None if weather == AUTO else weather,
        "base_fare": base_fare if base_fare > 0 else None,
        "per_km_rate": per_km_rate if per_km_rate > 0 else None,
        "per_minute_rate": per_minute_rate if per_minute_rate > 0 else None,
    }
    return {k: v for k, v in payload.items() if v is not None}


def _post(path: str, payload: dict) -> dict:
    """POST JSON to the API and return the decoded response."""
    url = f"{get_api_base()}{path}"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
