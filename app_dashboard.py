import streamlit as st
import altair as alt
import pandas as pd
import os


abs_path = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(abs_path, "data/processing/cleaner_output.csv"))
df2 = pd.read_csv(os.path.join(abs_path, "data/analyzed/final_output.csv"))


st.set_page_config(layout="wide")
up_col1, up_col2, up_col3 = st.columns(3)
down_col1, down_col2 = st.columns([2, 5])

st.markdown("""
            <style>
.appview-container .main .block-container{
        padding-top: 3rem;
        padding-bottom: 0rem;}
        
p {
  margin-bottom: 0px;
}

canvas {
    height: 35vh !important;
}
</style>
""", unsafe_allow_html=True)

with down_col1:

    st.markdown('<h5>Best Pairs to Trade</h5>', unsafe_allow_html=True)
    pairs = st.selectbox(
        'Select the pair for analysis:',
        [f'{row["Currency1"]}/{row["Currency2"]}' for __, row in df2.iterrows()]
    )

    currency1 = pairs.split('/')[0]
    currency2 = pairs.split('/')[1]

with down_col1:
    r = [row for __, row in df2.iterrows() if row['Currency1'] ==
         currency1 and row['Currency2'] == currency2][0]
    st.markdown('<h5>Details</h5>', unsafe_allow_html=True)
    st.markdown(
        f'<small style="text-align: left; margin-bottom:10px;">Correlation: {"{:.2f}".format(r["Correlation"] * 100)}%</small>', unsafe_allow_html=True)
    st.markdown(
        f'<small style="text-align: left">Is Cointegrated: {"Yes" if r["Cointegration"] < r["Criticals"] else "No"}</small>', unsafe_allow_html=True)
    st.markdown(
        f'<small style="text-align: left">Start date: {df.at[0,"Time"]}</small>', unsafe_allow_html=True)
    st.markdown(
        f'<small style="text-align: left">End date: {df.at[df.index[-1],"Time"]}</small>', unsafe_allow_html=True)
    st.markdown(
        f'<small style="text-align: left">Timeframe: {"1d"}</small>', unsafe_allow_html=True)


with down_col2:
    st.markdown('<h5>Daily Close Price</h5>', unsafe_allow_html=True)

    prices_graph = alt.Chart(df).mark_line().transform_fold(
        fold=[currency1, currency2],
        as_=['Currency', 'Price']
    ).encode(
        x=alt.X('Time'),
        y='Price:Q',
        color='Currency:N'
    ).interactive()

    # label2 = graph_currency2.mark_text().encode(text=currency2)

    st.altair_chart(prices_graph,
                    use_container_width=True)

with up_col1:
    st.markdown('<h1>Pairs Trading</h1>', unsafe_allow_html=True)
    st.markdown("""<small style="text-align: justify">
                Is a trading strategy that seeks 
                to identify 2 currencies that are 
                highly correlated and cointegrated.
                The trading opportunity occurs when 
                prices relationship are too deviated 
                from each other. That way, it should 
                buy the undervalued currency while 
                short-selling the overvalued currency 
                and exit positions when prices returns 
                to neutrality. This strategy can also 
                be referred as market neutral 
                or statistical arbitrage. 
                </small>""", unsafe_allow_html=True)


with up_col2:
    st.markdown('<h5>Relationship between currencies</h5>',
                unsafe_allow_html=True)

    scatter = alt.Chart(df).mark_point().encode(
        x=currency1,
        y=currency2
    ).properties(
        # height=250
        )

    regression = scatter.transform_regression(
        currency1, currency2).mark_line(color='green').interactive()

    # scatter = alt.Chart(df).mark_point().encode(
    #     x=currency1,
    #     y=currency2
    # )

    st.altair_chart(scatter + regression, use_container_width=True)



with up_col3:
    results = pd.read_csv(os.path.join(abs_path, f"data/backtested/{currency1}-{currency2}.csv"))
    st.markdown('<h5>Results</h5>', unsafe_allow_html=True)
    st.markdown(f'<small>Total of Trades: {results["n_trades"].values[0]} </small>', unsafe_allow_html=True)
    st.markdown(f'<small>Won Trades: {results["won"].values[0]} </small>', unsafe_allow_html=True)
    st.markdown(f'<small>Hit Rate: {results["hit_rate"].values[0]}%</small>', unsafe_allow_html=True)
    st.markdown(f'<small>Total Return: {results["return"].values[0]} </small>', unsafe_allow_html=True)
    st.markdown(f'<small>Sharpe Ratio: {results["sharperatio"].values[0]} </small>', unsafe_allow_html=True)
    st.markdown(f'<small>Drawdown: {results["drawdown"].values[0]} </small>', unsafe_allow_html=True)
