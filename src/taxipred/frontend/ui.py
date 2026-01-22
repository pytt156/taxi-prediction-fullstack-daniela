from __future__ import annotations

import streamlit as st

from taxipred.common.constants import TAXI_CSV_CLEANED, HEADER
from taxipred.common.explore import DataExplorer
from taxipred.frontend.api_client import (
    AUTO,
    build_prediction_payload,
    call_prediction_api,
)
from taxipred.frontend.data import load_training_data
from taxipred.frontend.map import geocode_nominatim, route_osrm, render_map


def configure_page() -> None:
    """Configure Streamlit page settings (title, icon, layout)."""
    st.set_page_config(page_title="Taxi Price Predictor", page_icon="🚕", layout="wide")


def render_header() -> None:
    """Render the page header image."""
    st.image(HEADER, width="stretch")


def render_app(max_distance_km: float) -> None:
    """Render the full app (sidebar, main panels, and info sections)."""
    form = _render_sidebar(max_distance_km)
    state = _handle_submit(form, max_distance_km)

    _render_main(state)
    _render_about()
    _render_training_stats()


def _render_sidebar(max_distance_km: float) -> dict:
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
                    max_value=max_distance_km,
                    value=5.0,
                    step=0.1,
                )
                place_a = ""
                place_b = ""
            else:
                distance_km_input = None
                place_a = st.text_input("Point A", value="Jordbro Centrum")
                place_b = st.text_input("Point B", value="Stockholm Centralstation")

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
                    per_minute_rate = st.number_input(
                        "Rate per minute", 0.0, 0.5, 0.0, 0.1
                    )

            submitted = st.form_submit_button("Predict", width="stretch")

        with st.expander("How it works"):
            st.markdown(
                """
                1. Enter trip details here in the sidebar  
                2. Optional parameters fall back to dataset-based defaults  
                3. Inputs are passed to a trained ML pipeline via FastAPI  
                4. The model returns an estimated trip price  
                """
            )

    return {
        "submitted": submitted,
        "input_mode": input_mode,
        "distance_km_input": float(distance_km_input)
        if distance_km_input is not None
        else None,
        "place_a": place_a,
        "place_b": place_b,
        "passenger_count": int(passenger_count),
        "time_of_day": str(time_of_day),
        "day_of_week": str(day_of_week),
        "traffic_conditions": str(traffic_conditions),
        "weather": str(weather),
        "base_fare": float(base_fare),
        "per_km_rate": float(per_km_rate),
        "per_minute_rate": float(per_minute_rate),
    }


def _handle_submit(form: dict, max_distance_km: float) -> dict:
    if not form["submitted"]:
        return {"submitted": False}

    try:
        route_data = None

        if form["input_mode"] == "Distance (km)":
            if form["distance_km_input"] is None:
                raise ValueError("Distance input is missing.")
            distance_km = float(form["distance_km_input"])
        else:
            if not form["place_a"].strip() or not form["place_b"].strip():
                raise ValueError("Both Point A and Point B must be provided.")

            with st.spinner("Geocoding..."):
                point_a = geocode_nominatim(form["place_a"])
                point_b = geocode_nominatim(form["place_b"])

            with st.spinner("Routing..."):
                route = route_osrm(
                    point_a["lon"],
                    point_a["lat"],
                    point_b["lon"],
                    point_b["lat"],
                )

            distance_km = float(route["distance_km"])
            if distance_km > max_distance_km:
                raise ValueError("Route distance exceeds model limits.")

            route_data = {
                "a": point_a,
                "b": point_b,
                "geometry": route["geometry"],
                "duration_min": float(route["duration_min"]),
            }

        payload = build_prediction_payload(
            trip_distance_km=distance_km,
            passenger_count=form["passenger_count"],
            time_of_day=form["time_of_day"],
            day_of_week=form["day_of_week"],
            traffic_conditions=form["traffic_conditions"],
            weather=form["weather"],
            base_fare=form["base_fare"],
            per_km_rate=form["per_km_rate"],
            per_minute_rate=form["per_minute_rate"],
        )

        with st.spinner("Predicting..."):
            prediction = call_prediction_api(payload)

        return {
            "submitted": True,
            "error_message": None,
            "prediction": prediction,
            "distance_km": distance_km,
            "route_data": route_data,
        }

    except Exception as e:
        return {
            "submitted": True,
            "error_message": str(e),
        }


def _render_main(state: dict) -> None:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Prediction")
        if not state.get("submitted"):
            st.info("Fill in the inputs and click Predict.")
        elif state.get("error_message"):
            st.error(state["error_message"])
        else:
            prediction = state["prediction"]
            distance_km = state["distance_km"]
            route_data = state.get("route_data")

            st.metric("Predicted price", f"{prediction['prediction']:.2f} $")
            st.metric("Distance", f"{distance_km:.2f} km")
            if route_data:
                st.metric("ETA", f"{route_data['duration_min']:.0f} min")

            with st.expander("Inputs used"):
                st.json(prediction.get("inputs_used", {}))

    with right:
        st.subheader("Map")
        route_data = state.get("route_data")
        if route_data:
            render_map(
                route_data["a"],
                route_data["b"],
                route_data["geometry"],
                state["distance_km"],
            )
        else:
            st.info("Map is shown when using Point A + Point B.")


def _render_about() -> None:
    with st.expander("About the site"):
        st.markdown(
            """
            **Source**  
            Historical taxi trip data used for training a regression model.

            **Target**  
            Trip price (continuous).

            **Key features**
            - Trip distance (km)
            - Time of day
            - Day of week
            - Passenger count
            - Traffic conditions
            - Weather conditions
            - Pricing parameters (base fare, per-km, per-minute)

            **Preprocessing**
            - Numerical features: median imputation
            - Categorical features: most-frequent imputation + one-hot encoding

            **Model**
            - Random Forest Regressor
            - Trained using a scikit-learn Pipeline

            **Notes**
            - Predictions are most reliable for trips under 50 km  
            - This is a demonstration model, not a production pricing system
            """
        )


def _render_training_stats() -> None:
    df = load_training_data(TAXI_CSV_CLEANED)
    explorer = DataExplorer(df)
    with st.expander("Training data stats"):
        stats_df = explorer.stats().df
        st.dataframe(stats_df, width="stretch", hide_index=True)
