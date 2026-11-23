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

def call_gemini_with_search(api_key, model, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.5
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
        candidate = result["candidates"][0]
        text = candidate["content"]["parts"][0]["text"]
        
        # Google検索から取得した本物の参照URLリストを抽出
        real_urls = []
        grounding = candidate.get("groundingMetadata", {})
        for chunk in grounding.get("groundingChunks", []):
            web = chunk.get("web", {})
            if web.get("uri"):
                real_urls.append(web["uri"])
                
        return text, real_urls

def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start:end+1])
    return json.loads(text)

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = now.strftime("%Y-%m-%d")
    current_year = now.year

    prompt = f"""
    今日は {today}（{current_year}年）です。
    必ずGoogle検索（google_search）を実行し、**直近1年以内（{current_year - 1}年〜{current_year}年）に発表された最新のウェルビーイング・ポジティブ心理学・組織行動学・動物福祉（アニマルウェルフェア）に関する学術研究論文・調査レポート・ニュース**を3件見つけてください。

    見つけた最新情報をもとに、株式会社アワーズ（アドベンチャーワールド運営）の社員・キャスト向けプラットフォーム『CWO Well-being Morning News』の最新記事を3本作成してください。

    【厳守ルール】
    1. **鮮度の徹底:** 必ず {current_year - 1}年〜{current_year}年 に発表された新しい研究・調査・ニュースのみを取り上げること。2024年以前の古い研究や古典論文は一切使わないこと。
    2. **事実とURLの正確性:** Google検索で見つかった実在の論文・記事タイトル、著者・機関名、公開年、およびそのページの正確なURLを記載すること。
    3. **バランス:** 3本の記事はPERMA分類（P, E, R, M, A）とターゲット（一般社員・キャスト / Well-being lab / アワーズ動物学院）を重複しないように割り振ること。
    4. **アワーズ文脈:** 「aw_value」では、アドベンチャーワールドのパーク運営、動物飼育、AWS-WAY、ゲストとスタッフのSmile創造にどう活かせるかを具体的に解説すること。

    【出力形式】以下のJSON形式のみを出力してください（余計な前置きは不要）。
    {{
      "date": "{today}",
      "articles": [
        {{
          "perma": "P, E, R, M, A のいずれか1文字",
          "category": "例: 最新組織心理学 / アニマルウェルフェア",
          "target": "一般社員・キャスト / Well-being lab / アワーズ動物学院 のいずれか",
          "title": "記事のタイトル",
          "summary": ["要約1", "要約2", "要約3"],
          "aw_value": "アドベンチャーワールド・アワーズの現場やAWS-WAYにどう活かせるかの解説",
          "source_jp": "日本語の解説・関連機関・研究テーマ名（発表年）",
          "source_en": "英語の原著論文名または最新ニュース記事タイトルと著者・発表年（{current_year - 1}または{current_year}）",
          "source_url": "Google検索で取得した実在する記事・論文のURL",
          "question": "今日の問いかけ"
        }}
      ]
    }}
    """

    models = get_available_models(api_key)
    print("Available models:", models)
    last_error = None

    for attempt in range(len(models) * 2):
        model = models[attempt % len(models)]
        try:
            print(f"Attempt {attempt + 1}: trying {model} with Google Search...")
            text, real_urls = call_gemini_with_search(api_key, model, prompt)
            parsed = extract_json(text)
            
            # もしAIが返したURLが空や不正な場合、Google検索で実際にヒットしたURLを自動補完
            for i, article in enumerate(parsed.get("articles", [])):
                if real_urls and (not article.get("source_url") or not article["source_url"].startswith("http")):
                    article["source_url"] = real_urls[i % len(real_urls)]

            with open("news.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            print(f"Success with {model}! Grounded URLs: {len(real_urls)}")
            return
        except Exception as e:
            print(f"Failed with {model}: {e}")
            last_error = e
            time.sleep(5)

    raise last_error

if __name__ == "__main__":
    main()
