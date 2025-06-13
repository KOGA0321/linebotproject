# main.py

import os
import logging
from dotenv import load_dotenv

# ① .env を読み込んで…
load_dotenv()
# ② ログレベルをDEBUGにセット
logging.basicConfig(level=logging.DEBUG)

# ③ Flaskアプリ作成＆ハンドラ登録（import handlers が decorator を動かす）
from app import create_app
import app.handlers

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



