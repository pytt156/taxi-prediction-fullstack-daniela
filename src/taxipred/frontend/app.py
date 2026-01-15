import streamlit as st
import requests

st.markdown("#Hejhej!")

API_URL = "http://localhost:8000/predict"
AUTO = "(auto)"

with st.form("prediction_form"):
    st.subheader("Required field:")
    trip_distance_km = st.number_input(
        "Trip distance (km)", min_value=0.1, value=5.0, step=0.1
    )

    passenger_count = None
    time_of_day = None
    day_of_week = None
    traffic_conditions = None
    weather = None
    base_fare = None
    per_km_rate = None
    per_minute_rate = None

    with st.expander("More options:"):
        st.caption("Leave empty to use defaults")

        passenger_count = st.number_input(
            "Number of passengers", min_value=1, max_value=8, value=1, step=1
        )
        time_of_day = st.selectbox(
            "Time of day", ["Now", "Morning", "Afternoon", "Evening", "Night"]
        )

        day_of_week = st.selectbox("Day of week", ["Today", "Weekday", "Weekend"])

        traffic_conditions = st.selectbox(
            "Traffic conditions", [AUTO, "Low", "Medium", "High"]
        )

        weather = st.selectbox("Weather", [AUTO, "Clear", "Rain", "Snow"])

        base_fare = st.number_input(
            "Base fare (optional)", min_value=0.0, value=0.0, step=0.5
        )

        per_km_rate = st.number_input(
            "Rate per kilometer (optional)", min_value=0.0, value=0.0, step=0.1
        )

        per_minute_rate = st.number_input(
            "Rate per minute (optional)", min_value=0.0, value=0.0, step=0.1
        )

    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "trip_distance_km": trip_distance_km,
        "time_of_day": None if time_of_day == "Now" else time_of_day,
        "day_of_week": None if day_of_week == "Today" else day_of_week,
        "passenger_count": passenger_count,
        "traffic_conditions": None
        if traffic_conditions == AUTO
        else traffic_conditions,
        "weather": None if weather == AUTO else weather,
        "base_fare": base_fare if base_fare > 0 else None,
        "per_km_rate": per_km_rate if per_km_rate > 0 else None,
        "per_minute_rate": per_minute_rate if per_minute_rate > 0 else None,
    }

    payload = {key: value for key, value in payload.items() if value is not None}

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        prediction = response.json()

        st.success(f"Prediciton: {prediction['prediction']:.2f}")

        with st.expander("Inputs used (incl. backend defaults)"):
            st.json(prediction.get("inputs_used", {}))

    except requests.Timeout:
        st.error("Timeout: API didn't answer in time")
    except requests.HTTPError:
        st.error(f"HTTP error {response.status_code}: {response.text}")
    except requests.RequestException as err:
        st.error(f"Request failed: {err}")
