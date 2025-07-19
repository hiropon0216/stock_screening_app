from flask import Flask, request, render_template
import pandas as pd

from TickersLoader import TickersLoader
from StockDataFetcher import StockDataFetcher
from StageAnalyzer import StageAnalyzer

app = Flask(__name__)

# 全銘柄の株価取得・EMA計算
def fetch_all_ema(tickers):
    fetcher = StockDataFetcher(period="60d", interval="1d")
    ema_data = {}
    for item in tickers:
        symbol = item['symbol']
        df = fetcher.fetch(symbol)
        if df is not None:
            ema_data[symbol] = df
        else:
            print(f"[警告] {symbol} のデータ取得失敗")
    return ema_data

# ステージ判定と結果整形
def analyze_stages(tickers, ema_data):
    analyzer = StageAnalyzer(short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40')
    stage_results = analyzer.analyze_all(ema_data)

    results = []
    for item in tickers:
        symbol = item['symbol']
        name = item['銘柄名']
        stage = stage_results.get(symbol, "データなし")
        chart_link = f"https://finance.yahoo.co.jp/chart/{symbol.replace('.T','')}"  # 適宜リンク調整してください
        results.append({
            'code': symbol,
            'name': name,
            'stage': stage,
            'chart_link': chart_link
        })
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    loader = TickersLoader()
    tickers = loader.get_all_tickers()
    # TODO キャッシュの考慮後、当該コードを削除
    tickers = tickers[:100]  # 最初の100件だけに絞る
    
    # すべての銘柄のEMA取得
    ema_data = fetch_all_ema(tickers)
    
    # ステージ判定
    results = analyze_stages(tickers, ema_data)

    # POST時はフォームから選択されたステージでフィルタ
    selected_stages = []
    filtered_results = results
    if request.method == "POST":
        selected_stages = request.form.getlist("stage")
        selected_stages = [f"ステージ{int(s)}" for s in selected_stages]
        filtered_results = [r for r in results if r['stage'] in selected_stages]

    return render_template("index.html", results=filtered_results, selected_stages=selected_stages)

if __name__ == "__main__":
    app.run(debug=True)
