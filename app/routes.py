
# app/routes.py
from flask import Blueprint, request, abort
import traceback             # 追加
from app.bot import handler

bp = Blueprint("webhook", __name__)

@bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body      = request.get_data(as_text=True)

    # デバッグ用ログ
    print(f"[Webhook] body: {body}")
    print(f"[Webhook] signature: {signature}")

    try:
        handler.handle(body, signature)
    except Exception:
        # 例外の内容をすべて出力
        print("------ Webhook Error ------")
        traceback.print_exc()
        print("-----------------------------")
        abort(400)

    return "OK"



