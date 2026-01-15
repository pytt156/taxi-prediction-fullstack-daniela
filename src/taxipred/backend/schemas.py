from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from datetime import datetime
from zoneinfo import ZoneInfo


class PredictionInput(BaseModel):
    trip_distance_km: float = Field(gt=0, le=150)

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
    def fill_defaults(self):
        now = datetime.now(ZoneInfo("Europe/Stockholm"))

        if self.day_of_week is None:
            self.day_of_week = "Weekend" if now.weekday() >= 5 else "Weekday"

        if self.time_of_day is None:
            hour = now.hour
            if 6 <= hour < 12:
                self.time_of_day = "Morning"
            elif 12 <= hour < 18:
                self.time_of_day = "Afternoon"
            elif 18 <= hour < 22:
                self.time_of_day = "Evening"
            else:
                self.time_of_day = "Night"

        if self.trip_duration_minutes is None:
            self.trip_duration_minutes = (self.trip_distance_km / 40.0) * 60.0
        return self
