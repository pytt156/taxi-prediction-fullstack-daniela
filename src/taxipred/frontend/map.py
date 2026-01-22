from __future__ import annotations

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


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
    if distance_km < 1:
        return 14
    if distance_km < 3:
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
            {
                "name": "Start",
                "label": point_a.get("display_name", "Point A"),
                "lat": point_a["lat"],
                "lon": point_a["lon"],
                "fill_color": [46, 204, 113, 230],
                "line_color": [255, 255, 255, 220],
            },
            {
                "name": "Destination",
                "label": point_b.get("display_name", "Point B"),
                "lat": point_b["lat"],
                "lon": point_b["lon"],
                "fill_color": [231, 76, 60, 230],
                "line_color": [255, 255, 255, 220],
            },
        ]
    )

    path_df = pd.DataFrame([{"path": geometry}])

    route_casing = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        get_color=[0, 0, 0, 140],
        width_min_pixels=8,
        rounded=True,
        pickable=False,
    )

    route_line = pdk.Layer(
        "PathLayer",
        data=path_df,
        get_path="path",
        get_color=[77, 163, 255, 220],
        width_min_pixels=4,
        rounded=True,
        pickable=False,
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_radius=110,
        get_fill_color="fill_color",
        get_line_color="line_color",
        line_width_min_pixels=3,
        pickable=True,
    )

    lons = [c[0] for c in geometry]
    lats = [c[1] for c in geometry]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    view_state = pdk.ViewState(
        latitude=(min_lat + max_lat) / 2,
        longitude=(min_lon + max_lon) / 2,
        zoom=zoom_for_distance_km(distance_km),
        pitch=0,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=[route_casing, route_line, scatter_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}\n{label}"},
        map_style="dark",
    )

    st.pydeck_chart(deck, width="stretch")
