Python
import json
import os
import requests
import feedparser
from openai import OpenAI

# 1. 常に「今現在」の最新ニュースを取得するリアルタイム検索キーワード
RSS_URLS = [
    # 最新のウェルビーイング・組織心理学Webニュース
    "https://news.google.com/rss/search?q=%E3%82%A6%E3%82%A7%E3%83%AB%E3%83%93%E3%83%BC%E3%82%A4%E3%83%B3%E3%82%B0+%E7%B5%84%E7%B9%94%E5%BF%83%E7%90%86%E5%AD%A6&hl=ja&gl=JP&ceid=JP:ja",
    # 最新のポジティブ心理学・心理的安全性記事
    "https://news.google.com/rss/search?q=%E3%83%9D%E3%82%B8%E3%83%86%E3%82%A3%E3%83%96%E5%BF%83%E7%90%86%E5%AD%A6+%E6%96%B0%E5%88%8A+%E6%9C%B8&hl=ja&gl=JP&ceid=JP:ja",
    # ホスピタリティ・動物介在・働く人のメンタルヘルス最新動向
    "https://news.google.com/rss/search?q=%E3%83%9B%E3%82%B9%E3%83%94%E3%82%BF%E3%83%AA%E3%83%86%E3%82%A3+%E3%83%A1%E3%83%B3%E3%82%BF%E3%83%AB%E3%83%98%E3%83%AB%E3%82%B9&hl=ja&gl=JP&ceid=JP:ja"
]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_article_with_ai(title, summary, link, index):
    prompt = f"""
あなたは株式会社アワーズのCWO（Chief Well-being Officer）古谷勝氏のアシスタントAIです。
収集された最新Webニュースまたは新刊書籍情報を分析し、JSON形式で回答してください。

【タイトル】: {title}
【概要】: {summary}

【出力条件】
1. perma: P, E, R, M, A のいずれか1文字
2. theme: 「レジリエンス/成長思考」「ストレングス（強み）」「マインドフルネス/フロー」「感謝・利他/Giver」のいずれか
3. target: 「一般社員・キャスト」「Well-being lab」「アワーズ動物学院」「朝礼用トピック」のいずれか
4. summary_3lines: WEB記事や新刊本の内容・要点を3行の箇条書き（・から始まる）で分かりやすく要約
5. aws_context: アドベンチャーワールド（キャスト、動物学院生、パーク運営等）での最新の実践価値（70文字以内）
6. reflection_question: 読んだ社員が思考や行動を起こせる「今日の問いかけ」（70文字以内）
7. source_ja: 関連するポジティブ心理学の日本語文献・理論名・書籍名
8. source_en: 関連する学術論文名または原著タイトル（英語表記）
9. source_url_ja: Google Booksまたは信頼できる日本語情報URL
10. source_url_en: Google Scholar等の学術原典検索URL

【JSONフォーマットのみで出力】:
{{
  "perma": "E",
  "theme": "マインドフルネス/フロー",
  "target": "一般社員・キャスト",
  "summary_3lines": "・要点1\\n・要点2\\n・要点3",
  "aws_context": "...",
  "reflection_question": "...",
  "source_ja": "...",
  "source_en": "...",
  "source_url_ja": "https://books.google.co.jp/",
  "source_url_en": "https://scholar.google.com/"
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        data["id"] = index
        data["title"] = title
        data["link"] = link
        return data
    except Exception as e:
        # 万が一APIエラーが起きた場合のバックアップ
        return {
            "id": index,
            "title": title,
            "link": link,
            "perma": "P",
            "theme": "マインドフルネス/フロー",
            "target": "一般社員・キャスト",
            "summary_3lines": "・最新Web記事のトピック確認\\n・今ここに意識を向ける実践\\n・本日の業務でのSmile意識",
            "aws_context": "日常業務におけるBeing（在り方）やSmile創造のヒントになります。",
            "reflection_question": "この記事から学べる小さな実践は何でしょうか？",
            "source_ja": "マーティン・セリグマン『ポジティブ心理学の挑戦』",
            "source_en": "Seligman, M. E. P. (2011). Flourish.",
            "source_url_ja": "https://books.google.co.jp/",
            "source_url_en": "https://scholar.google.com/"
        }

def main():
    articles = []
    item_id = 1
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]: # 各フィードから最新2件を取得
            ai_res = analyze_article_with_ai(entry.title, entry.get('summary', ''), entry.link, item_id)
            articles.append(ai_res)
            item_id += 1

    # 常に「今朝の最新データ」として data.json を上書き更新
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
