from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import RedirectResponse

# プロジェクト全体へのCORS設定
# from fastapi.middleware.cors import CORSMiddleware

from config import config

# ミドルウェアのインポート
from middleware import ErrorHandlingMiddleware, RateLimitMiddleware, CustomCORSMiddleware

# ルーティングモジュールをインポート
from api.open_source import router as open_source_router
from api.general import router as general_router
from api.excel import router as excel_router
from api.steel import router as steel_router
from api.rc import router as rc_router
from api.excel_test import test_router as excel_test_router


app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION,
    openapi_url=config.OPENAPI_URL,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    root_path=config.ROOT_PATH,
)

# # プロジェクト全体にCORS設定を行う
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=config.ALLOWED_ORIGINS,  # 許可されたオリジンを設定
#     allow_credentials=True,
#     allow_methods=["*"],  # 許可するHTTPメソッド
#     allow_headers=["*"],  # 許可するヘッダー
# )

# HTTPS カスタムミドルウェアを適用（本番環境用）
if config.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(CustomCORSMiddleware)

# カスタムミドルウェアを適用
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ルーターを登録
app.include_router(open_source_router, prefix="/free", tags=["Free"])
app.include_router(general_router, prefix="/general", tags=["General"])
app.include_router(excel_router, prefix="/excel", tags=["Excel"])
app.include_router(steel_router, prefix="/steel", tags=["Steel"])
app.include_router(rc_router, prefix="/rc", tags=["RC"])

# テスト用エンドポイントは本番環境では無効にする
if config.ENVIRONMENT != "production":
    app.include_router(excel_test_router, prefix="/test/excel", tags=["Test"])


# ルートはdocsにリダイレクト
@app.get("/")
def read_root():
    return RedirectResponse(f".{config.DOCS_URL}")
