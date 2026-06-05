from sqlalchemy.orm import Session
from models.antropometri_model import Antropometri
from schemas.antropometri_schema import AntropometriCreate


def get_antropometri(db: Session, antropometri_id: int):
    return db.query(Antropometri).filter(Antropometri.id == antropometri_id).first()


def get_antropometri_by_balita(db: Session, balita_id: int):
    return (
        db.query(Antropometri)
        .filter(Antropometri.balita_id == balita_id)
        .order_by(Antropometri.tanggal_timbang.desc())
        .all()
    )


def create_antropometri(db: Session, antropometri: AntropometriCreate, z_score: float, status_gizi: str):
    db_antropometri = Antropometri(
        balita_id=antropometri.balita_id,
        tanggal_timbang=antropometri.tanggal_timbang,
        berat_badan=antropometri.berat_badan,
        tinggi_badan=antropometri.tinggi_badan,
        lila=antropometri.lila,
        lingkar_kepala=antropometri.lingkar_kepala,
        status_imunisasi=antropometri.status_imunisasi,
        asi_eksklusif=antropometri.asi_eksklusif,
        z_score=z_score,
        status_gizi=status_gizi
    )
    db.add(db_antropometri)
    db.commit()
    db.refresh(db_antropometri)
    return db_antropometri


def delete_antropometri(db: Session, antropometri_id: int):
    db_antropometri = get_antropometri(db, antropometri_id)
    if db_antropometri:
        db.delete(db_antropometri)
        db.commit()
    return db_antropometri
