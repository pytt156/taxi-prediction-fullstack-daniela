from __future__ import annotations

import streamlit as st

from taxipred.utils.routing import geocode_nominatim, route_osrm, render_map
from taxipred.utils.prediction import (
    build_payload,
    call_prediction_api,
    AUTO,
)

st.set_page_config(
    page_title="Taxi Price Predictor",
    page_icon="🚕",
    layout="wide",
)

st.title("Taxi Price Predictor")
st.caption("Choose to enter distance directly or provide Point A and Point B.")

MAX_DISTANCE_KM = 50.0


################ SIDEBAR
with st.sidebar:
    st.header("Predict Taxi Price")

    input_mode = st.radio(
        "Input mode",
        ["Distance (km)", "Point A + Point B"],
        index=0,
    )

    with st.form("prediction_form"):
        if input_mode == "Distance (km)":
            distance_km_input = st.number_input(
                "Trip distance (km)",
                min_value=0.1,
                max_value=MAX_DISTANCE_KM,
                value=5.0,
                step=0.1,
            )
            place_a = place_b = ""
        else:
            place_a = st.text_input("Point A", value="Jordbro Centrum")
            place_b = st.text_input("Point B", value="Stockholm Centralstation")
            distance_km_input = None

        with st.expander("Optional parameters"):
            c1, c2 = st.columns(2)
            with c1:
                passenger_count = st.number_input("Passengers", 1, 8, 1)
                time_of_day = st.selectbox(
                    "Time of day",
                    ["Now", "Morning", "Afternoon", "Evening", "Night"],
                )
                traffic_conditions = st.selectbox(
                    "Traffic conditions",
                    [AUTO, "Low", "Medium", "High"],
                )
            with c2:
                day_of_week = st.selectbox(
                    "Day of week",
                    ["Today", "Weekday", "Weekend"],
                )
                weather = st.selectbox(
                    "Weather",
                    [AUTO, "Clear", "Rain", "Snow"],
                )

            st.divider()
            r1, r2, r3 = st.columns(3)
            with r1:
                base_fare = st.number_input("Base fare", 0.0, 5.0, 0.0, 0.5)
            with r2:
                per_km_rate = st.number_input("Rate per km", 0.0, 2.0, 0.0, 0.1)
            with r3:
                per_minute_rate = st.number_input("Rate per minute", 0.0, 0.5, 0.0, 0.1)

        submitted = st.form_submit_button("Predict", use_container_width=True)


################### MAIN
left, right = st.columns([1, 1], gap="large")

prediction = None
route_data = None
distance_km = None
error_message = None

if submitted:
    try:
        if input_mode == "Distance (km)":
            distance_km = float(distance_km_input)
        else:
            if not place_a.strip() or not place_b.strip():
                raise ValueError("Both Point A and Point B must be provided.")

            with st.spinner("Geocoding..."):
                point_a = geocode_nominatim(place_a)
                point_b = geocode_nominatim(place_b)

            with st.spinner("Routing..."):
                route = route_osrm(
                    point_a["lon"],
                    point_a["lat"],
                    point_b["lon"],
                    point_b["lat"],
                )

            distance_km = float(route["distance_km"])
            if distance_km > MAX_DISTANCE_KM:
                raise ValueError("Route distance exceeds model limits.")

            route_data = {
                "a": point_a,
                "b": point_b,
                "geometry": route["geometry"],
                "duration_min": route["duration_min"],
            }

        payload = build_payload(
            trip_distance_km=distance_km,
            passenger_count=passenger_count,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            traffic_conditions=traffic_conditions,
            weather=weather,
            base_fare=base_fare,
            per_km_rate=per_km_rate,
            per_minute_rate=per_minute_rate,
        )

        prediction = call_prediction_api(payload)

    except Exception as e:
        error_message = str(e)


with left:
    st.subheader("Prediction")
    if not submitted:
        st.info("Fill in the inputs and click Predict.")
    elif error_message:
        st.error(error_message)
    else:
        st.metric("Predicted price", f"{prediction['prediction']:.2f}")
        st.metric("Distance (km)", f"{distance_km:.2f}")
        if route_data:
            st.metric("ETA (min)", f"{route_data['duration_min']:.0f}")

        with st.expander("Inputs used"):
            st.json(prediction.get("inputs_used", {}))


with right:
    st.subheader("Map")
    if route_data:
        render_map(
            route_data["a"],
            route_data["b"],
            route_data["geometry"],
            distance_km,
        )
    else:
        st.info("Map is shown when using Point A + Point B.")
