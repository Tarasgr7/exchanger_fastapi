from pydantic import BaseModel

class ExpenseCreatedModel(BaseModel):
  category_id : int
  amount : int
  description : str
