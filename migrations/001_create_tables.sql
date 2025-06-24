-- まず最初に必要なテーブルを作る
CREATE TABLE IF NOT EXISTS members (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT UNIQUE,
  plan    TEXT DEFAULT'free',
  is_paid INTEGER DEFAULT 0,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS logs (...);
CREATE TABLE IF NOT EXISTS weekly_reports (...);
