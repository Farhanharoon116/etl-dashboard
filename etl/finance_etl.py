"""
FinanceETL – Extract → Transform → Load for Alpha Vantage data.
"""
import pandas as pd
from api_client.finance_client import FinanceClient


class FinanceETL:
    def __init__(self, client: FinanceClient):
        self.client = client

    # ── Extract ───────────────────────────────────────────────────────────────
    def extract_intraday(self, symbol: str, interval: str = "5min") -> dict:
        return self.client.intraday(symbol, interval)

    def extract_daily(self, symbol: str, outputsize: str = "compact") -> dict:
        return self.client.daily(symbol, outputsize)

    def extract_quote(self, symbol: str) -> dict:
        return self.client.quote(symbol)

    # ── Transform ─────────────────────────────────────────────────────────────
    def _parse_timeseries(self, raw: dict, ts_key: str) -> pd.DataFrame:
        series = raw.get(ts_key, {})
        rows = []
        for dt_str, vals in series.items():
            rows.append({
                "timestamp": pd.to_datetime(dt_str),
                "open": float(vals["1. open"]),
                "high": float(vals["2. high"]),
                "low": float(vals["3. low"]),
                "close": float(vals["4. close"]),
                "volume": int(vals["5. volume"]),
            })
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        # Derived columns
        df["price_change"] = df["close"].diff()
        df["pct_change"] = df["close"].pct_change() * 100
        df["ma_5"] = df["close"].rolling(5).mean()
        df["ma_20"] = df["close"].rolling(20).mean()
        df["volatility"] = df["close"].rolling(10).std()
        return df

    def transform_intraday(self, raw: dict, interval: str = "5min") -> pd.DataFrame:
        key = f"Time Series ({interval})"
        df = self._parse_timeseries(raw, key)
        meta = raw.get("Meta Data", {})
        df["symbol"] = meta.get("2. Symbol", "")
        return df

    def transform_daily(self, raw: dict) -> pd.DataFrame:
        df = self._parse_timeseries(raw, "Time Series (Daily)")
        meta = raw.get("Meta Data", {})
        df["symbol"] = meta.get("2. Symbol", "")
        return df

    def transform_quote(self, raw: dict) -> pd.DataFrame:
        q = raw.get("Global Quote", {})
        return pd.DataFrame([{
            "symbol": q.get("01. symbol", ""),
            "open": float(q.get("02. open", 0)),
            "high": float(q.get("03. high", 0)),
            "low": float(q.get("04. low", 0)),
            "price": float(q.get("05. price", 0)),
            "volume": int(q.get("06. volume", 0)),
            "latest_day": q.get("07. latest trading day", ""),
            "prev_close": float(q.get("08. previous close", 0)),
            "change": float(q.get("09. change", 0)),
            "change_pct": q.get("10. change percent", "0%").replace("%", ""),
        }])

    # ── Load ──────────────────────────────────────────────────────────────────
    @staticmethod
    def load(df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

    # ── Pipeline ──────────────────────────────────────────────────────────────
    def run(self, symbol: str, interval: str = "5min", mode: str = "daily") -> dict:
        """
        Returns dict with 'series' DataFrame and 'quote' DataFrame.
        mode: 'intraday' | 'daily'
        """
        if mode == "intraday":
            raw = self.extract_intraday(symbol, interval)
            df_series = self.transform_intraday(raw, interval)
        else:
            raw = self.extract_daily(symbol)
            df_series = self.transform_daily(raw)

        raw_q = self.extract_quote(symbol)
        df_quote = self.transform_quote(raw_q)
        return {"series": df_series, "quote": df_quote}
