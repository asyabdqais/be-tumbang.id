from sqlalchemy.orm import Session
from app.models.balita import Balita
from app.schemas.balita import BalitaCreate

def get_balita(db: Session, balita_id: int):
    return db.query(Balita).filter(Balita.id == balita_id, Balita.is_deleted == 0).first()

def get_balitas_by_orang_tua(db: Session, orang_tua_id: int):
    return db.query(Balita).filter(Balita.orang_tua_id == orang_tua_id, Balita.is_deleted == 0).all()

def get_all_balita(db: Session):
    return db.query(Balita).filter(Balita.is_deleted == 0).all()

def create_balita(db: Session, balita: BalitaCreate):
    db_balita = Balita(
        nik=balita.nik,
        nama=balita.nama,
        tanggal_lahir=balita.tanggal_lahir,
        jenis_kelamin=balita.jenis_kelamin,
        orang_tua_id=balita.orang_tua_id,
        rw_desa=balita.rw_desa,
        kondisi_geografis=balita.kondisi_geografis
    )
    db.add(db_balita)
    db.commit()
    db.refresh(db_balita)
    return db_balita

def soft_delete_balita(db: Session, balita_id: int):
    db_balita = get_balita(db, balita_id)
    if db_balita:
        db_balita.is_deleted = 1
        db.commit()
    return db_balita
