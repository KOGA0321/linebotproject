# daily_reminder.py


import sqlite3
import sqlite3
from dotenv import load_dotenv
import os

# daily_reminder.py の一番上に追加
import datetime, os

from app.db import get_paid_user_ids

# ログファイル（フルパス推奨）
heartbeat = "/Users/kogaabe/Desktop/linebotproject/heartbeat.log"
with open(heartbeat, "a") as f:
    f.write(f"{datetime.datetime.now().isoformat()} cron start\n")

# --- 以下、既存のコード ---


# LINE SDK v3 のインポート
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

# ──────────────
# ① 環境変数の読み込み
# ──────────────
load_dotenv()  # .env に CHANNEL_ACCESS_TOKEN, OPENAI_API_KEY などがある

# LINE Messaging API 初期化
configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# ──────────────
# ② SQLite から「有料会員(user_id)」を取得する関数
# ──────────────
def get_paid_user_ids():
    conn = sqlite3.connect("chatlog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM members WHERE is_paid = 1")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# ──────────────
# ③ 毎日 9:00 に送信するメイン処理
# ──────────────
def send_daily_reminder():
    # 有料会員の user_id 一覧を取得
    paid_ids = get_paid_user_ids()

    # もし有料会員が0人なら何もしない
    if not paid_ids:
        return

    # 送信したい固定メッセージ
    reminder_text = "🌙 今日はどんな1日だった？よかったら教えてね😊"

    for user_id in paid_ids:
        try:
            messaging_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=reminder_text)]
                )
            )
        except Exception as e:
            # 万が一送信エラーがあればログに出力
            print(f"LINE送信エラー（{user_id}）: {e}")

if __name__ == "__main__":
    send_daily_reminder()
