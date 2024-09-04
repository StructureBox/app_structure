import io
import os
import logging
from supabase import create_client, Client
from fastapi import HTTPException
from dotenv import load_dotenv
from datetime import timedelta

# 環境変数の読み込み
load_dotenv()

# Supabaseの設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "excel-templates"

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_name: str, file_data: io.BytesIO) -> None:
    """
    Supabaseにファイルをアップロードする関数。
    """
    logging.debug(f"Uploading {file_name} to Supabase storage")
    response = supabase.storage.from_("edited-files").upload(file_name, file_data.getvalue())
    logging.debug(f"Response from storage upload: {response}")

    if response is None or hasattr(response, 'error') and response.error:
        logging.error(f"Failed to upload {file_name} to Supabase storage")
        raise HTTPException(status_code=500, detail="Failed to upload file")

def generate_download_link(file_name: str, expiration_minutes: int = 10) -> str:
    """
    Supabase上のファイルに対して有効期限付きのダウンロードリンクを生成する関数。
    """
    logging.debug(f"Generating download link for {file_name}")
    expiration_time = int((timedelta(minutes=expiration_minutes)).total_seconds())
    response = supabase.storage.from_("edited-files").create_signed_url(file_name, expiration_time)
    logging.debug(f"Response from generating signed URL: {response}")

    if response is None or hasattr(response, 'error') and response.error:
        logging.error(f"Failed to generate download link for {file_name}")
        raise HTTPException(status_code=500, detail="Failed to generate download link")

    # レスポンスから signedURL を取得
    signed_url = response.get('signedURL')
    if not signed_url:
        logging.error(f"No signed URL returned for {file_name}")
        raise HTTPException(status_code=500, detail="No signed URL generated")
    
    return signed_url

def download_from_supabase(file_name: str) -> io.BytesIO:
    """
    Supabaseからファイルをダウンロードする関数。
    """
    logging.debug(f"Downloading {file_name} from Supabase storage")
    response = supabase.storage.from_("excel-templates").download(file_name)
    if response is None or hasattr(response, 'error') and response.error:
        logging.error(f"Failed to download {file_name} from Supabase storage")
        raise HTTPException(status_code=404, detail="File not found or failed to download")

    # 返ってくるresponseはバイト型のため、直接BytesIOに渡す
    return io.BytesIO(response)

if __name__ == "__main__":
    # ロギングの設定
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        # 1. テスト用のファイルパスを設定
        test_file_path = "temp/template.xlsx"
        with open(test_file_path, "rb") as file:
            test_data = io.BytesIO(file.read())  # ファイルの内容をBytesIOに読み込み

        # 2. Supabaseにファイルをアップロード
        logging.debug("Testing file upload to Supabase")
        upload_to_supabase("template.xlsx", test_data)
        logging.info(f"File {test_file_path} uploaded successfully")

        # 3. アップロードされたファイルのダウンロードリンクを生成
        logging.debug("Generating download link for the uploaded file")
        download_link = generate_download_link("template.xlsx", expiration_minutes=10)
        logging.info(f"Download link generated: {download_link}")

        # 4. ファイルをSupabaseからダウンロード
        logging.debug("Testing file download from Supabase")
        downloaded_file = download_from_supabase("template.xlsx")
        logging.info(f"File template.xlsx downloaded successfully")

    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
