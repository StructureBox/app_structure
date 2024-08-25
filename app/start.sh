#!/bin/bash

# Docker環境では.envファイルがない場合があるため、存在チェックを行う
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# デバッグ用: 環境変数の出力
echo "SUPABASE_URL is: $SUPABASE_URL"
echo "SUPABASE_KEY is: $SUPABASE_KEY"

# 開発環境でリロードを有効にする
if [ "$RELOAD" = "true" ]; then
  UVICORN_OPTS="--reload"
fi

# uvicornでアプリケーションを起動
uvicorn app:app $UVICORN_OPTS --host 0.0.0.0 --port ${PORT:-8000}
