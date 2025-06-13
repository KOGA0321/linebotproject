# cron/weekly_summary.py

import os
from datetime import datetime, timedelta
from collections import Counter

from app.db import fetch_logs, get_all_paid_users
from app.bot import push_message


def get_last_week_logs(user_id):
    """
    指定したユーザーの過去7日間のログを取得する
    Logs は dict 形式で、少なくとも 'emotion' キーを持つものとする
    """
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    return fetch_logs(user_id, start_date=week_ago, end_date=today)


def count_emotions(logs):
    """
    ログから感情ラベルをカウントして Counter を返す
    """
    emotions = [log.get("emotion") for log in logs if log.get("emotion")]
    return Counter(emotions)


def build_summary_message(counter: Counter) -> str:
    """
    カウンターから週次要約メッセージを生成する
    ポジティブ・ネガティブを集計し、上位のラベルも列挙
    """
    POSITIVE = {"楽しい", "幸せ", "感謝", "安堵"}
    NEGATIVE = {"死にたい", "つらい", "不安", "寂しい", "疲れ", "怒り", "ストレス"}

    total_pos = sum(counter.get(emo, 0) for emo in POSITIVE)
    total_neg = sum(counter.get(emo, 0) for emo in NEGATIVE)

    lines = ["今週の感情傾向："]
    # ポジティブ／ネガティブの合計を先に表示
    lines.append(f"・ポジティブ: {total_pos}回, ネガティブ: {total_neg}回")

    # 個別ラベルの頻度を上位順に表示
    for emo, cnt in counter.most_common():
        lines.append(f"・{emo}: {cnt}回")

    return "\n".join(lines)


def send_weekly_summary(user_id: str):
    """
    一人のユーザーに対して週次要約を生成しLINEで送信する
    """
    logs = get_last_week_logs(user_id)
    counter = count_emotions(logs)
    message = build_summary_message(counter)
    push_message(user_id, message)


if __name__ == "__main__":
    # 有料ユーザー全員に週次要約を送信
    for user_id in get_all_paid_users():
        send_weekly_summary(user_id)

