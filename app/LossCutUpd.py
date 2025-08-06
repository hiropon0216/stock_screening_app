import sqlite3
import yfinance as yf
import pandas as pd
import os

class LossCutUpdater:
    def __init__(self):
        # DBパスの設定
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, '..', 'db', 'stock.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def fetch_holding_stocks(self):
        # 保有銘柄の情報を取得（保有中のみ）
        self.cursor.execute('''
            SELECT id, code, position
            FROM holding_stocks
            WHERE possession_flag = 1
        ''')
        return self.cursor.fetchall()

    def fetch_latest_price_and_atr(self, code):
        # 銘柄コードをYahoo用に変換（例: 7203.T）
        ticker = f"{code}.T"

        try:
            df = yf.download(ticker, period="14d", interval="1d", progress=False)
            if df.empty or len(df) < 2:
                return None, None

            df['H-L'] = df['High'] - df['Low']
            df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
            df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
            df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
            df['ATR'] = df['TR'].rolling(window=14).mean()

            latest_close = df['Close'].iloc[-1]
            latest_atr = df['ATR'].iloc[-1]

            return latest_close, latest_atr

        except Exception as e:
            print(f"Error fetching data for {code}: {e}")
            return None, None

    def calculate_loss_cut_price(self, close, atr, position):
        if pd.isna(close) or pd.isna(atr):
            return None

        # ロスカット値の算出
        if position == "buy":
            price = close - 2 * atr
        elif position == "sell":
            price = close + 2 * atr
        else:
            return None

        # 10円単位に四捨五入
        rounded_price = round(price / 10) * 10
        return rounded_price

    def update_loss_cut_prices(self):
        stocks = self.fetch_holding_stocks()

        for stock_id, code, position in stocks:
            print(f"Processing {code} ({position})...")

            close, atr = self.fetch_latest_price_and_atr(code)
            if close is None or atr is None:
                print(f"  ➤ データ取得失敗: {code}")
                continue

            loss_price = self.calculate_loss_cut_price(close, atr, position)
            if loss_price is None:
                print(f"  ➤ ロスカット価格の計算失敗: {code}")
                continue

            # UPDATE文でloss_priceを更新
            self.cursor.execute('''
                UPDATE holding_stocks
                SET loss_price = ?
                WHERE id = ?
            ''', (loss_price, stock_id))

            print(f"  ➤ loss_price = {loss_price} に更新")

        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    updater = LossCutUpdater()
    updater.update_loss_cut_prices()
    updater.close()
