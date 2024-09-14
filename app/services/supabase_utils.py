import io
import logging
import requests
from datetime import timedelta
from urllib.parse import urlencode
from fastapi import HTTPException
from supabase import create_client, Client
from config import config  # Supabaseの設定をインポート

# Supabaseクライアントの作成
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def ensure_extension(file_name: str, extension: str) -> str:
    """
    ファイル名に指定した拡張子が含まれていない場合、自動的に追加する。
    """
    if not file_name.endswith(extension):
        file_name += extension
    return file_name

def generate_supabase_url(file_name: str, bucket_name: str, expiration_minutes: int = 5) -> str:
    """
    Supabaseからファイルのサイン付きURLを生成する関数。
    """
    logging.debug(f"Generating signed URL for {file_name} in bucket {bucket_name}")

    expiration_time = int(timedelta(minutes=expiration_minutes).total_seconds())

    try:
        response = supabase.storage.from_(bucket_name).create_signed_url(
            file_name, expiration_time
        )
        if hasattr(response, 'error') and response.error:
            error_detail = getattr(response.error, 'message', 'Unknown error')
            logging.error(f"Failed to generate signed URL: {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate signed URL: {error_detail}"
            )
        signed_url = response.get("signedURL")
        if not signed_url:
            logging.error(f"No signed URL returned for {file_name}")
            raise HTTPException(status_code=500, detail="No signed URL generated")

        # 'download' パラメータを追加してファイル名を指定
        params = {'download': file_name}
        query_string = urlencode(params)
        signed_url_with_download = f"{signed_url}&{query_string}"

        return signed_url_with_download
    except Exception as e:
        logging.error(f"Error generating signed URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate signed URL: {str(e)}"
        )

def upload_file_to_supabase(file_name: str, file_data: io.BytesIO, bucket_name: str) -> None:
    """
    Supabaseにファイルをアップロードする関数。
    """
    logging.debug(f"Uploading {file_name} to bucket {bucket_name}")

    response = supabase.storage.from_(bucket_name).upload(
        file_name, file_data.getvalue()
    )
    logging.debug(f"Response from storage upload: {response}")

    if response is None or (hasattr(response, "error") and response.error):
        logging.error(f"Failed to upload {file_name} to Supabase storage")
        raise HTTPException(status_code=500, detail="Failed to upload file")

def generate_download_link(file_name: str, bucket_name: str, expiration_minutes: int = 10) -> str:
    """
    Supabase上のファイルに対して有効期限付きのダウンロードリンクを生成する関数。
    """
    logging.debug(f"Generating download link for {file_name} in bucket {bucket_name}")
    expiration_time = int(timedelta(minutes=expiration_minutes).total_seconds())
    response = supabase.storage.from_(bucket_name).create_signed_url(
        file_name, expiration_time
    )
    logging.debug(f"Response from generating signed URL: {response}")

    if response is None or (hasattr(response, "error") and response.error):
        logging.error(f"Failed to generate download link for {file_name}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate download link"
        )

    signed_url = response.get("signedURL")
    if not signed_url:
        logging.error(f"No signed URL returned for {file_name}")
        raise HTTPException(status_code=500, detail="No signed URL generated")

    # 'download' パラメータを追加してファイル名を指定
    params = {'download': file_name}
    query_string = urlencode(params)
    signed_url_with_download = f"{signed_url}&{query_string}"

    return signed_url_with_download

def download_file_from_url(url: str) -> io.BytesIO:
    """
    URLからファイルをダウンロードし、BytesIOとして返す関数。
    """
    logging.debug(f"Downloading file from URL: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Failed to download file from URL: {url}")
        raise HTTPException(
            status_code=404, detail="File not found or failed to download"
        )

    return io.BytesIO(response.content)
