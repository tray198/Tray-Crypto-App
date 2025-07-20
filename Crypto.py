# --- Imports ---
import streamlit as st
import requests
import openai
import random

# --- Load API Key from Streamlit secrets ---
openai.api_key = st.secrets["openai"]["api_key"]

# --- Config ---
st.set_page_config(page_title="Crypto AI Deal Finder", layout="wide")
st.title("🧠📈 Crypto AI Deal Finder")

st.markdown("Choose a chain to get AI-powered altcoin picks that change every refresh. Suggestions use OpenAI and fallback to heuristics if needed.")

# --- Helper: Fetch coins by chain from CoinGecko ---
def get_chain_altcoins(chain_id):
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        coins = requests.get(url).json()
        chain_coins = []
        for coin in coins:
            coin_detail = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin['id']}").json()
            platforms = coin_detail.get("platforms", {})
            if chain_id in platforms and coin_detail["market_cap_rank"] and coin_detail["market_cap_rank"] > 100:
                chain_coins.append({
                    "id": coin_detail["id"],
                    "name": coin_detail["name"],
                    "symbol": coin_detail["symbol"],
                    "description": coin_detail["description"]["en"][:300] or "No description.",
                    "market_cap": coin_detail["market_data"]["market_cap"]["usd"],
                    "current_price": coin_detail["market_data"]["current_price"]["usd"]
                })
        return chain_coins
    except Exception as e:
        st.error(f"Error fetching coin data: {e}")
        return []

# --- AI Explanation ---
def get_ai_summary(coin_name, coin_desc):
    try:
        prompt = f"Explain why {coin_name} is a promising altcoin in simple terms using this description: {coin_desc}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"(Fallback summary) {coin_desc}"

# --- Search tokens by keyword ---
def keyword_search(keyword, chain_coins):
    keyword = keyword.lower()
    return [coin for coin in chain_coins if keyword in coin["name"].lower() or keyword in coin["description"].lower()]

# --- Search token by name ---
def token_name_search(name):
    try:
        result = requests.get(f"https://api.coingecko.com/api/v3/search?query={name}").json()
        if result["coins"]:
            coin_id = result["coins"][0]["id"]
            detail = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}").json()
            return {
                "name": detail["name"],
                "symbol": detail["symbol"],
                "description": detail["description"]["en"][:300],
                "market_cap": detail["market_data"]["market_cap"]["usd"],
                "price": detail["market_data"]["current_price"]["usd"]
            }
    except:
        return None

# --- Main ---
chains = {
    "Ethereum": "ethereum",
    "XRP": "ripple",
    "Cosmos": "cosmos"
}

selected_chain = st.selectbox("Choose blockchain", list(chains.keys()))
chain_id = chains[selected_chain]
chain_coins = get_chain_altcoins(chain_id)

# --- AI Picks ---
st.subheader(f"🔍 Top 5 {selected_chain} AI Picks")

if chain_coins:
    picks = random.sample(chain_coins, min(5, len(chain_coins)))
    for coin in picks:
        st.markdown(f"### {coin['name']} ({coin['symbol'].upper()})")
        st.markdown(f"- **Market Cap**: ${coin['market_cap']:,}")
        st.markdown(f"- **Price**: ${coin['current_price']}")
        st.markdown("**In simpler terms:**")
        st.markdown(get_ai_summary(coin["name"], coin["description"]))
        st.markdown("---")
else:
    st.warning("Could not fetch coins for this chain.")

# --- Keyword Dropdown ---
st.subheader("🔎 Explore by Keyword")
common_keywords = {
    "Ethereum": ["AI", "Gaming", "DeFi"],
    "XRP": ["Payments", "Staking", "Real World Assets"],
    "Cosmos": ["IBC", "AMM", "Governance"]
}

kw = st.selectbox("Pick a keyword", common_keywords[selected_chain])
filtered = keyword_search(kw, chain_coins)
for c in filtered[:3]:
    st.markdown(f"- {c['name']} ({c['symbol'].upper()})")

# --- Search Token by Name ---
st.subheader("🔍 Search for Token by Name")
token_name = st.text_input("Type token name (e.g., Chainlink, Algorand)")
if token_name:
    result = token_name_search(token_name)
    if result:
        st.markdown(f"### {result['name']} ({result['symbol'].upper()})")
        st.markdown(f"- **Market Cap**: ${result['market_cap']:,}")
        st.markdown(f"- **Price**: ${result['price']}")
        st.markdown("**In simpler terms:**")
        st.markdown(get_ai_summary(result["name"], result["description"]))
    else:
        st.warning("Token not found.")


