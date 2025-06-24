import sqlite3

conn = sqlite3.connect("chatlog.db")
cur  = conn.cursor()

for name, dlim, mlim, fee in [
    ("free",    10,   150, 5),
    ("personal", None, 300, 2),
    ("plus",    None, 1000, 0),
    ("premium", None, None, 0),
]:
    cur.execute("""
      INSERT OR REPLACE INTO plans
        (plan, daily_limit, monthly_limit, overage_fee)
      VALUES (?, ?, ?, ?)
    """, (name, dlim, mlim, fee))

conn.commit()
conn.close()

