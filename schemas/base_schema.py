from typing import Any, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Standar response wrapper untuk semua endpoint."""
    success: bool = True
    message: str  = "OK"
    data: Optional[Any] = None
