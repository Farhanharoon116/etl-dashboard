"""
FinanceClient – wraps Alpha Vantage API with local file caching.
"""
import json
import time
import hashlib
import requests
from pathlib import Path


CACHE_DIR = Path(".cache/finance")
CACHE_TTL = 300  # seconds


def _cache_key(params: dict) -> str:
    raw = json.dumps(params, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _load_cache(key: str):
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        with open(path) as f:
            entry = json.load(f)
        if time.time() - entry["ts"] < CACHE_TTL:
            return entry["data"]
    return None


def _save_cache(key: str, data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    with open(path, "w") as f:
        json.dump({"ts": time.time(), "data": data}, f)


class FinanceClient:
    BASE = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, params: dict) -> dict:
        params["apikey"] = self.api_key
        key = _cache_key(params)
        cached = _load_cache(key)
        if cached:
            return cached
        resp = requests.get(self.BASE, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "Error Message" in data:
            raise ValueError(f"Invalid symbol or API error: {data['Error Message']}")
        if "Note" in data:
            raise RuntimeError(f"Alpha Vantage rate limit hit: {data['Note']}")
        _save_cache(key, data)
        return data

    def intraday(self, symbol: str, interval: str = "5min") -> dict:
        return self._get({
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": "compact",
        })

    def daily(self, symbol: str, outputsize: str = "compact") -> dict:
        return self._get({
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
        })

    def quote(self, symbol: str) -> dict:
        return self._get({"function": "GLOBAL_QUOTE", "symbol": symbol})
