from sqlalchemy.orm import Session
from models.balita_model import Balita
from schemas.balita_schema import BalitaCreate


def get_balita(db: Session, balita_id: int):
    return db.query(Balita).filter(Balita.id == balita_id, Balita.is_deleted == 0).first()


def get_balitas_by_orang_tua(db: Session, orang_tua_id: int):
    return db.query(Balita).filter(Balita.orang_tua_id == orang_tua_id, Balita.is_deleted == 0).all()


def get_all_balita(db: Session):
    return db.query(Balita).filter(Balita.is_deleted == 0).all()


from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from models.user_model import User, Role

def create_balita(db: Session, balita: BalitaCreate):
    # Validate orang_tua_id
    parent = db.query(User).filter(User.id == balita.orang_tua_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="orang_tua_id tidak valid atau tidak ditemukan.")
    if parent.role != Role.ORANG_TUA:
        raise HTTPException(status_code=400, detail="User dengan orang_tua_id tersebut bukan merupakan Orang Tua.")

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
    try:
        db.commit()
        db.refresh(db_balita)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "nik" in error_msg.lower() or "unique" in error_msg.lower():
            raise HTTPException(status_code=400, detail="NIK sudah terdaftar.")
        raise HTTPException(status_code=400, detail="Terjadi kesalahan validasi data pada database.")
    
    return db_balita


def soft_delete_balita(db: Session, balita_id: int):
    db_balita = get_balita(db, balita_id)
    if db_balita:
        db_balita.is_deleted = 1
        db.commit()
    return db_balita
