from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from dependencies import get_db, require_roles
from models.user_model import Role
from models.balita_model import Balita
from models.antropometri_model import Antropometri

router = APIRouter()


@router.get("/ringkasan", dependencies=[Depends(require_roles(Role.ADMIN, Role.DOKTER, Role.KADER))])
def get_ringkasan_laporan(
    db: Session = Depends(get_db),
    bulan: Optional[int] = Query(None, description="Filter bulan (1-12)"),
    tahun: Optional[int] = Query(None, description="Filter tahun, contoh: 2025"),
):
    """
    Laporan ringkasan agregat stunting untuk Admin Puskesmas & Dokter.
    Menampilkan jumlah kasus per status gizi, bisa difilter per bulan/tahun.
    """
    query = db.query(
        Antropometri.status_gizi,
        func.count(Antropometri.id).label("jumlah")
    )

    if bulan and tahun:
        query = query.filter(
            func.extract('month', Antropometri.tanggal_timbang) == bulan,
            func.extract('year', Antropometri.tanggal_timbang) == tahun,
        )
    elif tahun:
        query = query.filter(func.extract('year', Antropometri.tanggal_timbang) == tahun)

    hasil = query.group_by(Antropometri.status_gizi).all()

    total            = sum(row.jumlah for row in hasil)
    kasus_stunting   = next((row.jumlah for row in hasil if row.status_gizi in ["Stunting", "Gizi Buruk"]), 0)
    persentase_stunting = round((kasus_stunting / total * 100), 2) if total > 0 else 0.0

    return {
        "filter": {"bulan": bulan, "tahun": tahun},
        "total_pemeriksaan": total,
        "total_kasus_bermasalah": kasus_stunting,
        "persentase_stunting": persentase_stunting,
        "rincian_per_status_gizi": [
            {"status_gizi": row.status_gizi, "jumlah": row.jumlah}
            for row in hasil
        ]
    }


@router.get("/per-wilayah", dependencies=[Depends(require_roles(Role.ADMIN, Role.DOKTER, Role.KADER))])
def get_laporan_per_wilayah(
    db: Session = Depends(get_db),
    tahun: Optional[int] = Query(None, description="Filter tahun"),
):
    """Laporan sebaran stunting per RW/Desa untuk pemetaan wilayah prioritas."""
    query = db.query(
        Balita.rw_desa,
        Antropometri.status_gizi,
        func.count(Antropometri.id).label("jumlah")
    ).join(Antropometri, Antropometri.balita_id == Balita.id)

    if tahun:
        query = query.filter(func.extract('year', Antropometri.tanggal_timbang) == tahun)

    hasil = query.group_by(Balita.rw_desa, Antropometri.status_gizi).all()

    wilayah_map = {}
    for row in hasil:
        rw = row.rw_desa or "Tidak Diketahui"
        if rw not in wilayah_map:
            wilayah_map[rw] = {"rw_desa": rw, "total": 0, "stunting": 0, "detail": []}
        wilayah_map[rw]["total"] += row.jumlah
        if row.status_gizi in ["Stunting", "Gizi Buruk"]:
            wilayah_map[rw]["stunting"] += row.jumlah
        wilayah_map[rw]["detail"].append({"status_gizi": row.status_gizi, "jumlah": row.jumlah})

    for rw_data in wilayah_map.values():
        total = rw_data["total"]
        rw_data["persentase_stunting"] = round((rw_data["stunting"] / total * 100), 2) if total > 0 else 0.0

    return {"filter": {"tahun": tahun}, "data": list(wilayah_map.values())}


@router.get("/balita-berisiko", dependencies=[Depends(require_roles(Role.ADMIN, Role.DOKTER, Role.KADER))])
def get_balita_berisiko(
    db: Session = Depends(get_db),
    bulan: Optional[int] = Query(None),
    tahun: Optional[int] = Query(None),
):
    """Daftar lengkap balita dengan status gizi buruk/stunting (untuk tindak lanjut)."""
    STATUS_BERISIKO = ["Stunting", "Gizi Buruk", "Kurang", "Wasting"]

    query = db.query(
        Balita.id,
        Balita.nik,
        Balita.nama,
        Balita.rw_desa,
        Balita.kondisi_geografis,
        Antropometri.tanggal_timbang,
        Antropometri.berat_badan,
        Antropometri.tinggi_badan,
        Antropometri.z_score,
        Antropometri.status_gizi,
    ).join(Antropometri, Antropometri.balita_id == Balita.id).filter(
        Antropometri.status_gizi.in_(STATUS_BERISIKO)
    )

    if bulan and tahun:
        query = query.filter(
            func.extract('month', Antropometri.tanggal_timbang) == bulan,
            func.extract('year', Antropometri.tanggal_timbang) == tahun,
        )
    elif tahun:
        query = query.filter(func.extract('year', Antropometri.tanggal_timbang) == tahun)

    hasil = query.order_by(Antropometri.z_score.asc()).all()

    return {
        "filter": {"bulan": bulan, "tahun": tahun},
        "total": len(hasil),
        "data": [
            {
                "balita_id":          row.id,
                "nik":                row.nik,
                "nama":               row.nama,
                "rw_desa":            row.rw_desa,
                "kondisi_geografis":  row.kondisi_geografis,
                "tanggal_timbang":    row.tanggal_timbang.isoformat(),
                "berat_badan":        row.berat_badan,
                "tinggi_badan":       row.tinggi_badan,
                "z_score":            row.z_score,
                "status_gizi":        row.status_gizi,
            }
            for row in hasil
        ]
    }
