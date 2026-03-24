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
    st.info("Ask about stocks, portfolios, or comparisons!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message:
            # Re-render visualizations if they exist in the message
            data = message["data"]
            portfolio_data = data.get("portfolio_data", {})
            if portfolio_data:
                cols = st.columns(len(portfolio_data))
                for i, (sym, results) in enumerate(portfolio_data.items()):
                    with cols[i]:
                        st.write(f"**{sym}**")
                        fig = go.Figure(data=[go.Candlestick(
                            x=[datetime.now()],
                            open=[100], high=[110], low=[90], close=[105]
                        )])
                        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)

# Helper to extract tickers from natural language
def extract_tickers(text):
    # Simple regex for ticker extraction (uppercase 2-10 chars, optional .NS etc)
    tickers = re.findall(r'\b[A-Z]{2,10}(?:\.[A-Z]{2})?\b', text)
    return list(set(tickers))

def determine_intent(text):
    text = text.lower()
    if "compare" in text or "vs" in text or "better buy" in text:
        return "comparison"
    if "portfolio" in text or "holdings" in text:
        return "portfolio"
    return "status"

# Accept user input
if prompt := st.chat_input("How is Reliance doing?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Pre-process query
    tickers = extract_tickers(prompt)
    if not tickers and "reliance" in prompt.lower(): # Fallback for common names 
        tickers = ["RELIANCE.NS"]
    
    intent = determine_intent(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # API Call
            response = requests.post(
                f"{api_base}/analyze",
                json={"symbols": tickers if tickers else ["RELIANCE.NS"], "intent": intent}
            )
            
            if response.status_code == 200:
                data = response.json()
                full_response = data.get("final_report", "I couldn't generate a report.")
                message_placeholder.markdown(full_response)
                
                # Visualizations
                portfolio_data = data.get("portfolio_data", {})
                if portfolio_data:
                    cols = st.columns(len(portfolio_data))
                    for i, (sym, results) in enumerate(portfolio_data.items()):
                        with cols[i]:
                            st.write(f"**{sym}**")
                            # Mock candlestick
                            fig = go.Figure(data=[go.Candlestick(
                                x=[datetime.now()],
                                open=[100], high=[110], low=[90], close=[105]
                            )])
                            fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0))
                            st.plotly_chart(fig, use_container_width=True)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "data": data
                })
            else:
                st.error(f"Error from agents: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")

st.markdown("---")
st.caption("AI Multi-Agent Analyst | Gemini & Groq Powered")
