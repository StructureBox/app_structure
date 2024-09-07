from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import config

# ルーティングモジュールをインポート
from api.steel import router as steel_router
from api.excel import router as excel_router
from api.excel_test import test_router as excel_test_router


app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION,
    openapi_url=config.OPENAPI_URL,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    root_path=config.ROOT_PATH)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,  # ConfigのALLOWED_ORIGINSを使用
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(steel_router, prefix="/steel", tags=["Steel"])
app.include_router(excel_router, prefix="/excel", tags=["Excel"])

# テスト用エンドポイントは本番環境では無効にする
if config.ENVIRONMENT != "production":
    app.include_router(excel_test_router, prefix="/test/excel", tags=["Test"])


# ルートはdocsにリダイレクト
@app.get("/")
def read_root():
    return RedirectResponse(f".{config.DOCS_URL}")
