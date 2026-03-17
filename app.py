"""
app.py – Main Streamlit dashboard for ETL Pipeline & Live Graph Dashboard.
Run: streamlit run app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from api_client import WeatherClient, FinanceClient
from etl import WeatherETL, FinanceETL
from analysis import WeatherAnalysis, FinanceAnalysis
from dashboard import WeatherPlots, FinancePlots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ETL Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f172a;
    color: #f1f5f9;
}
.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #38bdf8;
}
.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
}
.badge {
    display: inline-block;
    background: #0ea5e920;
    border: 1px solid #0ea5e940;
    color: #38bdf8;
    border-radius: 99px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    # API Keys
    with st.expander("🔑 API Keys", expanded=True):
        weather_key = st.text_input(
            "OpenWeatherMap Key",
            type="password",
            placeholder="e.g. abc123def456...",
            help="Free key from openweathermap.org",
        )
        finance_key = st.text_input(
            "Alpha Vantage Key",
            type="password",
            placeholder="e.g. DEMO or your key",
            help="Free key from alphavantage.co",
        )

    st.markdown("---")
    dataset = st.radio("📂 Dataset", ["🌤 Weather", "📈 Finance"], index=0)
    st.markdown("---")

    if "Weather" in dataset:
        st.markdown("### 🌤 Weather Settings")
        city = st.text_input("City", value="London", placeholder="e.g. Tokyo, Paris, New York")
        units = st.selectbox("Units", ["metric (°C)", "imperial (°F)", "standard (K)"])
        units_code = units.split(" ")[0]

    else:
        st.markdown("### 📈 Finance Settings")
        symbol = st.text_input("Stock Symbol", value="AAPL", placeholder="e.g. AAPL, TSLA, MSFT").upper()
        mode = st.selectbox("Time Series", ["Daily", "Intraday"])
        if mode == "Intraday":
            interval = st.selectbox("Interval", ["1min", "5min", "15min", "30min", "60min"])
        else:
            interval = "5min"
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=date.today() - timedelta(days=90))
        with col2:
            end_date = st.date_input("To", value=date.today())

    st.markdown("---")
    run_btn = st.button("▶ Run Pipeline", use_container_width=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
  <span style='font-size:2rem;'>📊</span>
  <div>
    <h1 style='margin:0; font-size:1.8rem; font-weight:700;'>ETL Dashboard</h1>
    <p style='margin:0; color:#94a3b8; font-size:0.9rem;'>
      Real-time data pipeline · Extract → Transform → Load · Live visualizations
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Helpers ───────────────────────────────────────────────────────────────────
def show_error(msg: str):
    st.error(f"❌ {msg}")

def show_pipeline_stages(stage: str):
    cols = st.columns(3)
    stages = ["Extract", "Transform", "Load"]
    for i, (col, s) in enumerate(zip(cols, stages)):
        active = stages.index(stage) >= i
        color = "#38bdf8" if active else "#334155"
        col.markdown(
            f"<div style='text-align:center; color:{color}; font-size:0.8rem; "
            f"font-family:monospace; border:1px solid {color}; border-radius:6px; padding:4px;'>"
            f"{'✓ ' if active else ''}{s}</div>",
            unsafe_allow_html=True,
        )

# ── Main logic ────────────────────────────────────────────────────────────────
if not run_btn:
    st.markdown("""
    <div style='text-align:center; padding:4rem 2rem; color:#475569;'>
        <div style='font-size:4rem;'>🚀</div>
        <h3 style='color:#64748b;'>Configure your parameters and click Run Pipeline</h3>
        <p>Enter API keys, select a dataset, and set your parameters in the sidebar.</p>
        <br/>
        <div style='display:flex; gap:16px; justify-content:center; flex-wrap:wrap;'>
            <div class='badge'>OpenWeatherMap</div>
            <div class='badge'>Alpha Vantage</div>
            <div class='badge'>pandas ETL</div>
            <div class='badge'>Plotly Charts</div>
            <div class='badge'>Local Cache</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── WEATHER ───────────────────────────────────────────────────────────────
    if "Weather" in dataset:
        if not weather_key:
            show_error("Please enter your OpenWeatherMap API key.")
            st.stop()

        with st.spinner("⚡ Running ETL pipeline…"):
            try:
                # --- Extract ---
                progress = st.empty()
                progress.info("🔄 **Extract** – Fetching data from OpenWeatherMap…")
                client = WeatherClient(weather_key)
                etl = WeatherETL(client)
                show_pipeline_stages("Extract")

                # --- Transform ---
                progress.info("🔄 **Transform** – Cleaning & structuring with pandas…")
                result = etl.run(city.strip(), units_code)
                df_cur = result["current"]
                df_fc = result["forecast"]
                show_pipeline_stages("Transform")

                # --- Analyse ---
                analysis = WeatherAnalysis()
                df_daily = analysis.daily_summary(df_fc)
                trend = analysis.trend(df_fc)

                # --- Load ---
                progress.info("🔄 **Load** – Saving to local CSV…")
                etl.load(df_fc, f".cache/{city}_forecast.csv")
                show_pipeline_stages("Load")
                progress.success(f"✅ Pipeline complete — {len(df_fc)} records loaded for **{city}**")

            except ValueError as e:
                show_error(str(e))
                st.stop()
            except Exception as e:
                show_error(f"API or network error: {e}")
                st.stop()

        # ── Current conditions ────────────────────────────────────────────────
        row = df_cur.iloc[0]
        st.markdown(f"### 🌍 {row['city']}, {row['country']} — Current Conditions")
        st.caption(f"Last updated: {row['timestamp']} UTC  |  Trend: **{trend}**")

        c1, c2, c3, c4, c5 = st.columns(5)
        for col, label, val in [
            (c1, "Temperature", f"{row['temp']:.1f}°"),
            (c2, "Feels Like", f"{row['feels_like']:.1f}°"),
            (c3, "Humidity", f"{row['humidity']}%"),
            (c4, "Wind", f"{row['wind_speed']} m/s"),
            (c5, "Conditions", row["weather_main"]),
        ]:
            col.markdown(
                f"<div class='metric-card'>"
                f"<div class='metric-value'>{val}</div>"
                f"<div class='metric-label'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gauges ────────────────────────────────────────────────────────────
        fig_gauges = WeatherPlots.current_gauges(df_cur)
        st.plotly_chart(fig_gauges, use_container_width=True)

        # ── Charts ────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(["🌡 Temperature Forecast", "💧 Humidity & Wind", "📅 Daily Summary", "📋 Raw Data"])

        with tab1:
            st.plotly_chart(WeatherPlots.forecast_temperature(df_fc, city), use_container_width=True)

        with tab2:
            st.plotly_chart(WeatherPlots.humidity_wind(df_fc, city), use_container_width=True)

        with tab3:
            st.dataframe(
                df_daily.style.format({
                    "temp_min": "{:.1f}°", "temp_max": "{:.1f}°", "temp_avg": "{:.1f}°",
                    "humidity_avg": "{:.0f}%", "wind_avg": "{:.1f} m/s", "rain_prob_max": "{:.0%}",
                }),
                use_container_width=True,
            )

        with tab4:
            st.dataframe(df_fc, use_container_width=True)

    # ── FINANCE ───────────────────────────────────────────────────────────────
    else:
        if not finance_key:
            show_error("Please enter your Alpha Vantage API key.")
            st.stop()

        with st.spinner("⚡ Running ETL pipeline…"):
            try:
                progress = st.empty()
                progress.info("🔄 **Extract** – Fetching data from Alpha Vantage…")
                client = FinanceClient(finance_key)
                etl = FinanceETL(client)
                show_pipeline_stages("Extract")

                progress.info("🔄 **Transform** – Cleaning & computing indicators…")
                result = etl.run(symbol, interval, mode.lower())
                df = result["series"]
                df_quote = result["quote"]
                show_pipeline_stages("Transform")

                # Date filter
                df = FinanceAnalysis.filter_date_range(df, str(start_date), str(end_date))
                if df.empty:
                    show_error(f"No data for {symbol} in selected date range.")
                    st.stop()

                # Indicators
                rsi = FinanceAnalysis.rsi(df)
                bb = FinanceAnalysis.bollinger_bands(df)
                stats = FinanceAnalysis.summary_stats(df)

                progress.info("🔄 **Load** – Saving to local CSV…")
                etl.load(df, f".cache/{symbol}_series.csv")
                show_pipeline_stages("Load")
                progress.success(f"✅ Pipeline complete — {len(df)} records loaded for **{symbol}**")

            except ValueError as e:
                show_error(str(e))
                st.stop()
            except RuntimeError as e:
                show_error(str(e))
                st.stop()
            except Exception as e:
                show_error(f"API or network error: {e}")
                st.stop()

        # ── Quote header ──────────────────────────────────────────────────────
        q = df_quote.iloc[0]
        direction = "▲" if float(q["change"]) >= 0 else "▼"
        color = "#34d399" if float(q["change"]) >= 0 else "#f87171"

        st.markdown(f"### 📈 {symbol} — Live Quote")
        st.caption(f"Latest trading day: {q['latest_day']}")

        c1, c2, c3, c4, c5 = st.columns(5)
        for col, label, val in [
            (c1, "Price", f"${q['price']:.2f}"),
            (c2, "Change", f"{direction} ${abs(float(q['change'])):.2f}"),
            (c3, "Day High", f"${q['high']:.2f}"),
            (c4, "Day Low", f"${q['low']:.2f}"),
            (c5, "Volume", f"{int(q['volume']):,}"),
        ]:
            col.markdown(
                f"<div class='metric-card'>"
                f"<div class='metric-value' style='color:{'#f87171' if label=='Change' and float(q['change']) < 0 else '#34d399' if label=='Change' else '#38bdf8'}'>{val}</div>"
                f"<div class='metric-label'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Stats bar ─────────────────────────────────────────────────────────
        if stats:
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Period High", f"${stats['period_high']:.2f}")
            s2.metric("Period Low", f"${stats['period_low']:.2f}")
            s3.metric("Total Return", f"{stats['total_return_pct']:.2f}%")
            s4.metric("Volatility", f"{stats['volatility_std']:.2f}")

        # ── Charts ────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(["🕯 Candlestick", "📊 RSI", "📉 Returns", "📋 Raw Data"])

        with tab1:
            st.plotly_chart(FinancePlots.candlestick(df, symbol, bb), use_container_width=True)

        with tab2:
            st.plotly_chart(FinancePlots.rsi_plot(df, rsi, symbol), use_container_width=True)

        with tab3:
            st.plotly_chart(FinancePlots.returns_histogram(df, symbol), use_container_width=True)

        with tab4:
            st.dataframe(df[["timestamp", "open", "high", "low", "close", "volume",
                              "pct_change", "ma_5", "ma_20"]].tail(100),
                         use_container_width=True)
