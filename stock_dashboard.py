import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Top NSE Stocks Dashboard", layout="wide")

# Title
st.title("Top 15 NSE Stocks Analysis Dashboard")

# Get NSE Index Data
@st.cache_data(ttl=3600)
def get_nse_data():
    nse = yf.download('^NSEI', period='2d', interval='1d')
    return nse

nse_data = get_nse_data()
today_close = float(nse_data['Close'].iloc[-1])
prev_close = float(nse_data['Close'].iloc[-2])
change = today_close - prev_close
change_percent = (change / prev_close) * 100

# Add NSE Index Cards at the top
st.markdown("### NSE Index Overview")
col_nse1, col_nse2 = st.columns(2)

with col_nse1:
    st.metric(
        "NSE Index (Previous Day)",
        f"₹{prev_close:,.2f}",
        delta=None
    )

with col_nse2:
    st.metric(
        "NSE Index (Today)",
        f"₹{today_close:,.2f}",
        delta=f"{change:,.2f} ({change_percent:.2f}%)"
    )

st.markdown("---")

# List of top 15 NSE stocks (adding .NS suffix for NSE stocks)
top_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'HDFC.NS',
    'KOTAKBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS'
]

# Sidebar
st.sidebar.header("Dashboard Settings")
selected_stock = st.sidebar.selectbox("Select Stock", top_stocks)
time_period = st.sidebar.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
)

# Function to get stock data
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_stock_data(symbol, period):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)
    return hist, stock.info

# Get data for selected stock
df, stock_info = get_stock_data(selected_stock, time_period)

# Main content
col1, col2 = st.columns(2)

# Stock Price Chart
with col1:
    st.subheader(f"Stock Price: {selected_stock}")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# Volume Chart
with col2:
    st.subheader("Trading Volume")
    fig_volume = px.bar(df, x=df.index, y='Volume')
    fig_volume.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        height=500
    )
    st.plotly_chart(fig_volume, use_container_width=True)

# Key Metrics
st.subheader("Key Metrics")
col3, col4, col5, col6 = st.columns(4)

with col3:
    st.metric("Current Price", f"₹{df['Close'].iloc[-1]:.2f}")
with col4:
    st.metric("Day Change", f"₹{(df['Close'].iloc[-1] - df['Open'].iloc[-1]):.2f}")
with col5:
    st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
with col6:
    price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    st.metric("Period Return", f"{price_change:.2f}%")

# Moving Averages
st.subheader("Technical Analysis")
ma_periods = [20, 50, 200]
for period in ma_periods:
    df[f'MA{period}'] = df['Close'].rolling(window=period).mean()

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
for period in ma_periods:
    fig_ma.add_trace(go.Scatter(x=df.index, y=df[f'MA{period}'], name=f'{period}-day MA'))

fig_ma.update_layout(
    title=f"Moving Averages ({', '.join(str(p) for p in ma_periods)} days)",
    xaxis_title="Date",
    yaxis_title="Price (INR)",
    height=500
)
st.plotly_chart(fig_ma, use_container_width=True)

# Comparison with NIFTY 50
st.subheader("Comparison with NIFTY 50")
nifty_data = yf.download('^NSEI', period=time_period)
normalized_stock = df['Close'] / df['Close'].iloc[0] * 100
normalized_nifty = nifty_data['Close'] / nifty_data['Close'].iloc[0] * 100

fig_comp = go.Figure()
fig_comp.add_trace(go.Scatter(x=df.index, y=normalized_stock, name=selected_stock))
fig_comp.add_trace(go.Scatter(x=nifty_data.index, y=normalized_nifty, name='NIFTY 50'))
fig_comp.update_layout(
    title="Normalized Price Comparison (Base=100)",
    xaxis_title="Date",
    yaxis_title="Normalized Price",
    height=500
)
st.plotly_chart(fig_comp, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data source: Yahoo Finance | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 