"""
FinanceAnalysis – statistical summaries and indicators from finance DataFrames.
"""
import pandas as pd
import numpy as np


class FinanceAnalysis:
    @staticmethod
    def summary_stats(df: pd.DataFrame) -> dict:
        if df.empty:
            return {}
        close = df["close"]
        return {
            "current_price": close.iloc[-1],
            "period_high": df["high"].max(),
            "period_low": df["low"].min(),
            "avg_volume": int(df["volume"].mean()),
            "total_return_pct": ((close.iloc[-1] / close.iloc[0]) - 1) * 100,
            "volatility_std": close.std(),
            "sharpe_proxy": close.pct_change().mean() / (close.pct_change().std() + 1e-9),
        }

    @staticmethod
    def rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
        delta = df["close"].diff()
        gain = delta.clip(lower=0).rolling(window).mean()
        loss = (-delta.clip(upper=0)).rolling(window).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        mid = df["close"].rolling(window).mean()
        std = df["close"].rolling(window).std()
        return pd.DataFrame({
            "bb_mid": mid,
            "bb_upper": mid + num_std * std,
            "bb_lower": mid - num_std * std,
        }, index=df.index)

    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        typical = (df["high"] + df["low"] + df["close"]) / 3
        cum_tv = (typical * df["volume"]).cumsum()
        cum_vol = df["volume"].cumsum()
        return cum_tv / (cum_vol + 1e-9)

    @staticmethod
    def filter_date_range(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
        mask = (df["timestamp"] >= pd.to_datetime(start)) & (df["timestamp"] <= pd.to_datetime(end))
        return df.loc[mask].reset_index(drop=True)
