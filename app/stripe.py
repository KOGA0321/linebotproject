# app/stripe.py
import os, stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# プラン名→Stripe Price ID のマッピング
PRICE_IDS = {
  "personal": "price_1RdgPx4gUt3SUpO2bjaAZv3c",
  "plus":     "price_DEF456",
  "premium":  "price_GHI789",
}

def create_checkout_session(user_id: str, plan: str):
    # 既存の customer を探す／なければ作成
    # ここでは毎回新規に customer.create していますが、
    # 実運用では members.stripe_customer_id を参照すると◎
    customer = stripe.Customer.create(metadata={"user_id": user_id})
    session  = stripe.checkout.Session.create(
        customer=customer.id,
        mode="subscription",
        line_items=[{"price": PRICE_IDS[plan], "quantity": 1}],
        success_url=os.getenv("DOMAIN_URL") + "/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url =os.getenv("DOMAIN_URL") + "/cancel",
    )
    print("[DEBUG] Stripe session.url:", session.url)

    return session
