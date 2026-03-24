import pytest
from unittest.mock import MagicMock, patch
from src.tools.yfinance_tool import YFinanceTool
from src.tools.search_tool import SearchTool

@patch("yfinance.Ticker")
def test_yfinance_tool(mock_ticker):
    # Setup mock
    instance = mock_ticker.return_value
    instance.info = {"currentPrice": 2500, "trailingPE": 25, "debtToEquity": 0.5}
    
    tool = YFinanceTool()
    result = tool.get_stock_info("RELIANCE.NS")
    
    assert result["symbol"] == "RELIANCE.NS"
    assert result["current_price"] == 2500
    assert result["pe_ratio"] == 25
    mock_ticker.assert_called_with("RELIANCE.NS")

@patch("src.tools.search_tool.DDGS")
def test_search_tool(mock_ddgs):
    # Setup mock
    instance = mock_ddgs.return_value
    instance.news.return_value = [{"title": "News 1", "url": "http://example.com"}]
    
    tool = SearchTool()
    result = tool.search_news("Reliance Stock")
    
    assert len(result) == 1
    assert result[0]["title"] == "News 1"
