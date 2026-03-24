from typing import TypedDict, Annotated, List, Dict
import operator

class GraphState(TypedDict):
    # Stock symbol (for single stock queries)
    symbol: str 
    # List of stock symbols for portfolio/comparison
    symbols: List[str]
    # Intent of the user (Status, Portfolio, Comparison)
    intent: str
    
    # Tool results (Individual)
    fundamental_data: Dict[str, any]
    technical_data: Dict[str, any]
    sentiment_data: List[Dict[str, any]]
    
    # Advanced Data (Phase 3)
    # Mapping of symbol -> {fundamental, technical, sentiment}
    portfolio_data: Annotated[Dict[str, Dict[str, any]], operator.ior]
    comparison_results: Dict[str, any]
    
    # Final consolidated report
    final_report: str
    
    # Internal logs/state
    messages: Annotated[List[str], operator.add]
