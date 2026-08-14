Python
import json
import os
import requests
import feedparser
from openai import OpenAI

# 最新ニュース・IPPA・Post-SDGs（IDGs）を包括するRSSフィード
RSS_URLS = [
    # 1. IPPA / 国際ポジティブ心理学 最新情報
    "https://news.google.com/rss/search?q=IPPA+Positive+Psychology+World+Congress&hl=en-US&gl=US&ceid=US:en",
    # 2. ポジティブ心理学・ウェルビーイング最新トピック（国内）
    "https://news.google.com/rss/search?q=%E3%82%A6%E3%82%A7%E3%83%AB%E3%83%93%E3%83%BC%E3%82%A4%E3%83%B3%E3%82%B0+%E7%B5%84%E7%B9%94%E5%BF%83%E7%90%86%E5%AD%A6&hl=ja&gl=JP&ceid=JP:ja",
    # 3. Post-SDGs / IDGs (Inner Development Goals) / ウェルビーイング経済
    "https://news.google.com/rss/search?q=IDGs+Inner+Development+Goals+Wellbeing&hl=ja&gl=JP&ceid=JP:ja",
    # 4. ホスピタリティ・動物介在・働く人のメンタルヘルス
    "https://news.google.com/rss/search?q=%E3%83%9B%E3%82%B9%E3%83%94%E3%82%BF%E3%83%AA%E3%83%86%E3%82%A3+%E3%83%A1%E3%83%B3%E3%82%BF%E3%83%AB%E3%83%98%E3%83%AB%E3%82%B9&hl=ja&gl=JP&ceid=JP:ja"
]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_article_with_ai(title, summary, link, index):
    prompt = f"""
あなたは株式会社アワーズのCWO（Chief Well-being Officer）古谷勝氏のアシスタントAIです。
収集された最新ニュース（IPPA最新情報、IDGs/Post-SDGs動向、ポジティブ心理学論文・WEB記事）を分析し、JSONフォーマットのみで出力してください。

【タイトル】: {title}
【概要】: {summary}

【必須条件】
1. perma: P, E, R, M, A のいずれか1文字
2. theme: 「レジリエンス/成長思考」「ストレングス（強み）」「マインドフルネス/フロー」「感謝・利他/Giver」「IPPA/国際動向」「IDGs/Post-SDGs」のいずれか
3. target: 「一般社員・キャスト」「Well-being lab」「アワーズ動物学院」「朝礼用トピック」のいずれか
4. summary_3lines: 要点を3行の箇条書き（・から始まる）で分かりやすく要約
5. aws_context: アドベンチャーワールド（キャスト、動物学院生、パーク運営等）での実践価値（70文字以内）
6. reflection_question: 読んだ社員が思考や行動を起こせる「今日の問いかけ」（70文字以内）
7. source_ja: 関連する日本語文献名・理論名・IDGs等の関連用語
8. source_en: 関連する英語論文名・著者・IPPA/IDGs等の公式原語
9. source_url_ja: Google Books/公式情報の信頼できるURL
10. source_url_en: Google Scholar/IPPA/IDGs公式等の英語リンクURL

【JSONフォーマット】:
{{
  "perma": "M",
  "theme": "IDGs/Post-SDGs",
  "target": "Well-being lab",
  "summary_3lines": "・SDGs達成に必要な内面の成長指標（IDGs）に関する最新動向\\n・Being（在り方）や対話が組織のサステナビリティを高める\\n・Beyond GDP（幸福度経済）への世界的なシフト事例",
  "aws_context": "アワーズが推進するSmile創造とSDGsの『次』をつなぐ重要な世界的視点です。",
  "reflection_question": "私たちの仕事や対話は、未来の社会やゲストのどんな心豊かな状態に寄与していますか？",
  "source_ja": "Inner Development Goals (IDGs) 内面的な成長目標",
  "source_en": "Inner Development Goals: Transformational Skills for Sustainable Development",
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
        return {
            "id": index,
            "title": title,
            "link": link,
            "perma": "M",
            "theme": "IPPA/国際動向",
            "target": "朝礼用トピック",
            "summary_3lines": "・IPPAおよび最新のポジティブ心理学国際動向\\n・持続的な幸福度（Well-being）を高める最新介入研究\\n・世界的なウェルビーイングの実践事例",
            "aws_context": "日常業務におけるBeing（在り方）やSmile創造のヒントになります。",
            "reflection_question": "この記事から学べる小さな実践は何でしょうか？",
            "source_ja": "IPPA（国際ポジティブ心理学会）最新研究",
            "source_en": "IPPA World Congress Literature",
            "source_url_ja": "https://books.google.co.jp/",
            "source_url_en": "https://scholar.google.com/"
        }

def main():
    articles = []
    item_id = 1
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            ai_res = analyze_article_with_ai(entry.title, entry.get('summary', ''), entry.link, item_id)
            articles.append(ai_res)
            item_id += 1

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
