from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException  # 追加
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

# CORSを適用するエンドポイントリスト
cors_endpoints = [
    "/general",
    "/excel",
    "/steel",
    "/rc",
]


# CORSミドルウェア
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for endpoint in cors_endpoints:
            if endpoint in request.url.path:
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type"
                break
        return response


# エラーハンドリングミドルウェア
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as ve:
            # バリデーションエラー (入力エラー)
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "入力データが無効です。正しい形式で入力してください。",
                    "errors": ve.errors(),
                },
            )
        except HTTPException as he:
            # HTTPエラー (例えば404 Not Found)
            if he.status_code == HTTP_404_NOT_FOUND:
                return JSONResponse(
                    status_code=HTTP_404_NOT_FOUND,
                    content={"detail": "指定されたリソースが見つかりませんでした。"},
                )
            else:
                return JSONResponse(
                    status_code=he.status_code,
                    content={"detail": "HTTPエラーが発生しました。"},
                )
        except Exception as e:
            # その他のエラー (サーバーエラーなど)
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "内部サーバーエラーが発生しました。後でもう一度お試しください。",
                    "error": str(e),
                },
            )
