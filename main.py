# main.py

import os
import logging
from dotenv import load_dotenv

# ① .env を読み込んで…
load_dotenv()




# ② ルートロガーは INFO 以上だけ出す
logging.basicConfig(level=logging.INFO)

# ③ 自分の app モジュールだけ DEBUG を出す
#logging.getLogger("app").setLevel(logging.DEBUG)

# ④ 外部ライブラリは WARNING 以上だけ出す
#logging.getLogger("openai").setLevel(logging.WARNING)
#logging.getLogger("httpcore").setLevel(logging.WARNING)
#logging.getLogger("httpx").setLevel(logging.WARNING)


# ⑤ Flaskアプリ作成＆ハンドラ登録
from app import create_app
import app.handlers
print("[DEBUG] STRIPE_SECRET_KEY:", os.getenv("STRIPE_SECRET_KEY"))

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



