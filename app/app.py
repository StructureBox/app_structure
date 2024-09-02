import io
import os

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

from excel import edit_excel_template, convert_excel_to_pdf
from steel import Steel


# 環境変数をロード
load_dotenv()

# Supabaseの設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPIアプリの作成
app = FastAPI()

# CORSミドルウェアの動的設定
origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 環境変数またはデフォルト値を使用
    allow_credentials=True,
    allow_methods=["*"],  # 全てのHTTPメソッドを許可
    allow_headers=["*"],  # 全てのヘッダーを許可
)

BUCKET_NAME = os.getenv("BUCKET_NAME")


def get_excel_template() -> io.BytesIO:
    """
    Supabaseからエクセルテンプレートを取得する関数。
    """
    response = supabase.storage().from_("excel-templates").download("template.xlsx")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Template not found")
    return io.BytesIO(response.body)


def upload_to_supabase(file_name: str, file_data: io.BytesIO) -> None:
    """
    Supabaseにファイルをアップロードする関数。
    """
    response = supabase.storage().from_("edited-files").upload(file_name, file_data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to upload file")


def generate_download_link(file_name: str, expiration_minutes: int = 10) -> str:
    """
    Supabase上のファイルに対して有効期限付きのダウンロードリンクを生成する関数。
    """
    expiration_time = int((timedelta(minutes=expiration_minutes)).total_seconds())
    return supabase.storage().from_("edited-files").create_signed_url(file_name, expiration_time)


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

    # 3. PDFに変換
    pdf_data = convert_excel_to_pdf(edited_excel)

    # 4. Supabaseにアップロード
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_file_name = f"edited_{timestamp}.xlsx"
    pdf_file_name = f"edited_{timestamp}.pdf"

    upload_to_supabase(excel_file_name, edited_excel)
    upload_to_supabase(pdf_file_name, pdf_data)

    # 5. ダウンロードリンクの生成
    excel_download_url = generate_download_link(excel_file_name)
    pdf_download_url = generate_download_link(pdf_file_name)

    return {"excel_download_url": excel_download_url, "pdf_download_url": pdf_download_url}


@app.post("/get_section/")
def get_section(input_data: SteelGetSectionInput):
    steel = Steel()
    shape, section, values = steel.get_section(input_data.size)
    if values is None:
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


# ルートエンドポイント
@app.get("/")
def read_root():
    return RedirectResponse("./docs")
