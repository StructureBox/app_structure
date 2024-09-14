import logging
from datetime import datetime
from fastapi import HTTPException
from services.supabase_utils import (
    ensure_extension,
    generate_supabase_url,
    upload_file_to_supabase,
    generate_download_link,
    download_file_from_url,
)

def process_zumen_file(template_name: str, extension: str) -> dict:
    """
    指定されたテンプレートをダウンロードし、ファイル名を変更してアップロードし、ダウンロードリンクを返す。
    """
    try:
        # 拡張子を確実に付ける
        original_file_name = ensure_extension(template_name, extension)

        # 'zumen-template' バケットからサイン付きURLを生成
        file_url = generate_supabase_url(original_file_name, bucket_name="zumen-template")
        downloaded_file = download_file_from_url(file_url)

        # ファイルが空でないか確認
        if downloaded_file.getbuffer().nbytes == 0:
            logging.error(f"Downloaded file {original_file_name} is empty.")
            raise HTTPException(status_code=500, detail="Downloaded file is empty.")

        # 一意のファイル名を作成（日時を用いて）
        timestamp_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        new_file_name = f"{timestamp_str}-{original_file_name}"

        # 'edited-zumen' バケットにファイルをアップロード
        upload_file_to_supabase(new_file_name, downloaded_file, bucket_name="edited-zumen")

        # ダウンロードリンクを生成
        download_link = generate_download_link(new_file_name, bucket_name="edited-zumen")

        return {"download_link": download_link}
    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        )
