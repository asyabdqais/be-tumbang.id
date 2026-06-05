from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_roles
from repositories import balita_repository
from schemas.balita_schema import BalitaCreate, BalitaResponse
from models.user_model import User, Role

router = APIRouter()


@router.post("/", response_model=BalitaResponse, dependencies=[Depends(require_roles(Role.KADER, Role.DOKTER, Role.ADMIN))])
def create_balita(balita: BalitaCreate, db: Session = Depends(get_db)):
    return balita_repository.create_balita(db=db, balita=balita)


@router.get("/", response_model=list[BalitaResponse])
def read_balitas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == Role.ORANG_TUA:
        return balita_repository.get_balitas_by_orang_tua(db, current_user.id)
    return balita_repository.get_all_balita(db)


@router.get("/{balita_id}", response_model=BalitaResponse)
def read_balita(balita_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_balita = balita_repository.get_balita(db, balita_id=balita_id)
    if db_balita is None:
        raise HTTPException(status_code=404, detail="Balita tidak ditemukan")
    if current_user.role == Role.ORANG_TUA and db_balita.orang_tua_id != current_user.id:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke data ini")
    return db_balita


@router.delete("/{balita_id}", response_model=BalitaResponse, dependencies=[Depends(require_roles(Role.DOKTER, Role.ADMIN))])
def soft_delete_balita(balita_id: int, db: Session = Depends(get_db)):
    db_balita = balita_repository.soft_delete_balita(db, balita_id=balita_id)
    if db_balita is None:
        raise HTTPException(status_code=404, detail="Balita tidak ditemukan")
    return db_balita
