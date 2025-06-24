import sqlite3
import os

# 環境変数を使うなら…
# DB_PATH = os.getenv("DATABASE_URL", "/Users/kogaabe/Desktop/linebotproject3/app.db")
# 直書きしたいなら： 
DB_PATH = "/Users/kogaabe/Desktop/linebotproject3/app.db"

def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) logs テーブルを作成（なければ）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            user_message TEXT,
            ai_reply TEXT,
            summary TEXT
        );
    """)

    # 2) logs テーブルに emotion カラムを追加（なければ）
    cur.execute("PRAGMA table_info(logs);")
    columns = [row[1] for row in cur.fetchall()]
    if "emotion" not in columns:
        cur.execute("""
            ALTER TABLE logs
              ADD COLUMN emotion TEXT DEFAULT '';
        """)
        print("🔧 Added column: emotion")
    else:
        print("ℹ️ Column 'emotion' already exists, skipping")

    # 3) plans テーブルを作成（なければ）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan          TEXT    PRIMARY KEY,
            daily_limit   INTEGER,      -- NULL = 日次無制限
            monthly_limit INTEGER,      -- NULL = 月次無制限
            overage_fee   INTEGER       -- 超過課金（円/通）
        );
    """)
    print("✔️ Ensured table: plans")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migrations()
