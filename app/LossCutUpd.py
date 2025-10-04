import sqlite3
import yfinance as yf
import pandas as pd
import math
import os
import requests

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/holding_stocks.db")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_LOSSCUT_WEBHOOK")

def notify_discord(message: str):
    """Discordに通知"""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL 未設定")
        return
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"Discord通知失敗: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Discord通知エラー: {e}")

def round_to_nearest_10(x):
    """10の位で四捨五入"""
    return int(round(x / 10.0) * 10)

def calculate_atr_safe(code, window=20):
    """20日間ATRと直近終値を取得"""
    ticker = yf.Ticker(code + ".T")
    hist = ticker.history(period="3mo", interval="1d", auto_adjust=True)
    if hist.empty or len(hist) < window:
        return None, None
    high = hist["High"]
    low = hist["Low"]
    close = hist["Close"]
    df = pd.DataFrame({"high": high, "low": low, "close": close})
    df["prev_close"] = df["close"].shift(1)
    df = df.dropna()
    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = (df["high"] - df["prev_close"]).abs()
    df["tr3"] = (df["low"] - df["prev_close"]).abs()
    df["tr"] = df[["tr1", "tr2", "tr3"]].max(axis=1)
    atr = df["tr"].rolling(window=window).mean().iloc[-1]
    current_price = df["close"].iloc[-1]
    return atr, current_price

def update_loss_cut():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, code, position, loss_price FROM holding_stocks")
    rows = cur.fetchall()
    if not rows:
        print("更新対象の銘柄がありません。")
        conn.close()
        return

    updated_stocks = []  # 更新対象リスト
    errors = []

    for row in rows:
        stock_id = row["id"]
        code = row["code"].rstrip(".T")
        position = row["position"]
        current_loss_price = row["loss_price"]

        try:
            atr, current_price = calculate_atr_safe(code)
            if atr is None:
                errors.append(f"{code}: ATRまたは価格取得失敗")
                continue

            if position == "買い":
                candidate = current_price - 1.5 * atr
                candidate = round_to_nearest_10(candidate)
                if candidate > current_loss_price:
                    cur.execute("UPDATE holding_stocks SET loss_price = ? WHERE id = ?", (candidate, stock_id))
                    updated_stocks.append((code, current_loss_price, candidate))
            elif position == "売り":
                candidate = current_price + 1.5 * atr
                candidate = round_to_nearest_10(candidate)
                if candidate < current_loss_price:
                    cur.execute("UPDATE holding_stocks SET loss_price = ? WHERE id = ?", (candidate, stock_id))
                    updated_stocks.append((code, current_loss_price, candidate))
            else:
                errors.append(f"{code}: positionが不明です ({position})")

        except Exception as e:
            errors.append(f"{code} 処理中エラー: {e}")

    conn.commit()
    conn.close()

    # Discord通知まとめ
    msg_lines = []
    if updated_stocks:
        msg_lines.append("🟢 ロスカット更新対象銘柄:")
        for c, old, new in updated_stocks:
            msg_lines.append(f"- {c}: {old}円 → {new}円")
    else:
        msg_lines.append("🔵 本日更新対象の銘柄はありません。")

    if errors:
        msg_lines.append("\n❌ エラー銘柄:")
        for e in errors:
            msg_lines.append(f"- {e}")

    notify_discord("\n".join(msg_lines))

if __name__ == "__main__":
    update_loss_cut()
