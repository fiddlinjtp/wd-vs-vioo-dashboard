import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="WD vs VIOO & 10Y Treasury")

TICKER_WD = "WD"
TICKER_BENCHMARK = "VIOO"  # Vanguard S&P Small-Cap 600 ETF
TICKER_10Y = "^TNX"        # 10-Year Treasury Yield Index
START_DATE = "2025-08-25"

st.title("📈 Walker & Dunlop (WD) vs. S&P 600 (VIOO) & 10-Year Treasury")
st.caption("Benchmarked from August 25, 2025 • Auto-refreshes with live market data")

@st.cache_data(ttl=300)
def load_data():
    tickers = [TICKER_WD, TICKER_BENCHMARK, TICKER_10Y]
    df = yf.download(tickers, start=START_DATE, interval="1d")["Close"]
    df = df.dropna()
    return df

data = load_data()

# Handle Yahoo Finance yield quoting format (^TNX can be quoted directly as 4.25 or 42.50)
if data[TICKER_10Y].iloc[-1] > 15:
    data["TNX_Yield"] = data[TICKER_10Y] / 10.0
else:
    data["TNX_Yield"] = data[TICKER_10Y]

# August 25, 2025 base values
base_wd = data[TICKER_WD].iloc[0]
base_vioo = data[TICKER_BENCHMARK].iloc[0]
base_tnx = data["TNX_Yield"].iloc[0]

# Latest values
latest_wd = data[TICKER_WD].iloc[-1]
latest_vioo = data[TICKER_BENCHMARK].iloc[-1]
latest_tnx = data["TNX_Yield"].iloc[-1]

# Calculate equity % return since Aug 25, 2025
pct_wd = ((latest_wd - base_wd) / base_wd) * 100
pct_vioo = ((latest_vioo - base_vioo) / base_vioo) * 100

data["WD_%"] = ((data[TICKER_WD] - base_wd) / base_wd) * 100
data["VIOO_%"] = ((data[TICKER_BENCHMARK] - base_vioo) / base_vioo) * 100

# Calculate Treasury basis point (bps) move (1% = 100 bps)
delta_bps = (latest_tnx - base_tnx) * 100

# Layout: Chart (Left 75%), Statistics (Right 25%)
col_chart, col_stats = st.columns([3, 1])

with col_chart:
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Left Axis: WD % Return
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["WD_%"],
            mode="lines",
            name="Walker & Dunlop (WD)",
            line=dict(color="#1E88E5", width=2.5)
        ),
        secondary_y=False
    )
    
    # Left Axis: VIOO % Return
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["VIOO_%"],
            mode="lines",
            name="Vanguard S&P 600 (VIOO)",
            line=dict(color="#FB8C00", width=2)
        ),
        secondary_y=False
    )
    
    # Right Axis: 10-Year Treasury Yield (%)
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["TNX_Yield"],
            mode="lines",
            name="10-Yr Treasury Yield (%)",
            line=dict(color="#6A1B9A", width=2, dash="dash")
        ),
        secondary_y=True
    )
    
    # 0% Return Baseline on Primary Axis
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, secondary_y=False)

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Date",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="% Return (from Aug 25, 2025)", secondary_y=False)
    fig.update_yaxes(title_text="10-Year Treasury Yield (%)", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("Performance Summary")
    st.caption("Since August 25, 2025")
    
    st.metric(
        label="Walker & Dunlop (WD)",
        value=f"${latest_wd:.2f}",
        delta=f"{pct_wd:+.2f}%"
    )
    st.caption(f"Base: ${base_wd:.2f}")
    
    st.divider()
    
    st.metric(
        label="S&P 600 ETF (VIOO)",
        value=f"${latest_vioo:.2f}",
        delta=f"{pct_vioo:+.2f}%"
    )
    st.caption(f"Base: ${base_vioo:.2f}")

    st.divider()
    
    # Equity Spread
    spread = pct_wd - pct_vioo
    st.metric(
        label="WD vs VIOO Spread",
        value=f"{spread:+.2f}%",
        delta="Outperforming" if spread > 0 else "Underperforming"
    )

    st.divider()

    # 10-Year Treasury Card
    st.metric(
        label="10-Year Treasury Yield",
        value=f"{latest_tnx:.2f}%",
        delta=f"{delta_bps:+.1f} bps"
    )
    st.caption(f"Base: {base_tnx:.2f}%")
