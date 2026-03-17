"""
WeatherAnalysis – statistical summaries and derived metrics from weather DataFrames.
"""
import pandas as pd


class WeatherAnalysis:
    @staticmethod
    def daily_summary(df_forecast: pd.DataFrame) -> pd.DataFrame:
        """Aggregate 3-hour forecast into daily min/max/avg."""
        df = df_forecast.copy()
        df["date"] = df["timestamp"].dt.date
        summary = df.groupby("date").agg(
            temp_min=("temp_min", "min"),
            temp_max=("temp_max", "max"),
            temp_avg=("temp", "mean"),
            humidity_avg=("humidity", "mean"),
            wind_avg=("wind_speed", "mean"),
            rain_prob_max=("pop", "max"),
        ).reset_index()
        summary["temp_range"] = summary["temp_max"] - summary["temp_min"]
        return summary

    @staticmethod
    def comfort_index(df: pd.DataFrame) -> pd.Series:
        """
        Simple apparent-comfort index combining temp and humidity.
        Returns a Series of labels: Cold / Cool / Comfortable / Warm / Hot
        """
        temp = df["temp"]
        hum = df["humidity"]
        heat_index = temp + 0.33 * (hum / 100 * 6.105) - 4.0
        bins = [-float("inf"), 5, 15, 25, 32, float("inf")]
        labels = ["Cold", "Cool", "Comfortable", "Warm", "Hot"]
        return pd.cut(heat_index, bins=bins, labels=labels)

    @staticmethod
    def trend(df_forecast: pd.DataFrame) -> str:
        """Simple rising/falling temperature trend over next 24 h."""
        next_24 = df_forecast.head(8)  # 8 × 3h = 24h
        if next_24.empty:
            return "unknown"
        first = next_24["temp"].iloc[0]
        last = next_24["temp"].iloc[-1]
        delta = last - first
        if delta > 2:
            return f"Rising (+{delta:.1f}°)"
        if delta < -2:
            return f"Falling ({delta:.1f}°)"
        return "Stable"
