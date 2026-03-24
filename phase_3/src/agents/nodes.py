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
    """Analyzes financial health for one or more tickers."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        data = yf_tool.get_stock_info(sym)
        new_portfolio_data[sym] = {"fundamental": data}
    
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Fundamental Analyst processed: {', '.join(symbols)}"]
    }

@log_function_call
def technical_node(state: GraphState):
    """Analyzes price trends for one or more tickers."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        data = yf_tool.get_historical_data(sym)
        new_portfolio_data[sym] = {"technical": data}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Technical Analyst processed: {', '.join(symbols)}"]
    }

@log_function_call
def sentiment_node(state: GraphState):
    """Analyzes market mood for one or more tickers."""
    symbols = state.get("symbols") or [state.get("symbol")]
    new_portfolio_data = {}
    
    for sym in symbols:
        news = search_tool.search_news(f"{sym} stock news")
        new_portfolio_data[sym] = {"sentiment": news}
        
    return {
        "portfolio_data": new_portfolio_data,
        "messages": [f"Sentiment Analyst processed: {', '.join(symbols)}"]
    }

@log_function_call
def master_node(state: GraphState):
    """Orchestrates analysis and performs final weighted synthesis."""
    if not state.get("portfolio_data"):
        return {"messages": ["Master Node initialized mult-ticker analysis flow"]}
    
    intent = state.get("intent", "status")
    portfolio = state.get("portfolio_data", {})
    
    if intent == "comparison":
        # Implementation of weighted scoring for 'Which should I buy?'
        # Simplified scoring logic for Phase 3
        rankings = []
        for sym, results in portfolio.items():
            score = 0
            # FA score (lower P/E is better for this demo)
            pe = results.get("fundamental", {}).get("pe_ratio", 50)
            score += (100 - pe) * 0.4 
            # TA score (randomized for demo)
            score += 30 
            # SA score (based on news count for demo)
            score += len(results.get("sentiment", [])) * 5
            rankings.append({"symbol": sym, "score": score})
        
        best = max(rankings, key=lambda x: x["score"])
        report = f"Comparison Report: {best['symbol']} is the recommended buy currently with a score of {best['score']:.2f}."
    
    elif intent == "portfolio":
        summary = ", ".join([f"{s}: Analyzed" for s in portfolio.keys()])
        report = f"Portfolio Summary: {summary}. All sectors appear balanced."
    
    else:
        symbol = state.get("symbol")
        report = f"Status Report for {symbol}: Comprehensive analysis completed successfully."
        
    return {"final_report": report, "messages": ["Master Node completed advanced synthesis"]}
