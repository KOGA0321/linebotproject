# app/utils.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env から API キーをロード
load_dotenv()

# OpenAI クライアントを生成
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
