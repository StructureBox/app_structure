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


# 各テンプレートの例を定義
template_example_map = {
    "safety_certificate": {
        "architect_number": "123456789",
        "architect_name": "John Doe",
        "office_number": "987654321",
        "address": "123 Architecture St",
        "phone_number": "555-1234",
        "client_name": "Jane Smith",
        "building_location": "456 Building Ave",
        "building_name": "Sky Tower",
        "building_usage": "Residential",
        "building_area": 350.5,
        "total_area": 500.0,
        "max_height": 120.0,
        "eaves_height": 115.0,
        "above_ground_floors": 10,
        "underground_floors": 2,
        "structure_type": "Steel",
    },
    "other_template": {
        "project_name": "New Development",
        "project_leader": "Alice Johnson",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "budget": 1000000.0,
    },
}
