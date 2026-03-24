import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Market Analyst API is running"}

@patch("src.tools.yfinance_tool.YFinanceTool.get_stock_info")
def test_get_stock(mock_get_info):
    mock_get_info.return_value = {"symbol": "RELIANCE.NS", "current_price": 2500}
    
    response = client.get("/stock/RELIANCE.NS")
    assert response.status_code == 200
    assert response.json()["symbol"] == "RELIANCE.NS"
    mock_get_info.assert_called_with("RELIANCE.NS")

@patch("src.tools.search_tool.SearchTool.search_news")
def test_search(mock_search):
    mock_search.return_value = [{"title": "Test News"}]
    
    response = client.get("/search?q=Reliance")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Test News"
    mock_search.assert_called_with("Reliance")
