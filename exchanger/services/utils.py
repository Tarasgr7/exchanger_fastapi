
from ..dependencies import SessionLocal
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..services.auth_service import get_current_user

def get_db():
  db= SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session,Depends(get_db)]


user_dependency=Annotated[dict,Depends(get_current_user)]



bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')