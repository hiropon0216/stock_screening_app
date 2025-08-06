import sqlite3
import os

# ベースディレクトリを取得（プロジェクトのルート）
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# dbディレクトリへの絶対パスを作成
db_path = os.path.join(base_dir, 'db', 'stock.db')

# 接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブル作成SQL（例）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS holding_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT NOT NULL,
        code TEXT NOT NULL,
        name TEXT,
        market TEXT NOT NULL,
        loss_price REAL NOT NULL,
        buy_price REAL NOT NULL,
        buy_date TEXT NOT NULL,
        possession_flag BOOLEAN NOT NULL,
        create_day TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
