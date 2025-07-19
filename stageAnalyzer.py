# stageAnalyzer.py
class StageAnalyzer:
    def __init__(self, short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40'):
        self.short = short_ema_col
        self.mid = mid_ema_col
        self.long = long_ema_col

    def determine_stage(self, row):
        short = row[self.short].iloc[-1]
        mid = row[self.mid].iloc[-1]
        long = row[self.long].iloc[-1]

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
        """
        ema_data_dict: dict[str, pd.DataFrame]
            - key: 銘柄コード
            - value: EMA計算済みのDataFrame
        """
        result = {}
        for ticker, df in ema_data_dict.items():
            if df.empty or len(df) < 1:
                result[ticker] = "データ不足"
                continue
            latest_row = df.iloc[-1]
            result[ticker] = self.determine_stage(latest_row)
        return result

# ここから下がテスト（直接実行用）コード
if __name__ == "__main__":
    import pandas as pd

    # 仮のデータを作成
    data = {
        'EMA_5':  [105],
        'EMA_25': [100],
        'EMA_40': [95],
    }
    df = pd.DataFrame(data)

    # テスト実行
    analyzer = StageAnalyzer()
    stage = analyzer.determine_stage(df)
    print("判定されたステージ:", stage)