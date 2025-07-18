# main.py

from stockScreener import StockScreener
from stockDataFetcher import StockDataFetcher
from stageAnalyzer import StageAnalyzer

def main():
    fetcher = StockDataFetcher()

    # 銘柄リスト
    tickers = ["7203.T", "6758.T", "9984.T"]

    data_dict = fetcher.fetch_data(tickers)

    # スクリーナーで候補銘柄を抽出（例: 東証プライム上場のすべて）
    screener = StockScreener(data_dict)
    tickers = screener.get_tickers()

    fetcher = StockDataFetcher()
    analyzer = StageAnalyzer()

    results = []

    for ticker in tickers:
        # 株価データとEMAを取得
        data = fetcher.get_stock_data(ticker)
        if data is None or len(data) < 100:
            continue  # データが不十分な銘柄はスキップ

        # ステージ分析
        stage = analyzer.analyze(data)

        # 条件に合うステージだけを出力（例: ステージ1）
        if stage == 1:
            results.append((ticker, stage))

    # 結果の出力
    print(f"ステージ1にある銘柄一覧（{len(results)}件）:")
    for ticker, stage in results:
        print(f"{ticker}: ステージ{stage}")

if __name__ == '__main__':
    main()
