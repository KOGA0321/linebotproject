import sqlite3
import os

# 環境変数を使うなら…
# DB_PATH = os.getenv("DATABASE_URL", "/Users/kogaabe/Desktop/linebotproject3/app.db")
# 直書きしたいなら： 
DB_PATH = "/Users/kogaabe/Desktop/linebotproject3/app.db"

def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) logs テーブルがなければ作成
    cur.execute("""
        SELECT name FROM sqlite_master
         WHERE type='table' AND name='logs';
    """)
    if not cur.fetchone():
        # テーブルが存在しない → 新規作成
        cur.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            user_message TEXT,
            ai_reply TEXT,
            summary TEXT
        );
        """)
        print("✔️ Created table: logs")

    # 2) logs テーブルに emotion カラムがなければ追加
    cur.execute("PRAGMA table_info(logs);")
    columns = [row[1] for row in cur.fetchall()]
    if "emotion" not in columns:
        cur.execute("""
            ALTER TABLE logs
            ADD COLUMN emotion TEXT DEFAULT '';
        """)
        print("🔧 Added column: emotion")
    else:
        print(" Column 'emotion' already exists, skipping")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migrations()



