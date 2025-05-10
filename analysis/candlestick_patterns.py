import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import talib
import numpy as np


# -------------------- Helper -------------------- #

def get_historical_data(alice, token, from_date, to_date, interval="D"):
    """Fetch historical data and return as a DataFrame."""
    instrument = alice.get_instrument_by_token('NSE', token)
    historical_data = alice.get_historical(instrument, from_date, to_date, interval)
    df = pd.DataFrame(historical_data).dropna()
    return instrument, df


# -------------------- Pattern Dictionary -------------------- #

SINGLE_CANDLE_PATTERNS = {
    'bullish': ['CDLHAMMER', 'CDLDOJI', 'CDLINVERTEDHAMMER'],
    'bearish': ['CDLSHOOTINGSTAR', 'CDLHANGINGMAN']
}

MULTIPLE_CANDLE_PATTERNS = {
    'bullish': ['CDLENGULFING', 'CDLPIERCING', 'CDLMORNINGSTAR'],
    'bearish': ['CDLENGULFING', 'CDLDARKCLOUDCOVER', 'CDLEVENINGSTAR']
}


# -------------------- Pattern Detection -------------------- #

def detect_patterns(df, pattern_list):
    results = {}
    for pattern_name in pattern_list:
        pattern_func = getattr(talib, pattern_name, None)
        if not pattern_func:
            continue
        result = pattern_func(df['open'], df['high'], df['low'], df['close'])
        results[pattern_name] = result
    return results


def analyze_candlestick_pattern(alice, token, candle_type='single', direction='bullish'):
    try:
        instrument, df = get_historical_data(
            alice, token, datetime.now() - timedelta(days=100), datetime.now(), interval="D"
        )
        if len(df) < 50:
            return None

        pattern_dict = SINGLE_CANDLE_PATTERNS if candle_type == 'single' else MULTIPLE_CANDLE_PATTERNS
        pattern_list = pattern_dict[direction]

        patterns = detect_patterns(df, pattern_list)

        for pattern_name, signal in patterns.items():
            if direction == 'bullish' and signal.iloc[-1] > 0:
                return {
                    'Token': token,
                    'Name': instrument.name.split('-')[0].strip(),
                    'Close': df['close'].iloc[-1],
                    'Pattern': pattern_name,
                    'Direction': 'Bullish'
                }
            elif direction == 'bearish' and signal.iloc[-1] < 0:
                return {
                    'Token': token,
                    'Name': instrument.name.split('-')[0].strip(),
                    'Close': df['close'].iloc[-1],
                    'Pattern': pattern_name,
                    'Direction': 'Bearish'
                }
    except Exception as e:
        print(f"Error in candlestick pattern analysis for token {token}: {e}")
        return None


# -------------------- Batch Analysis -------------------- #

def analyze_all_tokens_patterns(alice, tokens, candle_type='single', direction='bullish'):
    signals = []
    with ThreadPoolExecutor(max_workers=300) as executor:
        futures = {
            executor.submit(analyze_candlestick_pattern, alice, token, candle_type, direction): token
            for token in tokens
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    return signals
