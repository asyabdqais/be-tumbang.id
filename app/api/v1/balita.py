from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.crud import crud_balita
from app.schemas.balita import BalitaCreate, BalitaResponse
from app.models.user import User, Role

router = APIRouter()

allow_create_balita = RoleChecker([Role.KADER, Role.DOKTER, Role.ADMIN])
allow_delete_balita = RoleChecker([Role.DOKTER, Role.ADMIN])

@router.post("/", response_model=BalitaResponse, dependencies=[Depends(allow_create_balita)])
def create_balita(balita: BalitaCreate, db: Session = Depends(get_db)):
    return crud_balita.create_balita(db=db, balita=balita)

@router.get("/", response_model=list[BalitaResponse])
def read_balitas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == Role.ORANG_TUA:
        return crud_balita.get_balitas_by_orang_tua(db, current_user.id)
    return crud_balita.get_all_balita(db)

@router.get("/{balita_id}", response_model=BalitaResponse)
def read_balita(balita_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_balita = crud_balita.get_balita(db, balita_id=balita_id)
    if db_balita is None:
        raise HTTPException(status_code=404, detail="Balita not found")
    if current_user.role == Role.ORANG_TUA and db_balita.orang_tua_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")
    return db_balita

@router.delete("/{balita_id}", response_model=BalitaResponse, dependencies=[Depends(allow_delete_balita)])
def soft_delete_balita(balita_id: int, db: Session = Depends(get_db)):
    db_balita = crud_balita.soft_delete_balita(db, balita_id=balita_id)
    if db_balita is None:
        raise HTTPException(status_code=404, detail="Balita not found")
    return db_balita
