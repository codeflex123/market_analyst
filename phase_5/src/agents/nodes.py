import os
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.state import GraphState
from src.tools.yfinance_tool import YFinanceTool
from src.tools.search_tool import SearchTool
from src.logger import logger, log_function_call

from src.tools.cache_manager import CacheManager

# Initialize tools and cache
yf_tool = YFinanceTool()
search_tool = SearchTool()
cache_mgr = CacheManager()

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

@log_function_call
def sentiment_node(state: GraphState):
    """Fetches sentiment data and checks cache."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        # Check cache
        cached = cache_mgr.get(sym)
        if cached and "sentiment" in cached:
            new_portfolio_data[sym] = {"sentiment": cached["sentiment"]}
            continue
            
        news = search_tool.search_news(f"{sym} stock news")
        new_portfolio_data[sym] = {"sentiment": news}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Sentiment Analyst updated data for: {', '.join(symbols)}"]
    }

# Load API keys for real LLM synthesis
GEMINI_KEY_MASTER = os.getenv("GEMINI_API_KEY_MASTER")

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

    # Initialize Gemini for High-Fidelity Synthesis
    model = get_model("google", GEMINI_KEY_MASTER, "gemini-1.5-flash")
    
    # Construct a high-density structured context
    context = f"### USER QUERY INTENT: {intent.upper()}\n"
    for sym, data in portfolio.items():
        context += f"\n#### 📈 {sym} ANALYST BREAKDOWN\n"
        context += f"- **Fundamental**: {data.get('fundamental')}\n"
        context += f"- **Technical (Price Action)**: {data.get('technical')}\n"
        context += f"- **Sentiment (Market Mood)**: {data.get('sentiment')}\n"

    prompt = f"""
    You are a Senior Wall Street Investment Strategist. Your task is to provide a HIGHLY DETAILED and WELL-STRUCTURED market report based on raw data from specialized agents.
    
    REPORT STRUCTURE:
    1.  **Executive Summary**: A punchy 1-2 sentence overview.
    2.  **Deep Dive (per stock)**:
        - **Fundamentals**: Key metrics (P/E, Market Cap, Sector) and what they mean.
        - **Technical Setup**: Trend analysis and historical context.
        - **Sentiment**: Recent news impact and overall "vibe".
    3.  **Final Recommendation**: 
        - If multiple stocks: Rank them explicitly.
        - Actionable advice: "Buy", "Hold", or "Avoid" with specific reasoning.
    
    DATA CONTEXT:
    {context}
    
    OUTPUT SPECIFICATION:
    - Use professional, clean Markdown.
    - Be specific. Don't say "doing well", say "P/E is 20 which is healthy for the sector".
    - If data is missing or looks like an error, acknowledge it gracefully.
    
    Your response should look like a premium research note.
    """
    
    try:
        response = model.invoke(prompt)
        report = response.content
        
        # Persistent Cache update for this specific query
        cache_mgr.set(cache_key, {"full_report": report})
            
    except Exception as e:
        logger.error(f"LLM Synthesis failed: {str(e)}")
        report = f"## ⚠️ AI Synthesis Partial Failure\nRaw data is still available in the dashboard. Error details: {str(e)}"

    return {"final_report": report, "messages": ["Master Node completed premium AI synthesis"]}
