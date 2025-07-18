from stageAnalyzer import StageAnalyzer


class StockScreener:
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.analyzer = StageAnalyzer()

    def get_tickers(self):
        return list(self.data_dict.keys())

    def filter_by_stage(self, stage_number):
        result = {}

        for ticker, df in self.data_dict.items():
            if df.empty:
                continue

            required_columns = {"EMA5", "EMA20", "EMA40"}
            if not required_columns.issubset(df.columns):
                continue

            latest_row = df.iloc[-1]
            stage = self.analyzer.determine_stage(latest_row)

            if stage == stage_number:
                result[ticker] = df

        return result
