import io

# import os
import logging

from fastapi import HTTPException
from openpyxl import load_workbook
from services.supabase_dxf_utils import generate_supabase_dxf_url, download_dxf_from_url


def get_dxf_template(file_name: str):
    """
    Supabaseからサイン付きURLを使ってJWWテンプレートを取得する関数
    """
    logging.debug(f"Requesting signed URL for {file_name} from Supabase.")

    # 有効期限付きのサイン付きURLを取得（10分間有効）
    signed_url = generate_supabase_dxf_url(file_name)

    # サイン付きURLを使ってExcelファイルをダウンロード
    return download_dxf_from_url(signed_url)
