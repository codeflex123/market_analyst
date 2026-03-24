import json
import os
import time
from typing import Dict, Any, Optional
from phase_6.src.logger import logger

class CacheManager:
    """Manages persistent caching for stock analysis results."""
    
    def __init__(self, cache_file: str = "analysis_cache.json", ttl_seconds: int = 14400):
        self.cache_file = cache_file
        self.ttl_seconds = ttl_seconds
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache: {str(e)}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")

    def get(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached result if not expired."""
        if symbol in self.cache:
            entry = self.cache[symbol]
            timestamp = entry.get("timestamp", 0)
            if (time.time() - timestamp) < self.ttl_seconds:
                logger.info(f"Cache hit for {symbol}")
                return entry.get("data")
            else:
                logger.info(f"Cache expired for {symbol}")
                del self.cache[symbol]
                self._save_cache()
        return None

    def set(self, symbol: str, data: Dict[str, Any]):
        """Saves result to cache with current timestamp."""
        self.cache[symbol] = {
            "timestamp": time.time(),
            "data": data
        }
        self._save_cache()
        logger.info(f"Cache saved for {symbol}")
