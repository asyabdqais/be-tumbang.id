from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from database import Base
import enum


class Role(str, enum.Enum):
    KADER     = "Kader"
    DOKTER    = "Dokter"
    ORANG_TUA = "Orang Tua"
    ADMIN     = "Admin"


class User(Base):
    __tablename__ = "users"

    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String(100), unique=True, index=True)
    password  = Column(String(100))
    role      = Column(SQLEnum(Role), default=Role.KADER)
    is_active = Column(Boolean, default=True)

