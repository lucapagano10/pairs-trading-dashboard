import streamlit as st
import altair as alt
import os
import datetime

from research import Researcher
from backtester import Backtester

# import hydralit_components as hc


path = os.path.dirname(__file__)


class Dashboard(Backtester, Researcher):

    def __init__(self):
        super().__init__()

    def run(self) -> None:
        self.load_data()
        self.__set_page_config(layout="wide")
        self.__define_initial_style()
        self.__write_columns()

    def load_data(self) -> None:

        if 'hist_df' in st.session_state:

            self.hist_df = st.session_state['hist_df']
            self.cleared_df = st.session_state['cleared_df']
            self.corr_df = st.session_state['corr_df']
            self.coint_df = st.session_state['coint_df']
            self.researched_df = st.session_state['researched_df']
            self.backtested_df = st.session_state['backtested_df']
            self.backtested_fig = st.session_state['backtested_fig']

        else:
            self.__update_dashboard( '1d', 0.83, '2022-4-7' )
            # self.load_backtested_data()

    def __set_page_config(self, layout: str = "wide") -> None:
        st.set_page_config(layout=layout)

    def __define_initial_style(self) -> None:
        st.markdown("""
                    <style>
                        .block-container{
                            padding-top: 3em;
                            padding-bottom: 0rem;
                        }

                        [data-testid="stSidebar"] > div > div {
                            padding-top: 0rem;
                            padding-bottom: 0rem;
                        }

                        h5 {
                            padding-top: 0rem;
                            padding-bottom: 0.2rem;
                        }

                        h1, h2 {
                            padding-top: 0rem;
                            padding-bottom: 0.0rem;
                        }

                        p {
                            margin-bottom: 0px;
                        }

                        button p {
                            margin-bottom: 16px;
                        }

                        # canvas {
                        #     height: 35vh !important;
                        # }
                    </style>
                    """,
                    unsafe_allow_html=True)

    def __write_columns(self) -> None:
        # for 1 (index=5) from the standard loader group
        # with hc.HyLoader('Now loading',hc.Loaders.standard_loaders,index=5):
        #     time.sleep(2)

        with st.sidebar:
            st.markdown(
                '<h1 style="font-size:35px;">Pairs Trading</h1>', unsafe_allow_html=True)
            st.markdown("""<small style="text-align: justify; text-size: 0.000001rem">
                        <i>A strategy consisting in first identify 2 currencies that are
                        highly correlated and cointegrated and backtest them. After that,
                        if the price are too deviated (outside Bollinger Bands), we buy the undervalued
                        currency while short-sell the overvalued currency and exit
                        positions when prices returns to neutrality (middle Band). This strategy
                        can also be referred as market neutral or statistical arbitrage.</i>
                        <br></br>
                        </small><small>
                        The neutrality simplied formula is:

                        A - B * (A / B) = 0

So:</small>

                        Currency1 - Currency2 * Ratio

</small>
                        """, unsafe_allow_html=True)

        with st.sidebar:
            with st.form('Update Data'):
                st.markdown(
                    '<h1>Update Data</h1><small>(may take sometime)</small>', unsafe_allow_html=True)

                side_col1, side_col2 = st.columns(2)

                with side_col1:
                    timeframe = st.selectbox(
                        'Timeframe:',
                        ['4h', '1d', '1w'],
                        1
                    )

                with side_col2:
                    interval = st.date_input(
                        'Begin: (max 3 years)',
                        datetime.date(2022, 4, 7),
                        min_value=datetime.date(2020, 4, 7)
                    )

                min_correlation = st.number_input(
                    'Minimum Correlation Rate (%):',
                    min_value=0,
                    max_value=100,
                    value=83
                )
                
                form_button = st.form_submit_button('Update Data')

                if form_button:
                    self.__update_dashboard(
                        timeframe, round(float(min_correlation/100),2), interval)
        try:
            with st.sidebar:
                st.markdown('<h1>Pair Selection</h1>', unsafe_allow_html=True)
                pairs = st.selectbox(
                    'Select the pair for analysis:',
                    [f'{row["Currency1"]}/{row["Currency2"]}' for __,
                        row in self.researched_df.iterrows()]
                )

                currency1 = pairs.split('/')[0]
                currency2 = pairs.split('/')[1]
                ratio = self.researched_df.loc[(self.researched_df['Currency1'] == currency1) & (
                    self.researched_df['Currency2'] == currency2), 'Ratio'].values[0]

                r = [row for __, row in self.researched_df.iterrows() if row['Currency1'] ==
                     currency1 and row['Currency2'] == currency2][0]

                st.markdown(
                    f'<small style="text-align: left; margin-bottom:10px;">Correlation Rate: {"{:.2f}".format(r["Correlation"] * 100)}%</small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small style="text-align: left">Is Cointegrated: {"Yes" if r["Cointegration"] < r["Criticals"] else "No"}</small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small style="text-align: left">Ratio: {round(ratio, 6)}</small>', unsafe_allow_html=True)

            up_col1, up_col2 = st.columns([2, 3])
            down_col1, down_col2 = st.columns([5, 2])

            with down_col1:
                st.markdown('<h5>Trades over period</h5>',
                            unsafe_allow_html=True)

                fig = self.plot_backtest(
                    currency1, currency2, ratio, saveonly=True)
                
                fig.set_figwidth(16)
                
                st.pyplot(fig,
                          use_container_width=True
                          )

                st.session_state['backtested_df'] = self.backtested_df
                st.session_state['backtested_fig'] = self.backtested_fig

            with down_col2:

                results = self.backtested_df.loc[(self.backtested_df['Currency1'] == currency1) & (
                    self.backtested_df['Currency2'] == currency2)]
                # results = pd.read_csv(os.path.join(
                #     path, f"data/backtested/{currency1}-{currency2}.csv"))
                st.markdown('<h5>Results</h5>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Total of Trades: {results["N_trades"].values[0]} </small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Won Trades: {results["Won"].values[0]} </small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Win Rate: {results["Win_rate"].values[0]} %</small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Total Compound Return: {results["Roi"].values[0]} %</small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Sharpe Ratio: {results["Sharperatio"].values[0]} </small>', unsafe_allow_html=True)
                st.markdown(
                    f'<small>Max Drawdown: {results["Drawdown"].values[0]} </small>', unsafe_allow_html=True)

            with up_col1:
                st.markdown('<h5>Cointegration between currencies</h5>',
                            unsafe_allow_html=True)

                scatter = alt.Chart(self.cleared_df).mark_point().encode(
                    alt.X(f"{currency1}:Q", title=f"log( {currency1} )"), 
                    alt.Y(f"{currency2}:Q", title=f"log( {currency2} )")
                    # x=currency1,
                    # y=currency2
                ).properties(
                    # height=250
                )

                regression = scatter.transform_regression(
                    currency1, currency2).mark_line(color='green').interactive()

                st.altair_chart(scatter + regression, use_container_width=True)

            with up_col2:

                st.markdown('<h5>Daily Close Price</h5>',
                            unsafe_allow_html=True)

                cleared_df = self.cleared_df.reset_index()

                prices_graph = alt.Chart(cleared_df).mark_line().transform_fold(
                    fold=[currency1, currency2],
                    as_=['Currency', 'Price']
                ).encode(
                    x='Time:T',
                    y='Price:Q',
                    color='Currency:N'
                ).interactive()

                st.altair_chart(prices_graph,
                                use_container_width=True)
        except Exception as e: 
            st.warning('No data to show. Please update data.')
    
    def __update_dashboard(_self, timeframe: str, min_correlation: float, interval: str) -> None:
        _self.filter_research_data(timeframe=timeframe, min_correlation=min_correlation,
                                   interval=interval)
        
        if len(_self.researched_df):

            st.session_state['hist_df'] = _self.hist_df
            st.session_state['cleared_df'] = _self.cleared_df
            st.session_state['corr_df'] = _self.corr_df
            st.session_state['coint_df'] = _self.coint_df
            st.session_state['researched_df'] = _self.researched_df

        else:
            st.warning("No pairs trading found. Please adjust the parameters.")