from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_roles
from repositories import intervensi_repository
from schemas.intervensi_schema import IntervensiResponse, IntervensiUpdate
from models.user_model import User, Role

router = APIRouter()


@router.get("/unapproved", response_model=list[IntervensiResponse], dependencies=[Depends(require_roles(Role.DOKTER, Role.ADMIN))])
def get_unapproved_intervensi(db: Session = Depends(get_db)):
    """Mendapatkan semua intervensi yang belum divalidasi Dokter."""
    return intervensi_repository.get_unapproved_intervensi(db)


@router.get("/rujukan-rsud", response_model=list[IntervensiResponse], dependencies=[Depends(require_roles(Role.DOKTER, Role.ADMIN))])
def get_rujukan_rsud(db: Session = Depends(get_db)):
    """Mendapatkan semua kasus yang ditandai untuk dirujuk ke RSUD."""
    return intervensi_repository.get_rujukan_rsud(db)


@router.put("/{intervensi_id}", response_model=IntervensiResponse, dependencies=[Depends(require_roles(Role.DOKTER, Role.ADMIN))])
def validate_intervensi(
    intervensi_id: int,
    intervensi_update: IntervensiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dokter melakukan validasi terhadap rekomendasi:
    - Menyetujui (is_approved=True)
    - Merevisi rekomendasi
    - Menandai untuk Rujuk RSUD (is_rujukan_rsud=True)
    """
    db_intervensi = intervensi_repository.update_intervensi(
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


@router.get("/balita/{balita_id}", response_model=IntervensiResponse)
def get_intervensi_by_balita(
    balita_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan intervensi (rekomendasi AI) terakhir yang sudah disetujui dokter untuk seorang balita."""
    db_intervensi = intervensi_repository.get_latest_intervensi_by_balita(db, balita_id)
    if not db_intervensi:
        raise HTTPException(status_code=404, detail="Belum ada rekomendasi yang disetujui untuk balita ini.")
    return db_intervensi

@router.get("/{intervensi_id}", response_model=IntervensiResponse)
def read_intervensi(
    intervensi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Melihat detail intervensi — Orang Tua hanya bisa melihat jika sudah diapprove Dokter."""
    db_intervensi = intervensi_repository.get_intervensi(db, intervensi_id)
    if not db_intervensi:
        raise HTTPException(status_code=404, detail="Intervensi tidak ditemukan")

    if current_user.role == Role.ORANG_TUA and not db_intervensi.is_approved:
        raise HTTPException(
            status_code=403,
            detail="Intervensi ini belum divalidasi Dokter. Harap tunggu."
        )
    return db_intervensi


@router.post("/{intervensi_id}/regenerate", response_model=IntervensiResponse,
             dependencies=[Depends(require_roles(Role.DOKTER, Role.ADMIN))])
async def regenerate_intervensi_ai(
    intervensi_id: int,
    db: Session = Depends(get_db),
):
    """
    Dokter meminta regenerasi rekomendasi AI untuk intervensi tertentu.
    Memanggil ulang Gemini API dengan data balita & antropometri yang sama.
    """
    from services.gemini_service import generate_intervensi_resep
    from repositories import balita_repository
    from datetime import date as dt_date

    db_intervensi = intervensi_repository.get_intervensi(db, intervensi_id)
    if not db_intervensi:
        raise HTTPException(status_code=404, detail="Intervensi tidak ditemukan")

    antropometri = db_intervensi.antropometri
    if not antropometri:
        raise HTTPException(status_code=404, detail="Data antropometri tidak ditemukan")

    balita = antropometri.balita
    if not balita:
        raise HTTPException(status_code=404, detail="Data balita tidak ditemukan")

    umur_hari = (dt_date.today() - balita.tanggal_lahir).days
    umur_bulan = umur_hari // 30

    rekomendasi_baru = await generate_intervensi_resep(
        nama_balita=balita.nama,
        status_gizi=antropometri.status_gizi,
        berat_badan=antropometri.berat_badan,
        tinggi_badan=antropometri.tinggi_badan,
        umur_bulan=umur_bulan,
        jenis_kelamin=balita.jenis_kelamin.value,
        kondisi_geografis=balita.kondisi_geografis or "Daratan/Umum",
        lila=antropometri.lila,
        lingkar_kepala=antropometri.lingkar_kepala,
        status_imunisasi=antropometri.status_imunisasi,
        asi_eksklusif=antropometri.asi_eksklusif,
    )

    # Update the intervensi record with the new AI recommendation
    db_intervensi.rekomendasi_ai = rekomendasi_baru
    db.commit()
    db.refresh(db_intervensi)

    return db_intervensi
