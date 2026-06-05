from pydantic import BaseModel
from typing import Optional
from schemas.antropometri_schema import AntropometriResponse


class IntervensiBase(BaseModel):
    antropometri_id: int
    rekomendasi_ai:  str


class IntervensiCreate(IntervensiBase):
    pass


class IntervensiUpdate(BaseModel):
    rekomendasi_ai:  Optional[str]  = None
    is_approved:     Optional[bool] = None
    is_rujukan_rsud: Optional[bool] = None


class IntervensiResponse(IntervensiBase):
    id:              int
    is_approved:     bool
    is_rujukan_rsud: bool
    dokter_id:       Optional[int] = None
    
    antropometri: Optional[AntropometriResponse] = None

    model_config = {"from_attributes": True}
