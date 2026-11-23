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
            "temperature": 0.65
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
    あなたは株式会社アワーズ（アドベンチャーワールド運営）のCWO（最高ウェルビーイング責任者）を補佐する専門リサーチャーです。
    社員・キャスト向けプラットフォーム『CWO Well-being Morning News』に掲載する最新記事を **必ず3本だけ** 作成してください。

    【CWO品質基準・厳守ルール】
    1. **架空の論文タイトル・架空データの創作を厳禁とする:**
       - AIがそれらしく合成した架空の英語論文タイトルは絶対に作らないこと。
       - 必ず実在する著名な調査レポート・研究機関・大学・学術誌（例: World Happiness Report 2025/2026、Gallup State of the Global Workplace、Harvard Business Review、MIT Sloan Management Review、Journal of Positive Psychology、APA、Nature / Science、オックスフォード大学ウェルビーイングリサーチセンター、京都大学・東京大学などの実在研究）に基づく**一次情報**のみを使用すること。
       - 記事の要約（`summary`）には、**必ず具体的な調査数値・統計データ（例：「エンゲージメントが高いチームは生産性が21%高い」「1日5分の感謝の共有でバーンアウト率が〇%低下」など、調査対象人数やパーセンテージ等の客観的エビデンス）を1つ以上含めること**。
    2. **情報の鮮度とリンクの確実性:**
       - 直近（{current_year - 1}年〜{current_year}年）の最新レポートや最新の学術的知見・組織トレンドを取り上げること。
       - `source_en` には、実在するレポート名・調査機関名・研究プロジェクト名と発表年を正確に記載すること。
       - `source_url` には、その実在する調査名・機関名・論文キーワードでGoogle ScholarまたはGoogle検索で確実にヒットする検索URL（`https://scholar.google.com/scholar?q=...` または実在する公式トップURL）を設定すること。
    3. **記事構成・表記ルール:**
       - 記事数は **必ず3本のみ**。
       - `perma` には必ず `"P"`, `"E"`, `"R"`, `"M"`, `"A"` のいずれか1文字を入れること（絶対に空欄やundefinedにしない）。3本で異なるアルファベットを割り振ること。
       - `target` には「一般社員・キャスト」「パーク運営・飼育現場」「アワーズ動物学院」のいずれかを設定すること（※過去に存在した「Well-being lab」は現在実施していないため、本文・ターゲットともに一切使用しないこと）。
       - `aw_value` では、アドベンチャーワールドのパーク運営、動物飼育（アニマルウェルフェア）、AWS-WAY、ゲストとスタッフのSmile創造にどう活かせるかを経営・CWO視点で具体的に解説すること。

    【出力形式】必ず以下のJSON形式のみを出力してください。
    {{
      "date": "{today}",
      "articles": [
        {{
          "perma": "P, E, R, M, A のいずれか1文字",
          "category": "例: 最新組織行動学 / アニマルウェルフェア / ウェルビーイング統計",
          "target": "一般社員・キャスト / パーク運営・飼育現場 / アワーズ動物学院 のいずれか",
          "title": "記事のタイトル",
          "summary": [
            "具体的な調査機関・対象と数値データを含む要約1",
            "研究から明らかになったメカニズム・要因の要約2",
            "職場やチームへの示唆の要約3"
          ],
          "aw_value": "アドベンチャーワールド・アワーズの現場やAWS-WAYにどう活かせるかのCWO視点での解説",
          "source_jp": "日本語での調査・研究の概要（実在する機関名・発表年）",
          "source_en": "実在する原著レポート・調査名・研究機関名と発表年（{current_year - 1}または{current_year}）",
          "source_url": "https://scholar.google.com/scholar?q=実在する調査名や論文キーワードをURLエンコードした文字列",
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
            articles = parsed.get("articles", [])[:3]
            
            # PERMAが空や不正な場合の安全補正
            fallback_permas = ["P", "R", "M"]
            for idx, art in enumerate(articles):
                if art.get("perma") not in ["P", "E", "R", "M", "A"]:
                    art["perma"] = fallback_permas[idx % 3]

            parsed["articles"] = articles
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
