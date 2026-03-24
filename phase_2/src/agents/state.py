from typing import TypedDict, Annotated, List, Dict
import operator

class GraphState(TypedDict):
    # Stock symbol (e.g., RELIANCE.NS)
    symbol: str 
    # List of stock symbols for portfolio/comparison
    symbols: List[str]
    # Intent of the user (Status, Portfolio, Comparison)
    intent: str
    
    # Tool results
    fundamental_data: Dict[str, any]
    technical_data: Dict[str, any]
    sentiment_data: List[Dict[str, any]]
    
    # Final consolidated report
    final_report: str
    
    # Internal logs/state
    messages: Annotated[List[str], operator.add]
