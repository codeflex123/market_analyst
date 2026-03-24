import os
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.state import GraphState
from src.tools.yfinance_tool import YFinanceTool
from src.tools.search_tool import SearchTool
from src.logger import logger, log_function_call

# Initialize tools
yf_tool = YFinanceTool()
search_tool = SearchTool()

def get_model(provider: str, api_key: str, model_name: str):
    if provider == "groq":
        return ChatGroq(api_key=api_key, model=model_name)
    elif provider == "google":
        return ChatGoogleGenerativeAI(google_api_key=api_key, model=model_name)
    return None

@log_function_call
def fundamental_node(state: GraphState):
    """Analyzes financial health using Gemini."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    model = get_model("google", GEMINI_KEY_FUND, "gemini-1.5-flash")
    
    for sym in symbols:
        data = yf_tool.get_stock_info(sym)
        # LLM summary
        prompt = f"Analyze the following fundamental data for {sym} and provide a 2-sentence summary: {data}"
        try:
            summary = model.invoke(prompt).content
        except:
            summary = "Fundamental data fetched but analysis failed."
        new_portfolio_data[sym] = {"fundamental": data, "fundamental_summary": summary}
    
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Fundamental Analyst processed: {', '.join(symbols)}"]
    }

@log_function_call
def technical_node(state: GraphState):
    """Analyzes price trends using Groq."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    model = get_model("groq", GROQ_KEY_TECH, "llama3-70b-8192")
    
    for sym in symbols:
        data = yf_tool.get_historical_data(sym)
        # LLM summary
        prompt = f"Analyze the following technical/historical data for {sym} and provide a 2-sentence trend summary: {data}"
        try:
            summary = model.invoke(prompt).content
        except:
            summary = "Technical trend analysis failed."
        new_portfolio_data[sym] = {"technical": data, "technical_summary": summary}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Technical Analyst processed: {', '.join(symbols)}"]
    }

@log_function_call
def sentiment_node(state: GraphState):
    """Analyzes market mood using Groq."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    model = get_model("groq", GROQ_KEY_SENT, "llama3-70b-8192")
    
    for sym in symbols:
        news = search_tool.search_news(f"{sym} stock news")
        # LLM summary
        prompt = f"Analyze the following news for {sym} and provide a 2-sentence sentiment summary: {news}"
        try:
            summary = model.invoke(prompt).content
        except:
            summary = "Sentiment analysis failed."
        new_portfolio_data[sym] = {"sentiment": news, "sentiment_summary": summary}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Sentiment Analyst processed: {', '.join(symbols)}"]
    }

# Load API keys for real LLM integration
GEMINI_KEY_MASTER = os.getenv("GEMINI_API_KEY_MASTER")
GEMINI_KEY_FUND = os.getenv("GEMINI_API_KEY_FUNDAMENTAL")
GROQ_KEY_TECH = os.getenv("GROQ_API_KEY_TECHNICAL")
GROQ_KEY_SENT = os.getenv("GROQ_API_KEY_SENTIMENT")

@log_function_call
def master_node(state: GraphState):
    """Orchestrates analysis and performs final weighted synthesis using Gemini."""
    if not state.get("portfolio_data"):
        return {"messages": ["Master Node initialized analysis flow"]}
    
    intent = state.get("intent", "status")
    portfolio = state.get("portfolio_data", {})
    
    # Initialize Gemini for synthesis
    model = get_model("google", GEMINI_KEY_MASTER, "gemini-1.5-flash")
    
    # Construct context for the LLM
    context = f"Analysis Intent: {intent}\n"
    for sym, data in portfolio.items():
        context += f"\n--- {sym} Data ---\n"
        context += f"Fundamental: {data.get('fundamental')}\n"
        context += f"Technical: {data.get('technical')}\n"
        context += f"Sentiment: {data.get('sentiment')}\n"

    prompt = f"""
    You are a Master Market Analyst. Analyze the following data and provide a detailed response for the user's intent: {intent}.
    
    If intent is 'comparison', rank the stocks and explain why one is a better buy.
    If intent is 'portfolio', provide an overview of the holdings.
    If intent is 'status', provide a deep dive into the specific stock.
    
    Data Context:
    {context}
    
    Provide a professional, concise, and data-backed report.
    """
    
    try:
        response = model.invoke(prompt)
        report = response.content
    except Exception as e:
        logger.error(f"LLM Synthesis failed: {str(e)}")
        report = f"Error in AI Synthesis: {str(e)}. Data still available in dashboard."

    return {"final_report": report, "messages": ["Master Node completed AI synthesis"]}
