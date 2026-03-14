from pydantic import BaseModel
from typing import List

class UVResponse(BaseModel):
    uv_index: float
    level: str           # Low / Moderate / High / Very High / Extreme
    level_color: str     # hex color for frontend gauge
    burn_time_minutes: int
    alert_message: str
    spf_recommendation: str
    hourly_forecast: List[dict]  # [{time, uv_index, level}]