from sqlalchemy.orm import Session
from app.models.intervensi import Intervensi
from app.schemas.intervensi import IntervensiCreate

def get_intervensi(db: Session, intervensi_id: int):
    return db.query(Intervensi).filter(Intervensi.id == intervensi_id).first()

def get_intervensi_by_antropometri(db: Session, antropometri_id: int):
    return db.query(Intervensi).filter(Intervensi.antropometri_id == antropometri_id).first()

def create_intervensi(db: Session, intervensi: IntervensiCreate):
    db_intervensi = Intervensi(
        antropometri_id=intervensi.antropometri_id,
        rekomendasi_ai=intervensi.rekomendasi_ai
    )
    db.add(db_intervensi)
    db.commit()
    db.refresh(db_intervensi)
    return db_intervensi

def update_intervensi(
    db: Session,
    intervensi_id: int,
    dokter_id: int,
    rekomendasi_ai: str = None,
    is_approved: bool = None,
    is_rujukan_rsud: bool = None
):
    db_intervensi = get_intervensi(db, intervensi_id)
    if db_intervensi:
        db_intervensi.dokter_id = dokter_id
        if rekomendasi_ai is not None:
            db_intervensi.rekomendasi_ai = rekomendasi_ai
        if is_approved is not None:
            db_intervensi.is_approved = is_approved
        if is_rujukan_rsud is not None:
            db_intervensi.is_rujukan_rsud = is_rujukan_rsud
        db.commit()
        db.refresh(db_intervensi)
    return db_intervensi

def get_unapproved_intervensi(db: Session):
    return db.query(Intervensi).filter(Intervensi.is_approved == False).all()

def get_rujukan_rsud(db: Session):
    """Mengambil semua intervensi yang ditandai untuk dirujuk ke RSUD"""
    return db.query(Intervensi).filter(Intervensi.is_rujukan_rsud == True).all()
