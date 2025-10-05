import os
import sqlite3
from datetime import datetime

def create_buy_sell_analysis_db():
    # 出力先ディレクトリを作成
    output_dir = "db"
    os.makedirs(output_dir, exist_ok=True)

    # DBファイルパス
    db_path = os.path.join(output_dir, "buy_sell_analysis.db")

    # 既存DBを削除して再作成（※上書きしたくない場合はコメントアウト）
    if os.path.exists(db_path):
        os.remove(db_path)

    # DB接続
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # テーブル作成SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT,
        market TEXT NOT NULL,
        date TEXT NOT NULL,
        topix_stage INTEGER NOT NULL,
        topix_ema5 REAL NOT NULL,
        topix_ema20 REAL NOT NULL,
        topix_ema40 REAL NOT NULL,
        stock_stage INTEGER NOT NULL,
        stock_ema5 REAL NOT NULL,
        stock_ema20 REAL NOT NULL,
        stock_ema40 REAL NOT NULL,
        rsi REAL NOT NULL,
        rsi_delta REAL NOT NULL,
        macd REAL NOT NULL,
        macd_signal REAL NOT NULL,
        macd_histogram REAL NOT NULL,
        recent_golden_cross BOOLEAN NOT NULL,
        recent_dead_cross BOOLEAN NOT NULL,
        atr REAL NOT NULL,
        closing_price REAL NOT NULL,
        price_max_since_buy REAL,
        bb_plus_1sigma REAL NOT NULL,
        bb_plus_2sigma REAL NOT NULL,
        bb_minus_1sigma REAL NOT NULL,
        bb_minus_2sigma REAL NOT NULL,
        volume REAL NOT NULL,
        volume_avg_5d REAL NOT NULL,
        volume_avg_20d REAL NOT NULL,
        obv REAL NOT NULL,
        obv_pre_1 REAL NOT NULL,
        obv_pre_2 REAL NOT NULL,
        obv_pre_3 REAL NOT NULL,
        obv_ma_20 REAL NOT NULL,
        latest_settlement_date TEXT,
        create_day TEXT NOT NULL
    );
    """

    cur.execute(create_table_sql)
    conn.commit()

    print(f"✅ データベース '{db_path}' にテーブル 'analysis_results' を作成しました。")

    # 確認用：メタデータ出力
    cur.execute("PRAGMA table_info(analysis_results);")
    columns = cur.fetchall()
    print("\n📋 テーブル構造:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # 終了処理
    conn.close()


if __name__ == "__main__":
    create_buy_sell_analysis_db()
