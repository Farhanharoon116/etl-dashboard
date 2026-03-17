"""
WeatherClient – wraps OpenWeatherMap API with local file caching.
"""
import json
import time
import hashlib
import requests
from pathlib import Path


CACHE_DIR = Path(".cache/weather")
CACHE_TTL = 600  # seconds


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


class WeatherClient:
    BASE = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, endpoint: str, params: dict) -> dict:
        params["appid"] = self.api_key
        key = _cache_key({"endpoint": endpoint, **params})
        cached = _load_cache(key)
        if cached:
            return cached
        resp = requests.get(f"{self.BASE}/{endpoint}", params=params, timeout=10)
        if resp.status_code == 404:
            raise ValueError(f"City not found: {params.get('q', '')}")
        resp.raise_for_status()
        data = resp.json()
        _save_cache(key, data)
        return data

    def current(self, city: str, units: str = "metric") -> dict:
        return self._get("weather", {"q": city, "units": units})

    def forecast(self, city: str, units: str = "metric") -> dict:
        """5-day / 3-hour forecast."""
        return self._get("forecast", {"q": city, "units": units})
