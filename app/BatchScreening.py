import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from utils.stageAnalyzer import StageAnalyzer
from utils.stockDataFetcher import StockDataFetcher
from utils.discordNotifier import DiscordNotifier

# ---- 設定値 ----
CACHE_FILE = "cache/screening_result.json"
STOCK_LIST_FILE = "data/stock_list.csv"

# ---- Discord Webhook ----
DISCORD_NOTIFY_URL = os.getenv("DISCORD_NOTIFY_URL")                # 通常スクリーニング通知
DISCORD_CONFIRM_PROFIT_URL = os.getenv("DISCORD_CONFIRM_PROFIT_URL") # 利確通知用Webhook

# ---- 機能クラス初期化 ----
analyzer = StageAnalyzer()
fetcher = StockDataFetcher()
notifier = DiscordNotifier()


def load_stock_list():
    """銘柄リストをCSVから読み込み"""
    if not os.path.exists(STOCK_LIST_FILE):
        raise FileNotFoundError(f"銘柄リストが見つかりません: {STOCK_LIST_FILE}")
    return pd.read_csv(STOCK_LIST_FILE)


def load_previous_cache():
    """前回のスクリーニング結果を読み込み"""
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(data):
    """スクリーニング結果を保存"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def detect_stage_changes(prev_data, current_data):
    """ステージの変化を検出"""
    changes = []
    for code, info in current_data.items():
        prev_stage = prev_data.get(code, {}).get("stage")
        current_stage = info.get("stage")
        if prev_stage and prev_stage != current_stage:
            changes.append({
                "code": code,
                "name": info["name"],
                "prev_stage": prev_stage,
                "current_stage": current_stage,
            })
    return changes


def detect_profit_confirms(prev_data, current_data):
    """利確検知（例: ステージ1→ステージ3など、下降サイクル入りを検知）"""
    profits = []
    for code, info in current_data.items():
        prev_stage = prev_data.get(code, {}).get("stage")
        current_stage = info.get("stage")

        # 例: 上昇完了のシグナルを「1 → 3」などで判定
        if prev_stage == 1 and current_stage == 3:
            profits.append({
                "code": code,
                "name": info["name"],
                "prev_stage": prev_stage,
                "current_stage": current_stage,
            })
    return profits


def run_batch_screening():
    """スクリーニングバッチのメイン処理"""
    print(f"[INFO] Batch Screening started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    stock_list = load_stock_list()
    prev_data = load_previous_cache()
    current_data = {}

    for _, row in stock_list.iterrows():
        code = str(row["code"]).zfill(4)
        name = row["name"]

        try:
            df = fetcher.fetch_stock_data(code)
            stage = analyzer.analyze(df)
            current_data[code] = {"name": name, "stage": stage}
            time.sleep(1.5)  # API呼び出し制御

        except Exception as e:
            print(f"[ERROR] {code} {name}: {e}")
            continue

    save_cache(current_data)
    print("[INFO] Screening complete. Detecting changes...")

    # ステージ変化通知
    changes = detect_stage_changes(prev_data, current_data)
    if changes:
        message = "📈 **ステージ変化を検出しました**\n"
        for c in changes:
            message += f"・{c['name']}（{c['code']}）: Stage {c['prev_stage']} → {c['current_stage']}\n"
        notifier.send_discord(DISCORD_NOTIFY_URL, message)
        print(f"[INFO] {len(changes)}件の変化を通知しました。")
    else:
        print("[INFO] ステージ変化なし。")

    # 利確通知
    profits = detect_profit_confirms(prev_data, current_data)
    if profits:
        message = "💰 **利確シグナルを検出しました**\n"
        for p in profits:
            message += f"・{p['name']}（{p['code']}）: Stage {p['prev_stage']} → {p['current_stage']}\n"
        notifier.send_discord(DISCORD_CONFIRM_PROFIT_URL, message)
        print(f"[INFO] {len(profits)}件の利確シグナルを通知しました。")
    else:
        print("[INFO] 利確シグナルなし。")

    print(f"[INFO] Batch Screening finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_batch_screening()
