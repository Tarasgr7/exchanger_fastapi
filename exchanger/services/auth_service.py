import random
import string
import os
import smtplib
from datetime import datetime,timedelta
from typing import Annotated


from ..models.users_model import Users

from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import jwt,JWTError
from dotenv import load_dotenv

from email.message import EmailMessage
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

load_dotenv()

email_templates_env = Environment(loader=FileSystemLoader("exchanger/templates"))


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")




def encode_password(password: str) -> str:
    return bcrypt_context.hash(password)


def generate_password() -> str:
    length = 12

    uppercase = random.choice(string.ascii_uppercase)  
    lowercase = random.choice(string.ascii_lowercase)  
    digit = random.choice(string.digits)  

    other_characters = string.ascii_letters + string.digits
    remaining = ''.join(random.choices(other_characters, k=length - 3))

    password = list(uppercase + lowercase + digit + remaining)

    random.shuffle(password)

    return ''.join(password)

# Приклад використання




def authenticate_user(email:str,password:str,db):
   user=db.query(Users).filter(Users.email==email).first()
   if not user or not bcrypt_context.verify(password, user.hashed_password):
     return False
   return user

def create_access_token(email: str, id: str,role:str,is_active:bool, expires_delta: timedelta):
   encode={
      'sub': email,
      'id': id,
      'role':role,
      'status':is_active
      }
   expires=datetime.utcnow() + expires_delta
   encode.update({'exp':expires})
   return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
   try:
      payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
      email=payload.get('sub')
      id=payload.get('id')
      role=payload.get('role')
      is_active=payload.get('status')
      if email is None or id is None or is_active is False:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
      return{'email':email, 'id':id,'user_role':role}
   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Token expired')



def send_verification_email(email: str, token: str):
   template = email_templates_env.get_template("email_verify.html")
   verification_link = f"http://0.0.0.0:8000/auth/verify/{token}"
   html_content = template.render(verification_link=verification_link)
   msg = EmailMessage()
   msg['Subject'] = "Email Verify"
   msg['From'] = EMAIL_ADDRESS
   msg['To'] = email
   msg.set_content("This email requires an HTML-compatible email client.") 
   msg.add_alternative(html_content, subtype="html")


   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
      smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
      smtp.send_message(msg)




