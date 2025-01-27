from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import datetime


class Expense(Base):
  __tablename__ = 'expenses'
  id=Column(Integer, primary_key=True, index=True)
  user_id=Column(Integer, ForeignKey("users.id"))
  category_id=Column(Integer, ForeignKey("categories.id"),nullable=False)
  amount=Column(Integer, nullable=False)
  description=Column(String,nullable=False)
  created_at=Column(Date, default=datetime.now)
  updated_at=Column(Date, default=datetime.now,onupdate=datetime.now)