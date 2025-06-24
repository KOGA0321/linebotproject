# app/plans.py
"""
プランごとの利用制限と超過課金設定を管理するモジュール
"""

# プラン定義
PLANS = {
    "free": {
        "daily_limit": 10,      # 1日あたり10通まで
        "monthly_limit": 150,   # 1か月あたり150通まで
        "overage_fee": 5        # 超過時：5円/通
    },
    "personal": {
        "daily_limit": None,    # 日次無制限
        "monthly_limit": 300,
        "overage_fee": 2
    },
    "plus": {
        "daily_limit": None,
        "monthly_limit": 1000,
        "overage_fee": 0        # 超過なし
    },
    "premium": {
        "daily_limit": None,
        "monthly_limit": None,
        "overage_fee": 0        # 完全無制限
    }
}