from pydantic import BaseModel
from typing import Dict, Type

# 各テンプレートに対応する入力モデル
class SafetyCertificateInput(BaseModel):
    architect_number: str
    architect_name: str
    office_number: str
    address: str
    phone_number: str
    client_name: str
    building_location: str
    building_name: str
    building_usage: str
    building_area: float
    total_area: float
    max_height: float
    eaves_height: float
    above_ground_floors: int
    underground_floors: int
    structure_type: str


class OtherTemplateInput(BaseModel):
    project_name: str
    project_leader: str
    start_date: str
    end_date: str
    budget: float


# 各テンプレートの入力モデルとセルマッピングを辞書で管理
template_model_map: Dict[str, Type[BaseModel]] = {
    "safety_certificate": SafetyCertificateInput,
    "other_template": OtherTemplateInput
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
        "structure_type": "B62"
    },
    "other_template": {
        "project_name": "A1",
        "project_leader": "A2",
        "start_date": "A3",
        "end_date": "A4",
        "budget": "A5"
    }
}
