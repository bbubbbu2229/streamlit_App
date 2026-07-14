import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Global Top10 Market Cap Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Global Market Cap Top 10 Stock Dashboard")
st.markdown("최근 1년간 글로벌 시가총액 Top10 기업 주가 비교")

# 현재 글로벌 시가총액 Top10 대표 기업
stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B"
}

# Sidebar
st.sidebar.header("옵션")

period = st.sidebar.selectbox(
    "조회 기간",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

selected = st.sidebar.multiselect(
    "종목 선택",
    list(stocks.keys()),
    default=list(stocks.keys())
)

normalize = st.sidebar.checkbox(
    "시작일 기준 100으로 정규화",
    value=True
)

if len(selected) == 0:
    st.warning("한 개 이상의 종목을 선택하세요.")
    st.stop()

# 데이터 다운로드
price_df = pd.DataFrame()

with st.spinner("데이터 다운로드 중..."):

    for company in selected:
        ticker = stocks[company]

        try:
            data = yf.download(
                ticker,
                period=period,
                progress=False,
                auto_adjust=True
            )

            if len(data) > 0:
                price_df[company] = data["Close"]

        except Exception:
            pass

price_df.dropna(inplace=True)

if normalize:
    plot_df = price_df / price_df.iloc[0] * 100
    ylabel = "Normalized Price (Start = 100)"
else:
    plot_df = price_df
    ylabel = "Price (USD)"

# Plotly
fig = px.line(
    plot_df,
    x=plot_df.index,
    y=plot_df.columns,
    labels={
        "value": ylabel,
        "index": "Date",
        "variable": "Company"
    },
    template="plotly_dark"
)

fig.update_layout(
    height=700,
    hovermode="x unified",
    title="Global Market Cap Top10 Stock Performance"
)

st.plotly_chart(fig, use_container_width=True)

# 현재 수익률 계산
returns = ((price_df.iloc[-1] / price_df.iloc[0]) - 1) * 100

summary = pd.DataFrame({
    "Company": returns.index,
    "Return (%)": returns.values.round(2),
    "Latest Price": price_df.iloc[-1].values.round(2)
})

summary = summary.sort_values(
    by="Return (%)",
    ascending=False
)

st.subheader("📊 Performance Summary")

st.dataframe(
    summary,
    use_container_width=True
)

# 개별 차트

st.subheader("기업별 상세 차트")

company = st.selectbox(
    "기업 선택",
    selected
)

fig2 = px.line(
    price_df,
    x=price_df.index,
    y=company,
    template="plotly_white",
    title=f"{company} Stock Price"
)

fig2.update_layout(height=500)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.caption(
    f"Last Updated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
