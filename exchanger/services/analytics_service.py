from datetime import date,timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.expense_model import Expense
from fastapi import HTTPException

def calculate_date_range(period: str):
    today = date.today()
    if period == "day":
        start_date = today
        end_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Choose from: day, week, month, year.")
    return start_date, end_date

# CRUD-функція для загальної статистики витрат
def get_expenses_summary_for_user(db: Session, user_id: int, start_date: date, end_date: date):
    total_amount = (
        db.query(func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        )
        .scalar()
    )
    return {"total_amount": total_amount or 0.0}

# CRUD-функція для статистики за категоріями
def get_expenses_by_category_for_user(db: Session, user_id: int, start_date: date, end_date: date):
    results = (
        db.query(Expense.category_id, func.sum(Expense.amount).label("total"))
        .filter(
            Expense.user_id == user_id,
            Expense.created_at >= start_date,
            Expense.created_at <= end_date
        )
        .group_by(Expense.category_id)
        .all()
    )
    return [{"category_id": result.category_id, "total": result.total} for result in results]