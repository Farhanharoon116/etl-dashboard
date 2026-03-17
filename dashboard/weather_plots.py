"""
WeatherPlots – Plotly figures for weather data.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


THEME = dict(
    bg="#0f172a",
    surface="#1e293b",
    accent="#38bdf8",
    accent2="#818cf8",
    warm="#fb923c",
    cool="#34d399",
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


class WeatherPlots:
    @staticmethod
    def forecast_temperature(df_forecast: pd.DataFrame, city: str) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df_forecast["timestamp"], y=df_forecast["temp_max"],
            name="Max Temp", line=dict(color=THEME["warm"], width=2),
            fill=None,
        ))
        fig.add_trace(go.Scatter(
            x=df_forecast["timestamp"], y=df_forecast["temp_min"],
            name="Min Temp", line=dict(color=THEME["cool"], width=2),
            fill="tonexty", fillcolor="rgba(52,211,153,0.15)",
        ))
        fig.add_trace(go.Scatter(
            x=df_forecast["timestamp"], y=df_forecast["temp"],
            name="Avg Temp", line=dict(color=THEME["accent"], width=2, dash="dot"),
        ))
        fig.add_trace(go.Bar(
            x=df_forecast["timestamp"], y=df_forecast["pop"] * 100,
            name="Rain Prob %", marker_color=THEME["accent2"],
            opacity=0.4,
        ), secondary_y=True)
        layout = _base_layout(f"5-Day Forecast – {city}")
        layout["yaxis"] = dict(title="Temperature (°C)", gridcolor="#334155")
        layout["yaxis2"] = dict(title="Rain Probability (%)", gridcolor="#334155")
        fig.update_layout(**layout)
        return fig

    @staticmethod
    def current_gauges(df_current: pd.DataFrame) -> go.Figure:
        row = df_current.iloc[0]
        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
        )
        indicators = [
            ("Temperature", row["temp"], "°C", -20, 50, THEME["warm"]),
            ("Humidity", row["humidity"], "%", 0, 100, THEME["accent"]),
            ("Wind Speed", row["wind_speed"], " m/s", 0, 30, THEME["cool"]),
        ]
        for i, (name, val, suffix, mn, mx, color) in enumerate(indicators, 1):
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=val,
                number=dict(suffix=suffix, font=dict(color=color)),
                title=dict(text=name, font=dict(color=THEME["muted"])),
                gauge=dict(
                    axis=dict(range=[mn, mx], tickcolor=THEME["muted"]),
                    bar=dict(color=color),
                    bgcolor=THEME["surface"],
                    borderwidth=0,
                    steps=[dict(range=[mn, mx], color="#1e293b")],
                ),
            ), row=1, col=i)
        fig.update_layout(
            paper_bgcolor=THEME["bg"],
            font=dict(color=THEME["text"]),
            margin=dict(l=20, r=20, t=40, b=20),
            height=250,
        )
        return fig

    @staticmethod
    def humidity_wind(df_forecast: pd.DataFrame, city: str) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=df_forecast["timestamp"], y=df_forecast["humidity"],
            name="Humidity %", marker_color=THEME["accent"], opacity=0.7,
        ))
        fig.add_trace(go.Scatter(
            x=df_forecast["timestamp"], y=df_forecast["wind_speed"],
            name="Wind Speed m/s", line=dict(color=THEME["warm"], width=2),
        ), secondary_y=True)
        layout = _base_layout(f"Humidity & Wind – {city}")
        layout["yaxis"] = dict(title="Humidity (%)", gridcolor="#334155")
        layout["yaxis2"] = dict(title="Wind Speed (m/s)", gridcolor="#334155")
        fig.update_layout(**layout)
        return fig
