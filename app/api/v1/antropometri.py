from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.crud import crud_antropometri, crud_balita, crud_intervensi
from app.schemas.antropometri import AntropometriCreate, AntropometriResponse
from app.schemas.intervensi import IntervensiCreate
from app.models.user import User, Role
from app.services.zscore_service import calculate_zscore
from app.services.gemini_service import generate_intervensi_resep
from datetime import date
import asyncio

router = APIRouter()

allow_input_timbangan = RoleChecker([Role.KADER, Role.ADMIN])
allow_read_riwayat = RoleChecker([Role.KADER, Role.ADMIN, Role.DOKTER, Role.ORANG_TUA])


async def process_intervensi_background(
    db: Session,
    antropometri_id: int,
    # Data balita yang di-pass dari endpoint
    balita_nama: str,
    status_gizi: str,
    bb: float,
    tb: float,
    umur_bulan: int,
    jenis_kelamin: str,
    kondisi_geografis: str,
    # Data skrining tambahan
    lila: float,
    lingkar_kepala: float,
    status_imunisasi: str,
    asi_eksklusif: bool,
):
    """Background task: memanggil Gemini AI dan menyimpan hasilnya ke DB"""
    rekomendasi = await generate_intervensi_resep(
        nama_balita=balita_nama,
        status_gizi=status_gizi,
        berat_badan=bb,
        tinggi_badan=tb,
        umur_bulan=umur_bulan,
        jenis_kelamin=jenis_kelamin,
        kondisi_geografis=kondisi_geografis,
        lila=lila,
        lingkar_kepala=lingkar_kepala,
        status_imunisasi=status_imunisasi,
        asi_eksklusif=asi_eksklusif,
    )
    intervensi_data = IntervensiCreate(
        antropometri_id=antropometri_id,
        rekomendasi_ai=rekomendasi
    )
    crud_intervensi.create_intervensi(db, intervensi_data)


@router.post("/", response_model=AntropometriResponse, dependencies=[Depends(allow_input_timbangan)])
def create_antropometri(
    antropometri: AntropometriCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Kader menginput data timbangan bulanan.
    Sistem otomatis menghitung Z-Score dan memicu AI jika status gizi bermasalah.
    """
    balita = crud_balita.get_balita(db, antropometri.balita_id)
    if not balita:
        raise HTTPException(status_code=404, detail="Data balita tidak ditemukan")

    # Hitung usia dalam bulan
    umur_hari = (date.today() - balita.tanggal_lahir).days
    umur_bulan = umur_hari // 30

    # Hitung Z-Score dan Status Gizi (standar WHO/Kemenkes)
    z_score, status_gizi = calculate_zscore(
        berat_badan=antropometri.berat_badan,
        tinggi_badan=antropometri.tinggi_badan,
        umur_bulan=umur_bulan,
        jenis_kelamin=balita.jenis_kelamin.value
    )

    # Simpan data timbangan ke database
    db_antropometri = crud_antropometri.create_antropometri(
        db=db,
        antropometri=antropometri,
        z_score=z_score,
        status_gizi=status_gizi
    )

    # Trigger AI Gemini di background jika status gizi bermasalah
    STATUS_GIZI_BUTUH_INTERVENSI = ["Kurang", "Gizi Buruk", "Stunting", "Wasting"]
    if status_gizi in STATUS_GIZI_BUTUH_INTERVENSI:
        background_tasks.add_task(
            process_intervensi_background,
            db=db,
            antropometri_id=db_antropometri.id,
            balita_nama=balita.nama,
            status_gizi=status_gizi,
            bb=antropometri.berat_badan,
            tb=antropometri.tinggi_badan,
            umur_bulan=umur_bulan,
            jenis_kelamin=balita.jenis_kelamin.value,
            kondisi_geografis=balita.kondisi_geografis or "Daratan/Umum",
            lila=antropometri.lila,
            lingkar_kepala=antropometri.lingkar_kepala,
            status_imunisasi=antropometri.status_imunisasi,
            asi_eksklusif=antropometri.asi_eksklusif,
        )

    return db_antropometri


@router.get("/balita/{balita_id}", response_model=list[AntropometriResponse])
def get_riwayat_timbangan(
    balita_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Melihat riwayat timbangan bulanan seorang balita"""
    balita = crud_balita.get_balita(db, balita_id)
    if not balita:
        raise HTTPException(status_code=404, detail="Data balita tidak ditemukan")

    # Orang Tua hanya boleh lihat data anaknya sendiri
    if current_user.role == Role.ORANG_TUA and balita.orang_tua_id != current_user.id:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke data balita ini")

    return crud_antropometri.get_antropometri_by_balita(db, balita_id)


@router.delete("/{antropometri_id}", response_model=AntropometriResponse, dependencies=[Depends(allow_input_timbangan)])
def delete_antropometri(antropometri_id: int, db: Session = Depends(get_db)):
    """Kader/Admin menghapus data timbangan yang salah input"""
    db_antropometri = crud_antropometri.delete_antropometri(db, antropometri_id)
    if not db_antropometri:
        raise HTTPException(status_code=404, detail="Data timbangan tidak ditemukan")
    return db_antropometri
