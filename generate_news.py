import os
import json
import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    perma: str = Field(description="P, E, R, M, A のいずれか1文字")
    category: str = Field(description="例: マインドフルネス/フロー, 感謝・利他/Giver, レジリエンス/成長思考 など")
    target: str = Field(description="一般社員・キャスト, Well-being lab, アワーズ動物学院 のいずれか")
    title: str = Field(description="記事のタイトル")
    summary: list[str] = Field(description="AI 3行要約（箇条書き3つ）")
    aw_value: str = Field(description="アドベンチャーワールド・アワーズの現場やAWS-WAYにどう活かせるかの解説")
    source_jp: str = Field(description="日本語の参考文献・書籍名")
    source_en: str = Field(description="英語の原著論文名と著者・発表年")
    source_url: str = Field(description="論文や関連情報の検索URLまたはDOIリンク")
    question: str = Field(description="今日の問いかけ（Reflective Question）")

class DailyNewsList(BaseModel):
    date: str
    articles: list[NewsItem]

def main():
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(timeout=120.0)
    )
    today = datetime.date.today().strftime("%Y-%m-%d")

    prompt = f"""
    今日は {today} です。
    株式会社アワーズ（アドベンチャーワールド運営）の社員・キャスト向けの社内プラットフォーム『CWO Well-being Morning News』に掲載する最新記事を3本作成してください。

    【条件】
    - 心理学・ポジティブ心理学・組織開発の実在する学術研究や論文をベースにすること。
    - 3本の記事はそれぞれPERMA分類（P, E, R, M, A）とターゲット（一般社員・キャスト / Well-being lab / アワーズ動物学院）をバランスよく分けること。
    - 「AW/アワーズ文脈の価値」では、パーク運営・動物飼育・事務・AWS-WAY・Smile創造などに絡めた実践的な価値を書くこと。
    - 「元ネタ」には実在する有名な論文・書籍を正確に挙げること。
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyNewsList,
            temperature=0.7,
        ),
    )

    with open("news.json", "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    main()
