# 株価を取得するクラス

import yfinance as yf
import pandas as pd

class StockDataFetcher:
    def __init__(self, period='90d', interval='1d'):
        self.period = period
        self.interval = interval

    def fetch(self, ticker):
        """
        指定された銘柄コードの株価データを取得する
        """
        try:
            df = yf.download(ticker, period=self.period, interval=self.interval, auto_adjust=True)
            if df.empty:
                print(f"[警告] データが取得できません: {ticker}")
                return None
            return df
        except Exception as e:
            print(f"[エラー] データ取得失敗: {e}")
            return None
