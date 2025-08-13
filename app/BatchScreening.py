import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from TickersLoader import TickersLoader
from StockDataFetcher import StockDataFetcher
from StageAnalyzer import StageAnalyzer

def fetch_latest_price_volume(ticker):
    try:
        # 直近5営業日分のデータを取得（1日では空になることが多いため）
        df = yf.Ticker(ticker).history(period='5d')

        # 終値が存在する最新行を取得
        df = df[df['Close'].notnull()]

        if df.empty:
            print(f"{ticker}: 有効な終値データが存在しません。")
            return None, None

        # 最新のレコード（日付が未来のものを含まないように）
        latest_row = df.iloc[-1]
        latest_date = latest_row.name.to_pydatetime().date()
        today = datetime.now().date()

        if latest_date > today:
            print(f"{ticker}: 最新データの日付が未来の日付（{latest_date}）です。スキップします。")
            return None, None

        latest_close = float(latest_row['Close'])
        latest_volume = int(latest_row['Volume'])

        return latest_close, latest_volume

    except Exception as e:
        print(f"最新株価・出来高取得エラー: {ticker}: {e}")
        return None, None

def run_batch():
    selected_stages = [1, 2, 3, 4, 5, 6]

    # 銘柄一覧の取得
    loader = TickersLoader()
    tickers = loader.get_all_tickers()

    # クラス初期化
    fetcher = StockDataFetcher()
    stage_analyzer = StageAnalyzer(short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40')

    results = []

    for item in tickers:
        ticker = item['symbol']
        name = item['銘柄名']
        market = item.get('市場・商品区分', '')
        print(f"処理中: {ticker} - {name} - {market}")

        try:
            df = fetcher.fetch(ticker)
            if df is None or df.empty:
                print(f"データ取得失敗: {ticker}")
                continue

            # 最新行だけ渡して判定
            latest_row = df.iloc[-1]
            stage_str = stage_analyzer.determine_stage(latest_row)

            if stage_str.startswith("ステージ"):
                stage_num = int(stage_str.replace("ステージ", ""))
            else:
                continue  # 判定不能ならスキップ

            if stage_num in selected_stages:
                latest_close, latest_volume = fetch_latest_price_volume(ticker)
                results.append({
                    '市場・商品区分': market,
                    '銘柄コード': ticker,
                    '銘柄名': name,
                    '現在のステージ': stage_num,
                    '最新終値': latest_close,
                    '最新出来高': latest_volume
                })

        except Exception as e:
            print(f"エラー: {ticker} - {name}: {str(e)}")
            continue

    # DataFrameに変換
    result_df = pd.DataFrame(results)

    # outputフォルダ作成
    output_dir = 'app/output'
    os.makedirs(output_dir, exist_ok=True)

    filename = f'{output_dir}/screening_result.csv'
    result_df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"\nスクリーニング完了。結果を {filename} に保存しました。")

if __name__ == "__main__":
    run_batch()
