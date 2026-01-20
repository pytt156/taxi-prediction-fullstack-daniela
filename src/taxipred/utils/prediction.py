from __future__ import annotations
import requests

from taxipred.utils.routing import get_api_base


AUTO = "(auto)"


def build_payload(
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

    return {key: value for key, value in payload.items() if value is not None}


def call_prediction_api(payload: dict) -> dict:
    url = f"{get_api_base()}/predict"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
