import yfinance as yf
import pandas as pd
from StageAnalyzer import StageAnalyzer 
import ta

class StockDataFetcher:
    def __init__(self, period='45d', interval='1d'):
        self.period = period
        self.interval = interval

    def fetch(self, ticker):
        """
        銘柄コード(ticker)の株価を取得し、EMA(5,20,40)を計算して返す
        """
        df = yf.download(ticker, period=self.period, interval=self.interval, auto_adjust=True)
        if df.empty:
            return None
        df = self.add_ema_columns(df)
        return df

    def add_ema_columns(self, df):
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        for window in [5, 20, 40]:
            col_name = f'EMA_{window}'
            df[col_name] = ta.trend.EMAIndicator(close=close_series, window=window).ema_indicator()
        return df
    
    def filter_by_volume(self, df, volume_min=None, volume_max=None):
        """
        DataFrameの最新の出来高が、volume_min〜volume_maxの範囲にあるかを確認。
        条件に合致しない場合は None を返す。
        """
        if df is None or df.empty:
            return None

        latest_volume = df['Volume'].iloc[-1]

        if volume_min is not None and latest_volume < volume_min:
            return None
        if volume_max is not None and latest_volume > volume_max:
            return None

        return df

    def _convert_stage_label_to_number(self, label):
        """
        ステージの日本語ラベルを番号に変換（例: 'ステージ1' → '1'）

        Parameters:
            label (str): ステージラベル

        Returns:
            str: ステージ番号
        """
        if label.startswith("ステージ"):
            return label.replace("ステージ", "")
        return "その他"

# テスト実行用コード
if __name__ == "__main__":
    fetcher = StockDataFetcher(period="3mo", interval="1d")
    tickers = ["1301.T", "1305.T"]  # テスト用の銘柄コードリスト
    for ticker in tickers:
        df = fetcher.fetch(ticker)
        if df is not None:
            print(f"--- {ticker} のデータ ---")
            print(df.tail(10))
        else:
            print(f"{ticker} のデータ取得に失敗しました。")