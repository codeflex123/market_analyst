import yfinance as yf
from src.logger import logger, log_function_call

class YFinanceTool:
    @log_function_call
    def get_stock_info(self, symbol: str):
        """Fetches basic stock information and ratios."""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "current_price": info.get("currentPrice"),
            "pe_ratio": info.get("trailingPE"),
            "debt_to_equity": info.get("debtToEquity"),
            "revenue_growth": info.get("revenueGrowth"),
            "market_cap": info.get("marketCap")
        }

    @log_function_call
    def get_historical_data(self, symbol: str, period: str = "1mo"):
        """Fetches historical price data."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df.to_dict()
