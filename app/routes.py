
# app/routes.py

from flask import Blueprint, request, jsonify, abort
import traceback
import os
import stripe
import requests

# ← handler は v3 SDK の WebhookHandler のままでOK
from app.bot       import handler  
from app.stripe    import create_checkout_session
from app.db        import add_stripe_customer_id, set_user_plan
from app.utils     import plan_from_price

# ─────────── v2 SDK のインポート & クライアント初期化 ───────────
from linebot import LineBotApi
from linebot.models import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
)
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
# ──────────────────────────────────────────────────────────────

bp = Blueprint("webhook", __name__)

@bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body      = request.get_data(as_text=True)

    print(f"[Webhook] body:  {body}")
    print(f"[Webhook] signature: {signature}")

    try:
        handler.handle(body, signature)
    except Exception:
        print("------ Webhook Error ------")
        traceback.print_exc()
        print("-----------------------------")
        abort(400)

    return "OK"


@bp.route("/create-checkout/<plan>", methods=["POST"])
def create_checkout(plan):
    user_id = request.json.get("user_id")
    session = create_checkout_session(user_id, plan)
    add_stripe_customer_id(user_id, session.customer)
    return jsonify({"url": session.url})


@bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload, sig = request.data, request.headers.get("Stripe-Signature")
    try:
        evt = stripe.Webhook.construct_event(
            payload, sig, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception:
        abort(400)

    if evt["type"] == "checkout.session.completed":
        sess     = evt["data"]["object"]
        user_id  = sess["metadata"]["user_id"]
        sub_id   = sess["subscription"]
        price_id = sess["display_items"][0]["price"]["id"]
        plan     = plan_from_price(price_id)
        set_user_plan(user_id, sub_id, plan)
        # プランに応じてメニューをリンク
    if plan == "personal":
        rm_id = create_personal_rich_menu()
    else:  # plus の場合
        rm_id = create_plus_rich_menu()
    # このユーザーにだけ割り当て
        line_bot_api.link_rich_menu_to_user(user_id, rm_id)

    return "", 200


def create_personal_rich_menu():
    """Personalプラン用リッチメニューを作成"""
    rm = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Personalメニュー",
        chat_bar_text="Personalプラン",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=2500, height=1686),
                action=URIAction(
                    label="Personal購入",
                    uri=f"https://{os.getenv('DOMAIN')}/create-checkout/personal"
                )
            )
        ]
    )
    rm_id = line_bot_api.create_rich_menu(rm)
    
    with open("personal_plan.png", "rb") as f:
        try:
            # 空の JSON レスポンスで例外になるが、画像はアップロード済みなので無視
            line_bot_api.set_rich_menu_image(rm_id, "image/png", f)
        except requests.exceptions.JSONDecodeError:
            pass

    return rm_id

def create_plus_rich_menu():
    """Plusプラン用リッチメニューを作成"""
    rm = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Plusメニュー",
        chat_bar_text="Plusプラン",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=2500, height=1686),
                action=URIAction(
                    label="Plus購入",
                    uri=f"https://{os.getenv('DOMAIN')}/create-checkout/plus"
                )
            )
        ]
    )
    rm_id = line_bot_api.create_rich_menu(rm)
    with open("plus_plan.png", "rb") as f:
        try:
            line_bot_api.set_rich_menu_image(rm_id, "image/png", f)
        except requests.exceptions.JSONDecodeError:
            pass
    return rm_id