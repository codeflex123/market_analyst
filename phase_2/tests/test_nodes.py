import pytest
from unittest.mock import patch, MagicMock
from src.agents.nodes import fundamental_node, technical_node, sentiment_node, master_node

def test_fundamental_node():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.yf_tool.get_stock_info") as mock_info:
        mock_info.return_value = {"pe_ratio": 25, "debt_to_equity": 0.5}
        result = fundamental_node(state)
        assert "fundamental_data" in result
        assert result["fundamental_data"]["pe_ratio"] == 25
        assert "messages" in result

def test_technical_node():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.yf_tool.get_historical_data") as mock_hist:
        mock_hist.return_value = {"Close": {"2023-01-01": 2500}}
        result = technical_node(state)
        assert "technical_data" in result
        assert "messages" in result

def test_sentiment_node():
    state = {"symbol": "RELIANCE.NS"}
    with patch("src.agents.nodes.search_tool.search_news") as mock_search:
        mock_search.return_value = [{"title": "Good News"}]
        result = sentiment_node(state)
        assert len(result["sentiment_data"]) == 1
        assert "messages" in result

def test_master_node_initial():
    state = {"symbol": "RELIANCE.NS"}
    result = master_node(state)
    assert "messages" in result
    assert "initialized" in result["messages"][0]

def test_master_node_final():
    state = {
        "symbol": "RELIANCE.NS",
        "fundamental_data": {"pe": 25},
        "technical_data": {},
        "sentiment_data": []
    }
    result = master_node(state)
    assert "final_report" in result
    assert "messages" in result
