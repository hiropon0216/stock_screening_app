import yfinance as yf
import pandas as pd
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