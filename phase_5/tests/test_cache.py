import pytest
import time
import os
from src.tools.cache_manager import CacheManager

def test_cache_set_get():
    cache_file = "test_cache.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        
    mgr = CacheManager(cache_file=cache_file, ttl_seconds=2)
    data = {"test": "data"}
    mgr.set("REL", data)
    
    # Hit
    assert mgr.get("REL") == data
    
    # Expiry
    time.sleep(3)
    assert mgr.get("REL") is None
    
    if os.path.exists(cache_file):
        os.remove(cache_file)

def test_cache_persistence():
    cache_file = "test_persist.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        
    mgr1 = CacheManager(cache_file=cache_file)
    mgr1.set("TATA", {"price": 100})
    
    mgr2 = CacheManager(cache_file=cache_file)
    assert mgr2.get("TATA") == {"price": 100}
    
    if os.path.exists(cache_file):
        os.remove(cache_file)
