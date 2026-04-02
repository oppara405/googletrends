import os
import json
import google.generativeai as genai
from pytrends.request import TrendReq

# --- 設定項目 ---
# Google Trends カテゴリID (0: 総合, 25: 広告・マーケティング)
CATEGORY_IDS = [0, 25]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_trends():
    pytrends = TrendReq(hl='ja-JP', tz=360)
    all_data = {}
    
    for cid in CATEGORY_IDS:
        # トレンド取得（実際にはpytrendsの仕様に合わせて調整が必要）
        # ここでは簡易的に急上昇ワードを取得するロジック
        pytrends.build_payload(kw_list=[''], cat=cid, timeframe='now 1-d', geo='JP')
        df = pytrends.trending_searches(pn='japan')
        all_data[str(cid)] = df[0].tolist()[:10] # 上位10件
    return all_data

def get_gemini_insight(keywords):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"以下のトレンドワード上位3つについて、マーケティング視点での解説を各100文字以内で作成してください：{', '.join(keywords[:3])}"
    response = model.generate_content(prompt)
    return response.text

# 実行
trends = get_trends()
insights = {}
for cid, words in trends.items():
    insights[cid] = get_gemini_insight(words)

# 結果をJSON保存（index.htmlがこれを読み込む）
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump({"trends": trends, "insights": insights}, f, ensure_ascii=False)
