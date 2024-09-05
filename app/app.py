import os
import logging

from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# モデルをインポート
from models.excel_models import template_model_map, SafetyCertificateInput, template_example_map
from models.steel_input_models import SteelGetSectionInput

# Excel関連の関数をインポート
from utils.excel import get_excel_template, edit_excel_safety_certificate, edit_excel_template
from utils.steel import Steel

# Supabase操作をまとめた関数をインポート
from utils.supabase_utils import upload_to_supabase, generate_download_link

# 環境変数をロード
load_dotenv()

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)

# FastAPIアプリの作成
app = FastAPI()

# CORSミドルウェアの動的設定
origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/edit_excel/{template_name}")
async def process_excel(template_name: str, input_data: dict = Body(...)):
    # 入力モデルとセルマッピングを動的に選択
    model = template_model_map.get(template_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    # 入力データのバリデーション
    validated_data = model(**input_data).dict()

    # Excelテンプレートを取得
    template = get_excel_template(template_name)

    # セル位置を利用してExcelを編集
    edited_excel = edit_excel_template(template, template_name, validated_data)

    # Supabaseにアップロード
    excel_file_name = f"{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    upload_to_supabase(excel_file_name, edited_excel)

    # ダウンロードリンクを生成
    excel_download_url = generate_download_link(excel_file_name)
    return {"excel_download_url": excel_download_url}


@app.post("/edit_excel/{template_name}/with_example")
async def process_excel_with_example(template_name: str):
    # テンプレートに基づくexampleを取得
    example_data = template_example_map.get(template_name)
    if not example_data:
        raise HTTPException(status_code=404, detail=f"Example for template '{template_name}' not found")

    # example_dataを含むエンドポイントの定義
    return {"template_name": template_name, "example": example_data}


@app.post("/edit_excel/safety_certificate")
async def edit_safety_certificate(model: SafetyCertificateInput):
    logging.debug("Starting process_excel endpoint")

    # 1. エクセルテンプレートの取得
    template = get_excel_template("safety_certificate")

    # 2. テンプレートの編集
    edited_excel = edit_excel_safety_certificate(
        template,
        architect_number=model.architect_number,
        architect_name=model.architect_name,
        office_number=model.office_number,
        address=model.address,
        phone_number=model.phone_number,
        client_name=model.client_name,
        building_location=model.building_location,
        building_name=model.building_name,
        building_usage=model.building_usage,
        building_area=model.building_area,
        total_area=model.total_area,
        max_height=model.max_height,
        eaves_height=model.eaves_height,
        above_ground_floors=model.above_ground_floors,
        underground_floors=model.underground_floors,
        structure_type=model.structure_type,
        building_category=model.building_category,
        calculation_type=model.calculation_type,
        calculation_method=model.calculation_method,
        program_name=model.program_name,
        program_version=model.program_version,
    )

    # 3. Supabaseにアップロード
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_file_name = f"safety_certificate_{timestamp}.xlsx"
    upload_to_supabase(excel_file_name, edited_excel)

    # 4. ダウンロードリンクの生成
    excel_download_url = generate_download_link(excel_file_name)

    logging.debug("Completed process_excel endpoint")
    return {"excel_download_url": excel_download_url}


@app.post("/get_section/")
def get_section(input_data: SteelGetSectionInput):
    logging.debug(f"Getting section data for size: {input_data.size}")
    steel = Steel()
    shape, section, values = steel.get_section(input_data.size)
    if values is None:
        logging.error(f"No section data found for size: {input_data.size}")
        raise HTTPException(status_code=404, detail="指定された部材寸法に一致する断面が見つかりません")
    return {
        "A": values[0],
        "Ix": values[1],
        "Iy": values[2],
        "Zx": values[3],
        "Zy": values[4],
        "ix": values[5],
        "iy": values[6],
        "Cy": values[7] if len(values) > 7 else "N/A",  # Cyは一部の形状でのみ利用可能
    }


@app.get("/")
def read_root():
    return RedirectResponse("./docs")
