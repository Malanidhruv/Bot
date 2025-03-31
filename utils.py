import pandas as pd
import streamlit as st

def generate_tradingview_link(stock_name):
    """Generate a TradingView link for a given stock."""
    return f'<a href="https://in.tradingview.com/chart?symbol=NSE%3A{stock_name}" target="_blank">{stock_name}</a>'

def print_stocks_up(stocks):
    """Prints the stocks that gained 3-5% in descending order with TradingView links."""
    stocks_sorted = sorted(stocks, key=lambda x: -x['Change (%)'])  # Sort by highest Change% first
    
    print("\nStocks that were 3-5% up yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    
    for stock in stocks_sorted:
        link = f"https://in.tradingview.com/chart?symbol=NSE%3A{stock['Name']}"
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}  {link}")
    
    print('-' * 50)

def print_stocks_down(stocks):
    """Prints the stocks that lost 3-5% in descending order with TradingView links."""
    stocks_sorted = sorted(stocks, key=lambda x: x['Change (%)'])  # Sort by lowest Change% first (biggest drop on top)
    
    print("\nStocks that were 3-5% down yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)
    
    for stock in stocks_sorted:
        link = f"https://in.tradingview.com/chart?symbol=NSE%3A{stock['Name']}"
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}  {link}")
    
    print('-' * 50)

def display_buy_candidates(signals):
    """Displays the top 10 buy candidates in a Streamlit app with clickable links."""
    st.subheader("🚀 Top 10 Buy Candidates (Sorted by Strength)")
    
    if not signals:
        st.warning("No buy candidates found.")
        return
    
    # Corrected sorting order: Strength (highest first), then Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))
    top_candidates = sorted_signals[:10]
    
    df = pd.DataFrame(top_candidates)
    
    # Convert stock names into TradingView links
    df['Name'] = df['Name'].apply(generate_tradingview_link)
    
    # Select relevant columns
    df = df[['Name', 'Close', 'Support', 'Strength', 'Distance_pct', 'RSI', 'Trend']]
    
    # Display DataFrame with HTML rendering
    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

def display_sell_candidates(signals):
    """Displays the top 10 sell candidates in a Streamlit app with clickable links."""
    st.subheader("🔻 Top 10 Sell Candidates (Sorted by Strength)")
    
    if not signals:
        st.warning("No sell candidates found.")
        return
    
    # Corrected sorting order: Strength (highest first), then Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))
    top_candidates = sorted_signals[:10]
    
    df = pd.DataFrame(top_candidates)
    
    # Convert stock names into TradingView links
    df['Name'] = df['Name'].apply(generate_tradingview_link)
    
    # Select relevant columns
    df = df[['Name', 'Close', 'Resistance', 'Strength', 'Distance_pct', 'RSI', 'Trend']]
    
    # Display DataFrame with HTML rendering
    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
