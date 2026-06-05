from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Intervensi(Base):
    __tablename__ = "intervensi_ai"

    id              = Column(Integer, primary_key=True, index=True)
    antropometri_id = Column(Integer, ForeignKey("antropometri.id"))

    rekomendasi_ai  = Column(Text)
    is_approved     = Column(Boolean, default=False)
    is_rujukan_rsud = Column(Boolean, default=False)

    # Dokter yang memvalidasi
    dokter_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    antropometri = relationship("Antropometri", back_populates="intervensi")
    dokter       = relationship("User", backref="intervensis")
