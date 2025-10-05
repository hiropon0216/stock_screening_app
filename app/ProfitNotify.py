import sqlite3
import yfinance as yf
import os
import requests

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/holding_stocks.db")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_PROFIT_WEBHOOK")  # GitHub Actions Secret など

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
    """10円単位で四捨五入"""
    return int(round(x / 10.0) * 10)

def check_profit_targets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, code, name, position, target_price FROM holding_stocks")
    rows = cur.fetchall()
    conn.close()

    notify_list = []

    for row in rows:
        code = row["code"].rstrip(".T")
        name = row["name"]
        position = row["position"]
        target_price = row["target_price"]

        if position != "買い":
            continue  # 売りポジションはスキップ

        try:
            ticker = yf.Ticker(code + ".T")
            hist = ticker.history(period="5d", interval="1d", auto_adjust=True)
            if hist.empty:
                continue
            current_price = hist["Close"].iloc[-1]
            current_price = round_to_nearest_10(current_price)

            if current_price >= target_price:
                notify_list.append((code, name, current_price))

        except Exception as e:
            print(f"{code} 情報取得エラー: {e}")

    if notify_list:
        msg_lines = [
            "‼️売り時が来たにゃ‼️",
            "保有する銘柄を下記の条件で売るにゃ。\n",
            "銘柄　　　　　　　　　注文区分　　　　　　　　金額"
        ]
        for code, name, price in notify_list:
            msg_lines.append(f"{code}:{name}　売り注文　　　　　　　　{price}円")
        notify_discord("\n".join(msg_lines))
        print("\n".join(msg_lines))
    else:
        print("売り通知対象なし。")

if __name__ == "__main__":
    check_profit_targets()
