"""
app.py — ETL Dashboard · Glassmorphism Edition
Run: streamlit run app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config import OPENWEATHER_API_KEY, ALPHAVANTAGE_API_KEY
from api_client import WeatherClient, FinanceClient
from etl import WeatherETL, FinanceETL
from analysis import WeatherAnalysis, FinanceAnalysis
from dashboard import WeatherPlots, FinancePlots

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataPulse · ETL Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — Glassmorphism + Gradient Theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif;
    background: #060918;
    color: #e2e8f0;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #060918 0%, #0d1b3e 40%, #0a1628 70%, #060918 100%);
    min-height: 100vh;
}

/* Animated mesh background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(6,182,212,0.10) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(139,92,246,0.07) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(13, 20, 50, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(99,102,241,0.2);
}

[data-testid="stSidebar"] * { font-family: 'Outfit', sans-serif !important; }

/* ── Glassmorphism Cards ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s ease;
}
.glass-card:hover { border-color: rgba(99,102,241,0.35); }

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin: 1rem 0;
}
.metric-pill {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    text-align: center;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.metric-pill::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 14px 14px 0 0;
}
.metric-pill.blue::before  { background: linear-gradient(90deg, #6366f1, #06b6d4); }
.metric-pill.purple::before { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
.metric-pill.green::before  { background: linear-gradient(90deg, #10b981, #06b6d4); }
.metric-pill.orange::before { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.metric-pill.cyan::before   { background: linear-gradient(90deg, #06b6d4, #6366f1); }
.metric-pill:hover { transform: translateY(-2px); border-color: rgba(99,102,241,0.3); }
.metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, #e2e8f0, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.metric-val.up   { background: linear-gradient(135deg, #10b981, #06b6d4); -webkit-background-clip: text; }
.metric-val.down { background: linear-gradient(135deg, #ef4444, #f97316); -webkit-background-clip: text; }
.metric-lbl {
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-top: 4px;
}
.metric-sub {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 2px;
}

/* ── Page Header ── */
.page-header {
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.5rem;
}
.page-title {
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #e2e8f0 30%, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.page-subtitle { color: #64748b; font-size: 0.9rem; margin-top: 4px; }

/* ── Mode Toggle ── */
.mode-toggle {
    display: flex;
    gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 6px;
    margin-bottom: 1.5rem;
}
.mode-btn {
    flex: 1;
    padding: 10px 16px;
    border-radius: 8px;
    border: none;
    font-family: 'Outfit', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;
    text-align: center;
}
.mode-btn.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35);
}
.mode-btn.inactive {
    background: transparent;
    color: #64748b;
}

/* ── Section Labels ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6366f1;
    margin-bottom: 8px;
    margin-top: 16px;
}

/* ── Badge ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818cf8;
    border-radius: 99px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
}
.badge.green { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.25); color: #34d399; }
.badge.orange { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.25); color: #fbbf24; }

/* ── Trend Arrow ── */
.trend-up   { color: #10b981; font-weight: 600; }
.trend-down { color: #ef4444; font-weight: 600; }
.trend-flat { color: #64748b; font-weight: 600; }

/* ── Pipeline Steps ── */
.pipeline-row { display: flex; gap: 0; align-items: center; margin: 0.75rem 0; }
.pipeline-step {
    flex: 1;
    padding: 8px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.03);
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}
.pipeline-step:first-child { border-radius: 8px 0 0 8px; }
.pipeline-step:last-child  { border-radius: 0 8px 8px 0; }
.pipeline-step.done {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.3);
    color: #818cf8;
}
.pipeline-arrow { color: #334155; font-size: 1rem; padding: 0 4px; }

/* ── Weather specific ── */
.weather-icon { font-size: 3rem; }
.weather-condition {
    font-size: 1.1rem;
    font-weight: 500;
    color: #94a3b8;
    text-transform: capitalize;
}

/* ── Streamlit overrides ── */
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stDateInput"] > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
}

div[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

button[data-testid="baseButton-primary"],
div.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    transition: all 0.25s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}

div[data-testid="stTabs"] button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    color: #64748b !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #818cf8 !important;
    border-bottom-color: #6366f1 !important;
}

.stDataFrame { border-radius: 12px; overflow: hidden; }
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    color: #334155;
}
.empty-state h2 { color: #475569; font-size: 1.4rem; margin: 1rem 0 0.5rem; }
.empty-state p  { color: #334155; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────
COLORS = dict(
    bg         = "rgba(0,0,0,0)",
    surface    = "rgba(255,255,255,0.03)",
    grid       = "rgba(255,255,255,0.05)",
    indigo     = "#6366f1",
    violet     = "#8b5cf6",
    cyan       = "#06b6d4",
    emerald    = "#10b981",
    rose       = "#ef4444",
    amber      = "#f59e0b",
    text       = "#e2e8f0",
    muted      = "#64748b",
)

def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(color=COLORS["text"], size=14, family="Outfit"), x=0.02),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor =COLORS["surface"],
        font=dict(color=COLORS["text"], family="Outfit"),
        height=height,
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["muted"], size=11)),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["muted"], size=11)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["muted"])),
        margin=dict(l=10, r=10, t=45, b=10),
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#334155",
                        font=dict(color="#e2e8f0", family="Outfit")),
    )

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
WEATHER_ICONS = {
    "Clear":"☀️","Clouds":"☁️","Rain":"🌧️","Drizzle":"🌦️",
    "Thunderstorm":"⛈️","Snow":"❄️","Mist":"🌫️","Fog":"🌫️",
    "Haze":"🌫️","Smoke":"🌫️","Dust":"🌪️","Sand":"🌪️",
    "Ash":"🌋","Squall":"💨","Tornado":"🌪️",
}

def weather_icon(condition):
    return WEATHER_ICONS.get(condition, "🌡️")

def pill(val, label, color="blue", sub=None):
    sub_html = f"<div class='metric-sub'>{sub}</div>" if sub else ""
    return f"""
    <div class='metric-pill {color}'>
        <div class='metric-val'>{val}</div>
        <div class='metric-lbl'>{label}</div>
        {sub_html}
    </div>"""

def pipeline_bar(stage: int):
    stages = ["EXTRACT", "TRANSFORM", "LOAD"]
    html = "<div class='pipeline-row'>"
    for i, s in enumerate(stages):
        cls = "done" if i <= stage else ""
        check = "✓ " if i < stage else ("⟳ " if i == stage else "")
        html += f"<div class='pipeline-step {cls}'>{check}{s}</div>"
        if i < len(stages)-1:
            html += "<span class='pipeline-arrow'>→</span>"
    html += "</div>"
    return html

def format_temp(val, unit):
    suffix = {"metric":"°C","imperial":"°F","standard":"K"}[unit]
    return f"{val:.1f}{suffix}"

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem;'>
        <div style='font-size:1.4rem; font-weight:700; background:linear-gradient(135deg,#e2e8f0,#6366f1);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            DataPulse
        </div>
        <div style='font-size:0.75rem; color:#475569; margin-top:2px;'>ETL Pipeline Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Mode selector
    st.markdown("<div class='section-label'>Dataset Mode</div>", unsafe_allow_html=True)
    mode = st.radio("", ["🌤  Weather", "📈  Finance"], label_visibility="collapsed")
    is_weather = "Weather" in mode

    st.markdown("---")

    if is_weather:
        st.markdown("<div class='section-label'>Weather Parameters</div>", unsafe_allow_html=True)

        city = st.text_input("City", value="London", placeholder="e.g. Tokyo, Dubai, New York")

        unit_label = st.selectbox("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"])
        unit_map   = {"Celsius (°C)":"metric","Fahrenheit (°F)":"imperial","Kelvin (K)":"standard"}
        units      = unit_map[unit_label]

        st.markdown("<div class='section-label'>Display Options</div>", unsafe_allow_html=True)
        show_comfort  = st.toggle("Comfort Index", value=True)
        show_raw      = st.toggle("Show Raw Data", value=False)

    else:
        st.markdown("<div class='section-label'>Finance Parameters</div>", unsafe_allow_html=True)

        symbol   = st.text_input("Stock Symbol", value="AAPL", placeholder="e.g. TSLA, MSFT, NVDA").upper().strip()
        ts_mode  = st.selectbox("Time Series", ["Daily", "Intraday"])
        interval = "5min"
        if ts_mode == "Intraday":
            interval = st.selectbox("Interval", ["1min","5min","15min","30min","60min"])

        st.markdown("<div class='section-label'>Date Range</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=date.today()-timedelta(days=90))
        with col2:
            end_date = st.date_input("To", value=date.today())

        st.markdown("<div class='section-label'>Indicators</div>", unsafe_allow_html=True)
        show_ma       = st.toggle("Moving Averages", value=True)
        show_bb       = st.toggle("Bollinger Bands", value=True)
        show_rsi      = st.toggle("RSI (14)", value=True)
        show_vwap     = st.toggle("VWAP", value=False)
        show_raw      = st.toggle("Show Raw Data", value=False)

    st.markdown("---")
    run = st.button("▶  Run Pipeline", use_container_width=True)

    st.markdown("""
    <div style='margin-top:2rem; padding:0.75rem; background:rgba(99,102,241,0.08);
                border:1px solid rgba(99,102,241,0.15); border-radius:10px; font-size:0.72rem; color:#475569;'>
        <div style='color:#6366f1; font-weight:600; margin-bottom:4px;'>ℹ API Info</div>
        Keys are securely stored server-side. No input required.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN AREA HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='page-header'>
    <div style='display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;'>
        <div>
            <h1 class='page-title'>{'🌤  Weather Intelligence' if is_weather else '📈  Market Analytics'}</h1>
            <p class='page-subtitle'>
                {'Real-time meteorological data · OpenWeatherMap API · 5-day forecast' if is_weather
                 else 'Live financial data · Alpha Vantage API · OHLCV + Indicators'}
            </p>
        </div>
        <div style='display:flex; gap:8px; flex-wrap:wrap;'>
            <span class='badge green'>● Live</span>
            <span class='badge'>ETL Pipeline</span>
            <span class='badge orange'>Cached</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if not run:
    st.markdown(f"""
    <div class='empty-state'>
        <div style='font-size:5rem;'>{'🌍' if is_weather else '💹'}</div>
        <h2>{'Configure a city and run the pipeline' if is_weather else 'Configure a symbol and run the pipeline'}</h2>
        <p>{'Enter a city name in the sidebar and click Run Pipeline to fetch live weather data.' if is_weather
            else 'Enter a stock symbol like AAPL, TSLA or NVDA and click Run Pipeline.'}</p>
        <div style='display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-top:1.5rem;'>
            <span class='badge'>Extract → API</span>
            <span class='badge'>Transform → pandas</span>
            <span class='badge'>Load → CSV cache</span>
            <span class='badge'>Visualize → Plotly</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
# ██████████  WEATHER DASHBOARD  ██████████
# ─────────────────────────────────────────────────────────────
if is_weather:
    if not city.strip():
        st.error("Please enter a city name in the sidebar.")
        st.stop()

    pipe_placeholder = st.empty()
    pipe_placeholder.markdown(pipeline_bar(0), unsafe_allow_html=True)

    try:
        with st.spinner("Fetching weather data…"):
            client = WeatherClient(OPENWEATHER_API_KEY)
            etl    = WeatherETL(client)
            pipe_placeholder.markdown(pipeline_bar(1), unsafe_allow_html=True)
            result = etl.run(city.strip(), units)
            df_cur = result["current"]
            df_fc  = result["forecast"]
            pipe_placeholder.markdown(pipeline_bar(2), unsafe_allow_html=True)
            etl.load(df_fc, f".cache/{city.strip().lower()}_forecast.csv")
            pipe_placeholder.empty()

    except ValueError as e:
        pipe_placeholder.empty()
        st.error(f"❌ City not found: **{city}** — check spelling and try again.")
        st.stop()
    except Exception as e:
        pipe_placeholder.empty()
        st.error(f"❌ API error: {e}")
        st.stop()

    row      = df_cur.iloc[0]
    analysis = WeatherAnalysis()
    df_daily = analysis.daily_summary(df_fc)
    trend    = analysis.trend(df_fc)
    icon     = weather_icon(row["weather_main"])

    # ── Hero card ──────────────────────────────────────────────
    st.markdown(f"""
    <div class='glass-card' style='background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(6,182,212,0.05));
                border-color:rgba(99,102,241,0.2);'>
        <div style='display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;'>
            <div style='display:flex; align-items:center; gap:1rem;'>
                <div style='font-size:4rem; line-height:1;'>{icon}</div>
                <div>
                    <div style='font-size:1.8rem; font-weight:700; color:#e2e8f0;'>
                        {row['city']}, {row['country']}
                    </div>
                    <div class='weather-condition'>{row['weather_desc']}</div>
                    <div style='font-size:0.78rem; color:#475569; margin-top:4px;'>
                        Updated {row['timestamp'].strftime('%H:%M UTC')} ·
                        <span class='{"trend-up" if "Ris" in trend else "trend-down" if "Fall" in trend else "trend-flat"}'>
                            {trend}
                        </span>
                    </div>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-family:"JetBrains Mono",monospace; font-size:3.5rem; font-weight:700;
                            background:linear-gradient(135deg,#e2e8f0,#6366f1);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1;'>
                    {format_temp(row['temp'], units)}
                </div>
                <div style='color:#64748b; font-size:0.85rem; margin-top:4px;'>
                    Feels like {format_temp(row['feels_like'], units)}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric pills ───────────────────────────────────────────
    st.markdown(f"""
    <div class='metric-grid'>
        {pill(f"{row['humidity']}%",   "Humidity",    "blue",   "Relative")}
        {pill(f"{row['wind_speed']} m/s", "Wind Speed","cyan",  f"{row.get('wind_deg','—')}°")}
        {pill(f"{row['pressure']} hPa","Pressure",    "purple", "Sea level")}
        {pill(f"{row['clouds']}%",     "Cloud Cover", "purple", "Overcast")}
        {pill(f"{row['temp_max']:.1f}° / {row['temp_min']:.1f}°", "High / Low", "green", "Today")}
        {pill(f"{int(row['visibility']/1000) if row['visibility'] else '—'} km", "Visibility", "orange", "")}
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🌡  Temperature", "💧  Humidity & Wind", "📅  Daily Summary", "🌦  Precipitation"])

    with tab1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df_fc["timestamp"], y=df_fc["temp_max"], name="Max",
            line=dict(color=COLORS["rose"], width=2),
            fill=None,
        ))
        fig.add_trace(go.Scatter(
            x=df_fc["timestamp"], y=df_fc["temp_min"], name="Min",
            line=dict(color=COLORS["cyan"], width=2),
            fill="tonexty", fillcolor="rgba(6,182,212,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=df_fc["timestamp"], y=df_fc["temp"], name="Avg",
            line=dict(color=COLORS["indigo"], width=2.5, dash="dot"),
        ))
        fig.add_trace(go.Bar(
            x=df_fc["timestamp"], y=df_fc["pop"]*100, name="Rain %",
            marker_color=COLORS["violet"], opacity=0.35,
        ), secondary_y=True)
        layout = base_layout("Temperature Forecast — Next 5 Days", 420)
        layout["yaxis"]["title"]  = f"Temperature ({unit_label.split()[0]})"
        layout["yaxis2"] = dict(title="Rain Prob %", gridcolor=COLORS["grid"],
                                tickfont=dict(color=COLORS["muted"]))
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(
            x=df_fc["timestamp"], y=df_fc["humidity"], name="Humidity %",
            marker=dict(color=COLORS["indigo"], opacity=0.7,
                        line=dict(color=COLORS["violet"], width=0.5)),
        ))
        fig2.add_trace(go.Scatter(
            x=df_fc["timestamp"], y=df_fc["wind_speed"], name="Wind m/s",
            line=dict(color=COLORS["amber"], width=2.5),
            mode="lines+markers", marker=dict(size=5, color=COLORS["amber"]),
        ), secondary_y=True)
        layout2 = base_layout("Humidity & Wind Speed", 380)
        layout2["yaxis"]["title"] = "Humidity (%)"
        layout2["yaxis2"] = dict(title="Wind (m/s)", gridcolor=COLORS["grid"],
                                 tickfont=dict(color=COLORS["muted"]))
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        df_show = df_daily.copy()
        df_show["date"] = df_show["date"].astype(str)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Max Temp", x=df_show["date"], y=df_show["temp_max"],
                              marker_color=COLORS["rose"], opacity=0.8))
        fig3.add_trace(go.Bar(name="Min Temp", x=df_show["date"], y=df_show["temp_min"],
                              marker_color=COLORS["cyan"], opacity=0.8))
        fig3.add_trace(go.Scatter(name="Avg Temp", x=df_show["date"], y=df_show["temp_avg"],
                                  line=dict(color=COLORS["indigo"], width=2.5),
                                  mode="lines+markers", marker=dict(size=8)))
        layout3 = base_layout("Daily Temperature Summary", 360)
        layout3["barmode"] = "group"
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

        # Summary table
        st.markdown("<div class='section-label'>Daily Breakdown</div>", unsafe_allow_html=True)
        st.dataframe(
            df_show.rename(columns={
                "date":"Date","temp_min":"Min °","temp_max":"Max °",
                "temp_avg":"Avg °","humidity_avg":"Humidity","wind_avg":"Wind m/s",
                "rain_prob_max":"Rain Prob","temp_range":"Range",
            }).style.format({
                "Min °":"{:.1f}","Max °":"{:.1f}","Avg °":"{:.1f}",
                "Humidity":"{:.0f}%","Wind m/s":"{:.1f}","Rain Prob":"{:.0%}","Range":"{:.1f}",
            }).background_gradient(subset=["Max °"], cmap="RdYlBu_r"),
            use_container_width=True, hide_index=True,
        )

    with tab4:
        fig4 = go.Figure()
        df_rain = df_fc[df_fc["pop"] > 0].copy()
        fig4.add_trace(go.Bar(
            x=df_fc["timestamp"], y=df_fc["pop"]*100, name="Precipitation Probability",
            marker=dict(
                color=df_fc["pop"]*100,
                colorscale=[[0,"rgba(6,182,212,0.2)"],[0.5,"rgba(99,102,241,0.6)"],[1,"rgba(139,92,246,0.9)"]],
                showscale=True,
                colorbar=dict(title="Prob %", tickfont=dict(color=COLORS["muted"])),
            ),
        ))
        fig4.add_trace(go.Scatter(
            x=df_fc["timestamp"], y=df_fc["clouds"], name="Cloud Cover %",
            line=dict(color=COLORS["amber"], width=2, dash="dot"),
        ))
        layout4 = base_layout("Precipitation Probability & Cloud Cover", 380)
        fig4.update_layout(**layout4)
        st.plotly_chart(fig4, use_container_width=True)

    # Comfort index
    if show_comfort:
        comfort = analysis.comfort_index(df_fc)
        comfort_counts = comfort.value_counts()
        st.markdown("<div class='section-label'>Comfort Index Distribution</div>", unsafe_allow_html=True)
        fig_c = go.Figure(go.Pie(
            labels=comfort_counts.index.astype(str),
            values=comfort_counts.values,
            hole=0.55,
            marker=dict(colors=[COLORS["cyan"],COLORS["emerald"],COLORS["indigo"],COLORS["amber"],COLORS["rose"]]),
        ))
        fig_c.update_layout(**base_layout("Comfort Index — Forecast Period", 300))
        st.plotly_chart(fig_c, use_container_width=True)

    if show_raw:
        with st.expander("📋 Raw Forecast Data"):
            st.dataframe(df_fc, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# ██████████  FINANCE DASHBOARD  ██████████
# ─────────────────────────────────────────────────────────────
else:
    if not symbol:
        st.error("Please enter a stock symbol in the sidebar.")
        st.stop()

    pipe_placeholder = st.empty()
    pipe_placeholder.markdown(pipeline_bar(0), unsafe_allow_html=True)

    try:
        with st.spinner(f"Fetching {symbol} data…"):
            client   = FinanceClient(ALPHAVANTAGE_API_KEY)
            etl      = FinanceETL(client)
            pipe_placeholder.markdown(pipeline_bar(1), unsafe_allow_html=True)
            result   = etl.run(symbol, interval, ts_mode.lower())
            df       = result["series"]
            df_quote = result["quote"]
            pipe_placeholder.markdown(pipeline_bar(2), unsafe_allow_html=True)
            df       = FinanceAnalysis.filter_date_range(df, str(start_date), str(end_date))
            if df.empty:
                pipe_placeholder.empty()
                st.error(f"No data for **{symbol}** in selected date range. Try extending the range.")
                st.stop()
            rsi_s  = FinanceAnalysis.rsi(df)
            bb     = FinanceAnalysis.bollinger_bands(df)
            vwap_s = FinanceAnalysis.vwap(df)
            stats  = FinanceAnalysis.summary_stats(df)
            etl.load(df, f".cache/{symbol}_series.csv")
            pipe_placeholder.empty()

    except ValueError as e:
        pipe_placeholder.empty()
        st.error(f"❌ Invalid symbol: **{symbol}** — check and try again.")
        st.stop()
    except RuntimeError as e:
        pipe_placeholder.empty()
        st.warning(f"⚠️ Rate limit: {e}")
        st.stop()
    except Exception as e:
        pipe_placeholder.empty()
        st.error(f"❌ API error: {e}")
        st.stop()

    q       = df_quote.iloc[0]
    chg     = float(q["change"])
    chg_pct = float(q["change_pct"])
    is_up   = chg >= 0

    # ── Quote hero ─────────────────────────────────────────────
    arrow = "▲" if is_up else "▼"
    chg_color = "#10b981" if is_up else "#ef4444"
    st.markdown(f"""
    <div class='glass-card' style='background:linear-gradient(135deg,
        {"rgba(16,185,129,0.06)" if is_up else "rgba(239,68,68,0.06)"},
        rgba(99,102,241,0.05));
        border-color:{"rgba(16,185,129,0.25)" if is_up else "rgba(239,68,68,0.25)"};'>
        <div style='display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;'>
            <div>
                <div style='font-size:2rem; font-weight:700; color:#e2e8f0;'>{symbol}</div>
                <div style='color:#64748b; font-size:0.85rem;'>Latest trading day: {q['latest_day']}</div>
            </div>
            <div style='text-align:right;'>
                <div style='font-family:"JetBrains Mono",monospace; font-size:3rem; font-weight:700;
                            color:#e2e8f0; line-height:1;'>${q['price']:.2f}</div>
                <div style='color:{chg_color}; font-size:1rem; font-weight:600; margin-top:4px;'>
                    {arrow} ${abs(chg):.2f} ({abs(chg_pct):.2f}%)
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats pills ────────────────────────────────────────────
    ret_cls = "up" if stats.get("total_return_pct",0) >= 0 else "down"
    st.markdown(f"""
    <div class='metric-grid'>
        {pill(f"${q['high']:.2f}",      "Day High",      "green")}
        {pill(f"${q['low']:.2f}",       "Day Low",       "orange")}
        {pill(f"${stats.get('period_high',0):.2f}", "Period High", "blue")}
        {pill(f"${stats.get('period_low',0):.2f}",  "Period Low",  "purple")}
        {pill(f"{stats.get('total_return_pct',0):.2f}%", "Total Return", "cyan")}
        {pill(f"{int(q['volume']):,}",  "Volume",        "purple")}
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🕯  Candlestick", "📊  RSI & Momentum", "📉  Returns", "📐  Volume Analysis"])

    with tab1:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72, 0.28], vertical_spacing=0.04)
        fig.add_trace(go.Candlestick(
            x=df["timestamp"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name="OHLC",
            increasing=dict(line=dict(color=COLORS["emerald"], width=1.5), fillcolor="rgba(16,185,129,0.6)"),
            decreasing=dict(line=dict(color=COLORS["rose"],    width=1.5), fillcolor="rgba(239,68,68,0.6)"),
        ), row=1, col=1)

        if show_ma and df["ma_5"].notna().any():
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["ma_5"], name="MA 5",
                line=dict(color=COLORS["amber"], width=1.5, dash="dot")), row=1, col=1)
        if show_ma and df["ma_20"].notna().any():
            fig.add_trace(go.Scatter(x=df["timestamp"], y=df["ma_20"], name="MA 20",
                line=dict(color=COLORS["cyan"], width=1.5)), row=1, col=1)
        if show_bb and not bb.empty:
            fig.add_trace(go.Scatter(x=df["timestamp"], y=bb["bb_upper"], name="BB Upper",
                line=dict(color="#475569", width=1), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["timestamp"], y=bb["bb_lower"], name="BB Lower",
                line=dict(color="#475569", width=1),
                fill="tonexty", fillcolor="rgba(71,85,105,0.12)"), row=1, col=1)
        if show_vwap:
            fig.add_trace(go.Scatter(x=df["timestamp"], y=vwap_s, name="VWAP",
                line=dict(color=COLORS["violet"], width=1.5, dash="dashdot")), row=1, col=1)

        bar_colors = [COLORS["emerald"] if c >= 0 else COLORS["rose"]
                      for c in df["price_change"].fillna(0)]
        fig.add_trace(go.Bar(x=df["timestamp"], y=df["volume"], name="Volume",
                             marker_color=bar_colors, opacity=0.65), row=2, col=1)

        layout = base_layout(f"{symbol} — Price Chart", 500)
        layout["xaxis_rangeslider_visible"] = False
        layout["yaxis"]  = dict(title="Price (USD)", gridcolor=COLORS["grid"],
                                tickfont=dict(color=COLORS["muted"]))
        layout["yaxis2"] = dict(title="Volume",      gridcolor=COLORS["grid"],
                                tickfont=dict(color=COLORS["muted"]))
        layout["xaxis2"] = dict(gridcolor=COLORS["grid"], tickfont=dict(color=COLORS["muted"]))
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if show_rsi:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df["timestamp"], y=rsi_s, name="RSI",
                line=dict(color=COLORS["indigo"], width=2.5),
                fill="tozeroy", fillcolor="rgba(99,102,241,0.06)",
            ))
            fig_rsi.add_hline(y=70, line_color=COLORS["rose"],    line_dash="dash",
                               annotation_text="Overbought 70", annotation_font_color=COLORS["rose"])
            fig_rsi.add_hline(y=30, line_color=COLORS["emerald"], line_dash="dash",
                               annotation_text="Oversold 30",   annotation_font_color=COLORS["emerald"])
            fig_rsi.add_hrect(y0=30, y1=70, fillcolor="rgba(99,102,241,0.04)", line_width=0)
            layout_rsi = base_layout(f"{symbol} — RSI (14)", 350)
            layout_rsi["yaxis"] = dict(range=[0,100], gridcolor=COLORS["grid"],
                                       tickfont=dict(color=COLORS["muted"]))
            fig_rsi.update_layout(**layout_rsi)
            st.plotly_chart(fig_rsi, use_container_width=True)

            # RSI interpretation
            last_rsi = rsi_s.iloc[-1] if not rsi_s.empty else 50
            if last_rsi > 70:
                st.warning(f"⚠️ RSI {last_rsi:.1f} — **Overbought** territory. Potential pullback signal.")
            elif last_rsi < 30:
                st.success(f"✅ RSI {last_rsi:.1f} — **Oversold** territory. Potential bounce signal.")
            else:
                st.info(f"ℹ️ RSI {last_rsi:.1f} — **Neutral** zone (30–70).")

    with tab3:
        pct = df["pct_change"].dropna()
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Histogram(
            x=pct, name="Returns", nbinsx=40,
            marker=dict(
                color=pct,
                colorscale=[[0, COLORS["rose"]], [0.5, COLORS["indigo"]], [1, COLORS["emerald"]]],
                showscale=False,
            ),
            opacity=0.85,
        ))
        fig_ret.add_vline(x=0, line_color=COLORS["muted"], line_dash="dash")
        fig_ret.add_vline(x=pct.mean(), line_color=COLORS["amber"], line_dash="dot",
                          annotation_text=f"Mean {pct.mean():.2f}%",
                          annotation_font_color=COLORS["amber"])
        layout_ret = base_layout(f"{symbol} — Return Distribution", 360)
        layout_ret["xaxis"]["title"] = "Daily Return (%)"
        layout_ret["yaxis"]["title"] = "Frequency"
        layout_ret["bargap"] = 0.04
        fig_ret.update_layout(**layout_ret)
        st.plotly_chart(fig_ret, use_container_width=True)

        # Stats summary
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean Return", f"{pct.mean():.3f}%")
        c2.metric("Std Dev",     f"{pct.std():.3f}%")
        c3.metric("Max Gain",    f"{pct.max():.2f}%")
        c4.metric("Max Loss",    f"{pct.min():.2f}%")

    with tab4:
        fig_vol = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                row_heights=[0.5, 0.5], vertical_spacing=0.06)
        colors = [COLORS["emerald"] if c >= 0 else COLORS["rose"]
                  for c in df["price_change"].fillna(0)]
        fig_vol.add_trace(go.Bar(x=df["timestamp"], y=df["volume"], name="Volume",
                                  marker_color=colors, opacity=0.75), row=1, col=1)
        vol_ma = df["volume"].rolling(10).mean()
        fig_vol.add_trace(go.Scatter(x=df["timestamp"], y=vol_ma, name="Vol MA 10",
                                      line=dict(color=COLORS["amber"], width=2)), row=1, col=1)
        fig_vol.add_trace(go.Scatter(x=df["timestamp"], y=df["volatility"], name="Volatility",
                                      line=dict(color=COLORS["violet"], width=2),
                                      fill="tozeroy", fillcolor="rgba(139,92,246,0.08)"), row=2, col=1)
        layout_vol = base_layout(f"{symbol} — Volume & Volatility", 420)
        layout_vol["yaxis"]  = dict(title="Volume",     gridcolor=COLORS["grid"],
                                    tickfont=dict(color=COLORS["muted"]))
        layout_vol["yaxis2"] = dict(title="Volatility", gridcolor=COLORS["grid"],
                                    tickfont=dict(color=COLORS["muted"]))
        layout_vol["xaxis2"] = dict(gridcolor=COLORS["grid"], tickfont=dict(color=COLORS["muted"]))
        fig_vol.update_layout(**layout_vol)
        st.plotly_chart(fig_vol, use_container_width=True)

    if show_raw:
        with st.expander("📋 Raw Data"):
            st.dataframe(
                df[["timestamp","open","high","low","close","volume","pct_change","ma_5","ma_20"]],
                use_container_width=True,
            )
