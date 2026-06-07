from pydantic import BaseModel
from typing import Optional
from models.user_model import Role


class UserAuth(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[Role] = Role.KADER


class UserResponse(BaseModel):
    id:        int
    username:  str
    role:      Role
    is_active: bool = True

    model_config = {"from_attributes": True}

