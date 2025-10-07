# app/TechnicalIndicators.py
import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    df: yfinanceで取得した株価データ (Open, High, Low, Close, Volume)
    戻り値: 各種指標を dict 形式で返す
    """
    indicators = {}

    # ----- RSI（14日） -----
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    indicators['rsi'] = rsi.iloc[-1] if not rsi.empty else None
    indicators['rsi_delta'] = rsi.diff().iloc[-1] if len(rsi) > 1 else None

    # ----- MACD（12,26,9 EMA） -----
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    indicators['macd'] = macd_line.iloc[-1]
    indicators['macd_signal'] = signal_line.iloc[-1]
    indicators['macd_histogram'] = macd_hist.iloc[-1]

    # ----- ATR（14日） -----
    high_low = df['High'] - df['Low']
    high_close_prev = (df['High'] - df['Close'].shift()).abs()
    low_close_prev = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    indicators['atr'] = atr.iloc[-1]

    # ----- Bollinger Bands（20日, 1σ/2σ） -----
    sma20 = df['Close'].rolling(20).mean()
    std20 = df['Close'].rolling(20).std()
    indicators['bb_plus_1sigma'] = sma20.iloc[-1] + std20.iloc[-1]
    indicators['bb_plus_2sigma'] = sma20.iloc[-1] + 2*std20.iloc[-1]
    indicators['bb_minus_1sigma'] = sma20.iloc[-1] - std20.iloc[-1]
    indicators['bb_minus_2sigma'] = sma20.iloc[-1] - 2*std20.iloc[-1]

    # ----- OBV -----
    obv = ((df['Close'].diff() > 0).astype(int)*2 - 1) * df['Volume']
    obv = obv.cumsum()
    indicators['obv'] = obv.iloc[-1]
    indicators['obv_pre_1'] = obv.iloc[-2] if len(obv) > 1 else None
    indicators['obv_pre_2'] = obv.iloc[-3] if len(obv) > 2 else None
    indicators['obv_pre_3'] = obv.iloc[-4] if len(obv) > 3 else None
    indicators['obv_ma_20'] = obv.rolling(20).mean().iloc[-1]

    # ----- EMA5, EMA20 ゴールデンクロス/デッドクロス判定 -----
    ema5 = df['Close'].ewm(span=5, adjust=False).mean()
    ema20 = df['Close'].ewm(span=20, adjust=False).mean()

    if len(ema5) >= 2 and len(ema20) >= 2:
        prev_ema5 = float(ema5.iloc[-2])
        prev_ema20 = float(ema20.iloc[-2])
        curr_ema5 = float(ema5.iloc[-1])
        curr_ema20 = float(ema20.iloc[-1])

        recent_cross = (prev_ema5 < prev_ema20) and (curr_ema5 > curr_ema20)
        recent_dead_cross = (prev_ema5 > prev_ema20) and (curr_ema5 < curr_ema20)
    else:
        recent_cross = False
        recent_dead_cross = False

    indicators['recent_golden_cross'] = recent_cross
    indicators['recent_dead_cross'] = recent_dead_cross

    # ----- Volume 平均 -----
    indicators['volume_avg_5d'] = df['Volume'].rolling(5).mean().iloc[-1]
    indicators['volume_avg_20d'] = df['Volume'].rolling(20).mean().iloc[-1]

    # ----- 直近の最高値（price_max_since_buy） -----
    indicators['price_max_since_buy'] = df['Close'].max()

    return indicators
