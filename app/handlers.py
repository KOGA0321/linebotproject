
# app/handlers.py

import os
from datetime import datetime
from openai import OpenAI
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks               import MessageEvent
from dotenv import load_dotenv
from flask import current_app

# app/handlers.py の先頭近くに追記
from app.db import is_paid_user, save_log_to_sqlite
from app.utils import client  # OpenAI クライアントを作っているならここから


from app.emotion import classify_emotion_by_ai

from app.bot import messaging_api, handler

from app.db      import (
    fetch_last_n_logs,
    fetch_latest_weekly_report,
    save_log_to_sqlite,
    is_paid_user,
)
from app.bot     import messaging_api, handler

# .env を読み込んで環境変数をセット
load_dotenv()

# OpenAI クライアント
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



@handler.add(MessageEvent)
def handle_message(event: MessageEvent):
    # 1) ユーザー情報取得 & デバッグログ
    user_text   = event.message.text
    user_id     = event.source.user_id
    reply_token = event.reply_token

    log = current_app.logger

    # デバッグログを出力
    log.debug(f"handle_message called: user_id={user_id}, user_text={user_text}")
    log.debug(f"reply_token: {reply_token!r} (len={len(reply_token)})")


    # 2) コンテキスト組み立て
    context_messages = []
    latest = fetch_latest_weekly_report(user_id)
    if latest:
        context_messages.append({
            "role": "system",
            "content": "（以下は今週の週報です）\n" + latest
        })
    for u, a, emotion in fetch_last_n_logs(user_id, n=5):
        context_messages.append({"role":"user",      "content":u})
        context_messages.append({"role":"assistant", "content":a})
    context_messages.append({"role":"user", "content":user_text})

    # 3) モデル選択＆GPT呼び出し
    is_paid = is_paid_user(user_id)
    model   = "gpt-4o" if is_paid else "gpt-3.5-turbo"

    

    response = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":"あなたは共感力に優れたメンタルケアAIです。相手の気持ちに寄り添い、優しく親身になって相談にのってください。堅苦しい敬語は控えて、友達のようなフラットな口調で話しましょう。短く簡潔に返答し、一方的に解決策を押し付けるのではなく、一緒に原因を探るようにやりとりしてください。相手の発言に感情的なワードが含まれていれば、それに合わせた対応を心がけてください。"}]
                 + context_messages
    )
    reply_text = response.choices[0].message.content.strip()
    print(f"[DEBUG] reply_text: {reply_text!r} (len={len(reply_text)})")
    if not reply_text.strip():
        print("[WARN] reply_text empty, substituting fallback")
        reply_text = "すみません、メッセージの生成に失敗しました。"
    

    emotion = classify_emotion_by_ai(user_text)
    
    # 4) 要約生成＆DB保存
    summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"次の会話を一文で要約してください。"},
            {"role":"user","content":f"ユーザー:{user_text}\nAI:{reply_text}"}
        ]
    ).choices[0].message.content.strip()
    save_log_to_sqlite(user_id, user_text, reply_text,emotion, summary)

    # 5) LINE へ一度だけ返信
    log.debug("sending reply to LINE…")
    try:
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        log.debug(f"reply sent successfully to {user_id}")
    except Exception as e:
        log.error(f"failed to send reply: {e}")
        raise

