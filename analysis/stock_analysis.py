import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import argrelextrema


# -------------------- Helper Functions -------------------- #

def get_historical_data(alice, token, from_date, to_date, interval="D"):
    """Fetch historical data and return as a DataFrame."""
    instrument = alice.get_instrument_by_token('NSE', token)
    historical_data = alice.get_historical(instrument, from_date, to_date, interval)
    df = pd.DataFrame(historical_data).dropna()
    return instrument, df


def compute_rsi(prices, window=9):
    """Compute the Relative Strength Index (RSI) for a price series."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs)).iloc[-1]


def cluster_zones(zones, prices, tolerance_factor=0.3):
    """Group support or resistance zones based on price proximity."""
    clusters = []
    tolerance = np.std(prices) * tolerance_factor
    for zone in zones:
        found = False
        for cluster in clusters:
            if abs(zone['price'] - cluster['price']) <= tolerance:
                cluster['count'] += 1
                cluster['dates'].append(zone['date'])
                found = True
                break
        if not found:
            clusters.append({
                'price': zone['price'],
                'count': 1,
                'dates': [zone['date']]
            })
    return clusters


# -------------------- Price Change Functions -------------------- #

def fetch_stock_data_change(alice, token, direction="up"):
    """
    Fetch historical data and check if the stock's change meets the target conditions.
    For 'up', checks for a 3% or more gain.
    For 'down', checks for a 3% or more loss (negative).
    """
    try:
        instrument, df = get_historical_data(
            alice, token, datetime.now() - timedelta(days=5), datetime.now(), interval="D"
        )
        if len(df) < 2:
            return None  # Not enough data

        yesterday_close = df['close'].iloc[-1]
        day_before_close = df['close'].iloc[-2]
        pct_change = ((yesterday_close - day_before_close) / day_before_close) * 100

        if direction == "up" and pct_change >= 3:  # 3% or more up
            return {
                'Name': instrument.name,
                'Token': token,
                'Close': yesterday_close,
                'Change (%)': pct_change
            }
        elif direction == "down" and pct_change <= -3:  # 3% or more down
            return {
                'Name': instrument.name,
                'Token': token,
                'Close': yesterday_close,
                'Change (%)': pct_change
            }
    except Exception as e:
        print(f"Error processing token {token}: {e}")
    return None



# -------------------- Analysis Functions -------------------- #

def analyze_stock_bearish(alice, token):
    """
    Analyze stock for bearish signals using resistance zones, EMA crossover, and RSI filter.
    Logic:
      - Resistance zones are determined via local maximum analysis.
      - Current price must be 5-20% below a recent resistance and with sufficient volume.
      - Requires bearish EMA crossover (50 EMA < 200 EMA) and RSI not oversold.
    """
    try:
        instrument, df = get_historical_data(
            alice, token, datetime.now() - timedelta(days=730), datetime.now(), "D"
        )
        if len(df) < 100:
            return None

        df['50_EMA'] = df['close'].ewm(span=50).mean()
        df['200_EMA'] = df['close'].ewm(span=200).mean()
        rsi = compute_rsi(df['close'])

        close_prices = df['close'].values
        scaler = MinMaxScaler()
        normalized_prices = scaler.fit_transform(close_prices.reshape(-1, 1)).flatten()

        window_size = max(int(len(df) * 0.05), 5)
        local_max = argrelextrema(normalized_prices, np.greater_equal, order=window_size)[0]

        valid_resistances = []
        for m in local_max:
            # Only consider recent resistance points (within last 6 months)
            if m < len(df) - 126:
                continue
            resistance_price = close_prices[m]
            current_price = close_prices[-1]
            # Check if current price is 5-20% below resistance
            if 0.80 <= (current_price / resistance_price) <= 0.95:
                if df['volume'].iloc[-1] > df['volume'].iloc[m] * 0.8:
                    valid_resistances.append({
                        'price': resistance_price,
                        'date': df.index[m],
                        'touches': 1
                    })

        if not valid_resistances:
            return None

        resistance_clusters = cluster_zones(valid_resistances, close_prices)
        best_cluster = max(resistance_clusters, key=lambda x: x['count'])

        # Ensure bearish EMA crossover and filter oversold conditions
        if df['50_EMA'].iloc[-1] > df['200_EMA'].iloc[-1] or rsi < 35:
            return None

        current_price = close_prices[-1]
        distance_pct = (current_price / best_cluster['price'] - 1) * 100

        return {
            'Token': token,
            'Name': instrument.name.split('-')[0].strip(),
            'Close': current_price,
            'Resistance': best_cluster['price'],
            'Strength': best_cluster['count'],
            'Distance_pct': distance_pct,
            'RSI': rsi,
            'Trend': 'Bearish'
        }
  
    except Exception as e:
        print(f"Error analyzing bearish for token {token}: {str(e)}")
        return None


def analyze_stock_bullish(alice, token):
    """
    Analyze stock for bullish signals using support zones, EMA crossover, and RSI filter.
    Logic:
      - Support zones are determined via local minimum analysis.
      - Current price must be 5-20% above a recent support and with sufficient volume.
      - Requires bullish EMA crossover (50 EMA > 200 EMA) and RSI not overbought.
    """
    try:
        instrument, df = get_historical_data(
            alice, token, datetime.now() - timedelta(days=730), datetime.now(), "D"
        )
        if len(df) < 100:
            return None

        df['50_EMA'] = df['close'].ewm(span=50).mean()
        df['200_EMA'] = df['close'].ewm(span=200).mean()
        rsi = compute_rsi(df['close'])

        close_prices = df['close'].values
        scaler = MinMaxScaler()
        normalized_prices = scaler.fit_transform(close_prices.reshape(-1, 1)).flatten()

        window_size = max(int(len(df) * 0.05), 5)
        local_min = argrelextrema(normalized_prices, np.less_equal, order=window_size)[0]

        valid_supports = []
        for m in local_min:
            if m < len(df) - 126:
                continue
            support_price = close_prices[m]
            current_price = close_prices[-1]
            # Check if current price is 5-20% above support
            if 1.05 <= (current_price / support_price) <= 1.20:
                if df['volume'].iloc[-1] > df['volume'].iloc[m] * 0.8:
                    valid_supports.append({
                        'price': support_price,
                        'date': df.index[m],
                        'touches': 1
                    })

        if not valid_supports:
            return None

        support_clusters = cluster_zones(valid_supports, close_prices)
        best_cluster = max(support_clusters, key=lambda x: x['count'])

        # Ensure bullish EMA crossover and filter overbought conditions
        if df['50_EMA'].iloc[-1] < df['200_EMA'].iloc[-1] or rsi > 65:
            return None

        current_price = close_prices[-1]
        distance_pct = (current_price / best_cluster['price'] - 1) * 100

        return {
            'Token': token,
            'Name': instrument.name.split('-')[0].strip(),
            'Close': current_price,
            'Support': best_cluster['price'],
            'Strength': best_cluster['count'],
            'Distance_pct': distance_pct,
            'RSI': rsi,
            'Trend': 'Bullish'
        }

    except Exception as e:
        print(f"Error analyzing bullish for token {token}: {str(e)}")
        return None


# -------------------- Batch Analysis Functions -------------------- #

def analyze_all_tokens_bearish(alice, tokens):
    """Analyze all tokens for bearish signals."""
    signals = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_stock_bearish, alice, token): token for token in tokens}
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    return signals


def analyze_all_tokens_bullish(alice, tokens):
    """Analyze all tokens for bullish signals."""
    signals = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_stock_bullish, alice, token): token for token in tokens}
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    return signals
