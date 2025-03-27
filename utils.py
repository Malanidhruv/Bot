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
    """Displays the top 10 buy candidates in a Streamlit app."""
    st.subheader("🚀 Top 10 Buy Candidates (Sorted by Strength)")
    
    # Sort first by Strength (highest first), then by Distance% (lowest first)
    sorted_signals = sorted(signals, key=lambda x: (-x['Strength'], x['Distance%']))
    
    # Select the top 10 candidates after sorting
    top_candidates = sorted_signals[:10]
    
    if top_candidates:
        df = pd.DataFrame(top_candidates)
        df = df[['Name', 'Price', 'Support', 'Strength', 'Distance%', 'RSI', 'Trend']]
        st.dataframe(df)
    else:
        st.write("No buy candidates found.")

