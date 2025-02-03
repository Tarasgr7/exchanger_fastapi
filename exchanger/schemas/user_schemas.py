from pydantic import BaseModel

class CreateUserSchema(BaseModel):
  email: str
  full_name: str
  password: str
  role: str
