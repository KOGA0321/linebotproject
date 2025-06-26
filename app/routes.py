
# app/routes.py
from flask import Blueprint, request, abort
import traceback             # 追加
from app.bot import handler

import os
import stripe
from flask import Blueprint, request, jsonify, abort
from app.stripe import create_checkout_session
from app.db     import add_stripe_customer_id, set_user_plan
from app.utils  import plan_from_price   # もし逆引きヘルパーが別モジュールにあるなら
from app.db import add_stripe_customer_id, set_user_plan



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


#stripeのエンドポートを定義

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

    return ("", 200)

