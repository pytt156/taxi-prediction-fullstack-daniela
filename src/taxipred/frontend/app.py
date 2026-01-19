import streamlit as st
import requests

st.set_page_config(
    page_title="Taxi Price Predictor",
    page_icon="🚕",
    layout="wide",
)

st.title("Taxi Price Predictor")
st.caption("Enter trip details and get an estimated fare from the ML model.")

API_URL = "http://localhost:8000/predict"
AUTO = "(auto)"

left, right = st.columns([1, 1], gap="large")

with left:
    with st.form("prediction_form"):
        st.subheader("Trip basics")

        trip_distance_km = st.number_input(
            "Trip distance (km)",
            min_value=0.1,
            max_value=50.0,
            value=5.0,
            step=0.1,
            help="Supported range: 0.1–50 km (model is most reliable here).",
        )

        with st.expander("More options (optional)"):
            st.caption("Leave as default to let the backend use its defaults.")

            c1, c2 = st.columns(2)

            with c1:
                passenger_count = st.number_input(
                    "Passengers",
                    min_value=1,
                    max_value=8,
                    value=1,
                    step=1,
                )
                time_of_day = st.selectbox(
                    "Time of day",
                    ["Now", "Morning", "Afternoon", "Evening", "Night"],
                )
                traffic_conditions = st.selectbox(
                    "Traffic",
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
            st.caption("Custom pricing (override backend defaults)")

            r1, r2, r3 = st.columns(3)
            with r1:
                base_fare = st.number_input(
                    "Base fare",
                    min_value=0.0,
                    max_value=5.0,
                    value=0.0,
                    step=0.5,
                    help="Set to 0 to use backend default.",
                )
            with r2:
                per_km_rate = st.number_input(
                    "Rate / km",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.0,
                    step=0.1,
                    help="Set to 0 to use backend default.",
                )
            with r3:
                per_minute_rate = st.number_input(
                    "Rate / min",
                    min_value=0.0,
                    max_value=0.5,
                    value=0.0,
                    step=0.1,
                    help="Set to 0 to use backend default.",
                )

        submitted = st.form_submit_button("Predict", use_container_width=True)

with right:
    st.subheader("Result")
    result_box = st.container(border=True)

    if not submitted:
        with result_box:
            st.info("Fill in the form and click **Predict** to see the estimated fare.")
    else:
        payload = {
            "trip_distance_km": trip_distance_km,
            "time_of_day": None if time_of_day == "Now" else time_of_day,
            "day_of_week": None if day_of_week == "Today" else day_of_week,
            "passenger_count": passenger_count,
            "traffic_conditions": None if traffic_conditions == AUTO else traffic_conditions,
            "weather": None if weather == AUTO else weather,
            "base_fare": base_fare if base_fare > 0 else None,
            "per_km_rate": per_km_rate if per_km_rate > 0 else None,
            "per_minute_rate": per_minute_rate if per_minute_rate > 0 else None,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            with st.spinner("Calling the API..."):
                response = requests.post(API_URL, json=payload, timeout=10)
                response.raise_for_status()
                prediction = response.json()

            with result_box:
                st.metric(
                    label="Predicted price",
                    value=f"{prediction['prediction']:.2f}",
                )

                with st.expander("Inputs used (incl. backend defaults)"):
                    st.json(prediction.get("inputs_used", {}))

        except requests.Timeout:
            with result_box:
                st.error("Timeout: API didn't answer in time.")
        except requests.HTTPError:
            with result_box:
                st.error(f"HTTP error {response.status_code}: {response.text}")
        except requests.RequestException as err:
            with result_box:
                st.error(f"Request failed: {err}")
