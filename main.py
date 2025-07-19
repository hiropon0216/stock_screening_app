# main.py

from stockDataFetcher import StockDataFetcher
from stageAnalyzer import StageAnalyzer

fetcher = StockDataFetcher()
analyzer = StageAnalyzer()

# トヨタの株価を取得
ticker = "7203.T"
df = fetcher.fetch(ticker)

if df is not None:
    df = analyzer.add_ema_columns(df)
    latest_row = df.iloc[-1]
    stage = analyzer.determine_stage(latest_row)

    print(f"銘柄: {ticker} の現在ステージ: {stage}")
