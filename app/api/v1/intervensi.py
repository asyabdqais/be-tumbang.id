from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.crud import crud_intervensi
from app.schemas.intervensi import IntervensiResponse, IntervensiUpdate
from app.models.user import User, Role

router = APIRouter()

allow_validate_intervensi = RoleChecker([Role.DOKTER, Role.ADMIN])

@router.get("/unapproved", response_model=list[IntervensiResponse], dependencies=[Depends(allow_validate_intervensi)])
def get_unapproved_intervensi(db: Session = Depends(get_db)):
    """Mendapatkan semua intervensi yang belum divalidasi Dokter"""
    return crud_intervensi.get_unapproved_intervensi(db)

@router.get("/rujukan-rsud", response_model=list[IntervensiResponse], dependencies=[Depends(allow_validate_intervensi)])
def get_rujukan_rsud(db: Session = Depends(get_db)):
    """Mendapatkan semua kasus yang ditandai untuk dirujuk ke RSUD"""
    return crud_intervensi.get_rujukan_rsud(db)

@router.put("/{intervensi_id}", response_model=IntervensiResponse, dependencies=[Depends(allow_validate_intervensi)])
def validate_intervensi(
    intervensi_id: int,
    intervensi_update: IntervensiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dokter melakukan validasi terhadap rekomendasi AI:
    - Menyetujui (is_approved=True)
    - Merevisi rekomendasi AI
    - Menandai untuk Rujuk RSUD (is_rujukan_rsud=True)
    """
    db_intervensi = crud_intervensi.update_intervensi(
        db=db,
        intervensi_id=intervensi_id,
        dokter_id=current_user.id,
        rekomendasi_ai=intervensi_update.rekomendasi_ai,
        is_approved=intervensi_update.is_approved,
        is_rujukan_rsud=intervensi_update.is_rujukan_rsud
    )
    if not db_intervensi:
        raise HTTPException(status_code=404, detail="Intervensi tidak ditemukan")
    return db_intervensi

@router.get("/{intervensi_id}", response_model=IntervensiResponse)
def read_intervensi(
    intervensi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Melihat detail intervensi — Orang Tua hanya bisa melihat jika sudah diapprove Dokter"""
    db_intervensi = crud_intervensi.get_intervensi(db, intervensi_id)
    if not db_intervensi:
        raise HTTPException(status_code=404, detail="Intervensi tidak ditemukan")

    # Orang Tua hanya bisa lihat intervensi yang sudah divalidasi Dokter
    if current_user.role == Role.ORANG_TUA and not db_intervensi.is_approved:
        raise HTTPException(
            status_code=403,
            detail="Intervensi ini belum divalidasi Dokter. Harap tunggu."
        )

    return db_intervensi
