from pydantic import BaseModel, Field
from typing import Optional


class RcGetSectionInput(BaseModel):
    size: Optional[str] = Field("H-300*150*6.5*9", json_schema_extra={"example": "H-300*150*6.5*9"})
