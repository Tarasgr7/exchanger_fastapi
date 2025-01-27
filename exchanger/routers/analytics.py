from fastapi import APIRouter,Depends,status
from ..dependencies import SessionLocal
from..services.auth_service import get_current_user
from ..schemas.analytics_schemas import *
from ..services.analytics_service import *
from typing import Annotated
from ..services.utils import db_dependency,user_dependency





router=APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)


@router.get("/period-summary", response_model=SummaryResponse,status_code=status.HTTP_200_OK)
def statistics_summary_by_period(
    period: str,
    db: db_dependency,
    user: user_dependency
):
    start_date, end_date = calculate_date_range(period)
    summary = get_expenses_summary_for_user(db, user_id=user.get("id"), start_date=start_date, end_date=end_date)
    return {"period": period, "start_date": start_date, "end_date": end_date, "summary": summary}

# Ендпоінт для статистики за категоріями за період
@router.get("/period-by-category", response_model=CategoryStatsResponse,status_code=status.HTTP_200_OK)
def statistics_by_category_for_period(
    period: str,
    db: db_dependency,
    user: user_dependency
):
    start_date, end_date = calculate_date_range(period)
    stats = get_expenses_by_category_for_user(db, user_id=user.get("id"), start_date=start_date, end_date=end_date)
    return {"period": period, "start_date": start_date, "end_date": end_date, "statistics": stats}