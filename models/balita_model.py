from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class JenisKelamin(str, enum.Enum):
    L = "Laki-laki"
    P = "Perempuan"


class Balita(Base):
    __tablename__ = "balita"

    id              = Column(Integer, primary_key=True, index=True)
    nik             = Column(String(16), unique=True, index=True)
    nama            = Column(String(100), index=True)
    tanggal_lahir   = Column(Date)
    jenis_kelamin   = Column(SQLEnum(JenisKelamin))

    rw_desa          = Column(String(200), default="-")
    kondisi_geografis = Column(String(100), default="Daratan/Umum")

    # Referensi orang tua
    orang_tua_id = Column(Integer, ForeignKey("users.id"))

    # Soft delete
    is_deleted = Column(Integer, default=0)

    orang_tua   = relationship("User", backref="balitas")
    antropometris = relationship("Antropometri", back_populates="balita")

    @property
    def status_gizi_terbaru(self) -> str:
        if not self.antropometris:
            return "Normal"
        # Ambil antropometri dengan tanggal timbang terbaru, jika sama gunakan ID terbesar
        sorted_antro = sorted(self.antropometris, key=lambda x: (x.tanggal_timbang, x.id), reverse=True)
        return sorted_antro[0].status_gizi
