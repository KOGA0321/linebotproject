# main.py

import os
from app import create_app

app = create_app()


# main.py など、Flaskアプリの起動ファイル

from flask import Flask, request, abort
import traceback
from linebot import WebhookHandler

app = Flask(__name__)
handler = WebhookHandler( os.getenv("LINE_CHANNEL_SECRET") )

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    print(f"Request body: {body}")            # 受け取ったペイロードを出力
    print(f"Signature header: {signature}")   # 署名ヘッダを出力
    try:
        handler.handle(body, signature)
    except Exception as e:
        # ここで例外情報をすべて出力する
        print("------ Webhook Error ------")
        traceback.print_exc()
        print("-----------------------------")
        abort(400)
    return "OK"




if __name__ == "__main__":
    # PORT は環境変数から取るかデフォルト5000
    port = int(os.getenv("PORT", 5000))
    # 0.0.0.0 でバインドすると外部からもアクセス可
    app.run(host="0.0.0.0", port=port)


