'''
    株式売買にあたっての共通条件を管理するクラス
    市場フィルタ、予算フィルタ、出来高フィルタ、決算日フィルタの4指標
'''
import pandas as pd
from datetime import datetime, timedelta

class CommonConditions:
    def __init__(self, price_limit=3000, volume_threshold=50000, days_to_earnings=10):
        self.price_limit = price_limit
        self.volume_threshold = volume_threshold
        self.days_to_earnings = days_to_earnings

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        指定のDataFrameに対して共通条件でフィルタリングを行う。
        想定されるカラム: ['market', 'close', 'volume', 'next_earning_date']
        """
        df_filtered = df.copy()

        # プライム市場フィルタ
        df_filtered = df_filtered[df_filtered["market"] == "プライム"]

        # 終値ベースの価格上限フィルタ
        df_filtered = df_filtered[df_filtered["close"] <= self.price_limit]

        # 出来高フィルタ
        df_filtered = df_filtered[df_filtered["volume"] >= self.volume_threshold]

        # 決算日フィルタ
        today = datetime.today()
        deadline = today + timedelta(days=self.days_to_earnings)
        df_filtered["next_earning_date"] = pd.to_datetime(df_filtered["next_earning_date"], errors='coerce')
        df_filtered = df_filtered[
            (df_filtered["next_earning_date"].isna()) |
            (df_filtered["next_earning_date"] > deadline)
        ]

        return df_filtered
