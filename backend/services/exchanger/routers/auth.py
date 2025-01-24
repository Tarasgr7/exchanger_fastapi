import os
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter,Depends,status,BackgroundTasks
from fastapi.security import OAuth2PasswordBearer

from ..models.users_model import Users
from ..schemas.user_schemas import CreateUserSchema
from ..schemas.token_schemas import Token
from ..dependencies import SessionLocal
from ..services.auth_service import *

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import jwt,JWTError
import uuid

load_dotenv()

router=APIRouter(
   prefix='/auth',
   tags=['auth'],
   )



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
# oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

def get_db():
  db= SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session,Depends(get_db)]

@router.get('/users', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
  return db.query(Users).all()


@router.post("/register",status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUserSchema, db:db_dependency,background_tasks: BackgroundTasks):
  if db.query(Users).filter_by(email=user.email).first():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
  token = str(uuid.uuid4())
  create_user=Users(
    email=user.email,
    hashed_password=encode_password(user.hashed_password),
    full_name=user.full_name,
    role=user.role,
    is_active=False,
    verification_token=token
    )
  db.add(create_user)
  db.commit()
  background_tasks.add_task(send_verification_email, user.email, token)
  return {"message": "User registered. Check your email for verification."}



@router.get('/users', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
  return db.query(Users).all()

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db: db_dependency):
   user=authenticate_user(form_data.username,form_data.password,db)
   if not user or user.is_active == False:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
   token=create_access_token(user.email,user.id,user.role,user.is_active,timedelta(minutes=20))
   return {'access_token':token,'token_type':'bearer'}


@router.get("/verify/{token}")
async def verify_email(token: str, db: db_dependency):
    user = db.query(Users).filter(Users.verification_token==token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.is_active = True
    user.verification_token = None
    db.commit()
    return {"message": "Email successfully verified"}
