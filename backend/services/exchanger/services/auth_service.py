import os
from datetime import datetime,timedelta
from typing import Annotated


from ..models.users_model import Users

from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import jwt,JWTError
from dotenv import load_dotenv

load_dotenv()

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def authenticate_user(email:str,password:str,db):
   user=db.query(Users).filter(Users.email==email).first()
   if not user or not bcrypt_context.verify(password, user.hashed_password):
     return False
   return user

def create_access_token(email: str, id: str,role:str, expires_delta: timedelta):
    encode={'sub': email,'id': id,'role':role}
    expires=datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
       payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
       email=payload.get('sub')
       id=payload.get('id')
       role=payload.get('role')
       if email is None or id is None:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
       return{'email':email, 'id':id,'user_role':role}
    except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Token expired')





