import pytest
from unittest.mock import patch, MagicMock
from src.agents.nodes import fundamental_node, technical_node, sentiment_node, master_node

def test_portfolio_aggregation():
    # Test with multiple symbols
    state = {"symbols": ["RELIANCE.NS", "TATAMOTORS.NS"]}
    
    with patch("src.agents.nodes.yf_tool.get_stock_info") as mock_info:
        mock_info.return_value = {"pe_ratio": 25}
        result = fundamental_node(state)
        
        assert "portfolio_data" in result
        assert "RELIANCE.NS" in result["portfolio_data"]
        assert "TATAMOTORS.NS" in result["portfolio_data"]
        assert result["portfolio_data"]["RELIANCE.NS"]["fundamental"]["pe_ratio"] == 25

def test_comparison_recommendation():
    # Test Comparison intent and weighted scoring
    state = {
        "intent": "comparison",
        "symbols": ["TATA", "MAHINDRA"],
        "portfolio_data": {
            "TATA": {
                "fundamental": {"pe_ratio": 20},
                "technical": {},
                "sentiment": [{"title": "Good"}] * 5
            },
            "MAHINDRA": {
                "fundamental": {"pe_ratio": 40},
                "technical": {},
                "sentiment": [{"title": "Ok"}] * 1
            }
        }
    }
    
    result = master_node(state)
    assert "final_report" in result
    assert "TATA" in result["final_report"] # TATA should have higher score (lower PE, more news)
    assert "Comparison Report" in result["final_report"]

def test_portfolio_summary():
    # Test Portfolio intent
    state = {
        "intent": "portfolio",
        "symbols": ["INFY", "TCS"],
        "portfolio_data": {
            "INFY": {"fundamental": {}, "technical": {}, "sentiment": []},
            "TCS": {"fundamental": {}, "technical": {}, "sentiment": []}
        }
    }
    
    result = master_node(state)
    assert "final_report" in result
    assert "Portfolio Summary" in result["final_report"]
    assert "INFY" in result["final_report"]
    assert "TCS" in result["final_report"]
