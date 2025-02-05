import os
import smtplib
import logging
import redis.asyncio as redis
import json
from time import time
from datetime import datetime, timedelta
from typing import Annotated
from ..services.redis_client import get_redis

from fastapi import APIRouter, HTTPException, status, Path,Depends
from ..models.category_model import Category
from ..models.expense_model import Expense
from ..schemas.category_schemas import CreateCategory
from ..schemas.expense_schemas import ExpenseCreatedModel
from ..services.utils import db_dependency, user_dependency
from ..dependencies import logger


router = APIRouter(
  prefix="/expenses",
  tags=["expenses"]
)

router = APIRouter(
  prefix="/expenses",
  tags=["expenses"]
)


@router.get('/', status_code=status.HTTP_200_OK)
async def read_expenses(db: db_dependency, user: user_dependency, redis_client: redis.Redis = Depends(get_redis)):
    start_time = time()  # Початок вимірювання часу
    logger.info("Отримання списку витрат")
    
    # Генеруємо ключ для кешу
    cache_key = f"expenses_{user.get('id')}"
    
    # Перевіряємо наявність даних у кеші Redis
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        # Якщо дані є в кеші, парсимо їх і повертаємо
        expenses = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")
        # Якщо даних немає, виконуємо запит до БД
        expenses = db.query(Expense).filter(Expense.user_id == user.get('id')).all()
        logger.info(f"Знайдено {len(expenses)} витрат")
        
        # Зберігаємо дані в кеш Redis на 60 секунд
        expenses_data = [{"id": e.id, "amount": e.amount, "description": e.description} for e in expenses]
        await redis_client.set(cache_key, json.dumps(expenses_data), ex=60)
        logger.info(f"✅ Додано в кеш Redis на 60 секунд: {len(expenses)} витрат")

    # Вимірювання часу виконання
    execution_time = time() - start_time
    logger.info(f"⏳ Час виконання запиту: {execution_time:.4f} секунд")

    return expenses

@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_expense(expense: ExpenseCreatedModel, db: db_dependency, user: user_dependency):
    logger.info(f"Спроба створення витрати: {expense.description}, сума: {expense.amount}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    new_expense = Expense(
        amount=expense.amount,
        description=expense.description,
        category_id=expense.category_id,
        user_id=user.get('id')
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    logger.info(f"Витрата ID {new_expense.id} успішно створена")
    return new_expense

@router.put("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_expense(expense_id: int, expense: ExpenseCreatedModel, db: db_dependency, user: user_dependency):
    logger.info(f"Спроба оновлення витрати ID: {expense_id}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    exists_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.get('id')).first()
    if not exists_expense:
        logger.warning(f"Витрата ID {expense_id} не знайдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    
    exists_expense.amount = expense.amount
    exists_expense.description = expense.description
    exists_expense.category_id = expense.category_id
    db.commit()
    logger.info(f"Витрата ID {expense_id} оновлена")

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: int, db: db_dependency, user: user_dependency):
    logger.info(f"Спроба видалення витрати ID: {expense_id}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    exists_expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.get('id')).first()
    if not exists_expense:
        logger.warning(f"Витрата ID {expense_id} не знайдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    
    db.delete(exists_expense)
    db.commit()
    logger.info(f"Витрата ID {expense_id} видалена")