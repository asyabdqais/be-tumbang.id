from pydantic import BaseModel
from datetime import date
from typing import Optional
from schemas.balita_schema import BalitaResponse


class AntropometriBase(BaseModel):
    balita_id:       int
    tanggal_timbang: date
    berat_badan:     float
    tinggi_badan:    float
    # Data Skrining Tambahan (opsional)
    lila:             Optional[float] = None
    lingkar_kepala:   Optional[float] = None
    status_imunisasi: Optional[str]   = None   # Lengkap / Belum Lengkap / Sebagian
    asi_eksklusif:    Optional[bool]  = None


class AntropometriCreate(AntropometriBase):
    pass


class AntropometriResponse(AntropometriBase):
    id:          int
    z_score:     float
    status_gizi: str
    
    balita: Optional[BalitaResponse] = None

    model_config = {"from_attributes": True}
