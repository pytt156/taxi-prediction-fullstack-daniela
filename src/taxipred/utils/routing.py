import pandas as pd
import pydeck as pdk
import requests
import streamlit as st
import os

API_BASE = st.session_state.get(
    "api_base_url", os.getenv("TAXIPRED_API_URL", "http://localhost:8000")
).rstrip("/")
PREDICT_URL = f"{API_BASE}/predict"


def geocode_nominatim(query: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "taxi-prediction-lab/1.0 (streamlit demo)"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError(f"No geocoding results for: {query}")

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0].get("display_name", query),
    }


def route_osrm(a_lon: float, a_lat: float, b_lon: float, b_lat: float) -> dict:
    url = f"https://router.project-osrm.org/route/v1/driving/{a_lon},{a_lat};{b_lon},{b_lat}"
    params = {"overview": "full", "geometries": "geojson"}

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("OSRM routing failed.")

    route = data["routes"][0]
    return {
        "distance_km": route["distance"] / 1000.0,
        "duration_min": route["duration"] / 60.0,
        "geometry": route["geometry"]["coordinates"],
    }


def predict_price(trip_distance_km: float) -> dict:
    payload = {"trip_distance_km": float(trip_distance_km)}
    try:
        r = requests.post(PREDICT_URL, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        raise ValueError(f"Backend error {r.status_code}: {r.text}")


def zoom_for_distance_km(d: float) -> int:
    if d < 2:
        return 13
    if d < 8:
        return 12
    if d < 20:
        return 10
    return 9


def make_map(a: dict, b: dict, geometry: list, distance_km: float) -> None:
    points = pd.DataFrame(
        [
            {"name": "A", "lat": a["lat"], "lon": a["lon"]},
            {"name": "B", "lat": b["lat"], "lon": b["lon"]},
        ]
    )

    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_radius=60,
        pickable=True,
    )

    path_df = pd.DataFrame([{"path": geometry}])
    path = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        width_min_pixels=4,
        pickable=False,
    )

    view_state = pdk.ViewState(
        latitude=(a["lat"] + b["lat"]) / 2,
        longitude=(a["lon"] + b["lon"]) / 2,
        zoom=zoom_for_distance_km(distance_km),
    )

    deck = pdk.Deck(
        layers=[path, scatter],
        initial_view_state=view_state,
        tooltip={"text": "{name}"},
        map_style="light",
    )
    st.pydeck_chart(deck, use_container_width=True)
