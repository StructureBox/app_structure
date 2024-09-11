import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException  # 追加
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from config import config


# クライアントのリクエスト回数とタイムスタンプを保存するための辞書
request_counts = {}
RATE_LIMIT = 10  # 許可する最大リクエスト数
TIME_FRAME = 60  # リセットされる時間枠（秒）


# レートリミットミドルウェア
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # クライアントのIPアドレスを取得
        client_ip = request.client.host

        # 現在のタイムスタンプ
        current_time = time.time()

        if client_ip not in request_counts:
            # IPアドレスが初めての場合、初期化
            request_counts[client_ip] = []

        # タイムフレーム外の古いリクエストを削除
        request_counts[client_ip] = [
            timestamp for timestamp in request_counts[client_ip] if current_time - timestamp < TIME_FRAME
        ]

        # リクエスト回数が制限を超えているか確認
        if len(request_counts[client_ip]) >= RATE_LIMIT:
            # 制限を超えた場合のレスポンス
            return JSONResponse(
                status_code=429,  # 429 Too Many Requests
                content={"detail": "リクエスト回数の制限を超えました。時間をおいて再度お試しください。"},
            )

        # リクエストを記録
        request_counts[client_ip].append(current_time)

        # 通常のリクエスト処理
        response = await call_next(request)
        return response


# CORSを適用するエンドポイントリスト
cors_endpoints = [
    "/general",
    "/excel",
    "/steel",
    "/rc",
]


class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # リクエストURLのパスを取得
        request_path = request.url.path

        # エンドポイントがcors_endpointsリストに含まれているか確認
        if any(endpoint in request_path for endpoint in cors_endpoints):
            origin = request.headers.get("origin")
            # オリジンが許可されたリストに含まれているか確認
            if origin in config.ALLOWED_ORIGINS:
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS, PATCH, POST"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type"
                response.headers["Access-Control-Allow-Credentials"] = "true"  # 認証情報の送信を許可
                response.headers["Access-Control-Max-Age"] = "600"  # プリフライトリクエストのキャッシュ期間
                return response
            else:
                # 許可されていないオリジンに対してはCORSエラーを返す
                return JSONResponse(
                    status_code=403,  # Forbidden
                    content={"detail": "CORSエラー: オリジンが許可されていません。"},
                )
        # CORSが適用されない場合は通常のレスポンスを返す
        return await call_next(request)


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
