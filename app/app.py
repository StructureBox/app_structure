import io
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Excel関連の関数をインポート
from excel import get_excel_template, edit_excel_template
from steel import Steel

# Supabase操作をまとめた関数をインポート
from supabase_utils import upload_to_supabase, generate_download_link

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

class SteelGetSectionInput(BaseModel):
    size: str

@app.post("/edit_excel/")
async def process_excel(
    architect_number: str = Form(...),
    architect_name: str = Form(...),
    office_number: str = Form(...),
    address: str = Form(...),
    phone_number: str = Form(...),
    client_name: str = Form(...),
    building_location: str = Form(...),
    building_name: str = Form(...),
    building_usage: str = Form(...),
    building_area: float = Form(...),
    total_area: float = Form(...),
    max_height: float = Form(...),
    eaves_height: float = Form(...),
    above_ground_floors: int = Form(...),
    underground_floors: int = Form(...),
    structure_type: str = Form(...),
    building_category: str = Form(...),
    calculation_type: str = Form(...),
    calculation_method: str = Form(...),
    program_name: str = Form(...),
    program_version: str = Form(...),
):
    logging.debug("Starting process_excel endpoint")
    
    # 1. エクセルテンプレートの取得
    template = get_excel_template()

    # 2. テンプレートの編集
    edited_excel = edit_excel_template(
        template,
        architect_number=architect_number,
        architect_name=architect_name,
        office_number=office_number,
        address=address,
        phone_number=phone_number,
        client_name=client_name,
        building_location=building_location,
        building_name=building_name,
        building_usage=building_usage,
        building_area=building_area,
        total_area=total_area,
        max_height=max_height,
        eaves_height=eaves_height,
        above_ground_floors=above_ground_floors,
        underground_floors=underground_floors,
        structure_type=structure_type,
        building_category=building_category,
        calculation_type=calculation_type,
        calculation_method=calculation_method,
        program_name=program_name,
        program_version=program_version,
    )

    # 3. Supabaseにアップロード
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_file_name = f"edited_{timestamp}.xlsx"
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
