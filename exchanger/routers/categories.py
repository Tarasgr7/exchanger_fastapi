import os
import smtplib
import redis
import json
import logging
from datetime import datetime, timedelta
from time import time
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path,Depends
from ..models.category_model import Category
from ..schemas.category_schemas import CreateCategory
from ..services.redis_client import get_redis
from ..services.utils import db_dependency, user_dependency
from ..dependencies import logger
# Налаштування логування


router = APIRouter(
  prefix="/categories",
  tags=["categories"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def read_categories(db: db_dependency, redis_client: redis.Redis = Depends(get_redis)):
    start_time = time()  # Початок вимірювання часу
    cache_key = "categories_list"

    # Перевіряємо кеш у Redis
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        categories = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")
        categories = db.query(Category).all()
        categories_data = [{"id": c.id, "name": c.name} for c in categories]

        # Зберігаємо у Redis на 60 секунд
        await redis_client.set(cache_key, json.dumps(categories_data), ex=60)
        logger.info(f"✅ Додано в кеш Redis на 60 секунд: {len(categories)} категорій")

    execution_time = time() - start_time  # Кінець вимірювання часу
    logger.info(f"⏳ Час виконання запиту: {execution_time:.4f} секунд")

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
