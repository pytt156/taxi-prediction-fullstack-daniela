from __future__ import annotations

import os
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


def get_api_base() -> str:
    return st.session_state.get(
        "api_base_url",
        os.getenv("TAXIPRED_API_URL", "http://localhost:8000"),
    ).rstrip("/")


def geocode_nominatim(query: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "taxi-prediction-lab/1.0 (streamlit demo)"}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

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

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("OSRM routing failed")

    route = data["routes"][0]
    return {
        "distance_km": route["distance"] / 1000.0,
        "duration_min": route["duration"] / 60.0,
        "geometry": route["geometry"]["coordinates"],
    }


def zoom_for_distance_km(distance_km: float) -> int:
    if distance_km < 2:
        return 13
    if distance_km < 8:
        return 12
    if distance_km < 20:
        return 10
    return 9


def render_map(
    point_a: dict,
    point_b: dict,
    geometry: list,
    distance_km: float,
) -> None:
    points = pd.DataFrame(
        [
            {"name": "A", "lat": point_a["lat"], "lon": point_a["lon"]},
            {"name": "B", "lat": point_b["lat"], "lon": point_b["lon"]},
        ]
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_radius=60,
        pickable=True,
    )

    path_df = pd.DataFrame([{"path": geometry}])
    path_layer = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        width_min_pixels=4,
        pickable=False,
    )

    view_state = pdk.ViewState(
        latitude=(point_a["lat"] + point_b["lat"]) / 2,
        longitude=(point_a["lon"] + point_b["lon"]) / 2,
        zoom=zoom_for_distance_km(distance_km),
    )

    deck = pdk.Deck(
        layers=[path_layer, scatter_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"},
        map_style="light",
    )

    st.pydeck_chart(deck, use_container_width=True)
