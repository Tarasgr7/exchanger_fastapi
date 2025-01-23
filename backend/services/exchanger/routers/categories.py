from fastapi import APIRouter,HTTPException,status, Depends, Path
from ..models.category_model import Category
from ..schemas.category_schemas import CreateCategory
from ..services.auth_service import get_current_user
from ..dependencies import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter(
  prefix="/categories",
  tags=["categories"]
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

@router.get('/',status_code=status.HTTP_200_OK)
async def read_categories(db: db_dependency):
  return db.query(Category).all()

@router.post("/new",status_code=status.HTTP_201_CREATED)
async def create_category(category: CreateCategory, db:db_dependency, user:user_dependency):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  if db.query(Category).filter(Category.name==category.name).first():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
  new_category = Category(name=category.name, user_id=user.get('id'))
  db.add(new_category)
  db.commit()

@router.put("/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_category(user: user_dependency, db: db_dependency,category:CreateCategory, category_id: int=Path(gt=0)):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  exists_category = db.query(Category).filter(Category.id==category_id, Category.user_id==user.get('id')).first()
  if not exists_category:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
  exists_category.name = category.name
  db.commit()

@router.delete("/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(user: user_dependency, db: db_dependency,category_id: int=Path(gt=0)):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  category = db.query(Category).filter(Category.id==category_id, Category.user_id==user.get('id')).first()
  if not category:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
  db.delete(category)
  db.commit()

