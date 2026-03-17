"""
FinancePlots – Plotly figures for financial data.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


THEME = dict(
    bg="#0f172a",
    surface="#1e293b",
    accent="#38bdf8",
    accent2="#818cf8",
    up="#34d399",
    down="#f87171",
    text="#f1f5f9",
    muted="#94a3b8",
)


def _base_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=THEME["text"], size=16)),
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["surface"],
        font=dict(color=THEME["text"]),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        margin=dict(l=50, r=30, t=60, b=50),
    )


class FinancePlots:
    @staticmethod
    def candlestick(df: pd.DataFrame, symbol: str, bb: pd.DataFrame = None) -> go.Figure:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.7, 0.3], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(
            x=df["timestamp"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name="OHLC",
            increasing_line_color=THEME["up"],
            decreasing_line_color=THEME["down"],
        ), row=1, col=1)
        if df["ma_5"].notna().any():
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df["ma_5"], name="MA 5",
                line=dict(color=THEME["accent"], width=1.5, dash="dot"),
            ), row=1, col=1)
        if df["ma_20"].notna().any():
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df["ma_20"], name="MA 20",
                line=dict(color=THEME["accent2"], width=1.5),
            ), row=1, col=1)
        if bb is not None and not bb.empty:
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=bb["bb_upper"], name="BB Upper",
                line=dict(color="#475569", width=1), showlegend=False,
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=bb["bb_lower"], name="BB Lower",
                line=dict(color="#475569", width=1),
                fill="tonexty", fillcolor="rgba(71,85,105,0.2)",
            ), row=1, col=1)
        colors = [THEME["up"] if r >= 0 else THEME["down"] for r in df["price_change"].fillna(0)]
        fig.add_trace(go.Bar(
            x=df["timestamp"], y=df["volume"], name="Volume",
            marker_color=colors, opacity=0.7,
        ), row=2, col=1)
        layout = _base_layout(f"{symbol} – Price & Volume")
        layout["xaxis2"] = dict(gridcolor="#334155")
        layout["yaxis2"] = dict(title="Volume", gridcolor="#334155")
        layout["xaxis_rangeslider_visible"] = False
        fig.update_layout(**layout)
        return fig

    @staticmethod
    def rsi_plot(df: pd.DataFrame, rsi: pd.Series, symbol: str) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=rsi,
            name="RSI", line=dict(color=THEME["accent"], width=2),
        ))
        fig.add_hline(y=70, line_color=THEME["down"], line_dash="dash", annotation_text="Overbought")
        fig.add_hline(y=30, line_color=THEME["up"], line_dash="dash", annotation_text="Oversold")
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(56,189,248,0.05)", line_width=0)
        layout = _base_layout(f"{symbol} – RSI (14)")
        layout["yaxis"] = dict(range=[0, 100], gridcolor="#334155")
        fig.update_layout(**layout)
        return fig

    @staticmethod
    def returns_histogram(df: pd.DataFrame, symbol: str) -> go.Figure:
        pct = df["pct_change"].dropna()
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=pct, name="Daily Returns",
            marker_color=THEME["accent2"], opacity=0.8,
            nbinsx=40,
        ))
        fig.add_vline(x=0, line_color=THEME["muted"], line_dash="dash")
        layout = _base_layout(f"{symbol} – Return Distribution")
        layout["xaxis"] = dict(title="% Return", gridcolor="#334155")
        layout["yaxis"] = dict(title="Count", gridcolor="#334155")
        fig.update_layout(**layout, bargap=0.05)
        return fig
