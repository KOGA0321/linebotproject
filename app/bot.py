
# app/bot.py

import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import WebhookHandler

load_dotenv()

# — v3 SDK の初期化 —
configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client    = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# Webhook の検証・パースを担うハンドラー
handler = WebhookHandler(channel_secret=os.getenv("CHANNEL_SECRET"))

# 1日あたりメッセージ上限（必要に応じて参照）
PLAN_LIMITS = {
    "free":    10,    # 1日あたり10回
    "basic":   30,
    "plus":    100,
    "premium": None,  # Noneなら無制限扱い
}

def send_reply(reply_token: str, text: str):
    """
    v3 SDK を使ってLINEにテキストを返信するユーティリティ関数。
    handler.add(...) 内などで呼び出してください。
    """
    req = ReplyMessageRequest(
        reply_token=reply_token,
        messages=[TextMessage(type="text", text=text)]
    )
    try:
        messaging_api.reply_message(req)
    except Exception as e:
        print(f"[send_reply] failed: {e}")
