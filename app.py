import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="WD vs VIOO Tracker")

TICKER_WD = "WD"
TICKER_BENCHMARK = "VIOO"  # Vanguard S&P Small-Cap 600 ETF
START_DATE = "2025-08-25"  # Pinned base date

st.title("📈 Walker & Dunlop (WD) vs. S&P Small-Cap 600 (VIOO)")
st.caption(f"Benchmarked from August 25, 2025 • Auto-refreshes with live market prices")

@st.cache_data(ttl=300)  # Re-fetches fresh market data every 5 minutes
def load_data():
    df = yf.download([TICKER_WD, TICKER_BENCHMARK], start=START_DATE, interval="1d")["Close"]
    df = df.dropna()
    return df

data = load_data()

# Base prices anchored on August 25, 2025 (first row of dataset)
base_wd = data[TICKER_WD].iloc[0]
base_vioo = data[TICKER_BENCHMARK].iloc[0]

latest_wd = data[TICKER_WD].iloc[-1]
latest_vioo = data[TICKER_BENCHMARK].iloc[-1]

# Calculate % change since August 25, 2025
pct_wd = ((latest_wd - base_wd) / base_wd) * 100
pct_vioo = ((latest_vioo - base_vioo) / base_vioo) * 100

data["WD_%"] = ((data[TICKER_WD] - base_wd) / base_wd) * 100
data["VIOO_%"] = ((data[TICKER_BENCHMARK] - base_vioo) / base_vioo) * 100

# Layout: 75% width for Line Chart, 25% for Side Statistics Cards
col_chart, col_stats = st.columns([3, 1])

with col_chart:
    fig = go.Figure()
    
    # Walker & Dunlop Line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["WD_%"],
        mode="lines",
        name="Walker & Dunlop (WD)",
        line=dict(color="#2962FF", width=2.5)
    ))
    
    # VIOO S&P 600 ETF Line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["VIOO_%"],
        mode="lines",
        name="Vanguard S&P 600 (VIOO)",
        line=dict(color="#FF6D00", width=2)
    ))
    
    # Zero baseline reference
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.6)

    fig.update_layout(
        template="plotly_white",
        yaxis_title="% Cumulative Return (from Aug 25, 2025)",
        xaxis_title="Date",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("Performance")
    st.caption("Since August 25, 2025")
    
    st.metric(
        label="Walker & Dunlop (WD)",
        value=f"${latest_wd:.2f}",
        delta=f"{pct_wd:+.2f}%"
    )
    st.caption(f"Aug 25, 2025 Base: ${base_wd:.2f}")
    
    st.divider()
    
    st.metric(
        label="S&P 600 ETF (VIOO)",
        value=f"${latest_vioo:.2f}",
        delta=f"{pct_vioo:+.2f}%"
    )
    st.caption(f"Aug 25, 2025 Base: ${base_vioo:.2f}")

    st.divider()
    
    spread = pct_wd - pct_vioo
    st.metric(
        label="Relative Spread (WD vs VIOO)",
        value=f"{spread:+.2f}%",
        delta="Outperforming Index" if spread > 0 else "Underperforming Index"
    )