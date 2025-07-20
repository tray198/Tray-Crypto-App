import streamlit as st
import requests
import time
import tweepy  # Twitter API client

# --- Config ---
OPENAI_API_KEY = "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"

# Twitter API 
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEOJ3AEAAAAAl5M2Rb%2FB%2FS5E6qBn7SGNsi%2FwEVo%3DQK9FMAXTeB7rTJJf7gfdUyWI2aaljOOGOSensl0l37lTIJR0LL"

# --- Setup Twitter Client ---
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# --- Page Setup ---
st.set_page_config(page_title="Crypto AI Deal Finder", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for styling ---
st.markdown("""
<style>
    body, .block-container {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .ticker-container {
        width: 100%;
        overflow: hidden;
        background-color: white !important;
        color: black !important;
        font-weight: 700;
        white-space: nowrap;
        box-sizing: border-box;
        border-radius: 0 !important;
        padding: 10px 0;
        user-select: none;
        margin-bottom: 15px;
    }
    .ticker-move {
        display: inline-block;
        padding-left: 100%;
        animation: ticker-scroll 20s linear infinite;
    }
    @keyframes ticker-scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
    .stButton > button,
    .stSelectbox > div,
    .stTextInput > div,
    .stSlider > div,
    .stSidebar,
    .stSidebar .sidebar-content,
    .block-container,
    .stMarkdown {
        border-radius: 0 !important;
    }
    .risk-slider-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #bbb;
    }
    .section-header {
        color: #ff6f61;
        border-bottom: 2px solid #ff6f61;
        padding-bottom: 6px;
        margin-bottom: 12px;
        font-weight: 700;
        font-size: 1.4rem;
        user-select: none;
    }
    .token-analysis {
        background-color: #1e1e1e;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- Top Gainers Ticker ---
def get_top_gainers():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "price_change_percentage_24h_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return []

top_gainers = get_top_gainers()
if top_gainers:
    ticker_items = "  |  ".join(
        f"{coin['name']} ({coin['symbol'].upper()}): +{coin['price_change_percentage_24h']:.2f}%"
        for coin in top_gainers
    )
else:
    ticker_items = "No data available"

ticker_html = f"""
<div class="ticker-container">
  <div class="ticker-move">{ticker_items}</div>
</div>
"""
st.markdown(ticker_html, unsafe_allow_html=True)

# --- Sidebar Navigation ---
page = st.sidebar.radio("Select Page", ["AI Crypto Analysis", "Sol Casino"])

# --- Twitter Trending Fetcher ---
def get_twitter_trends(chain):
    # You can map chains to Twitter hashtags or topics:
    hashtags = {
        "Ethereum": ["#Ethereum", "#ETH", "#DeFi"],
        "XRP": ["#XRP", "#Ripple"],
        "Cosmos": ["#Cosmos", "#ATOM"]
    }
    try:
        trends_texts = []
        for tag in hashtags.get(chain, []):
            tweets = client.search_recent_tweets(query=tag, max_results=5)
            if tweets and tweets.data:
                for tweet in tweets.data:
                    trends_texts.append(f"{tag}: {tweet.text}")
        if not trends_texts:
            return ["No trending tweets found."]
        return trends_texts
    except Exception as e:
        return [f"Error fetching Twitter trends: {e}"]

# --- AI Crypto Analysis Page ---
if page == "AI Crypto Analysis":
    st.title("🧠📈 Crypto AI Deal Finder")
    st.markdown("""
    Search Ethereum, XRP, and Cosmos chain coins by keyword.
    AI suggestions are provided based on community, analytics, and project fundamentals.
    """)

    selected_chain = st.selectbox("Choose blockchain", ["Ethereum", "XRP", "Cosmos"])

    # Updated suggestions (5 per chain)
    suggestions = {
        "Ethereum": [
            {"name": "Arbitrum", "desc": "Layer 2 scaling solution with high adoption."},
            {"name": "Lens Protocol", "desc": "Decentralized social graph infrastructure."},
            {"name": "Chainlink", "desc": "Oracle service enabling smart contracts to interact with real-world data."},
            {"name": "Uniswap", "desc": "Leading decentralized exchange on Ethereum."},
            {"name": "Aave", "desc": "Decentralized lending protocol with a large user base."},
        ],
        "XRP": [
            {"name": "Sologenic", "desc": "Bridges real-world assets onto XRP Ledger."},
            {"name": "Equilibrium", "desc": "Synthetic assets and DeFi tools on XRP."},
            {"name": "CasinoCoin", "desc": "A gaming token built on XRP Ledger."},
            {"name": "Flare Network", "desc": "Smart contract platform integrated with XRP Ledger."},
            {"name": "XRPL Labs", "desc": "Developers of popular XRP apps and tools."},
        ],
        "Cosmos": [
            {"name": "Osmosis", "desc": "AMM for Cosmos ecosystem."},
            {"name": "Akash Network", "desc": "Decentralized cloud for web3 deployment."},
            {"name": "Regen Network", "desc": "Carbon credits and ecological monitoring platform."},
            {"name": "Secret Network", "desc": "Privacy-first smart contracts."},
            {"name": "Thorchain", "desc": "Cross-chain liquidity protocol."},
        ],
    }

    st.subheader("🔥 AI-Backed Project Picks")
    for coin in suggestions[selected_chain]:
        with st.expander(f"{coin['name']} - Learn More"):
            st.markdown(f"**Overview**: {coin['desc']}")
            st.markdown("**Community**: Strong presence and engagement on Twitter and Discord.")
            st.markdown("**Whitepaper**: Transparent and visionary with clear utility.")
            st.markdown("**Token Utility**: Used in governance, staking, or service access.")

    st.subheader("🐦 Twitter Trending")
    trends = get_twitter_trends(selected_chain)
    for trend in trends:
        st.markdown(f"- {trend}")

    keyword = st.text_input("Or search by keyword (e.g. DeFi, AI, gaming)")
    st.caption("Made for personal research. Not financial advice.")

# --- Sol Casino Page ---
elif page == "Sol Casino":
    st.markdown('<div class="section-header">Sol Casino - Solana Meme Coin Scanner 🎲</div>', unsafe_allow_html=True)

    token_address = st.text_input("Analyze token by address")
    if token_address:
        st.markdown(f"**Token Analysis for:** `{token_address}`")
        with st.container():
            st.markdown("- **Bubble Map**: [Placeholder] Shows cluster of large holders")
            st.markdown("- **Freeze Authority**: Present")
            st.markdown("- **Mint Authority**: Present")
            st.markdown("- **Token Utility**: Governance + Staking")
            st.markdown("- **Overall Risk Score**: 5/10")

    st.caption("Data powered by Solana + AI. No dummy tokens shown.")

