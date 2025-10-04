import yfinance as yf
from flask import Flask, render_template, request, jsonify
import sqlite3, os
from datetime import datetime
import pandas as pd

app = Flask(__name__)
DB_PATH = "db/holding_stocks.db"
os.makedirs("db", exist_ok=True)

# ---------------------------
# ATR計算
# ---------------------------
def calculate_atr(code, window=20):
    """直近window日間のATRを計算し、直近終値とともに返す"""
    ticker = yf.Ticker(code)
    hist = ticker.history(period="3mo", interval="1d", auto_adjust=True)
    if hist.empty or len(hist) < window:
        return None, None
    df = pd.DataFrame({
        "high": hist["High"],
        "low": hist["Low"],
        "close": hist["Close"]
    })
    df["prev_close"] = df["close"].shift(1)
    df = df.dropna()
    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = (df["high"] - df["prev_close"]).abs()
    df["tr3"] = (df["low"] - df["prev_close"]).abs()
    df["tr"] = df[["tr1", "tr2", "tr3"]].max(axis=1)
    atr = df["tr"].rolling(window=window).mean().iloc[-1]
    last_close = df["close"].iloc[-1]
    return atr, last_close

def round_to_nearest_10(x):
    """10の位で四捨五入"""
    return int(round(x / 10.0) * 10)

# ---------------------------
# トップページ：保有中銘柄一覧表示
# ---------------------------
@app.route("/", methods=["GET"])
def index():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM holding_stocks")
    stocks = cursor.fetchall()
    conn.close()
    return render_template("holding_stocks.html", stocks=stocks)

# ---------------------------
# 新規登録処理
# ---------------------------
@app.route("/add_stock", methods=["POST"])
def add_stock():
    try:
        data = request.form
        position = data["position"]
        code = data["code"].strip()
        buy_price = float(data["buy_price"])
        loss_price = float(data["loss_price"])
        buy_date = data["buy_date"]

        # 日本株の場合末尾に.Tを補完
        if not code.upper().endswith(".T"):
            code = code + ".T"

        # yfinanceで銘柄情報取得
        ticker = yf.Ticker(code)
        info = ticker.info
        name = info.get("shortName")
        market = info.get("exchange")
        if not name or not market:
            raise ValueError(f"銘柄コード {code} は不正または情報取得不可")

        # target_price = 直近終値 + 2ATR, 10の位で四捨五入
        atr, last_close = calculate_atr(code)
        if atr is None or last_close is None:
            raise ValueError(f"{code} のATRまたは価格取得失敗")
        target_price = round_to_nearest_10(last_close + 2 * atr)

        # DBに保存
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO holding_stocks
            (position, code, name, market, loss_price, buy_price, buy_date, target_price, create_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (position, code, name, market, loss_price, buy_price, buy_date, target_price,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------------------------
# 銘柄削除処理
# ---------------------------
@app.route("/delete_stock/<int:stock_id>", methods=["POST"])
def delete_stock(stock_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM holding_stocks WHERE id=?", (stock_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------------------------
# 銘柄更新処理（編集用）
# ---------------------------
@app.route("/update_stock", methods=["POST"])
def update_stock():
    try:
        data = request.form
        stock_id = int(data["id"])
        position = data["position"]
        code = data["code"].strip()
        buy_price = float(data["buy_price"])
        loss_price = float(data["loss_price"])
        buy_date = data["buy_date"]

        # 日本株の場合末尾に.Tを補完
        if not code.upper().endswith(".T"):
            code = code + ".T"

        # yfinanceで銘柄情報取得
        ticker = yf.Ticker(code)
        info = ticker.info
        name = info.get("shortName")
        market = info.get("exchange")
        if not name or not market:
            raise ValueError(f"銘柄コード {code} は不正または情報取得不可")

        # target_price = 直近終値 + 2ATR, 10の位で四捨五入
        atr, last_close = calculate_atr(code)
        if atr is None or last_close is None:
            raise ValueError(f"{code} のATRまたは価格取得失敗")
        target_price = round_to_nearest_10(last_close + 2 * atr)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE holding_stocks
            SET position=?, code=?, name=?, market=?, loss_price=?, buy_price=?, buy_date=?, target_price=?
            WHERE id=?
        """, (position, code, name, market, loss_price, buy_price, buy_date, target_price, stock_id))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ---------------------------
# Flask起動
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
