
# app/routes.py
from flask import Blueprint, request, abort
import app.handlers        # ← これが必須：handlers モジュールを読み込んでデコレータを登録
from app.bot import handler

bp = Blueprint("webhook", __name__)

@bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body      = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"


