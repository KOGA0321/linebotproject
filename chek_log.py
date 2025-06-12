import sqlite3
import pandas as pd
from app import add_paid_user
add_paid_user("U11009739723af3d83983d8c0fe82a0d3")  # 取得した自分のIDを入れる exit()



from linebot.v3.messaging.models import PushMessageRequest, TextMessage

message = TextMessage(text="こんにちは！これはPushメッセージです")
request = PushMessageRequest(
    to="U1e3a26835b887052fc8f641cd5a9436c",  # 宛先のユーザーID
    messages=[message]
)

#messaging_api.push_message(push_message_request=request)



def get_paid_user_ids():
    conn = sqlite3.connect("chatlog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM members WHERE is_paid = 1")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


from cron.weekly_summary import get_paid_user_ids  # あるいは app.py に定義を移しているなら app から
get_paid_user_ids()








# DBに接続
conn = sqlite3.connect("chatlog.db")

# pandasで読み込み
df = pd.read_sql("SELECT * FROM logs", conn)

# 表示
print(df)

conn.close()
