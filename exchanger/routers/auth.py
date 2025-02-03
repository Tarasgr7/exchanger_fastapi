from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..models.users_model import Users
from ..schemas.user_schemas import CreateUserSchema
from ..schemas.token_schemas import Token
from ..dependencies import SECRET_KEY, ALGORITHM,logger
from ..services.auth_service import *
from ..services.utils import db_dependency

import uuid
import logging


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get('/users', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    logger.info("Отримання всіх користувачів з бази даних")
    
    users = db.query(Users).all()
    
    if users:
        logger.info(f"Знайдено {len(users)} користувачів")
    else:
        logger.warning("Користувачів не знайдено")
    
    return users


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUserSchema, db: db_dependency, background_tasks: BackgroundTasks):
    logger.info(f"Реєстрація нового користувача: {user.email}")
    
    if db.query(Users).filter_by(email=user.email).first():
        logger.warning("Email вже зареєстрований")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already registered')
    
    token = str(uuid.uuid4())
    create_user = Users(
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        full_name=user.full_name,
        role=user.role,
        is_active=False,
        verification_token=token
    )
    
    db.add(create_user)
    db.commit()
    logger.info(f"Користувача {user.email} зареєстровано успішно")
    
    background_tasks.add_task(send_verification_email, user.email, token)
    return {"message": "User registered. Check your email for verification."}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    logger.info(f"Аутентифікація користувача: {form_data.username}")
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user or user.is_active is False:
        logger.warning("Не вдалося автентифікувати користувача")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    
    token = create_access_token(
        user.email,
        user.id,
        user.role,
        user.is_active,
        timedelta(minutes=20)
    )
    
    logger.info(f"Користувач {user.email} успішно отримав токен")
    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/verify/{token}")
async def verify_email(token: str, db: db_dependency):
    logger.info(f"Перевірка токена: {token}")
    
    user = db.query(Users).filter(Users.verification_token == token).first()
    if not user:
        logger.warning("Невірний або прострочений токен")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user.is_active = True
    user.verification_token = None
    db.commit()
    logger.info(f"Користувач {user.email} успішно верифікований")
    
    return {"message": "Email successfully verified"}
