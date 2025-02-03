import os
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from ..models.category_model import Category
from ..models.expense_model import Expense
from ..schemas.category_schemas import CreateCategory
from ..schemas.expense_schemas import ExpenseCreatedModel
from ..services.utils import db_dependency, user_dependency
from ..dependencies import logger


router = APIRouter(
  prefix="/categories",
  tags=["categories"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def read_categories(db: db_dependency):
    logger.info("Отримання списку категорій")
    categories = db.query(Category).all()
    logger.info(f"Знайдено {len(categories)} категорій")
    return categories

@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_category(category: CreateCategory, db: db_dependency, user: user_dependency):
    logger.info(f"Спроба створення категорії: {category.name}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if db.query(Category).filter(Category.name == category.name).first():
        logger.warning(f"Категорія {category.name} вже існує")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    new_category = Category(
        name=category.name,
        user_id=user.get('id'))
    db.add(new_category)
    db.commit()
    logger.info(f"Категорія {category.name} успішно створена")

@router.put("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(user: user_dependency, db: db_dependency, category: CreateCategory, category_id: int = Path(gt=0)):
    logger.info(f"Спроба оновлення категорії ID: {category_id}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    exists_category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.get('id')).first()
    if not exists_category:
        logger.warning(f"Категорія ID {category_id} не знайдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    exists_category.name = category.name
    db.commit()
    logger.info(f"Категорія ID {category_id} оновлена")

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(user: user_dependency, db: db_dependency, category_id: int = Path(gt=0)):
    logger.info(f"Спроба видалення категорії ID: {category_id}")
    if not user:
        logger.warning("Користувач не авторизований")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.get('id')).first()
    if not category:
        logger.warning(f"Категорія ID {category_id} не знайдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()
    logger.info(f"Категорія ID {category_id} видалена")

router = APIRouter(
  prefix="/expenses",
  tags=["expenses"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def read_expenses(db: db_dependency, user: user_dependency):
    logger.info("Отримання списку витрат")
    expenses = db.query(Expense).filter(Expense.user_id == user.get('id')).all()
    logger.info(f"Знайдено {len(expenses)} витрат")
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