from datetime import date
from pydantic import BaseModel

class SummaryResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    summary: dict

class CategoryStatsResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    statistics: list[dict]