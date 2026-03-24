import os
from dotenv import load_dotenv
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from phase_6.src.agents.state import GraphState
from phase_6.src.tools.yfinance_tool import YFinanceTool
from phase_6.src.tools.search_tool import SearchTool
from phase_6.src.logger import logger, log_function_call

from phase_6.src.tools.cache_manager import CacheManager

# Load environment variables
# Load environment variables from the project root (phase_6)
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "..", "..", ".env")
load_dotenv(dotenv_path)

# Initialize tools and cache
yf_tool = YFinanceTool()
search_tool = SearchTool()
cache_mgr = CacheManager()

def get_model(provider: str, api_key: str, model_name: str):
    if provider == "groq":
        return ChatGroq(api_key=api_key, model=model_name)
    elif provider == "google":
        return ChatGoogleGenerativeAI(google_api_key=api_key, model=model_name)
    return None

@log_function_call
def fundamental_node(state: GraphState):
    """Fetches financial data and checks cache."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        # Check cache
        cached = cache_mgr.get(sym)
        if cached and "fundamental" in cached:
            new_portfolio_data[sym] = {"fundamental": cached["fundamental"]}
            continue
            
        # Fetch fresh data
        data = yf_tool.get_stock_info(sym)
        new_portfolio_data[sym] = {"fundamental": data}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Fundamental Analyst updated data for: {', '.join(symbols)}"]
    }

@log_function_call
def technical_node(state: GraphState):
    """Fetches technical data and checks cache."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        # Check cache
        cached = cache_mgr.get(sym)
        if cached and "technical" in cached:
            new_portfolio_data[sym] = {"technical": cached["technical"]}
            continue
            
        data = yf_tool.get_historical_data(sym)
        new_portfolio_data[sym] = {"technical": data}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Technical Analyst updated data for: {', '.join(symbols)}"]
    }

from phase_6.src.tools.mcp_manager import mcp_mgr
import asyncio

@log_function_call
def sentiment_node(state: GraphState):
    """Fetches sentiment data using Brave Search MCP (fallback to DuckDuckGo)."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        # Check cache
        cached = cache_mgr.get(sym)
        if cached and "sentiment" in cached:
            new_portfolio_data[sym] = {"sentiment": cached["sentiment"]}
            continue
            
        # Try MCP DuckDuckGo Search
        try:
            mcp_result = asyncio.run(mcp_mgr.call_duckduckgo_search(f"{sym} stock news"))
            if mcp_result:
                news = mcp_result
            else:
                news = []
        except:
            news = []
            
        new_portfolio_data[sym] = {"sentiment": news}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Sentiment Analyst (MCP-Ready) updated data for: {', '.join(symbols)}"]
    }

# Load API keys with Streamlit Secrets fallback
def get_api_key(name):
    key = os.getenv(name)
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get(name)
        except:
            pass
    return key

GEMINI_API_KEY_MASTER = get_api_key("GEMINI_API_KEY_MASTER")
GEMINI_API_KEY_FUNDAMENTAL = get_api_key("GEMINI_API_KEY_FUNDAMENTAL")
GROQ_API_KEY_TECHNICAL = get_api_key("GROQ_API_KEY_TECHNICAL")
GROQ_API_KEY_SENTIMENT = get_api_key("GROQ_API_KEY_SENTIMENT")

# Load API keys for real LLM synthesis
GEMINI_KEYS = [
    GEMINI_API_KEY_MASTER,
    GEMINI_API_KEY_FUNDAMENTAL
]
# Filter out None or empty keys
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]

@log_function_call
def master_node(state: GraphState):
    """Performs high-quality final synthesis and intelligent caching."""
    portfolio = state.get("portfolio_data", {})
    if not portfolio:
        return {"messages": ["Master Node: No data to synthesize."]}
    
    intent = state.get("intent", "status")
    symbols = state.get("symbols") or [state.get("symbol")]
    
    # Check if a unified report is already cached for the primary set of symbols
    cache_key = "_".join(sorted(symbols)) + f"_{intent}"
    cached = cache_mgr.get(cache_key)
    if cached and "full_report" in cached:
        logger.info(f"Retrieved total synthesis from cache for {cache_key}")
        return {"final_report": cached["full_report"], "messages": ["Retrieved comprehensive report from cache"]}

    # Construct a high-density structured context with token-efficiency
    context = f"### USER QUERY INTENT: {intent.upper()}\n"
    for sym, data in portfolio.items():
        # Truncate Technical Data (verbose dict -> small summary)
        tech_raw = data.get('technical', {})
        if isinstance(tech_raw, dict) and 'Close' in tech_raw:
            closes = tech_raw['Close']
            # Get last 5 values if possible
            last_dates = sorted(closes.keys())[-5:]
            tech_summary = ", ".join([f"{d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)[:10]}: {closes[d]:.2f}" for d in last_dates])
            tech_final = f"Last 5 Days Close: {tech_summary}"
        else:
            tech_final = str(tech_raw)[:200]
            
        # Truncate Sentiment Data (titles + short snippets)
        sent_raw = data.get('sentiment', [])
        sent_pruned = []
        if isinstance(sent_raw, list):
            for item in sent_raw[:3]: # Only top 3 news items
                title = item.get('title', 'N/A')
                body = item.get('body', 'N/A')[:150] # Truncate body
                sent_pruned.append(f"Title: {title} | Snippet: {body}")
        sent_final = "\n".join(sent_pruned) if sent_pruned else "No recent news."

        context += f"\n#### 📈 {sym} ANALYST BREAKDOWN\n"
        context += f"- **Fundamental**: {str(data.get('fundamental'))[:500]}\n"
        context += f"- **Technical (Price Action)**: {tech_final}\n"
        context += f"- **Sentiment (Market Mood)**: {sent_final}\n"

    prompt = f"""
    You are a Senior Wall Street Investment Strategist. Your task is to provide a HIGHLY DETAILED market report.
    
    If multiple stocks are provided, you MUST:
    1.  Provide a clear analysis section for **EACH** individual stock.
    2.  Provide an **OVERALL ANALYSIS STATEMENT** at the end that compares them and gives a final unified recommendation.
    
    STRUCTURE FOR EVERY STOCK:
    - **Fundamental Analysis**: Metrics and health.
    - **Technical Analysis**: Price action trends.
    - **Sentiment Analysis**: Market mood and news impact.
    
    REQUIRED EXACT FINAL REPORT STRUCTURE:
    1.  **Individual Stock Breakdowns**: (Repeat for each ticker).
    2.  **Reasoning (Final Recommendation Statement)**: A high-quality, 4-6 line detailed statement combining all dimensions and stocks to justify the final call.
    3.  **Disclaimer**: End with the standard risk disclaimer.
    
    DATA CONTEXT:
    {context}
    
    OUTPUT SPECIFICATION:
    - Include specific metrics: PE ratio, Earning growth, Revenue, Profit margin, Market cap, Debt level for each stock.
    - Use professional, clean Markdown.
    
    IMPORTANT: AT THE VERY END, INCLUDE A HIDDEN JSON BLOCK FOR UI PARSING. 
    It MUST be a single JSON object with a "stocks" key mapping each ticker to its details:
    Format:
    ```json
    {{
      "overall_recommendation": "BUY/HOLD/SELL",
      "overall_reasoning": "...",
      "stocks": {{
        "TICKER1": {{
          "recommendation": "BUY",
          "scores": {{"fundamental": 8.0, "technical": 5.0, "sentiment": 7.0}},
          "metrics": {{
            "pe_ratio": "21.0",
            "earnings_growth": "46.8%",
            "revenue": "1.89T",
            "profit_margin": "8.33%",
            "market_cap": "3.52T",
            "debt_level": "High"
          }}
        }},
        "TICKER2": {{ ... }}
      }}
    }}
    ```
    """

    # Optional: Sequential Thinking MCP Step
    try:
        thought_process = asyncio.run(mcp_mgr.call_sequential_thinking(
            thought=f"I need to synthesize an institutional-grade market report for {', '.join(symbols)} with intent {intent}.",
            context=context[:2000]
        ))
        if thought_process:
            logger.info("Sequential Thinking Step Completed via MCP.")
            final_messages.append("Logic Layer: Sequential Thinking (Institutional Mode)")
    except Exception as e:
        logger.warning(f"Sequential Thinking MCP step skipped: {str(e)}")

    # Try Groq as the primary model first (Higher RPM/Reliability)
    report = None
    last_error = None
    final_messages = ["Master Node completed premium AI synthesis"]
    
    groq_key = os.getenv("GROQ_API_KEY_TECHNICAL")
    if groq_key:
        try:
            logger.info("Attempting primary synthesis via Groq...")
            model = get_model("groq", groq_key, "llama-3.3-70b-versatile")
            response = model.invoke(prompt)
            report = response.content
            # Persistent Cache update
            cache_mgr.set(cache_key, {"full_report": report})
            final_messages.append("Provider: Groq (Llama 3.3)")
        except Exception as e:
            last_error = f"Groq primary attempt failed: {str(e)}"
            logger.warning(last_error)

    # Fallback to Gemini if Groq failed or was skipped
    if not report:
        logger.info("Groq unavailable or failed. Falling back to Gemini...")
        for key in GEMINI_KEYS:
            try:
                model = get_model("google", key, "gemini-pro-latest")
                response = model.invoke(prompt)
                report = response.content
                # Persistent Cache update
                cache_mgr.set(cache_key, {"full_report": report})
                final_messages.append("Provider: Gemini (Pro)")
                break 
            except Exception as e:
                last_error = f"Gemini fallback failed: {str(e)}"
                logger.warning(last_error)

    if not report:
        logger.error(f"All AI providers failed. Final error: {last_error}")
        report = f"## ⚠️ AI Synthesis Failure\nRaw data is still available in the dashboard. Error details: {last_error}"

    return {"final_report": report, "messages": final_messages}
