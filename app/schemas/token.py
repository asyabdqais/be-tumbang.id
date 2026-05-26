from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    token_type: Optional[str] = None  # "access" atau "refresh"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
