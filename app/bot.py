# app/bot.py

import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhook import WebhookHandler

load_dotenv()

# LINE API
configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client    = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# WebhookHandler
handler = WebhookHandler(channel_secret=os.getenv("CHANNEL_SECRET"))

def send_reply(reply_token: str, text: str):
    """
    v3 SDK で LINE にテキストを返信する
    """
    # ReplyMessageRequest を作成
    req = ReplyMessageRequest(
        reply_token=reply_token,
        messages=[ TextMessage(type="text", text=text) ]
    )
    try:
        # 実際に返信を送信
        messaging_api.reply_message(req)
        #print(f"[send_reply] success: {text!r}")
    except Exception as e:
        # エラーがあればログに出力
        print(f"[send_reply] failed: {e}")
