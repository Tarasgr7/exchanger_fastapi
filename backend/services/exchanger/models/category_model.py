from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import datetime


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    user_id=Column(Integer, ForeignKey("users.id"))
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)
