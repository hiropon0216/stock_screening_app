import pandas as pd
import os

class TickersLoader:
    def __init__(self, csv_path=None):
        # デフォルトで絶対パスを使用
        if csv_path is None:
            self.csv_path = r'C:\Users\k1143\stock_screening_app\data\data_j.xls'
        else:
            self.csv_path = csv_path

    def get_all_tickers(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Excelファイルが見つかりません: {self.csv_path}")
        
        df = pd.read_excel(self.csv_path)
        print("Excelファイルの読み込み成功。先頭5行：")
        print(df.head())

        # '銘柄コード'列を4桁に揃えて文字列にし、".T"を付ける
        df['symbol'] = df['コード'].astype(str).str.zfill(4) + ".T"

        return df[['symbol', '銘柄名']].to_dict(orient='records')
    
# === ここから直接実行時のテスト用ブロック ===
# if __name__ == "__main__":
#     loader = TickersLoader()
#     tickers = loader.get_all_tickers()
#     print("読み込んだ銘柄情報：")
#     for ticker in tickers[:5]:  # 最初の5件だけ表示
#         print(ticker)
