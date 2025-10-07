import numpy as np

class StageAnalyzer:
    def __init__(self, short_ema_col='EMA_5', mid_ema_col='EMA_25', long_ema_col='EMA_40'):
        self.short = short_ema_col
        self.mid = mid_ema_col
        self.long = long_ema_col

    def determine_stage(self, df):
        """最新行からステージを判定"""
        try:
            # ✅ スカラー(float)として取得
            short = float(df[self.short].iloc[-1])
            mid = float(df[self.mid].iloc[-1])
            long = float(df[self.long].iloc[-1])
        except Exception as e:
            return f"データ取得エラー: {e}"

        # ✅ 欠損値チェック
        if np.isnan(short) or np.isnan(mid) or np.isnan(long):
            return "データ不足"

        # ✅ ステージ判定ロジック（スカラー同士の比較に変更）
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
            return "判定不能"

    def analyze_all(self, ema_data_dict):
        """各銘柄のDataFrameをまとめて解析"""
        result = {}
        for ticker, df in ema_data_dict.items():
            if df.empty or len(df) < 1:
                result[ticker] = "データ不足"
                continue
            stage = self.determine_stage(df)
            result[ticker] = stage
        return result


# テスト
if __name__ == "__main__":
    import pandas as pd

    data = {
        'EMA_5': [105],
        'EMA_25': [100],
        'EMA_40': [95],
    }

    df = pd.DataFrame(data)
    analyzer = StageAnalyzer()
    print("判定されたステージ:", analyzer.determine_stage(df))

