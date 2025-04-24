import streamlit as st
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from alice_client import initialize_alice, save_credentials, load_credentials
from analysis.stock_analysis import (
    analyze_all_tokens_bullish,
    analyze_all_tokens_bearish
)
from stock_lists import STOCK_LISTS

st.set_page_config(page_title="Stock Screener", layout="wide")
st.warning("This screener is based on statistical analysis. Please conduct your own due diligence before making any trading decisions. This application is best compatible with **Google Chrome**.")

# Try loading stored credentials
user_id, api_key = load_credentials()

if not user_id or not api_key:
    st.title("Admin Login - Enter AliceBlue API Credentials")
    new_user_id = st.text_input("Enter User ID", type="password")  # Hide input
    new_api_key = st.text_input("Enter API Key", type="password")  # Hide input
    if st.button("Login"):
        save_credentials(new_user_id, new_api_key)
        st.success("API credentials saved! Refreshing...")
        st.rerun()

try:
    alice = initialize_alice()
except Exception as e:
    st.error(f"Failed to initialize AliceBlue API: {e}")
    alice = None

@st.cache_data(ttl=300)
def fetch_screened_stocks(tokens, strategy):
    """Fetch and analyze stocks based on selected strategy."""
    try:
        if not alice:
            raise Exception("AliceBlue API is not initialized.")
        
        if strategy == "EMA, RSI & Support Zone (Buy)":
            return analyze_all_tokens_bullish(alice, tokens)

        elif strategy == "EMA, RSI & Resistance Zone (Sell)":
            return analyze_all_tokens_bearish(alice, tokens)
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return []


def clean_and_display_data(data, strategy):
    """Clean and convert the data into a DataFrame based on the strategy."""
    if not data or not isinstance(data, list):
        return pd.DataFrame()
    
    if strategy == "EMA, RSI & Support Zone (Buy)":
        df = pd.DataFrame(data)
        df["Close"] = df["Close"].astype(float).round(2)
        df["Support"] = df["Support"].astype(float).round(2)
        df["Distance_pct"] = df["Distance_pct"].astype(float).round(2)
        df["RSI"] = df["RSI"].astype(float).round(2)
        if "Strength" in df.columns:
            df = df.sort_values(by="Strength", ascending=False)
        
    elif strategy == "EMA, RSI & Resistance Zone (Sell)":
        df = pd.DataFrame(data)
        df["Close"] = df["Close"].astype(float).round(2)
        df["Resistance"] = df["Resistance"].astype(float).round(2)
        df["Distance_pct"] = df["Distance_pct"].astype(float).round(2)
        df["RSI"] = df["RSI"].astype(float).round(2)
        if "Strength" in df.columns:
            df = df.sort_values(by="Strength", ascending=False)
    
    return df


def safe_display(df, title):
    """Displays the stock data with clickable TradingView links."""
    if df.empty:
        st.warning(f"No stocks found for {title}")
    else:
        st.markdown(f"## {title}")
        if "Name" in df.columns:
            df["Name"] = df["Name"].apply(lambda x: f'<a href="https://in.tradingview.com/chart?symbol=NSE%3A{x}" target="_blank">{x}</a>')
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)


st.title("Stock Screener")

# Apply custom CSS to adjust column width
st.markdown("""
    <style>
        table { width: 100% !important; }
        th, td { padding: 10px !important; text-align: left !important; }
        td:nth-child(1) { min-width: 200px !important; }
        a { white-space: nowrap; }
    </style>
""", unsafe_allow_html=True)

selected_list = st.selectbox("Select Stock List:", list(STOCK_LISTS.keys()))
strategy = st.selectbox(
    "Select Strategy:", 
    [
        "EMA, RSI & Support Zone (Buy)",
        "EMA, RSI & Resistance Zone (Sell)"
    ]
)

if st.button("Start Screening"):
    tokens = STOCK_LISTS.get(selected_list, [])
    if not tokens:
        st.warning(f"No stocks found for {selected_list}.")
    else:
        with st.spinner("Fetching and analyzing stocks..."):
            screened_stocks = fetch_screened_stocks(tokens, strategy)
        df = clean_and_display_data(screened_stocks, strategy)
        safe_display(df, strategy)
