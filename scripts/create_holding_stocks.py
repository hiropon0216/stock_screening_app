import sqlite3

# DB接続（なければ stock.db が作られる）
conn = sqlite3.connect("db/holding_stocks.db")
cursor = conn.cursor()

# CREATE文の実行
cursor.execute("""
CREATE TABLE IF NOT EXISTS holding_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position TEXT NOT NULL, 
    code TEXT NOT NULL,
    name TEXT,
    market TEXT NOT NULL,
    loss_price REAL NOT NULL,
    buy_price REAL NOT NULL,
    buy_date TEXT NOT NULL,
    create_day TEXT NOT NULL
);
""")

conn.commit()
conn.close()
