# DataPulse — Dynamic ETL Pipeline & Live Dashboard

> Real-time Weather & Financial Intelligence · Built with Python, Streamlit & Plotly

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![pandas](https://img.shields.io/badge/pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=flat-square)](https://farhanharoon116-etl-dashboard.streamlit.app)

---

## Overview

DataPulse is a production-grade data engineering application that implements a full **Extract → Transform → Load (ETL)** pipeline with live interactive dashboards. It pulls real-time data from two industry-standard APIs — OpenWeatherMap and Alpha Vantage — and presents them through two completely distinct, purpose-built dashboards with glassmorphism aesthetics and Plotly-powered visualizations.

The app is designed with a clean modular architecture, server-side API key management, local response caching, and comprehensive error handling — making it suitable as both a university project deliverable and a real-world portfolio piece.

---

## Live Demo

🔗 **[datapulse.streamlit.app](https://etl-dashboard-new.streamlit.app)**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Dashboard UI | Streamlit |
| Visualizations | Plotly |
| Data Processing | pandas, NumPy |
| Weather API | OpenWeatherMap |
| Finance API | Alpha Vantage |
| Caching | Local JSON file cache |
| Deployment | Streamlit Community Cloud |
| Version Control | Git & GitHub |

---

## Features

### ETL Pipeline
- Live pipeline progress indicator — Extract → Transform → Load stages visible in the UI
- Local JSON caching with configurable TTL (10 min weather, 5 min finance) to avoid redundant API calls
- All data exported to CSV on each pipeline run
- Full error handling for invalid cities, invalid symbols, API failures, and rate limits

### Weather Dashboard
- Current conditions hero card — temperature, feels like, weather icon
- 5-day / 3-hour forecast with temperature bands (min/max/avg)
- Precipitation probability with color-scaled bar chart
- Humidity & Wind speed dual-axis chart
- Daily summary table with formatted metrics
- Comfort index distribution (pie chart)
- Toggleable display options in sidebar

### Finance Dashboard
- Live quote card that turns green or red based on price direction
- Candlestick chart with OHLCV data
- Toggleable overlays: Moving Averages (MA5, MA20), Bollinger Bands, VWAP
- RSI (14) chart with overbought/oversold zones and automatic interpretation text
- Return distribution histogram with mean and standard deviation
- Volume & Volatility dual-panel chart
- Period stats: high, low, total return, volatility

---

## Project Structure

```
etl_dashboard/
├── app.py                      # Streamlit entry point & full UI
├── config.py                   # Local API key config (gitignored)
├── requirements.txt
│
├── api_client/
│   ├── weather_client.py       # OpenWeatherMap wrapper + JSON caching
│   └── finance_client.py       # Alpha Vantage wrapper + JSON caching
│
├── etl/
│   ├── weather_etl.py          # Extract / Transform / Load — weather
│   └── finance_etl.py          # Extract / Transform / Load — finance
│
├── analysis/
│   ├── weather_analysis.py     # Daily summary, comfort index, trend
│   └── finance_analysis.py     # RSI, Bollinger Bands, VWAP, stats
│
└── dashboard/
    ├── weather_plots.py        # Plotly weather charts
    └── finance_plots.py        # Plotly finance charts
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Farhanharoon116/etl-dashboard.git
cd etl-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Create a `config.py` file in the root directory:

```python
OPENWEATHER_API_KEY  = "your_openweathermap_key"
ALPHAVANTAGE_API_KEY = "your_alphavantage_key"

WEATHER_CACHE_TTL = 600
FINANCE_CACHE_TTL = 300
```

Get free keys here:
- OpenWeatherMap → https://openweathermap.org/api
- Alpha Vantage → https://www.alphavantage.co/support/#api-key

### 5. Run the app

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Deployment (Streamlit Cloud)

1. Push code to GitHub (ensure `config.py` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file to `app.py`
4. Under **Settings → Secrets**, add:

```toml
OPENWEATHER_API_KEY  = "your_key"
ALPHAVANTAGE_API_KEY = "your_key"
```

5. Click **Deploy** — live in ~60 seconds

---

## API Key Security

API keys are **never hardcoded or committed to GitHub**. The app reads keys from:
- `st.secrets` when running on Streamlit Cloud (encrypted, server-side)
- `config.py` when running locally (gitignored, stays on your machine)

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Invalid city name | Friendly error, pipeline stops cleanly |
| Invalid stock symbol | Alpha Vantage error surfaced to user |
| Missing API key | Warning shown before any request is made |
| Network / API failure | Exception caught, error displayed |
| Rate limit hit | Specific rate-limit message shown |
| Empty date range | Clear message with suggestion to extend range |

---

## Usage

1. Select **Weather** or **Finance** mode from the sidebar
2. Enter a city name (e.g. `London`) or stock symbol (e.g. `AAPL`)
3. Configure parameters — units, date range, interval, indicators
4. Click **▶ Run Pipeline** and watch the ETL stages execute live
5. Explore the chart tabs and toggle indicators on/off

---

## Author

**Farhan Haroon**
BS Artificial Intelligence · Muhammad Ali Jinnah University, Karachi
[github.com/Farhanharoon116](https://github.com/Farhanharoon116)
