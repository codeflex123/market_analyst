from duckduckgo_search import DDGS
from src.logger import logger, log_function_call

class SearchTool:
    def __init__(self):
        self.ddgs = DDGS()

    @log_function_call
    def search_news(self, query: str, max_results: int = 5):
        """Searches for news articles using DuckDuckGo."""
        results = list(self.ddgs.news(query, max_results=max_results))
        return results
