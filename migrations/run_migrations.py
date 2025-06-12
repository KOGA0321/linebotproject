import sqlite3, glob, os

# データベースの場所
BASE = os.path.dirname(os.path.dirname(__file__))
db = os.path.join(BASE, "chatlog.db")

conn = sqlite3.connect(db)
cur  = conn.cursor()

# migrationsフォルダ内の .sql を番号順に取得
for path in sorted(glob.glob(os.path.join(BASE, "migrations", "*.sql"))):
    sql = open(path, "r", encoding="utf-8").read()
    try:
        cur.executescript(sql)
        print(f"Applied {os.path.basename(path)}")
    except sqlite3.OperationalError:
        # すでに適用済みなら飛ばす
        print(f"Skipped {os.path.basename(path)}")

conn.commit()
conn.close()
print("Migrations done.")

