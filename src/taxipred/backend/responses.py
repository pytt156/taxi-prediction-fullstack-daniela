import json
from fastapi.responses import JSONResponse


def df_to_json_response(df):
    return JSONResponse(json.loads(df.to_json(orient="records")))
