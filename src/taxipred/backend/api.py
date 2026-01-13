from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from taxipred.utils.constants import MODEL, TAXI_CSV_CLEANED
import joblib
import pandas as pd
from taxipred.backend.data_processing import (
    DataExplorer,
    PredictionInput,
    CreateDefaults,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL)
    app.state.df = pd.read_csv(TAXI_CSV_CLEANED)
    yield
    del app.state.df
    del app.state.model


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
    input_data = CreateDefaults(payload.model_dump()).apply()
    input_df = pd.DataFrame([input_data])
    prediction = app.state.model.predict(input_df)[0]
    return {"prediction": float(prediction)}
