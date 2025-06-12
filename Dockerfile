FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係を先にコピーしてインストール（キャッシュを効かせる）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 環境変数のデフォルト値
ENV FLASK_ENV=production
ENV PORT=5000

# ポート公開
EXPOSE 5000

# コンテナ起動時に実行するコマンド
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
