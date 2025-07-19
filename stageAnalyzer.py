import ta
import pandas as pd

class StageAnalyzer:
    def __init__(self, short_ema_name='EMA_5', mid_ema_name='EMA_20', long_ema_name='EMA_40'):
        self.short = short_ema_name
        self.mid = mid_ema_name
        self.long = long_ema_name

    def add_ema_columns(self, df):
        """
        データにEMA列（5, 20, 40）を追加する
        """
        # 念のため Close 列を 1次元の Series にしておく
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]

        short_ema = ta.trend.EMAIndicator(close=close_series, window=5).ema_indicator()
        mid_ema   = ta.trend.EMAIndicator(close=close_series, window=20).ema_indicator()
        long_ema  = ta.trend.EMAIndicator(close=close_series, window=40).ema_indicator()

        df[self.short] = short_ema
        df[self.mid] = mid_ema
        df[self.long] = long_ema
        return df


    def determine_stage(self, latest_row):
        short = latest_row[self.short].item()
        mid = latest_row[self.mid].item()
        long = latest_row[self.long].item()

        if short > mid > long:
            return "ステージ1"
        elif mid > short > long:
            return "ステージ2"
        elif mid > long > short:
            return "ステージ3"
        elif long > mid > short:
            return "ステージ4"
        elif long > short > mid:
            return "ステージ5"
        elif short > long > mid:
            return "ステージ6"
        else:
            return "不明"

