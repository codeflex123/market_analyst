import unittest
from unittest.mock import MagicMock, patch
import os
from phase_6.src.agents.nodes import master_node
from phase_6.src.agents.state import GraphState

class TestReportFormat(unittest.TestCase):
    @patch("phase_6.src.agents.nodes.get_model")
    @patch("phase_6.src.agents.nodes.cache_mgr")
    def test_master_node_report_structure(self, mock_cache, mock_get_model):
        # Setup mocks
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = """
        1. **Recommendation**: BUY
        2. **Reasoning**: Mahindra & Mahindra shows strong fundamental growth and positive technical trend. Sentiment is high due to new EV launches.
        3. **Fundamental Analysis Report**:
           - PE ratio: 20, Earning growth: 15%, Revenue: 500B, Profit margin: 10%, Market cap: 2T, Debt level: 50B.
           - Company is in good health.
        4. **Technical Analysis Report**:
           - PE ratio: 20, Earning growth: 15%, Revenue: 500B, Profit margin: 10%, Market cap: 2T, Debt level: 50B.
           - Price is above 200 SMA.
        5. **Sentiment Analyst Report**:
           - Sentiment Score: 8/10
           - PE ratio: 20, Earning growth: 15%, Revenue: 500B, Profit margin: 10%, Market cap: 2T, Debt level: 50B.
           - Market is bullish on leadership.
        """
        mock_model.invoke.return_value = mock_response
        mock_cache.get.return_value = None # Force LLM call
        
        # Prepare state
        state: GraphState = {
            "symbol": "M&M.NS",
            "symbols": ["M&M.NS"],
            "intent": "status",
            "portfolio_data": {
                "M&M.NS": {
                    "fundamental": {"pe_ratio": 20, "earnings_growth": 0.15, "revenue": 500000000, "profit_margin": 0.1, "market_cap": 2000000000, "debt_level": 50000000},
                    "technical": {"trend": "bullish"},
                    "sentiment": [{"title": "M&M launches new EV"}]
                }
            },
            "messages": [],
            "final_report": ""
        }
        
        # Run node
        result = master_node(state)
        
        # Assertions
        self.assertIn("final_report", result)
        report = result["final_report"]
        self.assertIn("Recommendation", report)
        self.assertIn("Reasoning", report)
        self.assertIn("Fundamental Analysis Report", report)
        self.assertIn("Technical Analysis Report", report)
        self.assertIn("Sentiment Analyst Report", report)
        self.assertIn("PE ratio", report)
        self.assertIn("Debt level", report)
        
        # Verify prompt content (informal check)
        args, kwargs = mock_model.invoke.call_args
        prompt = args[0]
        self.assertIn("PE ratio, Earning growth, Revenue, Profit margin, Market cap, Debt level", prompt)
        self.assertIn("EVERY one of the three reports", prompt)

if __name__ == "__main__":
    unittest.main()
