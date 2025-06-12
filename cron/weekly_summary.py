# weekly_summary.py



from datetime import datetime, timedelta
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
import sqlite3

from app.db import get_paid_user_ids, fetch_latest_weekly_report


# 「chatlog.db」に接続
conn = sqlite3.connect("chatlog.db", check_same_thread=False)
cursor = conn.cursor()

# すでに logs, members テーブルがある想定なので省略…
# ── 週報保存用テーブルを作成 ──
cursor.execute("""
CREATE TABLE IF NOT EXISTS weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    sent_at TEXT,
    weekly_report TEXT
)
""")
conn.commit()

# ──────────────
# ① 環境変数の読み込み
# ──────────────
load_dotenv()  # .env に CHANNEL_ACCESS_TOKEN, OPENAI_API_KEY などがある

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

# ──────────────
# ② 有料会員 ID を SQLite から取得する関数
# ──────────────
def get_paid_user_ids():
    conn = sqlite3.connect("chatlog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM members WHERE is_paid = 1")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# ──────────────
# ③ 週報送信用メイン処理
# ──────────────
def send_weekly_reports():
    log_dir = "logs"
    one_week_ago = datetime.now() - timedelta(days=7)

    # 事前に「感情キーワード」を定義
    emotional_keywords = {
        "悲しみ": ["悲しい", "つらい", "寂しい"],
        "不安": ["不安", "心配", "焦り"],
        "怒り": ["怒り", "むかつく", "腹が立つ"],
        "喜び": ["嬉しい", "楽しい", "幸せ"],
        "疲れ": ["疲れ", "しんどい", "だるい"],
        "驚き": ["驚き", "びっくり", "まさか"],
    }

    for user_id in get_paid_user_ids():
        log_file = os.path.join(log_dir, f"user_{user_id}.csv")
        if not os.path.exists(log_file):
            continue

        df = pd.read_csv(log_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        last_week_logs = df[df["timestamp"] > one_week_ago]
        if last_week_logs.empty:
            continue

        # ────────────
        # (1) 会話要約を作成
        # ────────────
        conversation = ""
        for _, row in last_week_logs.iterrows():
            conversation += f"ユーザー: {row['user_message']}\nAI: {row['ai_reply']}\n"

        try:
            summary_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "以下の会話を読んで、今週の状況をやさしく短くまとめてください。"
                                "あまりAIみたくならないように敬語はあまり使わないようにして友達に話すような文でまとめてください"
                            
                    },
                    {"role": "user", "content": conversation}
                ]
            )
            summary_text = summary_response.choices[0].message.content.strip()
        except Exception:
            summary_text = "今週のまとめ作成中にエラーが発生しました。"

        # ────────────
        # (2) 1週間の感情キーワード集計（ユーザー発言ベース）
        # ────────────
        # カウンター初期化
        emotion_counter = {label: 0 for label in emotional_keywords.keys()}

        # 各発言ごとにキーワードを検索
        for _, row in last_week_logs.iterrows():
            text = str(row["user_message"])
            for label, keywords in emotional_keywords.items():
                for kw in keywords:
                    if kw in text:
                        emotion_counter[label] += 1

        # 集計結果をテキストに整形
        # 0 のものは含めず、あるものだけ並べる
        emotion_report_parts = [
            f"{label}：{count}回"
            for label, count in emotion_counter.items()
            if count > 0
        ]
        if emotion_report_parts:
            emotion_report = "\n".join(emotion_report_parts)
        else:
            emotion_report = "今週は落ち着いた感じの１週間だったね！"

        # ────────────
        # (3) 週報メッセージ本文を組み立て
        # ────────────
        weekly_report = (
            f"🗓️ 今週のふりかえり！：\n{summary_text}\n\n"
            f"🧠 今週はどんな感情傾向だったかな？：\n{emotion_report}"
        )

        # ────────────
        # (4) LINE へプッシュ送信（PushMessageRequest を使用）
        # ────────────
        try:
            messaging_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=weekly_report)]
                )
            )
        except Exception as e:
            print(f"LINE送信エラー ({user_id}):", e)

        # データベースに保存
        sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO weekly_reports (user_id, sent_at, weekly_report)
            VALUES (?, ?, ?)
        """, (user_id, sent_at, weekly_report))
        conn.commit()



if __name__ == "__main__":
    send_weekly_reports()
