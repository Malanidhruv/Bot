import pandas as pd
import streamlit as st
import json

def generate_tradingview_link(stock_name):
    """Generate a TradingView link for a given stock."""
    return f'<a href="https://in.tradingview.com/chart?symbol=NSE%3A{stock_name}" target="_blank">{stock_name}</a>'

def print_stocks_up(stocks):
    """Prints the stocks that gained 3-5% in descending order with TradingView links."""
    
    # Debugging: Print raw data before sorting
    print("\nRaw Data Before Sorting (Stocks Up):")
    print(json.dumps(stocks, indent=2))
    
    # Convert Change% to float safely
    for stock in stocks:
        stock['Change (%)'] = float(stock.get('Change (%)', 0))  # Default to 0 if missing
    
    stocks_sorted = sorted(stocks, key=lambda x: -x['Change (%)'])  # Sort by Change % descending

    print("\nSorted Data (Stocks Up):")
    print(json.dumps(stocks_sorted, indent=2))  # Debug output

    print("\nStocks that were 3-5% up yesterday:")
    print(f"{'Name':<20} {'Token':<10} {'Close':<10} {'Change (%)':<10}")
    print('-' * 50)

    for stock in stocks_sorted:
        link = f"https://in.tradingview.com/chart?symbol=NSE%3A{stock['Name']}"
        print(f"{stock['Name']:<20} {stock['Token']:<10} {stock['Close']:<10.2f} {stock['Change (%)']:<10.2f}  {link}")
    
    print('-' * 50)

def print_stocks_down(stocks):
    """Prints the stocks that lost 3-5% in descending order with TradingView links."""
    
    # Debugging: Print raw data before sorting
    print("\nRaw Data Before Sorting (Stocks Down):")
    print(json.dumps(stocks, indent=2))
    
    # Convert Change% to float safely
    for stock in stocks:
        stock['Change (%)'] = float(stock.get('Change (%)', 0))  # Default to 0 if missing
    
    stocks_sorted = sorted(stocks, key=lambda x: x['Change (%)'])  # Sort by Change % ascending

    print("\nSorted Data (Stocks Down):")
    print(json.dumps(stocks_sorted, indent=2))  # Debug output

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

    # Debug: Print data before sorting
    st.text("Raw Buy Candidates Data:")
    st.text(json.dumps(signals[:10], indent=2))  # Pretty-print first 10 entries

    # Convert Strength & Distance_pct to float safely
    for signal in signals:
        signal['Strength'] = float(signal.get('Strength', 0))  # Default to 0 if missing
        signal['Distance_pct'] = float(signal.get('Distance_pct', 0))  # Default to 0 if missing

    # Corrected sorting order: Strength (highest first), then Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))

    # Debug: Print sorted data
    st.text("Sorted Data:")
    st.text(json.dumps(sorted_signals[:10], indent=2))

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

    # Debug: Print data before sorting
    st.text("Raw Sell Candidates Data:")
    st.text(json.dumps(signals[:10], indent=2))  # Pretty-print first 10 entries

    # Convert Strength & Distance_pct to float safely
    for signal in signals:
        signal['Strength'] = float(signal.get('Strength', 0))  # Default to 0 if missing
        signal['Distance_pct'] = float(signal.get('Distance_pct', 0))  # Default to 0 if missing

    # Corrected sorting order: Strength (highest first), then Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance_pct']))

    # Debug: Print sorted data
    st.text("Sorted Data:")
    st.text(json.dumps(sorted_signals[:10], indent=2))

    top_candidates = sorted_signals[:10]
    
    df = pd.DataFrame(top_candidates)
    
    # Convert stock names into TradingView links
    df['Name'] = df['Name'].apply(generate_tradingview_link)
    
    # Select relevant columns
    df = df[['Name', 'Close', 'Resistance', 'Strength', 'Distance_pct', 'RSI', 'Trend']]
    
    # Display DataFrame with HTML rendering
    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
