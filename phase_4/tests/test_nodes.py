import pytest
from unittest.mock import patch, MagicMock
from src.agents.nodes import fundamental_node, technical_node, sentiment_node, master_node

def test_fundamental_node_phase3():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.yf_tool.get_stock_info") as mock_info:
        mock_info.return_value = {"pe_ratio": 25}
        result = fundamental_node(state)
        # Verify it now uses portfolio_data
        assert "portfolio_data" in result
        assert "RELIANCE.NS" in result["portfolio_data"]
        assert result["portfolio_data"]["RELIANCE.NS"]["fundamental"]["pe_ratio"] == 25

def test_technical_node_phase3():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.yf_tool.get_historical_data") as mock_hist:
        mock_hist.return_value = {"Close": {}}
        result = technical_node(state)
        assert "portfolio_data" in result
        assert "RELIANCE.NS" in result["portfolio_data"]

def test_sentiment_node_phase3():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.search_tool.search_news") as mock_search:
        mock_search.return_value = [{"title": "Good"}]
        result = sentiment_node(state)
        assert "portfolio_data" in result
        assert len(result["portfolio_data"]["RELIANCE.NS"]["sentiment"]) == 1

def test_master_node_status():
    state = {"symbol": "RELIANCE.NS", "portfolio_data": {"RELIANCE.NS": {}}}
    result = master_node(state)
    assert "Status Report" in result["final_report"]
