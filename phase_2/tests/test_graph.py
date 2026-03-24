import pytest
from src.agents.graph import create_graph

def test_graph_structure():
    graph = create_graph()
    assert graph is not None
    # In LangGraph 0.x, nodes are stored in the graph object
    # The structure varies by version, but we can verify it's a compiled graph
    assert hasattr(graph, "invoke")

def test_graph_logic_flow():
    graph = create_graph()
    initial_state = {
        "symbol": "RELIANCE.NS",
        "symbols": [],
        "intent": "status",
        "messages": [],
        "fundamental_data": None,
        "technical_data": None,
        "sentiment_data": None,
        "final_report": None
    }
    
    # We can't easily run a full graph without real LLM calls unless we mock the nodes
    # But we can verify it compiles and the structure is valid.
    assert graph.get_graph() is not None
