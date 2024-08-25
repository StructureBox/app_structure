# 使用するベースイメージ
FROM python:3.11.3

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt ./
COPY ./app /app
COPY ./app/start.sh /app/start.sh


# 依存関係のインストール
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 非rootユーザーを作成
RUN useradd -m myuser

# ファイルの所有権を変更
RUN chown -R myuser:myuser /app

# スクリプトに実行権限を付与
RUN chmod +x start.sh

# 非rootユーザーに切り替え
USER myuser

# アプリケーションの起動コマンド
CMD ["./app/start.sh"]
