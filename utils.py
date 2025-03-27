# utils.py
import pandas as pd
import streamlit as st

def print_stocks_up(stocks):
    """Prints the stocks that gained 3-5%."""
    print("\nStocks that were 3-5% up yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    for stock in stocks:
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}")
    print('-' * 50)

def print_stocks_down(stocks):
    """Prints the stocks that lost 3-5%."""
    print("\nStocks that were 3-5% down yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    for stock in stocks:
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}")
    print('-' * 50)

def display_buy_candidates(signals):
    """
    Displays the top 10 buy (bullish) candidates in a Streamlit app.
    Enhanced with better error handling and formatting.
    """
    st.subheader("🚀 Top 10 Buy Candidates (Bullish)")
    
    if not signals:
        st.warning("No buy candidates found.")
        return
    
    # Sort candidates by highest strength first, then by lowest distance percentage
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))
    top_candidates = sorted_signals[:10]
    
    # Create a DataFrame with the expected bullish candidate columns
    df = pd.DataFrame(top_candidates)[['Name', 'Close', 'Support', 'Strength', 'Distance_pct', 'RSI', 'Trend']]
    
    # Formatting for better display
    st.dataframe(df.style.format({
        'Close': '{:.2f}',
        'Support': '{:.2f}',
        'Distance_pct': '{:.2f}%',
        'RSI': '{:.1f}'
    }))

def display_sell_candidates(signals):
    """
    Displays the top 10 sell (bearish) candidates in a Streamlit app.
    Enhanced with better error handling and formatting.
    """
    st.subheader("🔻 Top 10 Sell Candidates (Bearish)")
    
    if not signals:
        st.warning("No sell candidates found.")
        return
    
    # Sort candidates by highest strength first, then by lowest distance percentage
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))
    top_candidates = sorted_signals[:10]
    
    # Create a DataFrame with the expected bearish candidate columns
    df = pd.DataFrame(top_candidates)[['Name', 'Close', 'Resistance', 'Strength', 'Distance_pct', 'RSI', 'Trend']]
    
    # Formatting for better display
    st.dataframe(df.style.format({
        'Close': '{:.2f}',
        'Resistance': '{:.2f}',
        'Distance_pct': '{:.2f}%',
        'RSI': '{:.1f}'
    }))
