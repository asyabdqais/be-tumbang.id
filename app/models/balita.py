from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class JenisKelamin(str, enum.Enum):
    L = "Laki-laki"
    P = "Perempuan"

class Balita(Base):
    __tablename__ = "balita"

    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String(16), unique=True, index=True)
    nama = Column(String(100), index=True)
    tanggal_lahir = Column(Date)
    jenis_kelamin = Column(SQLEnum(JenisKelamin))
    
    rw_desa = Column(String(200), default="-")
    kondisi_geografis = Column(String(100), default="Daratan/Umum")
    
    # Orang tua reference
    orang_tua_id = Column(Integer, ForeignKey("users.id"))
    
    # Soft delete
    is_deleted = Column(Integer, default=0)

    orang_tua = relationship("User", backref="balitas")
    antropometris = relationship("Antropometri", back_populates="balita")
