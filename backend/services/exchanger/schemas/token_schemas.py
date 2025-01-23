from fastapi.security.oauth2 import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
  access_token: str
  token_type: str

