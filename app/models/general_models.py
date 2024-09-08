from pydantic import BaseModel, Field
from typing import Optional


class TypePointInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    p: Optional[float] = Field(10.0, description="集中荷重", example=10.0)
    a: Optional[float] = Field(3.0, description="荷重の作用位置", example=3.0)


class TypeZoneInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    a: Optional[float] = Field(1.0, description="荷重開始位置", example=1.0)
    b: Optional[float] = Field(3.0, description="荷重の作用長さ", example=3.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    awl: Optional[float] = Field(1.5, description="荷重左端の高さ", example=1.5)
    bwl: Optional[float] = Field(0.0, description="荷重右端の高さ", example=0.0)


class TypeRectFullInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


class TypeRectPartInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    a: Optional[float] = Field(1.0, description="荷重開始位置", example=1.0)
    b: Optional[float] = Field(3.0, description="荷重の作用長さ", example=3.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


class TypeTriRightFullInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


class TypeTriLeftFullInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


class TypeTriRightPartInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    a: Optional[float] = Field(1.0, description="荷重開始位置", example=1.0)
    b: Optional[float] = Field(3.0, description="荷重の作用長さ", example=3.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


class TypeTriLeftPartInput(BaseModel):
    al: Optional[float] = Field(6.0, description="部材長", example=6.0)
    a: Optional[float] = Field(1.0, description="荷重開始位置", example=1.0)
    b: Optional[float] = Field(3.0, description="荷重の作用長さ", example=3.0)
    w: Optional[float] = Field(10.0, description="等分布荷重", example=10.0)
    wl: Optional[float] = Field(1.5, description="荷重の高さ", example=1.5)


# 入力モデルを辞書で管理
type_model_map = {
    "type_point": TypePointInput,
    "type_zone": TypeZoneInput,
    "type_rect_full": TypeRectFullInput,
    "type_rect_part": TypeRectPartInput,
    "type_tri_right_full": TypeTriRightFullInput,
    "type_tri_left_full": TypeTriLeftFullInput,
    "type_tri_right_part": TypeTriRightPartInput,
    "type_tri_left_part": TypeTriLeftPartInput,
}
