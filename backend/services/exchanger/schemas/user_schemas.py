from pydantic import BaseModel

class CreateUserSchema(BaseModel):
  email: str
  hashed_password: str
  full_name: str
  role: str
