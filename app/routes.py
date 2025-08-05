
# app/routes.py

import os,pathlib
import traceback
import stripe
import requests

from flask import Blueprint, request, jsonify, abort

from linebot import LineBotApi
from linebot.models import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
)

from app.bot    import handler
from app.stripe import create_checkout_session
from app.db     import add_stripe_customer_id, set_user_plan
from app.utils  import plan_from_price
from config import BaseConfig


stripe.api_key = BaseConfig.STRIPE_SECRET_KEY

bp = Blueprint("webhook", __name__)

# LINE v2 SDK client for rich menu management
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))


@bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body      = request.get_data(as_text=True)

    print(f"[Webhook] body:      {body}")
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

        # save to DB
        set_user_plan(user_id, sub_id, plan)

       
           # プランに関わらず共通メニューを作成
    rm_id = create_main_rich_menu()

    return "", 200


def create_main_rich_menu():
    """Create and upload the 3-split CareFriend rich menu."""


    img_path = os.path.join(
        os.path.dirname(__file__),
        "static",
        "richmenu_carefriend_3split.jpg"
    )

    rm = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="CareFriendメニュー",
        chat_bar_text="メニューを開く",
        areas=[
            # Personalプラン
            RichMenuArea(
                bounds=RichMenuBounds(x=0,    y=0, width=833, height=1686),
                action=URIAction(
                    label="Personalプラン",
                    uri=os.getenv("DOMAIN_PERSONAL")
                    )
            ),
            # Plusプラン
            RichMenuArea(
                bounds=RichMenuBounds(x=833,  y=0, width=834, height=1686),
                action=URIAction(
                    label="Plusプラン",
                    uri=os.getenv("DOMAIN_PLUS")
                )
            ),
            # ホームページ
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=1686),
                action=URIAction(
                    label="ホームページ",
                    uri=os.getenv("DOMAIN_URL")  # 必要に応じて変更
                )
            ),
        ]
    )

    rm_id = line_bot_api.create_rich_menu(rm)
    with open(img_path, "rb") as f:
        line_bot_api.set_rich_menu_image(rm_id, "image/jpeg", f.read())
    return rm_id

    