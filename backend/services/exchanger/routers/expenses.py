from fastapi import APIRouter,Depends,HTTPException,Path,status
from sqlalchemy.orm import Session
from typing import Annotated
from ..models.expense_model import Expense
from ..schemas.expense_schemas import ExpenseCreatedModel
from ..dependencies import SessionLocal
from ..services.auth_service import get_current_user

router = APIRouter(
  prefix="/expenses",
  tags=["expenses"]
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
async def read_expenses(db: db_dependency, user: user_dependency):
  return db.query(Expense).filter(Expense.user_id==user.get('id')).all()

@router.post("/new",status_code=status.HTTP_201_CREATED)
async def create_expense(expense: ExpenseCreatedModel, db: db_dependency, user: user_dependency):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  
  new_expense = Expense(
    amount=expense.amount,
    description=expense.description,
    category_id=expense.category_id,
    user_id=user.get('id')
  )
  db.add(new_expense)
  db.commit()
  db.refresh(new_expense)
  return new_expense

@router.put("/{expense_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_expense(expense_id: int, expense: ExpenseCreatedModel, db: db_dependency, user: user_dependency):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  
  exists_expense = db.query(Expense).filter(Expense.id==expense_id, Expense.user_id==user.get('id')).first()
  if not exists_expense:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
  
  exists_expense.amount = expense.amount
  exists_expense.description = expense.description
  exists_expense.category_id = expense.category_id
  db.commit()

@router.delete("/{expense_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: int, db: db_dependency, user: user_dependency):
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  
  exists_expense = db.query(Expense).filter(Expense.id==expense_id, Expense.user_id==user.get('id')).first()
  if not exists_expense:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
  
  db.delete(exists_expense)
  db.commit()
