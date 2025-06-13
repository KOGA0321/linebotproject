# app/emotion.py

from app.utils import client

def classify_emotion_by_ai(text: str) -> str:
    prompt = (
        "次の文章の感情を1つだけ選んでください。\n"
        "選択肢：悲しい、楽しい、怒り、不安、幸せ、寂しい、疲れ、ストレス、安堵、感謝、その他\n\n"
        f"文章:「{text}」\n"
        "感情:"
    )
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1,
        temperature=0
    )
    return res.choices[0].message.content.strip()
