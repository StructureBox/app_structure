from pydantic import BaseModel, Field
from typing import Optional


class SteelPostSectionInput(BaseModel):
    size: Optional[str] = Field("H-300*150*6.5*9", json_schema_extra={"example": "H-300*150*6.5*9"})


# H形鋼の入力モデル
class HSectionInput(BaseModel):
    H: Optional[float] = Field(300, json_schema_extra={"example": 300})
    B: Optional[float] = Field(150, json_schema_extra={"example": 150})
    tw: Optional[float] = Field(6.5, json_schema_extra={"example": 6.5})
    tf: Optional[float] = Field(9, json_schema_extra={"example": 9})


# 溝形鋼(WC)の入力モデル
class WCSectionInput(BaseModel):
    H: Optional[float] = Field(300, json_schema_extra={"example": 300})
    B: Optional[float] = Field(100, json_schema_extra={"example": 100})
    tw: Optional[float] = Field(8, json_schema_extra={"example": 8})
    tf: Optional[float] = Field(12, json_schema_extra={"example": 12})


# リップ形鋼(LC)の入力モデル
class LCSectionInput(BaseModel):
    H: Optional[float] = Field(150, json_schema_extra={"example": 150})
    B: Optional[float] = Field(75, json_schema_extra={"example": 75})
    C: Optional[float] = Field(20, json_schema_extra={"example": 20})
    t: Optional[float] = Field(2.5, json_schema_extra={"example": 2.5})


# 正方形鋼管(BOX)の入力モデル
class BOXSectionInput(BaseModel):
    B: Optional[float] = Field(150, json_schema_extra={"example": 150})
    t: Optional[float] = Field(6, json_schema_extra={"example": 6})


# 円形鋼管(PIPE)の入力モデル
class PIPESectionInput(BaseModel):
    D: Optional[float] = Field(150, json_schema_extra={"example": 150})  # 外径
    t: Optional[float] = Field(6, json_schema_extra={"example": 6})  # 板厚
