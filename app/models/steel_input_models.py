from pydantic import BaseModel, Field
from typing import Optional


class SteelGetSectionInput(BaseModel):
    size: Optional[str] = Field("H-300*150*6.5*9")
