# 📊 ETL Dashboard — Dynamic Pipeline & Live Graph Dashboard

A modular ETL pipeline with a Streamlit dashboard for real-time weather and financial data.

---

## Features

- **Full ETL pipeline** — Extract → Transform → Load with stage feedback
- **Weather data** — Current conditions, 5-day forecast, temperature bands, humidity/wind
- **Finance data** — OHLCV candlestick, RSI, Bollinger Bands, VWAP, return distribution
- **User-controlled parameters** — city, stock symbol, date range, interval, units
- **Local caching** — avoids redundant API calls (600s TTL for weather, 300s for finance)
- **Error handling** — invalid city, invalid symbol, API failures, rate limits
- **Modular structure** — clean separation across `api_client/`, `etl/`, `analysis/`, `dashboard/`

---

## Project Structure

```
etl_dashboard/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── api_client/
│   ├── __init__.py
│   ├── weather_client.py     # OpenWeatherMap wrapper + caching
│   └── finance_client.py     # Alpha Vantage wrapper + caching
├── etl/
│   ├── __init__.py
│   ├── weather_etl.py        # Extract / Transform / Load for weather
│   └── finance_etl.py        # Extract / Transform / Load for finance
├── analysis/
│   ├── __init__.py
│   ├── weather_analysis.py   # Daily summary, comfort index, trend
│   └── finance_analysis.py   # RSI, Bollinger Bands, VWAP, stats
└── dashboard/
    ├── __init__.py
    ├── weather_plots.py      # Plotly weather charts
    └── finance_plots.py      # Plotly finance charts
```

---

## Setup

### 1. Clone / extract the project

```bash
cd etl_dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API keys (both are free)

| Service | URL | Free tier |
|---|---|---|
| OpenWeatherMap | https://openweathermap.org/api | 60 calls/min |
| Alpha Vantage | https://www.alphavantage.co/support/#api-key | 25 calls/day |

### 5. Run the dashboard

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Usage

1. **Enter API keys** in the sidebar (stored in session only, never persisted)
2. **Select dataset** — Weather or Finance
3. **Set parameters**:
   - Weather: city name, units (metric/imperial/standard)
   - Finance: symbol (e.g. AAPL), mode (Daily/Intraday), date range, interval
4. **Click ▶ Run Pipeline** — watch the ETL stages execute in real time
5. **Explore tabs** — charts auto-populate, raw data available in last tab

---

## Caching

API responses are cached in `.cache/` as JSON files with timestamps.

- Weather: 10-minute TTL
- Finance: 5-minute TTL

To clear the cache:

```bash
rm -rf .cache/
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Invalid city name | Friendly error message, pipeline stops |
| Invalid stock symbol | Error from Alpha Vantage surfaced to user |
| API key missing | Prompt shown before any request is made |
| Network failure | Exception caught, error displayed |
| Rate limit hit (Alpha Vantage) | Specific rate-limit message shown |
| Empty date range result | Error message explaining no data found |

---

## Extending

- Add new data sources by creating a new client in `api_client/` and ETL class in `etl/`
- Add new charts by extending `dashboard/weather_plots.py` or `finance_plots.py`
- Add new analytics in `analysis/`
- The Streamlit app in `app.py` can be updated to add new tabs/sections with minimal changes

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Interactive dashboard UI |
| `pandas` | Data cleaning and transformation |
| `plotly` | Interactive charts |
| `requests` | HTTP API calls |
| `numpy` | Numerical operations for indicators |
