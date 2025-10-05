# stageAnalyzer.py
class StageAnalyzer:
    def __init__(self, short_ema_col='EMA_5', mid_ema_col='EMA_25', long_ema_col='EMA_40'):
        self.short = short_ema_col
        self.mid = mid_ema_col
        self.long = long_ema_col

    def determine_stage(self, row):
        """
        最新行（Series）からステージを判定する。
        """
        short = row[self.short]
        mid = row[self.mid]
        long = row[self.long]

        # 一目均衡表 大循環分析の基本ロジック
        if short > mid > long:
            return "ステージ1"  # 上昇相場の初期
        elif mid > short > long:
            return "ステージ2"
        elif mid > long > short:
            return "ステージ3"  # 上昇相場から下降相場への転換期
        elif long > mid > short:
            return "ステージ4"  # 下降相場
        elif long > short > mid:
            return "ステージ5"
        elif short > long > mid:
            return "ステージ6"
        else:
            return "判定不能"

    def analyze_all(self, ema_data_dict):
        """
        各銘柄ごとに最新ステージを判定して返す。
        ema_data_dict: dict[str, pd.DataFrame]
        """
        result = {}
        for ticker, df in ema_data_dict.items():
            if df.empty or len(df) < 1:
                result[ticker] = "データ不足"
                continue

            latest_row = df.iloc[-1]  # 最新行
            stage = self.determine_stage(latest_row)
            result[ticker] = stage
        return result


# テストコード
if __name__ == "__main__":
    import pandas as pd

    data = {
        'EMA_5':  [105],
        'EMA_25': [100],
        'EMA_40': [95],
    }
    df = pd.DataFrame(data)

    analyzer = StageAnalyzer()
    stage = analyzer.determine_stage(df.iloc[-1])  # 最新行を渡す
    print("判定されたステージ:", stage)
