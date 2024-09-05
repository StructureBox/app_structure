import os
import logging

from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from openpyxl import load_workbook

# モデルをインポート
from models.excel_models import (
    template_model_map,
    template_cell_map,
)
from models.steel_input_models import SteelGetSectionInput

# Excel関連の関数をインポート
from utils.excel import get_excel_template, edit_excel_template

# 構造計算関連の関数をインポート
from utils.steel import Steel

# Supabase操作をまとめた関数をインポート
from utils.supabase_utils import upload_to_supabase, generate_download_link, delete_from_supabase

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


@app.post("/edit_excel/{template_name}/test")
async def process_excel_test(template_name: str, input_data: dict = Body(...)):
    """
    テスト用エンドポイント。Supabaseにアップロードし、ダウンロードリンク取得後、ファイルを削除。
    """
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

    # Supabaseへのアップロードとダウンロードリンクの生成
    excel_file_name = f"{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    try:
        # Supabaseにアップロード
        upload_to_supabase(excel_file_name, edited_excel)
        upload_message = f"File {excel_file_name} uploaded to Supabase successfully."

        # ダウンロードリンクを生成
        excel_download_url = generate_download_link(excel_file_name)
        download_link_message = f"Download link generated: {excel_download_url}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload or generate download link: {str(e)}")

    # 編集されたExcelファイルが実際に編集されているか確認
    try:
        # Excelの内容を読み取って確認（確認用の処理）
        edited_excel.seek(0)
        workbook = load_workbook(edited_excel)
        sheet = workbook.active

        # models/excel_models.pyで定義されたセルマッピングを取得
        cell_map = template_cell_map.get(template_name)
        if not cell_map:
            raise HTTPException(status_code=500, detail="Template cell map not found")

        # 結果の辞書
        edited_cells = {}
        error_cells = {}

        # 各セルの編集結果を確認
        for field, cell in cell_map.items():
            try:
                # セルの内容を確認して返す
                cell_value = sheet[cell].value
                edited_cells[cell] = cell_value
            except Exception as e:
                # セルの編集に失敗した場合はエラーメッセージを追加
                error_cells[cell] = str(e)

        # ファイルを削除する処理（確認後にSupabase上のファイルを削除）
        delete_message = delete_from_supabase(excel_file_name)

        # 確認用のメッセージ
        return {
            "message": "Excel edited successfully" if not error_cells else "Excel edited with errors",
            "validated_data": validated_data,
            "edited_cells": edited_cells,  # 編集されたセルの内容
            "error_cells": error_cells,  # 編集に失敗したセルとその原因
            "upload_message": upload_message,  # アップロード成功メッセージ
            "download_link_message": download_link_message,  # ダウンロードリンク生成メッセージ
            "delete_message": delete_message,  # 削除成功メッセージ
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify edited Excel: {str(e)}")


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
