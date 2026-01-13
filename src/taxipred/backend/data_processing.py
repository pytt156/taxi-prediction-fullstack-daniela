from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
import json
from fastapi.responses import JSONResponse


class PredictionInput(BaseModel):
    trip_distance_km: float = Field(gt=0)
    time_of_day: Optional[Literal["Morning", "Afternoon", "Evening", "Night"]] = None
    day_of_week: Optional[Literal["Weekday", "Weekend"]] = None

    passenger_count: int = Field(default=1, ge=1, le=8)
    traffic_conditions: Optional[Literal["Low", "Medium", "High"]] = None
    weather: Optional[Literal["Clear", "Rain", "Snow"]] = None

    base_fare: Optional[float] = None
    per_km_rate: Optional[float] = None
    per_minute_rate: Optional[float] = None

    trip_duration_minutes: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def fill_duration_if_missing(self):
        if self.trip_duration_minutes is None:
            self.trip_duration_minutes = (self.trip_distance_km / 40.0) * 60.0
        return self


class DataExplorer:
    def __init__(self, df, limit=100):
        self._df_full = df
        self._df = df.head(limit)

    @property
    def df(self):
        return self._df

    def stats(self):
        self._df = self._df_full.describe().drop(["count"]).T.reset_index()
        return self

    def sample(self, sample_size: int = 10):
        self._df = self._df_full.sample(sample_size)
        return self

    def json_response(self):
        json_data = self.df.to_json(orient="records")
        return JSONResponse(json.loads(json_data))
