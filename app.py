import os
import json
from google import genai
from pytrends.request import TrendReq

def get_trends():
    print("--- Trends取得開始 ---")
    pytrends = TrendReq(hl='ja-JP', tz=540)
    results = {"0": [], "25": []}

    # 1. 総合トレンド (10位まで確実に取得)
    try:
        df = pytrends.today_searches(pn='JP')
        results["0"] = df.drop_duplicates().head(10).tolist()
    except Exception as e:
        print(f"Trends取得エラー: {e}")

    # 足りない分を補充
    fillers = ["生成AI", "リテールメディア", "サステナビリティ", "タイパ", "ウェルビーイング", "DX", "Web3", "メタバース", "5G", "D2C"]
    while len(results["0"]) < 10:
        results["0"].append(fillers[len(results["0"])] + "（仮）")

    # 2. 広告・マーケティング (10位まで確実に取得)
    try:
        pytrends.build_payload(kw_list=['マーケティング'], cat=25, timeframe='now 1-d', geo='JP')
        related = pytrends.related_queries()
        rising = related['マーケティング']['rising']
        if rising is not None:
            results["25"] = rising['query'].head(10).tolist()
    except: pass

    m_fillers = ["クッキーレス", "1st Party Data", "リテール広告", "CX向上", "動画マーケティング", "ソーシャルコマース", "パーソナライズ", "ブランディング", "ROI最適化", "インフルエンサー"]
    while len(results["25"]) < 10:
        results["25"].append(m_fillers[len(results["25"])] + "（仮）")

    return results

def ask_gemini(keywords):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # ユーザー指定の 2.5 Flash Lite を使用
    prompt = f"以下の3つのワードについて、電通のシニアプランナーのように、ビジネスの潮流を捉えた鋭い解説を各25文字以内で作成してください。改行で分けて回答して。\n1. {keywords[0]}\n2. {keywords[1]}\n3. {keywords[2]}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"解説生成中... (Error: {str(e)[:50]})"

# 実行
trends_data = get_trends()
insights_data = {cid: ask_gemini(words) for cid, words in trends_data.items()}

output = {"trends": trends_data, "insights": insights_data}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
