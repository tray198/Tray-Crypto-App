import streamlit as st
import requests
import openai
import time

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]


# --- Page Setup ---
st.set_page_config(page_title="Crypto AI Deal Finder", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown("""
<style>
    body, .block-container {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    .simple-terms {
        font-style: italic;
        color: #ccc;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper: fetch altcoins by chain from CoinGecko ---
def fetch_altcoins(chain_id, per_page=100):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": chain_id,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []

# Mapping for chain to CoinGecko category ID or fallback to chain slug:
CHAIN_CATEGORY = {
    "Ethereum": "ethereum-ecosystem",
    "XRP": None,       # No exact category, fallback to filtering by platform below
    "Cosmos": None,    # Same as XRP
}

# Helper to filter coins by platform for chains without category
CHAIN_PLATFORM_SLUGS = {
    "XRP": "ripple",
    "Cosmos": "cosmos",
}

# --- Helper: get good altcoin picks with OpenAI ---
def get_ai_picks(chain, altcoins):
    """
    Send coin list names to OpenAI with a prompt asking to pick top 5 altcoins
    with potential on that chain with detailed description + simpler terms.
    """
    coin_names = [coin["name"] for coin in altcoins]
    coin_list_str = ", ".join(coin_names[:50])  # limit to 50 to reduce prompt length
    
    prompt = (
        f"You are a crypto analyst. From the following list of coins on the {chain} blockchain:\n"
        f"{coin_list_str}\n"
        "Pick the top 5 lesser-known altcoins with massive potential. "
        "For each pick, provide:\n"
        "1. Coin name\n"
        "2. A detailed 3-paragraph explanation about the project, technology, and potential\n"
        "3. A 'Simpler terms' section with a short easy explanation.\n\n"
        "Format the response as:\n"
        "Coin Name:\nDetailed Explanation...\nSimpler terms: ...\n\nRepeat for all 5 picks."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.75,
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        return None

# --- Fallback: top 5 altcoins by volume ---
def fallback_picks(altcoins):
    # Sort by volume desc, exclude top 3 by market cap (assuming those are big coins)
    filtered = sorted(altcoins, key=lambda x: x["total_volume"], reverse=True)
    filtered = [c for c in filtered if c["market_cap_rank"] and c["market_cap_rank"] > 3]
    picks = filtered[:5]
    return picks

# --- Main UI ---
st.title("🧠📈 Crypto AI Deal Finder")
st.markdown("Search altcoins by blockchain. AI suggests 5 promising altcoins with detailed and simplified explanations.")

chain = st.selectbox("Choose blockchain", ["Ethereum", "XRP", "Cosmos"])

# Fetch altcoins for selected chain
if CHAIN_CATEGORY.get(chain):
    coins_data = fetch_altcoins(CHAIN_CATEGORY[chain])
else:
    # No category: fetch top 100 coins and filter by platform
    coins_all = fetch_altcoins("all", per_page=100)  # 'all' category doesn't exist, fallback fetch top100
    platform_slug = CHAIN_PLATFORM_SLUGS.get(chain)
    if platform_slug:
        coins_data = [c for c in coins_all if platform_slug in (c.get("platforms") or {})]
    else:
        coins_data = coins_all

if not coins_data:
    st.error("Could not fetch coin data at the moment. Please try again later.")
    st.stop()

# Get AI picks text
ai_picks_text = get_ai_picks(chain, coins_data)

if ai_picks_text:
    st.subheader(f"🔥 AI Suggested Projects on {chain}")
    # Parse AI output into individual picks (simple split by coin name and description)
    # This is rough parsing based on expected format; may need tweaking
    picks = ai_picks_text.split("\n\n")
    current_coin = None
    for block in picks:
        lines = block.strip().split("\n")
        if not lines:
            continue
        # Assuming first line is coin name (ends with colon)
        if lines[0].endswith(":"):
            coin_name = lines[0][:-1].strip()
            details = "\n".join(lines[1:])
            # Separate "Simpler terms" if present
            simpler_start = details.lower().find("simpler terms:")
            if simpler_start != -1:
                detailed_text = details[:simpler_start].strip()
                simpler_text = details[simpler_start + len("simpler terms:"):].strip()
            else:
                detailed_text = details
                simpler_text = ""
            with st.expander(f"{coin_name} - Learn More"):
                st.markdown(detailed_text)
                if simpler_text:
                    st.markdown(f"<p class='simple-terms'>Simpler terms: {simpler_text}</p>", unsafe_allow_html=True)
        else:
            # Sometimes AI may output unexpected format; just show block
            st.markdown(block)
else:
    st.warning("AI suggestions not available. Showing fallback picks.")
    fallback = fallback_picks(coins_data)
    for coin in fallback:
        with st.expander(f"{coin['name']} ({coin['symbol'].upper()}) - Learn More"):
            st.markdown(f"**Market Cap Rank:** {coin.get('market_cap_rank', 'N/A')}")
            st.markdown(f"**Current Price:** ${coin.get('current_price', 'N/A')}")
            st.markdown(f"**24h Volume:** ${coin.get('total_volume', 'N/A')}")
            st.markdown(f"**More info:** [CoinGecko]({coin.get('links', {}).get('homepage', [''])[0]})")

# Keyword search box and autocomplete (optional feature to implement separately)
st.markdown("---")
st.markdown("### Search for altcoins by name or keyword (Coming Soon)")

st.caption("Made for personal research. Not financial advice.")


