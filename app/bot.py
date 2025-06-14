# app/bot.py

import os
from dotenv import load_dotenv
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhook    import WebhookHandler

load_dotenv()

# LINE API
configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client    = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# WebhookHandler
handler = WebhookHandler(channel_secret=os.getenv("CHANNEL_SECRET"))

