"""
WeatherETL – Extract → Transform → Load for OpenWeatherMap data.
"""
import pandas as pd
from datetime import datetime
from api_client.weather_client import WeatherClient


class WeatherETL:
    def __init__(self, client: WeatherClient):
        self.client = client

    # ── Extract ───────────────────────────────────────────────────────────────
    def extract_current(self, city: str, units: str = "metric") -> dict:
        return self.client.current(city, units)

    def extract_forecast(self, city: str, units: str = "metric") -> dict:
        return self.client.forecast(city, units)

    # ── Transform ─────────────────────────────────────────────────────────────
    def transform_current(self, raw: dict) -> pd.DataFrame:
        row = {
            "city": raw["name"],
            "country": raw["sys"]["country"],
            "timestamp": datetime.utcfromtimestamp(raw["dt"]),
            "temp": raw["main"]["temp"],
            "feels_like": raw["main"]["feels_like"],
            "temp_min": raw["main"]["temp_min"],
            "temp_max": raw["main"]["temp_max"],
            "humidity": raw["main"]["humidity"],
            "pressure": raw["main"]["pressure"],
            "wind_speed": raw["wind"]["speed"],
            "wind_deg": raw["wind"].get("deg", None),
            "weather_main": raw["weather"][0]["main"],
            "weather_desc": raw["weather"][0]["description"],
            "visibility": raw.get("visibility", None),
            "clouds": raw["clouds"]["all"],
        }
        return pd.DataFrame([row])

    def transform_forecast(self, raw: dict) -> pd.DataFrame:
        rows = []
        for item in raw["list"]:
            rows.append({
                "city": raw["city"]["name"],
                "country": raw["city"]["country"],
                "timestamp": datetime.utcfromtimestamp(item["dt"]),
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "temp_min": item["main"]["temp_min"],
                "temp_max": item["main"]["temp_max"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "wind_speed": item["wind"]["speed"],
                "weather_main": item["weather"][0]["main"],
                "weather_desc": item["weather"][0]["description"],
                "pop": item.get("pop", 0),  # probability of precipitation
                "clouds": item["clouds"]["all"],
            })
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    # ── Load ──────────────────────────────────────────────────────────────────
    @staticmethod
    def load(df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

    # ── Pipeline (all-in-one) ─────────────────────────────────────────────────
    def run(self, city: str, units: str = "metric") -> dict:
        """Returns dict with 'current' and 'forecast' DataFrames."""
        raw_cur = self.extract_current(city, units)
        raw_fc = self.extract_forecast(city, units)
        df_cur = self.transform_current(raw_cur)
        df_fc = self.transform_forecast(raw_fc)
        return {"current": df_cur, "forecast": df_fc}
