import os
import json
from google import genai
from pytrends.request import TrendReq

def get_trends():
    print("--- Trends取得開始 ---")
    pytrends = TrendReq(hl='ja-JP', tz=540)
    results = {"0": [], "25": []}

    # 1. 総合トレンド
    try:
        df = pytrends.today_searches(pn='JP')
        results["0"] = df.drop_duplicates().head(10).tolist()
        
        # 10件に満たない場合の補充（仮を付与）
        fillers = ["生成AI", "リテールメディア", "サステナビリティ", "タイパ", "ウェルビーイング", "DX", "Web3", "メタバース", "5G", "D2C"]
        for f in fillers:
            if len(results["0"]) < 10:
                results["0"].append(f + "（仮）")
        print("総合トレンド取得完了")
    except Exception as e:
        print(f"総合トレンド取得でエラー: {e}")
        # 全滅時はすべて（仮）のワード
        results["0"] = [f + "（仮）" for f in ["生成AI", "リテールメディア", "サステナビリティ", "タイパ", "ウェルビーイング", "DX", "Web3", "メタバース", "5G", "D2C"]]

    # 2. 広告・マーケティング (カテゴリ25)
    try:
        pytrends.build_payload(kw_list=['マーケティング'], cat=25, timeframe='now 1-d', geo='JP')
        related = pytrends.related_queries()
        rising = related['マーケティング']['rising']
        if rising is not None:
            results["25"] = rising['query'].head(10).tolist()
        
        # 10件に満たない場合の補充（仮を付与）
        m_fillers = ["クッキーレス", "1st Party Data", "リテール広告", "CX向上", "動画マーケティング", "ソーシャルコマース", "パーソナライズ", "ブランディング", "ROI最適化", "インフルエンサー"]
        for f in m_fillers:
            if len(results["25"]) < 10:
                results["25"].append(f + "（仮）")
        print("広告カテゴリ取得完了")
    except Exception as e:
        print(f"カテゴリトレンド取得失敗: {e}")
        # 全滅時はすべて（仮）のワード
        results["25"] = [f + "（仮）" for f in ["クッキーレス", "1st Party Data", "リテール広告", "CX向上", "動画マーケティング", "ソーシャルコマース", "パーソナライズ", "ブランディング", "ROI最適化", "インフルエンサー"]]

    return results

def ask_gemini(keywords):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "API Key Error"

    try:
        client = genai.Client(api_key=api_key)
        # 上位3つを対象に解説（（仮）がついていてもそのままGeminiに渡します）
        prompt = f"以下のワード上位3つについて、電通のマーケター風に25文字以内で1行ずつ解説して: {', '.join(keywords[:3])}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

# 実行と保存
trends_data = get_trends()
insights_data = {cid: ask_gemini(words) for cid, words in trends_data.items()}

output = {"trends": trends_data, "insights": insights_data}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("--- 処理完了 ---")
