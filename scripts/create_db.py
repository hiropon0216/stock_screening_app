import sqlite3
import os

# ディレクトリとDBパスの指定
db_dir = os.path.join(os.path.dirname(__file__), "..", "db")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "screened_stocks.db")

# DB接続とテーブル作成
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS screened_stocks (
    symbol TEXT NOT NULL,
    name TEXT,
    date TEXT NOT NULL,
    price REAL NOT NULL,

    obv_1 REAL,
    obv_2 REAL,
    obv_3 REAL,
    obv_ma20 REAL,

    volume_ma5 INTEGER,
    volume_ma20 INTEGER,

    rsi REAL,

    macd REAL,
    macd_signal REAL,
    macd_cross_days INTEGER,

    close_band_sigma TEXT,
    band_width_trend TEXT,

    score INTEGER NOT NULL,
    signal TEXT NOT NULL,

    entry_price REAL,
    atr_entry REAL,
    stop_loss_price REAL,
    tp_multiplier REAL,
    entry_date TEXT,
    position_type TEXT,

    PRIMARY KEY(symbol, date)
);
''')

conn.commit()
conn.close()

print(f"✅ DB作成完了: {db_path}")
