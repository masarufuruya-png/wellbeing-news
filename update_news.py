Python
import json
import os
import requests
import feedparser
from openai import OpenAI

# AW文脈・ポジティブ心理学特化のニュースフィード
RSS_URLS = [
    "https://news.google.com/rss/search?q=%E3%82%A6%E3%82%A7%E3%83%AB%E3%83%93%E3%83%BC%E3%82%A4%E3%83%B3%E3%82%B0+%E7%B5%84%E7%B9%94%E5%BF%83%E7%90%86%E5%AD%A6&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=%E3%83%9D%E3%82%B8%E3%83%86%E3%82%A3%E3%83%96%E5%BF%83%E7%90%86%E5%AD%A6+%E5%BF%83%E7%90%86%E7%9A%84%E5%AE%89%E5%85%A8%E6%80%A7&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=%E5%8B%95%E7%89%A9%E4%BB%8B%E5%9C%A8%E7%99%82%E6%B3%95+%E3%83%9B%E3%82%B9%E3%83%94%E3%82%BF%E3%83%AA%E3%83%86%E3%82%A3&hl=ja&gl=JP&ceid=JP:ja"
]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_article_with_ai(title, summary, index, link):
    prompt = f"""
あなたは株式会社アワーズのCWO（Chief Well-being Officer）古谷勝氏のアシスタントAIです。
以下のニュース記事を分析し、JSONフォーマットのみで出力してください。

【タイトル】: {title}
【概要】: {summary}

【必須出力フィールド】:
1. perma: P, E, R, M, A のいずれか1文字
2. theme: 「レジリエンス/成長思考」「ストレングス（強み）」「マインドフルネス/フロー」「感謝・利他/Giver」のいずれか
3. target: 「一般社員・キャスト」「Well-being lab」「アワーズ動物学院」「朝礼用トピック」のいずれか
4. summary_3lines: 要点を3行の箇条書き（・から始まる）で記述
5. aws_context: アドベンチャーワールド（キャスト、動物学院生、パーク運営等）での実践価値（70文字以内）
6. reflection_question: 読んだ社員が成長思考や行動を起こせる「今日の問いかけ」（70文字以内）
7. source_en: このニュースの根拠となるポジティブ心理学の論文名・著者・原著タイトル（英語表記）
8. source_ja: 上記文献・理論の日本語名称および著者解説
9. source_url_en: 原語論文や著者文献が確認できる外部WebサイトのURL (PubMed, Google Scholar, Psychology Today等)
10. source_url_ja: 日本語での理論解説や関連書籍・YeeY等の公式リンクURL

【JSONフォーマット】:
{{
  "perma": "E",
  "theme": "マインドフルネス/フロー",
  "target": "一般社員・キャスト",
  "summary_3lines": "・要点1\\n・要点2\\n・要点3",
  "aws_context": "...",
  "reflection_question": "...",
  "source_en": "Csikszentmihalyi, M. (1990). Flow: The Psychology of Optimal Experience.",
  "source_ja": "ミハイ・チクセントミハイ『フロー体験 喜びの心理学』",
  "source_url_en": "https://www.psychologytoday.com/us/basics/flow",
  "source_url_ja": "https://positivepsychology.yeey.co/"
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
        return {
            "id": index,
            "title": title,
            "link": link,
            "perma": "P",
            "theme": "マインドフルネス/フロー",
            "target": "一般社員・キャスト",
            "summary_3lines": "・ニュース概要の確認\\n・今ここに意識を向ける実践\\n・本日の業務でSmileを意識",
            "aws_context": "日常業務におけるBeing（在り方）やSmile創造のヒントになります。",
            "reflection_question": "この記事から学べる小さな実践は何でしょうか？",
            "source_en": "Seligman, M. E. P. (2011). Flourish.",
            "source_ja": "マーティン・セリグマン『ポジティブ心理学の挑戦』",
            "source_url_en": "https://www.authentichappiness.sas.upenn.edu/",
            "source_url_ja": "https://positivepsychology.yeey.co/"
        }

def main():
    articles = []
    item_id = 1
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            ai_res = analyze_article_with_ai(entry.title, entry.get('summary', ''), item_id, entry.link)
            articles.append(ai_res)
            item_id += 1

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
