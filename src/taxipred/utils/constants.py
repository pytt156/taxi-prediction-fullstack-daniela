from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3].resolve()
DATA_PATH = PROJECT_ROOT / "data"
CLEANED_DATA = DATA_PATH / "processed"

TAXI_CSV_RAW = DATA_PATH / "raw" / "taxi_trip_pricing.csv"
TAXI_CSV_CLEANED = CLEANED_DATA / "taxi_fillednan_all_columns.csv"

MODEL_PATH = Path(__file__).parents[3].resolve() / "models"
MODEL = MODEL_PATH / "taxi_price_predictor"
