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

def insert_results_to_db(results):
    """DBに結果を全量INSERT"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # テーブル作成（存在しない場合のみ）
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT,
        market TEXT NOT NULL,
        date TEXT NOT NULL,
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

    # 既存レコード削除
    cur.execute("DELETE FROM analysis_results;")
    conn.commit()

    # 全件INSERT
    for record in results:
        cur.execute("""
            INSERT INTO analysis_results (
                code, name, market, date,
                stock_stage, stock_ema5, stock_ema20, stock_ema40,
                rsi, rsi_delta, macd, macd_signal, macd_histogram,
                recent_golden_cross, recent_dead_cross, atr, closing_price, price_max_since_buy,
                bb_plus_1sigma, bb_plus_2sigma, bb_minus_1sigma, bb_minus_2sigma,
                volume, volume_avg_5d, volume_avg_20d,
                obv, obv_pre_1, obv_pre_2, obv_pre_3, obv_ma_20,
                latest_settlement_date, create_day
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            record['code'], record['name'], record['market'], record['date'],
            record['stock_stage'], record['stock_ema5'], record['stock_ema20'], record['stock_ema40'],
            record['rsi'], record['rsi_delta'], record['macd'], record['macd_signal'], record['macd_histogram'],
            record['recent_golden_cross'], record['recent_dead_cross'], record['atr'], record['closing_price'],
            record['price_max_since_buy'], record['bb_plus_1sigma'], record['bb_plus_2sigma'],
            record['bb_minus_1sigma'], record['bb_minus_2sigma'], record['volume'], record['volume_avg_5d'],
            record['volume_avg_20d'], record['obv'], record['obv_pre_1'], record['obv_pre_2'],
            record['obv_pre_3'], record['obv_ma_20'], record['latest_settlement_date'], record['create_day']
        ))
    conn.commit()
    conn.close()
    print(f"✅ {len(results)} 件の分析結果をDBに格納しました。")

def run_batch():
    loader = TickersLoader()
    tickers = loader.get_all_tickers()
    fetcher = StockDataFetcher()
    stage_analyzer = StageAnalyzer(short_ema_col='EMA_5', mid_ema_col='EMA_20', long_ema_col='EMA_40')
    results = []

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
            stock_stage_str = stage_analyzer.determine_stage(df)
            stock_stage = int(stock_stage_str.replace("ステージ","")) if stock_stage_str.startswith("ステージ") else None

            # 技術指標計算（RSI, MACD, ATR, Bollinger, OBVなど）
            indicators = calculate_indicators(df)  # 戻り値は dict

            closing_price, volume = fetch_latest_price_volume(ticker)
            record = {
                'code': ticker,
                'name': name,
                'market': market,
                'date': datetime.now().strftime("%Y-%m-%d"),
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

    # DBに格納
    insert_results_to_db(results)

if __name__ == "__main__":
    run_batch()
