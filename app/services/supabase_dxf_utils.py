import io
import logging
import requests
from config import config  # configからSupabaseの設定をインポート
from datetime import timedelta
from fastapi import HTTPException
from supabase import create_client, Client
from urllib.parse import urlencode

# Supabaseクライアントの作成
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def ensure_dxf_extension(file_name: str) -> str:
    """
    ファイル名に拡張子が含まれていない場合、自動的に.dxfを追加する。
    """
    if not file_name.endswith(".dxf"):
        file_name += ".dxf"
    return file_name


def generate_supabase_dxf_url(file_name: str, expiration_minutes: int = 5) -> str:
    file_name = ensure_dxf_extension(file_name)
    logging.debug(f"Generating signed URL for {file_name}")

    expiration_time = int(timedelta(minutes=expiration_minutes).total_seconds())

    # Supabaseのサイン付きURLを生成
    try:
        response = supabase.storage.from_("dxf_template").create_signed_url(
            file_name, expiration_time
        )
        if hasattr(response, 'error') and response.error:
            error_detail = response.error.get('message', 'Unknown error')
            logging.error(f"Failed to generate signed URL: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {error_detail}")
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
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {e}")



def upload_dxf_to_supabase(file_name: str, file_data: io.BytesIO) -> None:
    """
    Supabaseにファイルをアップロードする関数。
    """
    file_name = ensure_dxf_extension(file_name)
    logging.debug(f"Uploading {file_name} to Supabase storage")

    # Content-Typeの指定を削除
    response = supabase.storage.from_("edited-dxf-files").upload(
        file_name, file_data.getvalue()
    )
    logging.debug(f"Response from storage upload: {response}")

    if response is None or hasattr(response, "error") and response.error:
        logging.error(f"Failed to upload {file_name} to Supabase storage")
        raise HTTPException(status_code=500, detail="Failed to upload file")



def generate_dxf_download_link(
    file_name: str, expiration_minutes: int = 10
) -> str:
    file_name = ensure_dxf_extension(file_name)
    logging.debug(f"Generating download link for {file_name}")
    expiration_time = int((timedelta(minutes=expiration_minutes)).total_seconds())
    response = supabase.storage.from_("edited-dxf-files").create_signed_url(
        file_name, expiration_time
    )
    logging.debug(f"Response from generating signed URL: {response}")

    if response is None or hasattr(response, "error") and response.error:
        logging.error(f"Failed to generate download link for {file_name}")
        raise HTTPException(
            status_code=500, detail="Failed to generate download link"
        )

    # レスポンスから signedURL を取得
    signed_url = response.get("signedURL")
    if not signed_url:
        logging.error(f"No signed URL returned for {file_name}")
        raise HTTPException(status_code=500, detail="No signed URL generated")

    # 'download' パラメータを追加してファイル名を指定
    params = {'download': file_name}
    query_string = urlencode(params)
    signed_url_with_download = f"{signed_url}&{query_string}"

    return signed_url_with_download


def download_dxf_from_url(url: str) -> io.BytesIO:
    """
    URLからDXFファイルをダウンロードし、BytesIOとして返す関数。
    """
    logging.debug(f"Downloading DXF file from URL: {url}")

    # headers = {"Accept": "application/dxf"}  # Content-Typeの指定を削除

    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Failed to download DXF file from URL: {url}")
        raise HTTPException(
            status_code=404, detail="File not found or failed to download"
        )

    # コンテンツタイプの確認も削除
    # content_type = response.headers.get("Content-Type", "")
    # if "application/dxf" not in content_type and "image/vnd.dxf" not in content_type:
    #     logging.error(
    #         f"Unexpected Content-Type: {content_type}. Expected 'application/dxf' or 'image/vnd.dxf'."
    #     )
    #     raise HTTPException(
    #         status_code=500, detail="Unexpected content type when downloading file."
    #     )

    return io.BytesIO(response.content)


def delete_dxf_from_supabase(file_name: str) -> str:
    """
    Supabase上のファイルを削除する関数。
    """
    file_name = ensure_dxf_extension(file_name)
    try:
        response = supabase.storage.from_("edited-dxf-files").remove([file_name])
        # `response` がリストのため、エラーチェックを修正
        if isinstance(response, list) and response and "error" in response[0]:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {file_name}")
        logging.info(f"File {file_name} deleted successfully from Supabase.")
        return f"File {file_name} deleted successfully from Supabase."
    except Exception as e:
        logging.error(f"Error deleting file from Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


if __name__ == "__main__":
    # ロギングの設定
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        logging.debug("Testing generate file URL from Supabase")

        # ファイルのURLを生成
        file_name = "wrc-standard-drawing-1"  # 拡張子を省略しても自動で追加される
        file_url = generate_supabase_dxf_url(file_name)
        logging.info(f"File URL generated: {file_url}")

        # URLからファイルをダウンロード
        logging.debug("Downloading file from generated URL")
        downloaded_file = download_dxf_from_url(file_url)

        # ダウンロード成功の判定
        if downloaded_file.getbuffer().nbytes > 0:
            logging.info(f"File {file_name} downloaded successfully and has data.")
        else:
            logging.error(f"File {file_name} downloaded but is empty.")

    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
