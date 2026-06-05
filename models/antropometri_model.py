from sqlalchemy import Column, Integer, Float, Date, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Antropometri(Base):
    __tablename__ = "antropometri"

    id        = Column(Integer, primary_key=True, index=True)
    balita_id = Column(Integer, ForeignKey("balita.id"))
    tanggal_timbang = Column(Date)

    # Data Timbangan Utama
    berat_badan  = Column(Float)   # kg
    tinggi_badan = Column(Float)   # cm

    # Data Skrining Tambahan
    lila             = Column(Float, nullable=True)         # Lingkar Lengan Atas (cm)
    lingkar_kepala   = Column(Float, nullable=True)         # Lingkar Kepala (cm)
    status_imunisasi = Column(String(50), nullable=True)    # Lengkap / Belum Lengkap / Sebagian
    asi_eksklusif    = Column(Boolean, nullable=True)

    # Calculated — otomatis dari Z-Score Service
    z_score     = Column(Float)
    status_gizi = Column(String(50))  # Normal, Kurang, Gizi Buruk, Stunting

    balita     = relationship("Balita", back_populates="antropometris")
    intervensi = relationship("Intervensi", back_populates="antropometri", uselist=False)
