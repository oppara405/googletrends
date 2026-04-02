import os
import json
from google import genai  # 新しいSDK
from pytrends.request import TrendReq

def get_trends():
    print("--- Trends取得開始 ---")
    pytrends = TrendReq(hl='ja-JP', tz=540)
    results = {"0": [], "25": []}

    # 1. 総合トレンド (RSSフィードベースの方法に切り替え)
    try:
        # 404を避けるため、trending_searches ではなく today_searches を試行
        df = pytrends.today_searches(pn='JP')
        results["0"] = df.head(10).tolist()
        print("総合トレンド取得完了")
    except Exception as e:
        print(f"総合トレンド取得でエラー(回避策実行): {e}")
        results["0"] = ["AI", "マーケティング", "DX"] # 失敗時のダミー

    # 2. 広告・マーケティング (カテゴリ25)
    try:
        # 空文字ではなく、広義のワードを指定して関連キーワードの急上昇を取る
        pytrends.build_payload(kw_list=['マーケティング'], cat=25, timeframe='now 1-d', geo='JP')
        related = pytrends.related_queries()
        rising = related['マーケティング']['rising']
        if rising is not None:
            results["25"] = rising['query'].head(10).tolist()
        print("広告カテゴリ取得完了")
    except Exception as e:
        print(f"カテゴリトレンド取得失敗: {e}")
        results["25"] = ["データ分析中"]

    return results

def ask_gemini(keywords):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "API Key Error"

    try:
        # 2026年最新の SDK 記述方式
        client = genai.Client(api_key=api_key)
        prompt = f"以下のワードについて、電通のマーケター風に30文字以内で一言解説して: {', '.join(keywords[:3])}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", # 最新モデルを指定
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

print("--- すべての処理が正常終了しました ---")
