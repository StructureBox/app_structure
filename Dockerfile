# 使用するベースイメージ
FROM python:3.11.3

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt ./

# 依存関係のインストール
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# アプリケーションのソースコードをコピー
COPY ./app ./
COPY ./app/start.sh ./start.sh

# 非rootユーザーを作成,ファイルの所有権を変更,スクリプトに実行権限を付与
RUN useradd -m myuser && \
    chown -R myuser:myuser /app && \
    chmod +x start.sh

# 非rootユーザーに切り替え
USER myuser

# アプリケーションの起動コマンド
CMD ["./start.sh"]
