# app/utils.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env から API キーをロード
load_dotenv()

# OpenAI クライアントを生成
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
# app/utils.py

def plan_from_price(price_id):
    """
    Stripe の Price ID (price_xxx…) から
    アプリ内で使うプラン名を返す関数。

    price_id: Stripe ダッシュボードで発行された price_ で始まる ID
    返り値: 'free' / 'personal' / 'plus' など
    """
    mapping = {
        'price_1RdgPx4gUt3SUpO2bjaAZv3c': 'personal',  # Personal プラン用の Price ID
        'price_1Re2434gUt3SUpO2heY7gl1b': 'plus',      # Plus プラン用の Price ID
    }
    return mapping.get(price_id, 'free')
