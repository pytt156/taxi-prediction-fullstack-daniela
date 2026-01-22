import json
import pandas as pd
from fastapi.responses import JSONResponse


def df_to_json_response(df: pd.DataFrame) -> JSONResponse:
    """Serialize a DataFrame to a JSON array response (records orientation)."""
    return JSONResponse(json.loads(df.to_json(orient="records")))
