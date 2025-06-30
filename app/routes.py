
# app/routes.py

import os
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

        # link corresponding rich menu
        if plan == "personal":
            rm_id = create_personal_rich_menu()
        else:
            rm_id = create_plus_rich_menu()
        line_bot_api.link_rich_menu_to_user(user_id, rm_id)

    return "", 200


def create_personal_rich_menu():
    """Create and upload image for Personal plan rich menu."""
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

    # upload image from app/static
    img_path = os.path.join(os.path.dirname(__file__), "static", "Personal_plan.png")
    with open(img_path, "rb") as f:
        data = f.read()
    try:
        line_bot_api.set_rich_menu_image(rm_id, "image/png", data)
    except requests.exceptions.JSONDecodeError:
        pass

    return rm_id


def create_plus_rich_menu():
    """Create and upload image for Plus plan rich menu."""
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

    img_path = os.path.join(os.path.dirname(__file__), "static", "Plus_plan.png")
    with open(img_path, "rb") as f:
        data = f.read()
    try:
        line_bot_api.set_rich_menu_image(rm_id, "image/png", data)
    except requests.exceptions.JSONDecodeError:
        pass

    return rm_id