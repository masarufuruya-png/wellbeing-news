import os
import json
import datetime
import urllib.request

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    today = datetime.date.today().strftime("%Y-%m-%d")

    prompt = f"""
    今日は {today} です。
    株式会社アワーズ（アドベンチャーワールド運営）の社員・キャスト向けの社内プラットフォーム『CWO Well-being Morning News』に掲載する最新記事を3本作成してください。

    【出力形式】必ず以下のJSON形式のみを出力してください（マークダウンの```などは不要）。
    {{
      "date": "{today}",
      "articles": [
        {{
          "perma": "P, E, R, M, A のいずれか1文字",
          "category": "例: マインドフルネス/フロー",
          "target": "一般社員・キャスト / Well-being lab / アワーズ動物学院 のいずれか",
          "title": "記事のタイトル",
          "summary": ["要約1", "要約2", "要約3"],
          "aw_value": "アドベンチャーワールド・アワーズの現場やAWS-WAYにどう活かせるかの解説",
          "source_jp": "日本語の参考文献・書籍名",
          "source_en": "英語の原著論文名と著者・発表年",
          "source_url": "論文や関連情報の検索URL",
          "question": "今日の問いかけ"
        }}
      ]
    }}

    【条件】
    - 心理学・ポジティブ心理学の実在する学術研究をベースにすること。
    - 3本の記事はPERMA分類とターゲットをバランスよく分けること。
    - 「AW/アワーズ文脈の価値」ではパーク運営・動物飼育・AWS-WAY・Smile創造に絡めること。
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=120) as res:
        result = json.loads(res.read().decode("utf-8"))
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
