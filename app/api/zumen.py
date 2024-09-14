import logging
from fastapi import APIRouter, HTTPException, Body
from services.zumen import get_dxf_template
from services.supabase_dxf_utils import ensure_dxf_extension, generate_supabase_dxf_url,upload_dxf_to_supabase, generate_dxf_download_link,download_dxf_from_url
from datetime import datetime

# ルーターの作成
router = APIRouter()


@router.post("/dxf/{template_name}")
def process_dxf_template(template_name: str):
    """
    SupabaseからDXFファイルをダウンロードし、ファイル名を変更して再度アップロードし、
    そのダウンロードリンクを返すエンドポイント。
    """
    try:
        # 元のファイル名を作成（拡張子を追加）
        original_file_name = ensure_dxf_extension(template_name)

        # 'dxf-template'バケットからファイルのサイン付きURLを生成
        file_url = generate_supabase_dxf_url(original_file_name)

        # ファイルをダウンロード
        downloaded_file = download_dxf_from_url(file_url)

        # ダウンロードしたファイルが空でないか確認
        if downloaded_file.getbuffer().nbytes == 0:
            logging.error(f"Downloaded file {original_file_name} is empty.")
            raise HTTPException(status_code=500, detail="Downloaded file is empty.")

        # 今日の日付で新しいファイル名を作成
        today_str = datetime.now().strftime("%Y-%m-%d")
        new_file_name = f"{today_str}-{original_file_name}"

        # 'edited-dxf-files'バケットにファイルをアップロード
        upload_dxf_to_supabase(new_file_name, downloaded_file)

        # アップロードしたファイルのダウンロードリンクを生成
        download_link = generate_dxf_download_link(new_file_name)

        # ダウンロードリンクを返す
        return {"download_link": download_link}

    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
