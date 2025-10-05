# app/BatchScreening.py
import os
import sqlite3
from datetime import datetime
import pandas as pd
import yfinance as yf
from TickersLoader import TickersLoader
from StockDataFetcher import StockDataFetcher
from StageAnalyzer import StageAnalyzer
from TechnicalIndicators import calculate_indicators  # RSI, MACD, ATR, BB, OBV計算

DB_PATH = "db/buy_sell_analysis.db"

# -------------------------
# DB操作関連
# -------------------------
def create_analysis_table(conn):
    """分析結果テーブル作成"""
    create_sql = """
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
    conn.execute(create_sql)
    conn.commit()

def clear_analysis_table(conn):
    """既存レコードを削除"""
    conn.execute("DELETE FROM analysis_results;")
    conn.commit()

def insert_results(conn, results):
    """分析結果をDBにINSERT"""
    insert_sql = """
        INSERT INTO analysis_results (
            code, name, market, date, topix_stage, topix_ema5, topix_ema20, topix_ema40,
            stock_stage, stock_ema5, stock_ema20, stock_ema40, rsi, rsi_delta,
            macd, macd_signal, macd_histogram, recent_golden_cross, recent_dead_cross,
            atr, closing_price, price_max_since_buy,
            bb_plus_1sigma, bb_plus_2sigma, bb_minus_1sigma, bb_minus_2sigma,
            volume, volume_avg_5d, volume_avg_20d,
            obv, obv_pre_1, obv_pre_2, obv_pre_3, obv_ma_20,
            latest_settlement_date, create_day
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    for record in results:
        conn.execute(insert_sql, (
            record['code'], record['name'], record['market'], record['date'], record['topix_stage'],
            record['topix_ema5'], record['topix_ema20'], record['topix_ema40'],
            record['stock_stage'], record['stock_ema5'], record['stock_ema20'], record['stock_ema40'],
            record['rsi'], record['rsi_delta'], record['macd'], record['macd_signal'], record['macd_histogram'],
            record['recent_golden_cross'], record['recent_dead_cross'], record['atr'], record['closing_price'],
            record['price_max_since_buy'], record['bb_plus_1sigma'], record['bb_plus_2sigma'],
            record['bb_minus_1sigma'], record['bb_minus_2sigma'], record['volume'], record['volume_avg_5d'],
            record['volume_avg_20d'], record['obv'], record['obv_pre_1'], record['obv_pre_2'], record['obv_pre_3'],
            record['obv_ma_20'], record['latest_settlement_date'], record['create_day']
        ))
    conn.commit()
    print(f"✅ {len(results)} 件の分析結果をDBに格納しました。")

# -------------------------
# 株価取得関連
# -------------------------
def fetch_latest_price_volume(ticker):
    """最新株価と出来高を取得"""
    try:
        df = yf.Ticker(ticker).history(period='5d')
        df = df[df['Close'].notnull()]
        if df.empty:
            return None, None
        latest_row = df.iloc[-1]
        latest_date = latest_row.name.to_pydatetime().date()
        today = datetime.now().date()
        if latest_date > today:
            return None, None
        return float(latest_row['Close']), int(latest_row['Volume'])
    except Exception as e:
        print(f"{ticker}: 最新株価・出来高取得エラー: {e}")
        return None, None

# -------------------------
# メイン処理
# -------------------------
def run_batch():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_analysis_table(conn)
    clear_analysis_table(conn)

    loader = TickersLoader()
    tickers = loader.get_all_tickers()
    fetcher = StockDataFetcher()
    stage_analyzer = StageAnalyzer(short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40')
    results = []

    # TOPIX取得
    topix_df = fetcher.fetch("^TOPX")
    topix_stage_analyzer = StageAnalyzer(short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40')
    latest_topix_row = topix_df.iloc[-1]
    topix_stage = int(topix_stage_analyzer.determine_stage(latest_topix_row).replace("ステージ",""))
    topix_ema5 = latest_topix_row['EMA_5']
    topix_ema20 = latest_topix_row['EMA_20']
    topix_ema40 = latest_topix_row['EMA_40']

    for item in tickers:
        ticker = item['symbol']
        name = item['銘柄名']
        market = item.get('市場・商品区分','')
        print(f"処理中: {ticker} - {name} - {market}")
        try:
            df = fetcher.fetch(ticker)
            if df is None or df.empty:
                continue

            latest_row = df.iloc[-1]
            stock_stage_str = stage_analyzer.determine_stage(latest_row)
            stock_stage = int(stock_stage_str.replace("ステージ","")) if stock_stage_str.startswith("ステージ") else None

            # 技術指標計算
            indicators = calculate_indicators(df)

            closing_price, volume = fetch_latest_price_volume(ticker)
            record = {
                'code': ticker,
                'name': name,
                'market': market,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'topix_stage': topix_stage,
                'topix_ema5': topix_ema5,
                'topix_ema20': topix_ema20,
                'topix_ema40': topix_ema40,
                'stock_stage': stock_stage,
                'stock_ema5': latest_row['EMA_5'],
                'stock_ema20': latest_row['EMA_20'],
                'stock_ema40': latest_row['EMA_40'],
                'rsi': indicators['rsi'],
                'rsi_delta': indicators['rsi_delta'],
                'macd': indicators['macd'],
                'macd_signal': indicators['macd_signal'],
                'macd_histogram': indicators['macd_histogram'],
                'recent_golden_cross': indicators['recent_golden_cross'],
                'recent_dead_cross': indicators['recent_dead_cross'],
                'atr': indicators['atr'],
                'closing_price': closing_price,
                'price_max_since_buy': indicators.get('price_max_since_buy'),
                'bb_plus_1sigma': indicators['bb_plus_1sigma'],
                'bb_plus_2sigma': indicators['bb_plus_2sigma'],
                'bb_minus_1sigma': indicators['bb_minus_1sigma'],
                'bb_minus_2sigma': indicators['bb_minus_2sigma'],
                'volume': volume,
                'volume_avg_5d': indicators['volume_avg_5d'],
                'volume_avg_20d': indicators['volume_avg_20d'],
                'obv': indicators['obv'],
                'obv_pre_1': indicators['obv_pre_1'],
                'obv_pre_2': indicators['obv_pre_2'],
                'obv_pre_3': indicators['obv_pre_3'],
                'obv_ma_20': indicators['obv_ma_20'],
                'latest_settlement_date': item.get('latest_settlement_date'),
                'create_day': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(record)
        except Exception as e:
            print(f"エラー: {ticker} - {name}: {e}")
            continue

    insert_results(conn, results)
    conn.close()

if __name__ == "__main__":
    run_batch()
