from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from taxipred.utils.constants import MODEL, TAXI_CSV_CLEANED
import joblib
import pandas as pd


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL)
    app.state.df = pd.read_csv(TAXI_CSV_CLEANED)
    yield
    del app.state.df
    del app.state.model


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api")


@router.get("/summary")
async def read_summary_data():
    pass
