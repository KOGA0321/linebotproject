# app/db.py

import sqlite3
from datetime import datetime
from app.plans import PLAN_LIMITS
from functools import lru_cache
# DB ファイルパス（環境変数でも定義可能）
DB_PATH = "chatlog.db"

conn   = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# テーブル作成: logs に emotion カラムを追加
cursor.executescript("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    timestamp TEXT,
    user_message TEXT,
    ai_reply TEXT,
    summary TEXT,
    emotion TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    is_paid INTEGER DEFAULT 0,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    sent_at TEXT,
    weekly_report TEXT
);
CREATE TABLE IF NOT EXISTS usage_limit (
    user_id    TEXT,
    date       TEXT,      -- 'YYYY-MM-DD'
    call_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, date)
""")
conn.commit()

# 関数定義

@lru_cache(maxsize=None)
def load_plans() -> dict:
    cursor.execute("SELECT plan, daily_limit, monthly_limit, overage_fee FROM plans")
    return {
        plan: {"daily_limit": dlim, "monthly_limit": mlim, "overage_fee": fee}
        for plan, dlim, mlim, fee in cursor.fetchall()
    }

def get_plan_config(user_id: str) -> dict:
    cursor.execute("SELECT plan FROM members WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    plan = row[0] if row else "free"
    return load_plans().get(plan, load_plans()["free"])

def is_within_limit(user_id: str) -> bool:
    cfg   = get_plan_config(user_id)
    today = datetime.today().isoformat()
    month = today[:7]  # 'YYYY-MM'

    # 日次チェック
    dlim = cfg["daily_limit"]
    if dlim is not None:
        cursor.execute(
          "SELECT call_count FROM usage_limit WHERE user_id=? AND date=?",
          (user_id, today))
        row = cursor.fetchone()
        if row and row[0] >= dlim:
            return False

    # 月次チェック
    mlim = cfg["monthly_limit"]
    if mlim is not None:
        cursor.execute(
          "SELECT call_count FROM monthly_usage WHERE user_id=? AND month=?",
          (user_id, month))
        rowm = cursor.fetchone()
        if rowm and rowm[0] >= mlim:
            return False

    return True

def increment_usage(user_id: str):
    # 日次カウント
    today = datetime.today().isoformat()
    cursor.execute("""
      INSERT INTO usage_limit (user_id, date, call_count)
        VALUES (?, ?, 1)
      ON CONFLICT(user_id, date) DO UPDATE
        SET call_count = call_count + 1
    """, (user_id, today))

    # 月次カウント
    month = today[:7]
    cursor.execute("""
      INSERT INTO monthly_usage (user_id, month, call_count)
        VALUES (?, ?, 1)
      ON CONFLICT(user_id, month) DO UPDATE
        SET call_count = call_count + 1
    """, (user_id, month))

    conn.commit()


def fetch_last_n_logs(user_id: str, n=5):
    cursor.execute(
        "SELECT user_message, ai_reply, emotion FROM logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, n)
    )
    rows = cursor.fetchall()
    # 最新順取得後、結果を逆順にして古い順へ
    return [(r[0], r[1], r[2]) for r in reversed(rows)]


def fetch_latest_weekly_report(user_id: str) -> str:
    cursor.execute(
        "SELECT weekly_report FROM weekly_reports WHERE user_id = ? ORDER BY sent_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else ""


def save_log_to_sqlite(user_id, user_text, ai_reply, summary_text, emotion):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO logs (user_id, timestamp, user_message, ai_reply, summary, emotion) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, ts, user_text, ai_reply, summary_text, emotion)
    )
    conn.commit()

def get_user_plan(user_id: str) -> str:
    cursor.execute(
        "SELECT plan FROM members WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else "free"

def is_within_limit(user_id: str) -> bool:
    # 1) ユーザーのプランを取得
    plan  = get_user_plan(user_id)
    # 2) プランごとの上限を得る
    limit = PLAN_LIMITS.get(plan)

    # 3) 無制限プランならOK
    if limit is None:
        return True

    # 4) 日次利用回数のチェック
    today = datetime.today().isoformat()
    cursor.execute(
        "SELECT call_count FROM usage_limit WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    row = cursor.fetchone()
    # まだ記録がなければ True、あれば < limit かどうか
    return (row is None) or (row[0] < limit)

def increment_usage(user_id: str):
    today = datetime.today().isoformat()
    cursor.execute("""
        INSERT INTO usage_limit (user_id, date, call_count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, date) DO UPDATE SET call_count = call_count + 1
    """, (user_id, today))
    conn.commit()


def is_paid_user(user_id: str) -> bool:
    cursor.execute(
        "SELECT is_paid FROM members WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    return bool(row and row[0] == 1)


def add_paid_user(user_id: str):
    cursor.execute(
        "INSERT OR IGNORE INTO members (user_id, is_paid, created_at) VALUES (?, 1, datetime('now'))",
        (user_id,)
    )
    conn.commit()


def remove_paid_user(user_id: str):
    cursor.execute(
        "UPDATE members SET is_paid = 0 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()


def get_paid_user_ids():
    cursor.execute(
        "SELECT user_id FROM members WHERE is_paid = 1"
    )
    return [r[0] for r in cursor.fetchall()]

