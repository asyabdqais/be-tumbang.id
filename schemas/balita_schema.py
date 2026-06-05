from pydantic import BaseModel, Field
from datetime import date
from models.balita_model import JenisKelamin
from typing import Optional


class BalitaBase(BaseModel):
    nik:              str = Field(min_length=16, max_length=16)
    nama:             str
    tanggal_lahir:    date
    jenis_kelamin:    JenisKelamin
    orang_tua_id:     int
    rw_desa:          Optional[str] = "-"
    kondisi_geografis: Optional[str] = "Daratan/Umum"


class BalitaCreate(BalitaBase):
    pass


class BalitaResponse(BalitaBase):
    id:         int
    is_deleted: int
    status_gizi_terbaru: Optional[str] = "Normal"

    model_config = {"from_attributes": True}
