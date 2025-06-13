# daily_reminder.py


# cron/daily_reminder.py

import os
from datetime import datetime
from dotenv import load_dotenv

from app.db import get_paid_user_ids
from app.bot import push_message

load_dotenv()

def build_reminder_text():
    today_str = datetime.now().strftime("%Y年%m月%d日")
    return (
        f"こんばんは！\n"
        f"{today_str} はどんな一日でしたか？\n"
        "良かったことや大変だったことがあれば、ぜひ教えてください😊"
    )

def send_daily_reminder():
    paid_ids = get_paid_user_ids()
    text = build_reminder_text()
    for user_id in paid_ids:
        try:
            push_message(user_id, text)
        except Exception as e:
            print(f"送信エラー ({user_id}): {e}")

if __name__ == "__main__":
    send_daily_reminder()
