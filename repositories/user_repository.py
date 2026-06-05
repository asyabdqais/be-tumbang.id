from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.user_model import User, Role
from schemas.user_schema import UserCreate
from dependencies import hash_password


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(func.lower(User.username) == username.lower()).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate):
    hashed_pw = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        password=hashed_pw,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users_by_role(db: Session, role: Optional[Role] = None):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.all()
