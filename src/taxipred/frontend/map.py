import os
import requests
import folium

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY missing")


def geocode(address: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data["status"] != "OK":
        return None

    location = data["results"][0]["geometry"]["location"]
    return location["lat"], location["lon"]


def get_route(origin: str, destination: str):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def build_map(a_latlon, b_latlon):
    center = [(a_latlon[0], b_latlon[0]) / 2, (a_latlon[1], b_latlon[1]) / 2]
    map = folium.Map(location=center, zoom_start=10)
    folium.Marker(a_latlon, popup="A").add_to(map)
    folium.Marker(b_latlon, popup="B").add_to(map)
    folium.Polyline([a_latlon, b_latlon]).add_to(map)
    return map
