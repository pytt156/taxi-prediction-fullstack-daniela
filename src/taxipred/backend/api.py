from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from taxipred.backend.schemas import PredictionInput
from taxipred.backend.responses import df_to_json_response
from taxipred.backend.services import apply_dataset_defaults, predict_with_model
from taxipred.backend.dependencies import (
    load_model,
    load_training_data,
    compute_dataset_defaults,
)
from taxipred.common.explore import DataExplorer


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = load_model()
    df = load_training_data()
    defaults = compute_dataset_defaults(df)

    app.state.model = model
    app.state.df = df
    app.state.defaults = defaults

    yield

    del app.state.model
    del app.state.df
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
    explorer = DataExplorer(app.state.df)
    return df_to_json_response(explorer.stats().df)


@app.get("/trips/sample")
async def sample(sample_size: int = Query(10, ge=1, le=100)):
    explorer = DataExplorer(app.state.df)
    return df_to_json_response(explorer.sample(sample_size).df)


@app.post("/predict")
async def predict(payload: PredictionInput):
    input_data = payload.model_dump()
    input_data = apply_dataset_defaults(input_data, app.state.defaults)
    prediction = predict_with_model(app.state.model, input_data)
    return {
        "prediction": prediction,
        "inputs_used": input_data,
    }
