from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from taxipred.utils.constants import MODEL, TAXI_CSV_CLEANED
import joblib
import pandas as pd
from taxipred.backend.schemas import PredictionInput
from taxipred.backend.explore import DataExplorer


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL)
    app.state.df = pd.read_csv(TAXI_CSV_CLEANED)
    app.state.defaults = {
        "base_fare": app.state.df["base_fare"].median(),
        "per_km_rate": app.state.df["per_km_rate"].median(),
        "per_minute_rate": app.state.df["per_minute_rate"].median(),
        "weather": app.state.df["weather"].mode().iloc[0],
        "traffic_conditions": app.state.df["traffic_conditions"].mode().iloc[0],
    }
    yield
    del app.state.df
    del app.state.model
    del app.state.defaults


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def start():
    return {"message": "Taxi Prediction API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/stats")
async def stats():
    data = DataExplorer(app.state.df)
    return data.stats().json_response()


@app.get("/trips/sample")
async def sample(sample_size: int = Query(10, ge=1, le=100)):
    data = DataExplorer(app.state.df)
    return data.sample(sample_size).json_response()


@app.post("/predict")
async def predict(payload: PredictionInput):
    input_data = payload.model_dump()
    for key, value in app.state.defaults.items():
        if input_data.get(key) is None:
            input_data[key] = value
    input_df = pd.DataFrame([input_data])
    prediction = app.state.model.predict(input_df)[0]
    return {"prediction": float(prediction), "inputs_used": input_data}
