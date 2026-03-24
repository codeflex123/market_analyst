import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import re

# Page config
st.set_page_config(page_title="Market Analyst AI", layout="wide")

st.title("🤖 Market Analyst AI Chatbot")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    api_base = st.text_input("API Base URL", value="http://localhost:8000")
    if st.button("Clear Cache"):
        if os.path.exists("analysis_cache.json"):
            os.remove("analysis_cache.json")
            st.success("Cache cleared!")
    st.info("Ask about stocks, portfolios, or comparisons!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Map common names to tickers
NAME_MAP = {
    "reliance": "RELIANCE.NS",
    "kotak": "KOTAKBANK.NS",
    "tata motors": "TATAMOTORS.NS",
    "mahindra": "M&M.NS",
    "infosys": "INFY.NS",
    "tata": "TATASTEEL.NS",
    "hdfc": "HDFCBANK.NS"
}

def extract_tickers(text):
    text = text.lower()
    tickers = []
    # Check for direct matches in name map
    for name, ticker in NAME_MAP.items():
        if name in text:
            tickers.append(ticker)
    
    # Also find uppercase tickers (case-insensitive search)
    found = re.findall(r'\b([A-Za-z]{2,10}(?:\.[A-Z]{2})?)\b', text)
    for f in found:
        if f.upper().endswith(".NS") or len(f) >= 3:
             # Heuristic: skip if it's a common word like 'how', 'is', 'doing'
             if f.lower() not in ["how", "is", "doing", "was", "the", "and", "buy", "sell", "compare"]:
                tickers.append(f.upper())
    
    return list(set(tickers))

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message:
            data = message["data"]
            portfolio_data = data.get("portfolio_data", {})
            if portfolio_data:
                for sym, results in portfolio_data.items():
                    st.write(f"📊 **{sym} Performance Chart**")
                    tech_data = results.get("technical", {})
                    if tech_data and "historical_data" in tech_data:
                        hist = pd.DataFrame(tech_data["historical_data"])
                        if not hist.empty:
                            fig = go.Figure(data=[go.Candlestick(
                                x=hist.index if hasattr(hist, 'index') else range(len(hist)),
                                open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']
                            )])
                            fig.update_layout(height=400, title=f"{sym} Price Action (1 Mo)")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"No historical data found for {sym}.")

def determine_intent(text):
    text = text.lower()
    if "compare" in text or "vs" in text or "better buy" in text:
        return "comparison"
    if "portfolio" in text or "holdings" in text:
        return "portfolio"
    return "status"

# Accept user input
if prompt := st.chat_input("How is Kotak doing?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    tickers = extract_tickers(prompt)
    if not tickers:
        st.error("I couldn't identify the stock ticker. Please try mentioning it clearly (e.g., 'How is RELIANCE.NS doing?').")
    else:
        intent = determine_intent(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 Gathering data from FA, TA, and SA agents...")
            
            try:
                response = requests.post(
                    f"{api_base}/analyze",
                    json={"symbols": tickers, "intent": intent}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    full_report = data.get("final_report", "I couldn't generate a report.")
                    message_placeholder.markdown(full_report)
                    
                    # Real Visualizations
                    portfolio_data = data.get("portfolio_data", {})
                    for sym, results in portfolio_data.items():
                        st.write(f"📊 **{sym} Live Analysis Chart**")
                        tech_data = results.get("technical", {})
                        if tech_data and "historical_data" in tech_data:
                            hist = pd.DataFrame(tech_data["historical_data"])
                            if not hist.empty:
                                fig = go.Figure(data=[go.Candlestick(
                                    x=hist.index,
                                    open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']
                                )])
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)

                    st.session_state.messages.append({"role": "assistant", "content": full_report, "data": data})
                else:
                    st.error(f"Error from agents: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
            else:
                st.error(f"Error from agents: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")

st.markdown("---")
st.caption("AI Multi-Agent Analyst | Gemini & Groq Powered")
