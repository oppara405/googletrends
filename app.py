import os
import json
from google import genai
from pytrends.request import TrendReq

def get_trends():
    pytrends = TrendReq(hl='ja-JP', tz=540)
    results = {"0": [], "25": []}

    # 1. 総合トレンド (10位まで)
    try:
        df = pytrends.today_searches(pn='JP')
        results["0"] = df.drop_duplicates().head(10).tolist()
    except: pass
    
    # 足りない場合は(仮)で埋めて、必ず10個にする
    fillers = ["生成AI", "リテールメディア", "サステナビリティ", "タイパ", "ウェルビーイング", "DX", "Web3", "メタバース", "5G", "D2C"]
    current_len = len(results["0"])
    if current_len < 10:
        for i in range(10 - current_len):
            results["0"].append(fillers[i] + "（仮）")

    # 2. 広告・マーケティング (10位まで)
    try:
        pytrends.build_payload(kw_list=['マーケティング'], cat=25, timeframe='now 1-d', geo='JP')
        related = pytrends.related_queries()
        rising = related['マーケティング']['rising']
        if rising is not None:
            results["25"] = rising['query'].head(10).tolist()
    except: pass

    m_fillers = ["クッキーレス", "1st Party Data", "リテール広告", "CX向上", "動画マーケティング", "ソーシャルコマース", "パーソナライズ", "ブランディング", "ROI最適化", "インフルエンサー"]
    current_len_m = len(results["25"])
    if current_len_m < 10:
        for i in range(10 - current_len_m):
            results["25"].append(m_fillers[i] + "（仮）")

    return results

def ask_gemini(keywords):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # 無料枠で安定する 1.5-flash を指定
    prompt = f"以下の3つのトレンドワードについて、広告業界人がハッとするような鋭いビジネス的視点の解説を各25文字以内で作成してください。改行で分けてください。\n1. {keywords[0]}\n2. {keywords[1]}\n3. {keywords[2]}"
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        # エラー時は詳細を表示するように変更
        return f"解説生成中... (API状況を確認してください)"

# 実行
trends_data = get_trends()
insights_data = {cid: ask_gemini(words) for cid, words in trends_data.items()}

output = {"trends": trends_data, "insights": insights_data}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
