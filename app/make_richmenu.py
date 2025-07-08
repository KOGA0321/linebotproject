"""
make_richmenu.py
----------------
1. Personal 用リッチメニューを作成
2. PNG をアップロード
3. 全ユーザーのデフォルトメニューに設定
"""

import os
import time
from dotenv import load_dotenv

# .env を読み込む  (.env が不要ならこの2行は消してOK)
load_dotenv()                   

from linebot import LineBotApi
from linebot.models import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
)

# ----------------------------------------
# ① LINE クライアント初期化
# ----------------------------------------
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
if not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError("環境変数 CHANNEL_ACCESS_TOKEN が設定されていません。")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ----------------------------------------
# ② リッチメニュー定義
# ----------------------------------------
def create_personal_rich_menu():
    rm = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Personalメニュー",
        chat_bar_text="Personalプラン",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=2500, height=1686),
                action=URIAction(
                    label="Personal購入",
                    uri=f"https://{os.getenv('DOMAIN')}/create-checkout/personal"
                )
            )
        ]
    )

    # ③ メニュー本体を作成
    rm_id = line_bot_api.create_rich_menu(rm)
    print("リッチメニュー作成:", rm_id)

    # ④ PNG をアップロード
    img_path = os.path.join(
        os.path.dirname(__file__),      # …/linebotproject3
         "static", "Personal_plan_stretched.jpg"
    )
    print("画像パス:", img_path)
    with open(img_path, "rb") as f:
        line_bot_api.set_rich_menu_image(rm_id, "image/png", f.read())
    print("画像アップ完了")

    return rm_id


if __name__ == "__main__":
    # ----------------------------------------
    # ⑤ 作成 + 適用
    # ----------------------------------------
    richmenu_id = create_personal_rich_menu()

    # 非同期反映に 2〜3 秒ほど待つ
    time.sleep(3)

    # ⑥ 全ユーザーのデフォルトに設定
    line_bot_api.set_default_rich_menu(richmenu_id)
    print("デフォルトメニューに設定しました！")
