from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date,Enum
from datetime import datetime

class Users(Base):
  __tablename__ = 'users'
  id=Column(Integer, primary_key=True,index=True)
  email=Column(String, unique=True,nullable=False)
  hashed_password=Column(String,nullable=False)
  full_name=Column(String,nullable=False)
  role = Column(String, nullable=False)
  created_at=Column(Date, default=datetime.now)
  updated_at=Column(Date, default=datetime.now,onupdate=datetime.now)
