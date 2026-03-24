from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.logger import logger, log_function_call
from src.agents.graph import create_graph

app = FastAPI(title="Market Analyst - Advanced API")
graph = create_graph()

class AnalysisRequest(BaseModel):
    symbols: List[str]
    intent: Optional[str] = "status"

@app.get("/")
@log_function_call
async def root():
    return {"message": "Market Analyst Phase 4 API is active"}

@app.post("/analyze")
@log_function_call
async def analyze_stocks(request: AnalysisRequest):
    """Invokes the LangGraph orchestrator for the given symbols."""
    try:
        initial_state = {
            "symbols": request.symbols,
            "intent": request.intent,
            "symbol": request.symbols[0] if request.symbols else "",
            "messages": [],
            "portfolio_data": {},
            "final_report": ""
        }
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
