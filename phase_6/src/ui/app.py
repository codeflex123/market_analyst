import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import re
import os
import json

def main():
    # Premium CSS for the dashboard
    st.markdown("""
<style>
    .reportview-container {
        background-color: #0E1117;
    }
    .main {
        background-color: #0E1117;
    }
    .stCard {
        background-color: #1E2130;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .score-card {
        background: linear-gradient(145deg, #1e2130, #161924);
        border-radius: 15px;
        padding: 20px;
        text-align: left;
        color: white;
        min-height: 120px;
        border-left: 5px solid #4CAF50;
    }
    .score-val {
        font-size: 32px;
        font-weight: bold;
        color: #4CAF50;
    }
    .score-label {
        font-size: 14px;
        color: #8E94AA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .recommendation-card {
        background-color: #1E2130;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #3E4451;
    }
    .status-circle {
        height: 40px;
        width: 40px;
        border-radius: 50%;
        display: inline-block;
        vertical-align: middle;
        margin-right: 15px;
    }
    .status-buy { background-color: #4CAF50; }
    .status-hold { background-color: #FFC107; }
    .status-sell { background-color: #F44336; }
    
    .recommendation-text {
        font-size: 48px;
        font-weight: 800;
        display: inline-block;
        vertical-align: middle;
        color: white;
        letter-spacing: 2px;
    }
    .reasoning-box {
        background-color: #F0F2F6;
        border-radius: 10px;
        padding: 20px;
        color: #1E2130;
        font-size: 16px;
        line-height: 1.6;
        border-left: 5px solid #3498db;
        margin-bottom: 10px;
    }
    .metric-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        padding: 20px 0;
    }
    .metric-box {
        text-align: left;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #111;
    }
    .disclaimer-box {
        background-color: #FFEBEE;
        border-radius: 8px;
        padding: 15px;
        margin-top: 30px;
        border: 1px solid #FFCDD2;
        color: #C62828;
        font-size: 0.9em;
    }
    .mode-header {
        background: linear-gradient(90deg, #1E2130, #0E1117);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
    }
    .overall-summary-card {
        background: linear-gradient(135deg, #1E2130 0%, #2D3241 100%);
        border-radius: 20px;
        padding: 40px;
        margin-top: 40px;
        border: 2px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2622/2622649.png", width=100)
    st.title("Market Analyst AI")
    st.markdown("---")
    
    analysis_mode = st.radio(
        "Navigation Mode",
        ["Market Analyst", "Stock Comparison", "Portfolio Analysis"],
        index=0
    )
    
    st.markdown("---")
    st.info(f"📍 Mode: **{analysis_mode}**")
    st.markdown("---")
    st.markdown("""
    ### 💡 Quick Tips
    - **Single Stock**: Just type 'Reliance'
    - **Comparison**: 'Compare Tata and M&M'
    - **Portfolio**: 'Analysis for Kotak, HDFC, SBI'
    """)
    st.markdown("---")
    with st.expander("🛡️ About Analyst AI"):
        st.caption("A multi-agent system powered by Gemini & Groq, utilizing the Model Context Protocol (MCP) for deep market reasoning.")

# Map modes to intents
MODE_INTENT_MAP = {
    "Market Analyst": "status",
    "Stock Comparison": "comparison",
    "Portfolio Analysis": "portfolio"
}

api_base = "http://localhost:8000" # Hardcoded for background sync

st.markdown(f"""
<div class='mode-header'>
    <h2 style='margin: 0; color: white;'>{analysis_mode}</h2>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome Screen for Empty State
if not st.session_state.messages:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1E2130 0%, #11141D 100%); padding: 60px; border-radius: 20px; text-align: center; border: 1px solid #3E4451; margin-top: 40px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/2622/2622649.png" width="80" style="margin-bottom: 20px;">
        <h1 style='color: white; margin-bottom: 10px;'>Your AI Institutional Analyst</h1>
        <p style='color: #8E94AA; font-size: 18px; max-width: 600px; margin: 0 auto;'>
            Welcome to the premium Market Analyst workflow. Access real-time technicals, 
            deep fundamentals, and sentiment analysis powered by a multi-agent logic layer.
        </p>
        <div style='margin-top: 40px; display: flex; justify-content: center; gap: 20px;'>
            <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'>
                <h4 style='color: #4CAF50; margin: 0;'>70+ India Stocks</h4>
                <p style='color: #666; font-size: 12px; margin-top: 5px;'>Mapped & Verified</p>
            </div>
            <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'>
                <h4 style='color: #3498db; margin: 0;'>Multi-Agent</h4>
                <p style='color: #666; font-size: 12px; margin-top: 5px;'>Parallel Analysis</p>
            </div>
            <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'>
                <h4 style='color: #FFC107; margin: 0;'>MCP Logic</h4>
                <p style='color: #666; font-size: 12px; margin-top: 5px;'>Deep Reasoning</p>
            </div>
        </div>
        <p style='color: #3E4451; margin-top: 40px; font-size: 14px;'>Select a mode in the sidebar and enter a query below to begin.</p>
    </div>
    """, unsafe_allow_html=True)

# Map common names to tickers
NAME_MAP = {
    "reliance": "RELIANCE.NS",
    "kotak": "KOTAKBANK.NS",
    "tata motors": "TATAMOTORS.NS",
    "mahindra": "M&M.NS",
    "m&m": "M&M.NS",
    "infosys": "INFY.NS",
    "tata steel": "TATASTEEL.NS",
    "tata": "TATASTEEL.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfc": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "state bank": "SBIN.NS",
    "axis": "AXISBANK.NS",
    "itc": "ITC.NS",
    "wipro": "WIPRO.NS",
    "tcs": "TCS.NS"
}

BLACKLIST = {"how", "is", "doing", "was", "the", "and", "buy", "sell", "compare", "portfolio", "analysis", "for", "against", "versus", "vs", "stock", "stocks", "market", "query", "answer"}

def extract_tickers(text):
    text = text.lower()
    tickers = []
    
    # Try direct mapping first
    for name, ticker in NAME_MAP.items():
        if name in text:
            tickers.append(ticker)
    
    # Regex for remaining potential symbols
    found = re.findall(r'\b([A-Za-z]{2,10}(?:\.[A-Z]{2})?)\b', text)
    for f in found:
        # Check against blacklist and existing tickers
        if f.lower() not in BLACKLIST and len(f) >= 3:
            # If it's pure alpha, it's likely a ticker if not in blacklist
            val = f.upper()
            if not val.endswith(".NS") and val.isalpha():
                # For Indian market focus, default to .NS if not found in NAME_MAP
                if val not in [t.split('.')[0] for t in tickers]:
                    tickers.append(f"{val}.NS")
            elif val.endswith(".NS"):
                tickers.append(val)
    
    return list(set(tickers))

def parse_premium_report(full_report):
    """Extracts JSON data and main text from the report."""
    json_match = re.search(r'```json\n(.*?)\n```', full_report, re.DOTALL)
    report_data = None
    main_text = full_report
    
    if json_match:
        try:
            report_data = json.loads(json_match.group(1))
            main_text = full_report.replace(json_match.group(0), "").strip()
        except:
            pass
            
    return report_data, main_text

def render_stock_card(sym, stock_data):
    """Renders a dashboard card for a single stock."""
    if not stock_data:
        return
        
    rec = stock_data.get("recommendation", "HOLD").upper()
    status_class = "status-hold"
    if "BUY" in rec: status_class = "status-buy"
    elif "SELL" in rec: status_class = "status-sell"
    
    st.markdown(f"#### 🏦 {sym} Analysis")
    
    # Scores
    scores = stock_data.get("scores", {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""<div class='score-card' style='border-left-color: #4CAF50;'>
            <div class='score-label'>Fundamental</div>
            <div class='score-val' style='color: #4CAF50;'>{scores.get('fundamental', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='score-card' style='border-left-color: #3498db;'>
            <div class='score-label'>Technical</div>
            <div class='score-val' style='color: #3498db;'>{scores.get('technical', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='score-card' style='border-left-color: #FFC107;'>
            <div class='score-label'>Sentiment</div>
            <div class='score-val' style='color: #FFC107;'>{scores.get('sentiment', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div>
        </div>""", unsafe_allow_html=True)

    # Metrics
    metrics = stock_data.get("metrics", {})
    st.markdown(f"""
    <div style='background-color: white; border-radius: 12px; padding: 25px; color: #333; margin-top: 15px;'>
        <div class="metric-container">
            <div class="metric-box"><div class="metric-label">PE Ratio</div><div class="metric-value">{metrics.get('pe_ratio', 'N/A')}</div></div>
            <div class="metric-box"><div class="metric-label">Earning Growth</div><div class="metric-value">{metrics.get('earnings_growth', 'N/A')}</div></div>
            <div class="metric-box"><div class="metric-label">Revenue</div><div class="metric-value">{metrics.get('revenue', 'N/A')}</div></div>
            <div class="metric-box"><div class="metric-label">Profit Margin</div><div class="metric-value">{metrics.get('profit_margin', 'N/A')}</div></div>
            <div class="metric-box"><div class="metric-label">Market Cap</div><div class="metric-value">{metrics.get('market_cap', 'N/A')}</div></div>
            <div class="metric-box"><div class="metric-label">Debt Level</div><div class="metric-value">{metrics.get('debt_level', 'N/A')}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"**Individual Recommendation**: :{ 'green' if 'BUY' in rec else 'orange' if 'HOLD' in rec else 'red' }[{rec}]")
    st.write("---")

def render_overall_summary(report_data):
    """Renders the final overall recommendation card."""
    rec = report_data.get("overall_recommendation", report_data.get("recommendation", "HOLD")).upper()
    reasoning = report_data.get("overall_reasoning", "Detailed analysis completed.")
    
    status_class = "status-hold"
    if "BUY" in rec: status_class = "status-buy"
    elif "SELL" in rec: status_class = "status-sell"
    
    st.markdown(f"""
    <div class='overall-summary-card'>
        <h2 style='color: white; margin-top: 0;'>📝 Final Analysis Summary</h2>
        <div class='recommendation-card'>
            <p style='color: #8E94AA; margin-bottom: 10px;'>Overall Portfolio/Comparison Call</p>
            <div class='status-circle {status_class}'></div>
            <div class='recommendation-text' style='color: {"#4CAF50" if "BUY" in rec else "#FFC107" if "HOLD" in rec else "#F44336"};'>
                {rec}
            </div>
        </div>
        <div class='reasoning-box'>
            <strong>Investment Strategist Outlook:</strong><br/>
            {reasoning}
        </div>
        <div class="disclaimer-box">
            ⚠️ <strong>Note</strong>: Investment is subject to market risk. Do not rely solely on this AI-generated analysis; always consult with a certified financial professional before making investment decisions.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            report_data, main_text = parse_premium_report(message["content"])
            if report_data and "stocks" in report_data:
                for sym, s_data in report_data["stocks"].items():
                    render_stock_card(sym, s_data)
                render_overall_summary(report_data)
            elif report_data:
                # Old format fallback
                render_stock_card("Market Analysis", report_data)
                render_overall_summary(report_data)
            else:
                st.markdown(message["content"])
        else:
            st.markdown(message["content"])
            
        if "data" in message:
            data = message["data"]
            portfolio_data = data.get("portfolio_data", {})
            if portfolio_data:
                for sym, results in portfolio_data.items():
                    tech_data = results.get("technical", {})
                    if tech_data and "historical_data" in tech_data:
                        st.write(f"📊 **{sym} Performance Chart**")
                        hist = pd.DataFrame(tech_data["historical_data"])
                        if not hist.empty:
                            fig = go.Figure(data=[go.Candlestick(
                                x=hist.index if hasattr(hist, 'index') else range(len(hist)),
                                open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']
                            )])
                            fig.update_layout(height=400, title=f"{sym} Price Action (1 Mo)", template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)

# Accept user input
if prompt := st.chat_input("Enter stock symbol or market query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    tickers = extract_tickers(prompt)
    if not tickers:
        st.error("I couldn't identify the stock ticker. Please try mentioning it clearly (e.g., 'Analyze ICICI and RELIANCE').")
    else:
        intent = MODE_INTENT_MAP.get(analysis_mode, "status")
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(f"🔍 Initializing **{analysis_mode}** workflow for: {', '.join(tickers)}")
            
            try:
                response = requests.post(f"{api_base}/analyze", json={"symbols": tickers, "intent": intent})
                if response.status_code == 200:
                    data = response.json()
                    full_report = data.get("final_report", "I couldn't generate a report.")
                    report_data, main_text = parse_premium_report(full_report)
                    message_placeholder.empty()
                    
                    if report_data and "stocks" in report_data:
                        for sym, s_data in report_data["stocks"].items():
                            render_stock_card(sym, s_data)
                        render_overall_summary(report_data)
                    elif report_data:
                        render_stock_card(tickers[0], report_data)
                        render_overall_summary(report_data)
                    else:
                        st.markdown(full_report)
                    
                    # Real Visualizations
                    portfolio_data = data.get("portfolio_data", {})
                    for sym, results in portfolio_data.items():
                        tech_data = results.get("technical", {})
                        if tech_data and "historical_data" in tech_data:
                            st.write(f"📊 **{sym} Live Price Chart**")
                            hist = pd.DataFrame(tech_data["historical_data"])
                            if not hist.empty:
                                fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                                fig.update_layout(height=400, template="plotly_dark")
                                st.plotly_chart(fig, use_container_width=True)

                    st.session_state.messages.append({"role": "assistant", "content": full_report, "data": data})
                else:
                    st.error(f"Error from agents: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")

    st.markdown("---")
    st.caption("AI Multi-Agent Analyst | Gemini & Groq Powered")

if __name__ == "__main__":
    main()
