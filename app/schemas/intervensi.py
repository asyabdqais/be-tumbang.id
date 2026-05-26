from pydantic import BaseModel
from typing import Optional

class IntervensiBase(BaseModel):
    antropometri_id: int
    rekomendasi_ai: str

class IntervensiCreate(IntervensiBase):
    pass

class IntervensiUpdate(BaseModel):
    rekomendasi_ai: Optional[str] = None
    is_approved: Optional[bool] = None
    is_rujukan_rsud: Optional[bool] = None  # Dokter bisa langsung rujuk ke RSUD

class IntervensiResponse(IntervensiBase):
    id: int
    is_approved: bool
    is_rujukan_rsud: bool
    dokter_id: Optional[int] = None

    class Config:
        from_attributes = True
