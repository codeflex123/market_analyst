import pytest
from unittest.mock import patch, MagicMock
from src.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_analyze_endpoint_mocked():
    # Test the API endpoint with mocked Graph invocation
    with patch("src.api.main.graph.invoke") as mock_invoke:
        mock_invoke.return_value = {
            "final_report": "Mocked Recommendation",
            "portfolio_data": {"RELIANCE.NS": {"fundamental": {"pe_ratio": 20}}}
        }
        
        response = client.post(
            "/analyze",
            json={"symbols": ["RELIANCE.NS"], "intent": "status"}
        )
        
        assert response.status_code == 200
        assert response.json()["final_report"] == "Mocked Recommendation"
        mock_invoke.assert_called_once()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Phase 4 API is active" in response.json()["message"]
