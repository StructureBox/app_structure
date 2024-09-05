from pydantic import BaseModel, Field
from typing import Dict, Type, Optional


# 各テンプレートに対応する入力モデル
class SafetyCertificateInput(BaseModel):
    architect_number: Optional[str] = Field("111111")
    architect_name: Optional[str] = Field("string")
    office_number: Optional[str] = Field("string")
    address: Optional[str] = Field("string")
    phone_number: Optional[str] = Field("string")
    client_name: Optional[str] = Field("string")
    building_location: Optional[str] = Field("string")
    building_name: Optional[str] = Field("string")
    building_usage: Optional[str] = Field("string")
    building_area: Optional[float] = Field(1000.00)
    total_area: Optional[float] = Field(1000.00)
    max_height: Optional[float] = Field(5.000)
    eaves_height: Optional[float] = Field(5.000)
    above_ground_floors: Optional[int] = Field(3)
    underground_floors: Optional[int] = Field(1)
    structure_type: Optional[str] = Field("string")


class OtherTemplateInput(BaseModel):
    project_name: Optional[str] = Field("string")
    project_leader: Optional[str] = Field("string")
    start_date: Optional[str] = Field("string")
    end_date: Optional[str] = Field("string")
    budget: Optional[float] = Field(1000.00)


# 各テンプレートの入力モデルとセルマッピングを辞書で管理
template_model_map: Dict[str, Type[BaseModel]] = {
    "safety_certificate": SafetyCertificateInput,
    "other_template": OtherTemplateInput,
}

template_cell_map = {
    "safety_certificate": {
        "architect_number": "B47",
        "architect_name": "B48",
        "office_number": "B49",
        "address": "B50",
        "phone_number": "B51",
        "client_name": "B52",
        "building_location": "B53",
        "building_name": "B54",
        "building_usage": "B55",
        "building_area": "B56",
        "total_area": "B57",
        "max_height": "B58",
        "eaves_height": "B59",
        "above_ground_floors": "B60",
        "underground_floors": "B61",
        "structure_type": "B62",
    },
    "other_template": {
        "project_name": "A1",
        "project_leader": "A2",
        "start_date": "A3",
        "end_date": "A4",
        "budget": "A5",
    },
}
