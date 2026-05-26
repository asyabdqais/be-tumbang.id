from pydantic import BaseModel
from typing import Optional
from app.models.user import Role

class UserAuth(BaseModel):
    username: str
    password: str

class UserCreate(UserAuth):
    role: Optional[Role] = Role.KADER

class UserResponse(BaseModel):
    id: int
    username: str
    role: Role

    class Config:
        from_attributes = True