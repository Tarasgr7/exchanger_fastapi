import os
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from ..models.category_model import Category
from ..schemas.category_schemas import CreateCategory
from ..services.utils import db_dependency, user_dependency
from ..dependencies import logger
# Налаштування логування


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
