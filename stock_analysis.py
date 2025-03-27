import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import argrelextrema


def fetch_stock_data_up(alice, token):
    """Fetch historical data and check if the stock gained 3-5%."""
    try:
        instrument = alice.get_instrument_by_token('NSE', token)
        to_datetime = datetime.now()
        from_datetime = to_datetime - timedelta(days=5)
        interval = "D"
        historical_data = alice.get_historical(instrument, from_datetime, to_datetime, interval)
        df = pd.DataFrame(historical_data)

        if len(df) < 2:
            return None  # Not enough data

        yesterday_close = df['close'].iloc[-1]
        day_before_close = df['close'].iloc[-2]
        pct_change = ((yesterday_close - day_before_close) / day_before_close) * 100

        if 3 <= pct_change <= 5:
            return {
                'Name': instrument.name,
                'Token': token,
                'Close': yesterday_close,
                'Change (%)': pct_change
            }
    except Exception as e:
        print(f"Error processing token {token}: {e}")
    return None


def fetch_stock_data_down(alice, token):
    """Fetch historical data and check if the stock lost 3-5%."""
    try:
        instrument = alice.get_instrument_by_token('NSE', token)
        to_datetime = datetime.now()
        from_datetime = to_datetime - timedelta(days=5)
        interval = "D"
        historical_data = alice.get_historical(instrument, from_datetime, to_datetime, interval)
        df = pd.DataFrame(historical_data)

        if len(df) < 2:
            return None  # Not enough data

        yesterday_close = df['close'].iloc[-1]
        day_before_close = df['close'].iloc[-2]
        pct_change = ((yesterday_close - day_before_close) / day_before_close) * 100

        if -5 <= pct_change <= -3:
            return {
                'Name': instrument.name,
                'Token': token,
                'Close': yesterday_close,
                'Change (%)': pct_change
            }
    except Exception as e:
        print(f"Error processing token {token}: {e}")
    return None


def compute_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs)).iloc[-1]

def analyze_stock(alice, token):
    """Analyze stock for bearish signals using resistance, EMA, and RSI."""
    try:
        instrument = alice.get_instrument_by_token('NSE', token)
        from_date = datetime.now() - timedelta(days=730)
        historical_data = alice.get_historical(instrument, from_date, datetime.now(), "D")
        df = pd.DataFrame(historical_data).dropna()

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
            if m < len(df) - 126:  # Older than 6 months
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

        resistance_clusters = []
        tolerance = np.std(close_prices) * 0.3
        for res in valid_resistances:
            found = False
            for cluster in resistance_clusters:
                if abs(res['price'] - cluster['price']) <= tolerance:
                    cluster['count'] += 1
                    found = True
                    break
            if not found:
                resistance_clusters.append({
                    'price': res['price'],
                    'count': 1,
                    'dates': [res['date']]
                })

        if not resistance_clusters:
            return None

        best_cluster = max(resistance_clusters, key=lambda x: x['count'])

        # Require bearish EMA crossover
        if df['50_EMA'].iloc[-1] > df['200_EMA'].iloc[-1]:
            return None

        # Filter out oversold conditions
        if rsi < 35:
            return None

        current_price = close_prices[-1]
        distance_pct = (current_price / best_cluster['price'] - 1) * 100

        return {
            'Token': token,
            'Name': instrument.name.split('-')[0].strip(),
            'Price': current_price,
            'Resistance': best_cluster['price'],
            'Strength': best_cluster['count'],
            'Distance%': distance_pct,
            'RSI': rsi,
            'Trend': 'Bearish' if df['50_EMA'].iloc[-1] < df['200_EMA'].iloc[-1] else 'Bullish'
        }
    except Exception as e:
        print(f"Error analyzing {token}: {str(e)}")
        return None

def analyze_all_tokens(alice, tokens):
    """Analyze all tokens and collect bearish signals."""
    signals = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_stock, alice, token): token for token in tokens}
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    return signals
