# app/api/zumen.py

import logging
from fastapi import APIRouter
from services.zumen import process_zumen_file

# ルーターの作成
router = APIRouter()

@router.post("/dxf/{template_name}")
def process_dxf_template(template_name: str):
    """
    DXFテンプレートを処理し、ダウンロードリンクを返すエンドポイント。
    """
    return process_zumen_file(template_name, ".dxf")

@router.post("/jww/{template_name}")
def process_jww_template(template_name: str):
    """
    JWWテンプレートを処理し、ダウンロードリンクを返すエンドポイント。
    """
    return process_zumen_file(template_name, ".jww")
