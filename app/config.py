import os
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()


class Config:
    """プロジェクト全体で使用する設定"""

    # CORS設定
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

    # Supabase設定
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # アプリの基本設定
    APP_TITLE = "StructureBox API"
    APP_VERSION = "1.0.0"
    OPENAPI_URL = "/openapi.json"
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    ROOT_PATH = "/v1"

    # description.md ファイルを読み込む
    @staticmethod
    def load_description():
        """APIの説明用のMarkdownファイルを読み込む"""
        with open("description.md", "r", encoding="utf-8") as file:
            return file.read()

    # 説明文のロード
    APP_DESCRIPTION = load_description()

    # 環境設定
    ENVIRONMENT = os.getenv("APP_ENV")  # 環境変数で設定する


config = Config()
