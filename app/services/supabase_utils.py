import io
import logging
import requests
from datetime import timedelta
from fastapi import HTTPException
from supabase import create_client, Client
from config import config  # configからSupabaseの設定をインポート

# Supabaseクライアントの作成
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def ensure_xlsx_extension(file_name: str) -> str:
    """
    ファイル名に拡張子が含まれていない場合、自動的に.xlsxを追加する。
    """
    if not file_name.endswith(".xlsx"):
        file_name += ".xlsx"
    return file_name


def generate_supabase_file_url(file_name: str, expiration_minutes: int = 5) -> str:
    """
    Supabaseのファイルに対して有効期限付きのサインURLを生成し、セキュリティを強化したダウンロードURLを生成する関数
    """
    file_name = ensure_xlsx_extension(file_name)
    logging.debug(f"Generating signed URL for {file_name}")

    expiration_time = int(timedelta(minutes=expiration_minutes).total_seconds())

    # Supabaseのサイン付きURLを生成
    try:
        response = supabase.storage.from_("excel_templates").create_signed_url(file_name, expiration_time)
    except Exception as e:
        logging.error(f"Error generating signed URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate signed URL")

    if response is None or (hasattr(response, "error") and response.error):
        logging.error(f"Failed to generate signed URL for {file_name}. Response: {response}")
        raise HTTPException(status_code=500, detail="Failed to generate signed URL")

    signed_url = response.get("signedURL")
    if not signed_url:
        logging.error(f"No signed URL returned for {file_name}")
        raise HTTPException(status_code=500, detail="No signed URL generated")

    return signed_url


def upload_to_supabase(file_name: str, file_data: io.BytesIO) -> None:
    """
    Supabaseにファイルをアップロードする関数。
    """
    file_name = ensure_xlsx_extension(file_name)
    logging.debug(f"Uploading {file_name} to Supabase storage")
    response = supabase.storage.from_("edited-files").upload(file_name, file_data.getvalue())
    logging.debug(f"Response from storage upload: {response}")

    if response is None or hasattr(response, "error") and response.error:
        logging.error(f"Failed to upload {file_name} to Supabase storage")
        raise HTTPException(status_code=500, detail="Failed to upload file")


def generate_download_link(file_name: str, expiration_minutes: int = 10) -> str:
    """
    Supabase上のファイルに対して有効期限付きのダウンロードリンクを生成する関数。
    """
    file_name = ensure_xlsx_extension(file_name)
    logging.debug(f"Generating download link for {file_name}")
    expiration_time = int((timedelta(minutes=expiration_minutes)).total_seconds())
    response = supabase.storage.from_("edited-files").create_signed_url(file_name, expiration_time)
    logging.debug(f"Response from generating signed URL: {response}")

    if response is None or hasattr(response, "error") and response.error:
        logging.error(f"Failed to generate download link for {file_name}")
        raise HTTPException(status_code=500, detail="Failed to generate download link")

    # レスポンスから signedURL を取得
    signed_url = response.get("signedURL")
    if not signed_url:
        logging.error(f"No signed URL returned for {file_name}")
        raise HTTPException(status_code=500, detail="No signed URL generated")

    return signed_url


def download_from_supabase(file_name: str) -> io.BytesIO:
    """
    Supabaseからファイルをダウンロードする関数。
    """
    file_name = ensure_xlsx_extension(file_name)
    logging.debug(f"Downloading {file_name} from Supabase storage")
    try:
        response = supabase.storage.from_("excel_templates").download(file_name)
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail="Error downloading file")

    if response is None or hasattr(response, "error") and response.error:
        logging.error(f"Failed to download {file_name} from Supabase storage")
        raise HTTPException(status_code=404, detail="File not found or failed to download")

    # 返ってくるresponseはバイト型のため、直接BytesIOに渡す
    return io.BytesIO(response)


# 公開URLからファイルをダウンロードする関数
def download_excel_from_url(url: str) -> io.BytesIO:
    """
    URLからエクセルファイルをダウンロードし、BytesIOとして返す関数。
    """
    logging.debug(f"Downloading Excel file from URL: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Failed to download Excel file from URL: {url}")
        raise HTTPException(status_code=404, detail="File not found or failed to download")

    return io.BytesIO(response.content)


def delete_from_supabase(file_name: str) -> str:
    """
    Supabase上のファイルを削除する関数。
    """
    file_name = ensure_xlsx_extension(file_name)
    try:
        response = supabase.storage.from_("edited-files").remove([file_name])
        # `response` がリストのため、エラーチェックを修正
        if isinstance(response, list) and response and "error" in response[0]:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {file_name}")
        logging.info(f"File {file_name} deleted successfully from Supabase.")
        return f"File {file_name} deleted successfully from Supabase."
    except Exception as e:
        logging.error(f"Error deleting file from Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


# テスト用の処理
if __name__ == "__main__":
    # ロギングの設定
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        logging.debug("Testing generate file URL from Supabase")

        # 1. ファイルのURLを生成
        file_name = "safety_certificate"  # 拡張子を省略しても自動で追加される
        file_url = generate_supabase_file_url(file_name)
        logging.info(f"File URL generated: {file_url}")

        # 2. URLからファイルをダウンロード
        logging.debug("Downloading file from generated URL")
        downloaded_file = download_excel_from_url(file_url)

        # 3. ダウンロード成功の判定
        if downloaded_file.getbuffer().nbytes > 0:
            logging.info(f"File {file_name} downloaded successfully and has data.")
        else:
            logging.error(f"File {file_name} downloaded but is empty.")

        # 4. テストのためにファイルをアップロード
        logging.debug(f"Uploading file {file_name} to Supabase for deletion test.")
        test_file_data = io.BytesIO(downloaded_file.getvalue())  # ダウンロードしたファイルを再アップロード
        upload_to_supabase(file_name, test_file_data)

        logging.info(f"File {file_name} uploaded to Supabase successfully.")

        # 5. アップロードされたファイルを削除
        logging.debug(f"Deleting file {file_name} from Supabase.")
        delete_message = delete_from_supabase(file_name)
        logging.info(delete_message)

    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
