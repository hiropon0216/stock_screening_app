class StageAnalyzer:
    def __init__(self, short_ema_name='EMA_5', mid_ema_name='EMA_25', long_ema_name='EMA_50'):
        self.short = short_ema_name
        self.mid = mid_ema_name
        self.long = long_ema_name

    def determine_stage(self, row):
        short = row[self.short]
        mid = row[self.mid]
        long = row[self.long]

        if short > mid > long:
            return 1  # ステージ1：上昇トレンド
        elif mid > short > long:
            return 2  # ステージ2：調整
        elif mid > long > short:
            return 3  # ステージ3：下降トレンド初期
        elif long > mid > short:
            return 4  # ステージ4：下降トレンド
        elif long > short > mid:
            return 5  # ステージ5：反発の兆し
        elif short > long > mid:
            return 6  # ステージ6：上昇準備
        else:
            return 0  # 判定できない・横ばいなど
