import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from fastapi import Depends
from typing import Annotated
from dotenv import load_dotenv



load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOPIC_NOTIFACATION = os.getenv("TOPIC_NOTIFACATION")

SQLALCHEMY_DATABASE_URL = 'sqlite:///exchanger.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

