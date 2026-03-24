from fastapi import FastAPI
from src.logger import logger, log_function_call
from src.tools.yfinance_tool import YFinanceTool
from src.tools.search_tool import SearchTool

app = FastAPI(title="Market Analyst API")

yf_tool = YFinanceTool()
search_tool = SearchTool()

@app.get("/")
@log_function_call
async def root():
    return {"message": "Market Analyst API is running"}

@app.get("/stock/{symbol}")
@log_function_call
async def get_stock(symbol: str):
    return yf_tool.get_stock_info(symbol)

@app.get("/search")
@log_function_call
async def search(q: str):
    return search_tool.search_news(q)
