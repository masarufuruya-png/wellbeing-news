import os
import json
import time
import datetime
import urllib.request

def get_available_models(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode("utf-8"))
        models = []
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods and "flash" in name and "tts" not in name and "image" not in name:
                models.append(name)
        return models

def call_gemini(api_key, model, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.85
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=90) as res:
        result = json.loads(res.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    current_year = now.year

    # 既存のnews.jsonがあれば履歴として読み込む
    history = []
    if os.path.exists("news.json"):
        try:
            with open("news.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                history = old_data.get("history", [])
                if old_data.get("articles"):
                    history.insert(0, {
                        "label": old_data.get("updated_at") or old_data.get("date") or "過去の配信",
                        "date": old_data.get("date", ""),
                        "articles": old_data["articles"][:3]
                    })
        except Exception:
            pass

    prompt = f"""
    今日は {today}（{current_year}年）です。
    株式会社アワーズ（アドベンチャーワールド運営）の社員・キャスト向けプラットフォーム『CWO Well-being Morning News』に掲載する最新記事を **必ず3本だけ** 作成してください。

    【重要ルール】
    - **記事数は必ず3本のみ**とすること。
    - **必ず {current_year - 1}年〜{current_year}年 に発表された新しい学術研究・調査レポート・トレンド**をテーマにすること（古い古典論文は使わないこと）。
    - `source_url` は、その論文タイトルやキーワードで直接検索できる確実なGoogle Scholar URL（`https://scholar.google.com/scholar?q=...`）にすること。
    - 3本の記事はPERMA分類（P, E, R, M, A）が重複しないようにバランスよく割り振ること。
    - ターゲット（`target`）は「一般社員・キャスト」「パーク運営・飼育現場」「アワーズ動物学院」のいずれかを設定すること（※過去に存在した「Well-being lab」という名称は現在実施していないため、本文・ターゲットともに一切使用しないこと）。
    - 「aw_value」では、アドベンチャーワールドのパーク運営、動物飼育、AWS-WAY、ゲストとスタッフのSmile創造にどう活かせるかを具体的に解説すること。

    【出力形式】必ず以下のJSON形式のみを出力してください。
    {{
      "date": "{today}",
      "articles": [
        {{
          "perma": "P, E, R, M, A のいずれか1文字",
          "category": "例: 最新組織心理学 / アニマルウェルフェア",
          "target": "一般社員・キャスト / パーク運営・飼育現場 / アワーズ動物学院 のいずれか",
          "title": "記事のタイトル",
          "summary": ["要約1", "要約2", "要約3"],
          "aw_value": "アドベンチャーワールド・アワーズの現場やAWS-WAYにどう活かせるかの解説",
          "source_jp": "日本語の解説・関連機関・研究テーマ名（発表年）",
          "source_en": "英語の原著論文タイトルと著者・発表年（{current_year - 1}または{current_year}）",
          "source_url": "https://scholar.google.com/scholar?q=論文タイトルをURLエンコードした文字列",
          "question": "今日の問いかけ"
        }}
      ]
    }}
    """

    models = get_available_models(api_key)
    last_error = None

    for attempt in range(len(models) * 2):
        model = models[attempt % len(models)]
        try:
            print(f"Attempt {attempt + 1}: trying {model}...")
            text = call_gemini(api_key, model, prompt)
            parsed = json.loads(text)
            parsed["articles"] = parsed.get("articles", [])[:3]
            parsed["updated_at"] = timestamp
            parsed["history"] = history[:30]
            with open("news.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            print(f"Success with {model}!")
            return
        except Exception as e:
            print(f"Failed with {model}: {e}")
            last_error = e
            time.sleep(3)

    raise last_error

if __name__ == "__main__":
    main()
