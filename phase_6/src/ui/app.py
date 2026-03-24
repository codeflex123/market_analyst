import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import re
import os
import json

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
    for name, ticker in NAME_MAP.items():
        if name in text: tickers.append(ticker)
    found = re.findall(r'\b([A-Za-z]{2,10}(?:\.[A-Z]{2})?)\b', text)
    for f in found:
        if f.lower() not in BLACKLIST and len(f) >= 3:
            val = f.upper()
            if not val.endswith(".NS") and val.isalpha():
                if val not in [t.split('.')[0] for t in tickers]:
                    tickers.append(f"{val}.NS")
            elif val.endswith(".NS"): tickers.append(val)
    return list(set(tickers))

def parse_premium_report(full_report):
    json_match = re.search(r'```json\n(.*?)\n```', full_report, re.DOTALL)
    report_data = None
    main_text = full_report
    if json_match:
        try:
            report_data = json.loads(json_match.group(1))
            main_text = full_report.replace(json_match.group(0), "").strip()
        except: pass
    return report_data, main_text

def render_stock_card(sym, stock_data):
    if not stock_data: return
    rec = stock_data.get("recommendation", "HOLD").upper()
    st.markdown(f"#### 🏦 {sym} Analysis")
    scores = stock_data.get("scores", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='score-card' style='border-left-color: #4CAF50;'><div class='score-label'>Fundamental</div><div class='score-val' style='color: #4CAF50;'>{scores.get('fundamental', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='score-card' style='border-left-color: #3498db;'><div class='score-label'>Technical</div><div class='score-val' style='color: #3498db;'>{scores.get('technical', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='score-card' style='border-left-color: #FFC107;'><div class='score-label'>Sentiment</div><div class='score-val' style='color: #FFC107;'>{scores.get('sentiment', 'N/A')}<span style='font-size: 16px; color: #8E94AA;'>/10</span></div></div>", unsafe_allow_html=True)
    metrics = stock_data.get("metrics", {})
    st.markdown(f"<div style='background-color: white; border-radius: 12px; padding: 25px; color: #333; margin-top: 15px;'><div class='metric-container'><div class='metric-box'><div class='metric-label'>PE Ratio</div><div class='metric-value'>{metrics.get('pe_ratio', 'N/A')}</div></div><div class='metric-box'><div class='metric-label'>Earning Growth</div><div class='metric-value'>{metrics.get('earnings_growth', 'N/A')}</div></div><div class='metric-box'><div class='metric-label'>Revenue</div><div class='metric-value'>{metrics.get('revenue', 'N/A')}</div></div><div class='metric-box'><div class='metric-label'>Profit Margin</div><div class='metric-value'>{metrics.get('profit_margin', 'N/A')}</div></div><div class='metric-box'><div class='metric-label'>Market Cap</div><div class='metric-value'>{metrics.get('market_cap', 'N/A')}</div></div><div class='metric-box'><div class='metric-label'>Debt Level</div><div class='metric-value'>{metrics.get('debt_level', 'N/A')}</div></div></div></div>", unsafe_allow_html=True)
    st.markdown(f"**Individual Recommendation**: :{ 'green' if 'BUY' in rec else 'orange' if 'HOLD' in rec else 'red' }[{rec}]")
    st.write("---")

def render_overall_summary(report_data):
    rec = report_data.get("overall_recommendation", report_data.get("recommendation", "HOLD")).upper()
    reasoning = report_data.get("overall_reasoning", "Detailed analysis completed.")
    status_class = "status-buy" if "BUY" in rec else "status-sell" if "SELL" in rec else "status-hold"
    st.markdown(f"<div class='overall-summary-card'><h2 style='color: white; margin-top: 0;'>📝 Final Analysis Summary</h2><div class='recommendation-card'><p style='color: #8E94AA; margin-bottom: 10px;'>Overall Portfolio/Comparison Call</p><div class='status-circle {status_class}'></div><div class='recommendation-text' style='color: {'#4CAF50' if 'BUY' in rec else '#FFC107' if 'HOLD' in rec else '#F44336'};'>{rec}</div></div><div class='reasoning-box'><strong>Investment Strategist Outlook:</strong><br/>{reasoning}</div><div class='disclaimer-box'>⚠️ <strong>Note</strong>: Investment is subject to market risk. Do not rely solely on this AI-generated analysis.</div></div>", unsafe_allow_html=True)

def main(analysis_mode):
    # CSS
    st.markdown("""<style>
    .reportview-container { background-color: #0E1117; }
    .main { background-color: #0E1117; }
    .score-card { background: linear-gradient(145deg, #1e2130, #161924); border-radius: 15px; padding: 20px; color: white; min-height: 120px; border-left: 5px solid #4CAF50; }
    .score-val { font-size: 32px; font-weight: bold; }
    .score-label { font-size: 14px; color: #8E94AA; text-transform: uppercase; }
    .recommendation-card { background-color: #1E2130; border-radius: 15px; padding: 30px; text-align: center; border: 1px solid #3E4451; }
    .status-circle { height: 40px; width: 40px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 15px; }
    .status-buy { background-color: #4CAF50; } .status-hold { background-color: #FFC107; } .status-sell { background-color: #F44336; }
    .recommendation-text { font-size: 48px; font-weight: 800; display: inline-block; vertical-align: middle; color: white; }
    .reasoning-box { background-color: #F0F2F6; border-radius: 10px; padding: 20px; color: #1E2130; font-size: 16px; border-left: 5px solid #3498db; }
    .metric-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px 0; }
    .mode-header { background: linear-gradient(90deg, #1E2130, #0E1117); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4CAF50; }
    .overall-summary-card { background: linear-gradient(135deg, #1E2130 0%, #2D3241 100%); border-radius: 20px; padding: 40px; margin-top: 40px; border: 2px solid #4CAF50; }
    </style>""", unsafe_allow_html=True)

    MODE_INTENT_MAP = {"Market Analyst": "status", "Stock Comparison": "comparison", "Portfolio Analysis": "portfolio"}
    api_base = "http://localhost:8000"

    st.markdown(f"<div class='mode-header'><h2 style='margin: 0; color: white;'>{analysis_mode}</h2></div>", unsafe_allow_html=True)

    if "messages" not in st.session_state: st.session_state.messages = []

    if not st.session_state.messages:
        st.markdown(f"""<div style='background: linear-gradient(135deg, #1E2130 0%, #11141D 100%); padding: 60px; border-radius: 20px; text-align: center; border: 1px solid #3E4451; margin-top: 40px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/2622/2622649.png' width='80' style='margin-bottom: 20px;'>
            <h1 style='color: white; margin-bottom: 10px;'>Your AI Institutional Analyst</h1>
            <p style='color: #8E94AA; font-size: 18px; max-width: 600px; margin: 0 auto;'>Welcome to the premium Market Analyst workflow. Access real-time technicals, deep fundamentals, and sentiment analysis.</p>
            <div style='margin-top: 40px; display: flex; justify-content: center; gap: 20px;'>
                <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'><h4 style='color: #4CAF50; margin: 0;'>70+ India Stocks</h4></div>
                <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'><h4 style='color: #3498db; margin: 0;'>Multi-Agent</h4></div>
                <div style='background: #2D3241; padding: 20px; border-radius: 12px; width: 180px;'><h4 style='color: #FFC107; margin: 0;'>MCP Logic</h4></div>
            </div></div>
            <p style='color: #3E4451; margin-top: 40px; font-size: 14px;'>Select a mode in the sidebar and enter a query below to begin.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion Pills
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🚀 Try one of these:")
    
    suggestions = {
        "Market Analyst": ["Analyze Reliance", "Status of HDFC Bank", "ICICI Fundamental score"],
        "Stock Comparison": ["Compare Kotak and HDFC", "SBI vs Axis Bank", "Tata Motors vs Mahindra"],
        "Portfolio Analysis": ["Analysis for RELIANCE, TCS, INFY", "Portfolio: Wipro, ITC, SBI", "Check Kotak, HDFC, ICICI"]
    }
    
    cols = st.columns(3)
    current_suggestions = suggestions.get(analysis_mode, suggestions["Market Analyst"])
    
    for i, suggestion in enumerate(current_suggestions):
        with cols[i % 3]:
            if st.button(f"💬 {suggestion}", use_container_width=True, key=f"sugg_{i}"):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.session_state.trigger_analysis = True
                st.rerun()

    # Analysis Trigger Logic for Buttons/Suggestions
    if st.session_state.get("trigger_analysis"):
        st.session_state.trigger_analysis = False # Reset
        prompt = st.session_state.messages[-1]["content"]
        tickers = extract_tickers(prompt)
        if tickers:
            intent = MODE_INTENT_MAP.get(analysis_mode, "status")
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown(f"🔍 Initializing **{analysis_mode}** workflow...")
                try:
                    response = requests.post(f"{api_base}/analyze", json={"symbols": tickers, "intent": intent})
                    if response.status_code == 200:
                        data = response.json()
                        full_report = data.get("final_report", "")
                        st.session_state.messages.append({"role": "assistant", "content": full_report, "data": data})
                        st.rerun()
                except Exception as e: st.error(f"Error: {str(e)}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                report_data, _ = parse_premium_report(message["content"])
                if report_data and "stocks" in report_data:
                    for sym, s_data in report_data["stocks"].items(): render_stock_card(sym, s_data)
                    render_overall_summary(report_data)
                elif report_data:
                    render_stock_card("Market Analysis", report_data)
                    render_overall_summary(report_data)
                else: st.markdown(message["content"])
            else: st.markdown(message["content"])
            if "data" in message:
                portfolio_data = message["data"].get("portfolio_data", {})
                for sym, results in portfolio_data.items():
                    tech_data = results.get("technical", {})
                    if tech_data and "historical_data" in tech_data:
                        st.write(f"📊 **{sym} Performance Chart**")
                        hist = pd.DataFrame(tech_data["historical_data"])
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(height=400, template="plotly_dark")
                        st.plotly_chart(fig, use_container_width=True)

    if prompt := st.chat_input("Enter stock symbol or market query..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun() # Ensure prompt shows up immediately

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        prompt = st.session_state.messages[-1]["content"]
        tickers = extract_tickers(prompt)
        if not tickers: st.error("I couldn't identify the stock ticker.")
        else:
            intent = MODE_INTENT_MAP.get(analysis_mode, "status")
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown(f"🔍 Initializing **{analysis_mode}** workflow...")
                try:
                    response = requests.post(f"{api_base}/analyze", json={"symbols": tickers, "intent": intent})
                    if response.status_code == 200:
                        data = response.json()
                        full_report = data.get("final_report", "")
                        placeholder.empty()
                        report_data, _ = parse_premium_report(full_report)
                        if report_data and "stocks" in report_data:
                            for sym, s_data in report_data["stocks"].items(): render_stock_card(sym, s_data)
                            render_overall_summary(report_data)
                        else: st.markdown(full_report)
                        st.session_state.messages.append({"role": "assistant", "content": full_report, "data": data})
                        st.rerun()
                    else: st.error(f"Error from agents: {response.text}")
                except Exception as e: st.error(f"Failed to connect to backend: {str(e)}")

if __name__ == "__main__":
    main("Market Analyst")
