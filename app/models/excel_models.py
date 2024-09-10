from pydantic import BaseModel, Field
from typing import Dict, Type, Optional


# 各テンプレートに対応する入力モデル
class SafetyCertificateInput(BaseModel):
    date_year: Optional[int] = Field(2025, json_schema_extra={"example": 2025})
    date_month: Optional[int] = Field(1, json_schema_extra={"example": 1})
    date_day: Optional[int] = Field(1, json_schema_extra={"example": 1})
    architect_number_1: Optional[str] = Field("一級", json_schema_extra={"example": "一級"})
    architect_number_2: Optional[str] = Field("大臣", json_schema_extra={"example": "大臣"})
    architect_number_3: Optional[str] = Field("111111", json_schema_extra={"example": "111111"})
    architect_name: Optional[str] = Field(
        "○○建築設計事務所", json_schema_extra={"example": "○○建築設計事務所"}
    )
    office_1: Optional[str] = Field("一級", json_schema_extra={"example": "一級"})
    office_2: Optional[str] = Field("東京都", json_schema_extra={"example": "東京都"})
    office_3: Optional[str] = Field("111111", json_schema_extra={"example": "111111"})
    address: Optional[str] = Field(
        "東京都港区芝５丁目２６−２０", json_schema_extra={"example": "東京都港区芝５丁目２６−２０"}
    )
    phone_number: Optional[str] = Field("00-0000-0000", json_schema_extra={"example": "00-0000-0000"})
    client_name: Optional[str] = Field("○○　○○", json_schema_extra={"example": "○○　○○"})
    building_location: Optional[str] = Field(
        "東京都港区芝５丁目２６−２０", json_schema_extra={"example": "東京都港区芝５丁目２６−２０"}
    )
    building_name: Optional[str] = Field("○○新築工事", json_schema_extra={"example": "○○新築工事"})
    building_usage: Optional[str] = Field("一戸建ての住宅", json_schema_extra={"example": "一戸建ての住宅"})
    building_area: Optional[float] = Field(1000.00, json_schema_extra={"example": 1000.00})
    total_area: Optional[float] = Field(1000.00, json_schema_extra={"example": 1000.00})
    max_height: Optional[float] = Field(9.000, json_schema_extra={"example": 9.000})
    eaves_height: Optional[float] = Field(6.000, json_schema_extra={"example": 6.000})
    ground_floors: Optional[int] = Field(3, json_schema_extra={"example": 3})
    underground_floors: Optional[int] = Field(1, json_schema_extra={"example": 1})
    structure_type_1: Optional[str] = Field("木造", json_schema_extra={"example": "木造"})
    structure_type_2: Optional[str] = Field(
        "鉄筋コンクリート造", json_schema_extra={"example": "鉄筋コンクリート造"}
    )
    building_kubun: Optional[int] = Field(3, json_schema_extra={"example": 3})
    keisan_kubun: Optional[int] = Field(5, json_schema_extra={"example": 5})
    keisan_nintei: Optional[int] = Field(1, json_schema_extra={"example": 1})
    program_name: Optional[str] = Field("Super Build/SS7", json_schema_extra={"example": "Super Build/SS7"})
    program_nintei: Optional[int] = Field(2, json_schema_extra={"example": 2})
    program_nintei_number: Optional[int] = Field(0, json_schema_extra={"example": 0})


class OtherTemplateInput(BaseModel):
    project_name: Optional[str] = Field("string", json_schema_extra={"example": "プロジェクトA"})
    project_leader: Optional[str] = Field("string", json_schema_extra={"example": "田中 太郎"})
    start_date: Optional[str] = Field("string", json_schema_extra={"example": "2024-01-01"})
    end_date: Optional[str] = Field("string", json_schema_extra={"example": "2024-12-31"})
    budget: Optional[float] = Field(1000.00, json_schema_extra={"example": 1000000.00})


# 各テンプレートの入力モデルとセルマッピングを辞書で管理
template_model_map: Dict[str, Type[BaseModel]] = {
    "safety_certificate": SafetyCertificateInput,
    "other_template": OtherTemplateInput,
}

template_cell_map = {
    "safety_certificate": {
        "date_year": "AI1",
        "date_month": "AI2",
        "date_day": "AI3",
        "architect_number_1": "AI4",
        "architect_number_2": "AI5",
        "architect_number_3": "AI6",
        "architect_name": "AI7",
        "office_1": "AI8",
        "office_2": "AI9",
        "office_3": "AI10",
        "address": "AI11",
        "phone_number": "AI12",
        "client_name": "AI13",
        "building_location": "AI14",
        "building_name": "AI15",
        "building_usage": "AI16",
        "building_area": "AI17",
        "total_area": "AI18",
        "max_height": "AI19",
        "eaves_height": "AI20",
        "ground_floors": "AI21",
        "underground_floors": "AI22",
        "structure_type_1": "AI23",
        "structure_type_2": "AI24",
        "building_kubun": "AI25",
        "keisan_kubun": "AI26",
        "keisan_nintei": "AI27",
        "program_name": "AI28",
        "program_nintei": "AI29",
        "program_nintei_number": "AI30",
    },
    "other_template": {
        "project_name": "A1",
        "project_leader": "A2",
        "start_date": "A3",
        "end_date": "A4",
        "budget": "A5",
    },
}
