import json
from fastapi.responses import JSONResponse


class DataExplorer:
    def __init__(self, df, limit=100):
        self._df_full = df
        self._df = df.head(limit)

        @property
        def df(self):
            return self._df

        def summary(self):
            self._df = self._df_full.describe().T

        def json_response(self):
            json_data = self.df.to_json(orient="records")
            return JSONResponse(json.loads(json_data))
