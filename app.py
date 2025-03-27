# app.py
import streamlit as st
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from alice_client import initialize_alice, save_credentials, load_credentials
from stock_analysis import (
    analyze_all_tokens_bullish,
    analyze_all_tokens_bearish,
    fetch_stock_data_change
)
from stock_lists import STOCK_LISTS

# Custom CSS for animations and styling
st.markdown("""
<style>
@keyframes fadeIn {
    0% { opacity: 0; }
    100% { opacity: 1; }
}

.header-image {
    animation: fadeIn 1.5s;
    margin-bottom: 2rem;
}

.stAlert {
    border-radius: 10px;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
    padding: 8px;
}

.stDataFrame {
    border-radius: 10px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.progress-bar {
    height: 4px;
    background: linear-gradient(90deg, #4F8BF9 0%, #FF4B4B 100%);
    margin-top: 1rem;
    border-radius: 2px;
}

.disclaimer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #ffffff;
    padding: 1rem;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)

# App configuration
st.set_page_config(
    page_title="Stock Screener Pro",
    layout="wide",
    page_icon="📈"
)

# Header with animated logo
st.markdown('<div class="header-image">', unsafe_allow_html=True)
st.image("https://cdn-icons-png.flaticon.com/512/2781/2781399.png", width=100)
st.markdown('</div>', unsafe_allow_html=True)

# Custom warning message with emoji
st.markdown("""
🔔 **Important Notice**  
This screener uses statistical analysis - always verify signals with fundamental analysis.  
Best viewed in **Chrome** | Data delay: 15 minutes
""")

# Auth section with improved layout
def auth_section():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.title("🔒 AliceBlue Login")
    with col2:
        with st.form("auth-form"):
            new_user_id = st.text_input("User ID", type="password")
            new_api_key = st.text_input("API Key", type="password")
            if st.form_submit_button("🚀 Connect"):
                if new_user_id and new_api_key:
                    save_credentials(new_user_id, new_api_key)
                    st.toast("Authentication successful!", icon="✅")
                    st.rerun()
                else:
                    st.error("Please fill both fields!")

# Main screening interface
def main_interface():
    st.title("📊 Stock Screener Pro")
    
    # Strategy cards
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1rem 0;">
        <div style="padding: 1rem; background: #f0f2f6; border-radius: 10px;">
            <h3>📈 Bullish Strategies</h3>
            <ul>
                <li>EMA Golden Cross</li>
                <li>Support Zone Bounce</li>
                <li>RSI Neutrality</li>
            </ul>
        </div>
        <div style="padding: 1rem; background: #f0f2f6; border-radius: 10px;">
            <h3>📉 Bearish Strategies</h3>
            <ul>
                <li>EMA Death Cross</li>
                <li>Resistance Rejection</li>
                <li>RSI Overbought</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Strategy selection with icons
    selected_list = st.selectbox(
        "🏷️ Select Stock List:", 
        list(STOCK_LISTS.keys()),
        help="Choose from pre-configured market indices"
    )
    
    strategy = st.selectbox(
        "🎯 Select Screening Strategy:", 
        [
            "🚀 3-5% Gainers (Intraday Momentum)",
            "🔻 3-5% Losers (Pullback Candidates)",
            "🛡️ Support Zone Strategy (Buy)",
            "⛔ Resistance Zone Strategy (Sell)"
        ],
        index=2
    )

    # Strategy mapping
    strategy_map = {
        "🚀 3-5% Gainers (Intraday Momentum)": ("3-5% Gainers", "up"),
        "🔻 3-5% Losers (Pullback Candidates)": ("3-5% Losers", "down"),
        "🛡️ Support Zone Strategy (Buy)": ("EMA, RSI & Support Zone (Buy)", None),
        "⛔ Resistance Zone Strategy (Sell)": ("EMA, RSI & Resistance Zone (Sell)", None)
    }

    if st.button("🔍 Start Screening", use_container_width=True):
        tokens = STOCK_LISTS.get(selected_list, [])
        if not tokens:
            st.warning("No stocks in selected list!")
        else:
            with st.status("🔎 Scanning market...", expanded=True) as status:
                st.write("Initializing API connection...")
                progress_bar = st.empty()
                
                screened_stocks = fetch_screened_stocks(
                    tokens, 
                    strategy_map[strategy][0]
                )
                
                progress_bar.progress(100, "Analysis complete!")
                status.update(label="Screening complete!", state="complete", expanded=False)
            
            if screened_stocks:
                display_strategy_insights(strategy_map[strategy][0])
                display_results(screened_stocks, strategy_map[strategy][0])
            else:
                st.error("No matching stocks found!")

def display_strategy_insights(strategy):
    """Show strategy-specific visual explanations"""
    with st.expander("📖 Strategy Breakdown", expanded=False):
        if "Support" in strategy:
            st.markdown("""
            **🛡️ Support Zone Strategy Logic:**
            - Price 5-20% above validated support
            - Bullish EMA crossover (50 > 200)
            - RSI between 35-65
            - High volume confirmation
            """)
        elif "Resistance" in strategy:
            st.markdown("""
            **⛔ Resistance Zone Strategy Logic:**
            - Price 5-20% below strong resistance
            - Bearish EMA crossover (50 < 200)
            - RSI between 35-65
            - Volume-supported rejection
            """)

def display_results(data, strategy):
    """Enhanced dataframe display with conditional formatting"""
    df = pd.DataFrame(data)
    
    if df.empty:
        st.warning("No results matching criteria")
        return
    
    # Dynamic column configuration
    grid = st.columns(3)
    with grid[0]:
        st.metric("Total Candidates", len(df))
    with grid[1]:
        avg_rsi = df['RSI'].mean().round(1)
        st.metric("Average RSI", avg_rsi)
    with grid[2]:
        st.metric("Strongest Signal", df.iloc[0]['Name'])
    
    # Interactive search
    search_term = st.text_input("🔍 Filter Results:", "")
    if search_term:
        df = df[df['Name'].str.contains(search_term, case=False)]
    
    # Conditional formatting
    styled_df = df.style.format({
        'Close': '{:.2f}',
        'Support': '{:.2f}',
        'Resistance': '{:.2f}',
        'Distance_pct': '{:.2f}%',
        'RSI': '{:.1f}'
    }).applymap(color_rsi, subset=['RSI'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_order=['Name', 'Close', 'Support' if 'Support' in df.columns else 'Resistance',
                     'Strength', 'Distance_pct', 'RSI', 'Trend']
    )

def color_rsi(val):
    """Color RSI values based on thresholds"""
    if val > 70: return 'background-color: #ffcccc'
    if val < 30: return 'background-color: #ccffcc'
    return ''

@st.cache_data(ttl=300)
def fetch_screened_stocks(tokens, strategy):
    """Optimized fetching with progress tracking"""
    try:
        if strategy == "3-5% Gainers":
            return process_change_signals(tokens, "up")
        elif strategy == "3-5% Losers":
            return process_change_signals(tokens, "down")
        elif "Support" in strategy:
            return analyze_all_tokens_bullish(alice, tokens)
        elif "Resistance" in strategy:
            return analyze_all_tokens_bearish(alice, tokens)
    except Exception as e:
        st.error(f"Screening error: {str(e)}")
        return []

def process_change_signals(tokens, direction):
    """Parallel processing with progress"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_stock_data_change, alice, token, direction): token for token in tokens}
        return [f.result() for f in as_completed(futures) if f.result()]

# Main app flow
try:
    user_id, api_key = load_credentials()
    if not user_id or not api_key:
        auth_section()
    else:
        alice = initialize_alice()
        main_interface()
        
        # Fixed disclaimer footer
        st.markdown("""
        <div class="disclaimer">
        <hr>
        <small>📌 Disclaimer: This tool provides informational purposes only. Past performance ≠ future results. Consult a financial advisor before trading.</small>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Critical error: {str(e)}")
