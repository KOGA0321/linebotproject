# app/db.py

import sqlite3
from datetime import datetime

conn   = sqlite3.connect("chatlog.db", check_same_thread=False)
cursor = conn.cursor()

# テーブル作成
cursor.executescript("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    timestamp TEXT,
    user_message TEXT,
    ai_reply TEXT,
    summary TEXT
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
""")
conn.commit()

# 関数定義
def fetch_last_n_logs(user_id: str, n=5):
    cursor.execute("SELECT user_message, ai_reply FROM logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, n))
    rows = cursor.fetchall()
    return [(r[0], r[1]) for r in reversed(rows)]

def fetch_latest_weekly_report(user_id: str) -> str:
    cursor.execute("SELECT weekly_report FROM weekly_reports WHERE user_id = ? ORDER BY sent_at DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else ""

def save_log_to_sqlite(user_id, user_text, ai_reply, summary_text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO logs (user_id, timestamp, user_message, ai_reply, summary) VALUES (?, ?, ?, ?, ?)",
        (user_id, ts, user_text, ai_reply, summary_text)
    )
    conn.commit()

def is_paid_user(user_id: str) -> bool:
    cursor.execute("SELECT is_paid FROM members WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return bool(row and row[0] == 1)

def add_paid_user(user_id: str):
    cursor.execute("INSERT OR IGNORE INTO members (user_id, is_paid, created_at) VALUES (?, 1, datetime('now'))", (user_id,))
    conn.commit()

def remove_paid_user(user_id: str):
    cursor.execute("UPDATE members SET is_paid = 0 WHERE user_id = ?", (user_id,))
    conn.commit()

def get_paid_user_ids():
    cursor.execute("SELECT user_id FROM members WHERE is_paid = 1")
    return [r[0] for r in cursor.fetchall()]
