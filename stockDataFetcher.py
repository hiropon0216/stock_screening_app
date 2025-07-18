import yfinance as yf
import pandas as pd

class StockDataFetcher:
    def fetch_price_data(self, ticker: str, period="3mo", interval="1d") -> pd.DataFrame:
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if df.empty:
                print(f"データが取得できませんでした: {ticker}")
                return pd.DataFrame()

            # EMAの計算
            df["EMA5"] = df["Close"].ewm(span=5, adjust=False).mean()
            df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
            df["EMA40"] = df["Close"].ewm(span=40, adjust=False).mean()

            return df.dropna()
        except Exception as e:
            print(f"エラーが発生しました（{ticker}）: {e}")
            return pd.DataFrame()
        
    def fetch_data(self, tickers: list, period="3mo", interval="1d") -> dict:
        data_dict = {}
        for ticker in tickers:
            df = self.fetch_price_data(ticker, period, interval)
            if not df.empty:
                data_dict[ticker] = df
        return data_dict
