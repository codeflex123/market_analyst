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
    symbol = state.get("symbol")
    data = yf_tool.get_stock_info(symbol)
    
    # In a real scenario, we'd pass this data to Gemini
    # For Phase 2 implementation, we simulate the LLM synthesis
    report = f"Fundamental analysis for {symbol}: P/E is {data.get('pe_ratio')}, Debt/Equity is {data.get('debt_to_equity')}."
    
    return {
        "fundamental_data": data,
        "messages": [f"Fundamental Analyst finished for {symbol}"]
    }

@log_function_call
def technical_node(state: GraphState):
    """Analyzes price trends using Groq."""
    symbol = state.get("symbol")
    data = yf_tool.get_historical_data(symbol)
    
    # Simulate Groq synthesis
    report = f"Technical analysis for {symbol}: Trend appears stable based on historical data."
    
    return {
        "technical_data": data,
        "messages": [f"Technical Analyst finished for {symbol}"]
    }

@log_function_call
def sentiment_node(state: GraphState):
    """Analyzes market mood using Groq."""
    symbol = state.get("symbol")
    news = search_tool.search_news(f"{symbol} stock news")
    
    # Simulate Groq synthesis
    report = f"Sentiment analysis for {symbol}: Processed {len(news)} news articles."
    
    return {
        "sentiment_data": news,
        "messages": [f"Sentiment Analyst finished for {symbol}"]
    }

@log_function_call
def master_node(state: GraphState):
    """Orchestrates and synthesizes final report using Gemini."""
    # This node will be called twice: once for initial processing, and once for final synthesis
    if not state.get("fundamental_data"):
        # Initial call: Symbol extraction (simulated)
        return {"messages": ["Master Node initialized analysis flow"]}
    
    # Final call: Synthesis
    report = "Final Comprehensive Report: [Simulated Synthesis of FA, TA, SA]"
    return {"final_report": report, "messages": ["Master Node completed synthesis"]}
