import os
import requests
import streamlit as st
from taxipred.utils.routing import (
    geocode_nominatim,
    make_map,
    predict_price,
    route_osrm,
)

st.set_page_config(page_title="Routes", page_icon="🗺️", layout="wide")

st.title("Route-based taxi prediction")
st.caption(
    "Enter A and B. The app geocodes with Nominatim, routes via OSRM, "
    "uses the route distance for prediction, and shows the route on a map."
)

API_BASE = st.session_state.get(
    "api_base_url", os.getenv("TAXIPRED_API_URL", "http://localhost:8000")
).rstrip("/")
PREDICT_URL = f"{API_BASE}/predict"
MAX_DISTANCE_KM = 50.0


with st.sidebar:
    st.subheader("Backend")
    st.code(PREDICT_URL)
    st.caption(f"Model distance limit: {MAX_DISTANCE_KM:.0f} km")


left, right = st.columns([1, 1], gap="large")

with left:
    with st.form("route_form"):
        st.subheader("Route inputs")
        place_a = st.text_input("Place A", value="Stockholm Centralstation")
        place_b = st.text_input("Place B", value="Arlanda Airport")
        submitted = st.form_submit_button("Route + predict", use_container_width=True)

with right:
    result_box = st.container(border=True)

if not submitted:
    with result_box:
        st.info("Enter A and B, then click **Route + predict**.")
else:
    try:
        with st.spinner("Geocoding A and B..."):
            a = geocode_nominatim(place_a)
            b = geocode_nominatim(place_b)

        with st.spinner("Routing via OSRM..."):
            route = route_osrm(a["lon"], a["lat"], b["lon"], b["lat"])

        distance_km = float(route["distance_km"])

        if distance_km > MAX_DISTANCE_KM:
            with result_box:
                st.error(
                    f"Route distance is {distance_km:.2f} km, which exceeds the model's supported range "
                    f"({MAX_DISTANCE_KM:.0f} km). Choose closer locations."
                )
            st.stop()

        with st.spinner("Calling FastAPI /predict..."):
            pred = predict_price(distance_km)

        with result_box:
            st.metric("Distance (km)", f"{distance_km:.2f}")
            st.metric("ETA (min)", f"{route['duration_min']:.0f}")
            st.metric("Predicted price", f"{float(pred['prediction']):.2f}")

            with st.expander("Resolved locations"):
                st.write("A:", a["display_name"])
                st.write("B:", b["display_name"])

            with st.expander("Inputs used (incl. backend defaults)"):
                st.json(pred.get("inputs_used", {"trip_distance_km": distance_km}))

        st.divider()
        st.subheader("Map")
        make_map(a, b, route["geometry"], distance_km)

    except ValueError as e:
        with result_box:
            st.error(str(e))
    except requests.Timeout:
        with result_box:
            st.error("Timeout: geocoding/routing/prediction took too long.")
    except requests.RequestException as e:
        with result_box:
            st.error(f"Request failed: {e}")
