from pydantic import BaseModel
from typing import Optional
from app.schemas.user import User

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None

class TokenPayload(BaseModel):
    sub: str = None
