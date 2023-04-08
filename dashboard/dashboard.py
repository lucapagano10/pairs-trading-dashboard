import streamlit as st
import altair as alt
import pandas as pd
import os
import datetime

from research import Researcher
from backtester import Backtester

# import hydralit_components as hc
import time


path = os.path.dirname(__file__)


class Dashboard():
    def __init__(self):
        self.researcher = Researcher()
        self.backtester = Backtester()

        self.hist_df = pd.DataFrame()
        self.cleared_df = pd.DataFrame()
        self.corr_df = pd.DataFrame()
        self.coint_df = pd.DataFrame()
        self.researched_df = pd.DataFrame()
        self.backtested_df = pd.DataFrame()

    def load_data(self) -> None:
        self.researcher.load_data()
        self.backtester.read_data(self.researcher)
        self.backtester.run_backtest()

        self.hist_df = self.backtester.hist_df
        self.cleared_df = self.backtester.cleared_df
        self.corr_df = self.backtester.corr_df
        self.coint_df = self.backtester.coint_df
        self.researched_df = self.backtester.researched_df
        self.backtested_df = self.backtester.backtested_df

    def __update_data(self, timeframe: str, min_correlation: float, interval: str, end_date: str = None) -> None:
        """
        :param timeframe: e.g. '1d', '4h', '3S', '15m' 
        :type: str

        :param interval: e.g. '1 year ago', '10days ago', 'datetime'
        :type: str

        :param min_correlation: e.g. '0.83' is 83%
        :type: float
        """
        self.researcher.update_data(timeframe, min_correlation, interval, end_date)
        self.backtester.read_data(self.researcher)
        self.backtester.run_backtest()

        self.hist_df = self.backtester.hist_df
        self.cleared_df = self.backtester.cleared_df
        self.corr_df = self.backtester.corr_df
        self.coint_df = self.backtester.coint_df
        self.researched_df = self.backtester.researched_df
        self.backtested_df = self.backtester.backtested_df
        print(self.backtested_df)
        self.__write_columns()

    def run(self) -> None:
        self.__set_page_config(layout="wide")
        self._define_initial_style()
        self.__write_columns()

    def __set_page_config(self, layout: str = "wide") -> None:
        st.set_page_config(layout=layout)

    def _define_initial_style(self) -> None:
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

            with st.form('Update Data'):
                st.markdown('<h1>Update Data</h1><small>(take few minutes to complete)</small>', unsafe_allow_html=True)
                # with side_col1:
                timeframe = st.selectbox(
                    'Timeframe:',
                    ['5m', '15m', '1h', '4h', '1d', '1S', '1M'],
                    4
                )
                
                side_col1, side_col2 = st.columns(2)
                
                with side_col1:
                    start_date = st.date_input(
                        'Start Date:',
                        datetime.date(2022,4,8)
                        
                    )
                
                with side_col2:
                    end_date = st.date_input(
                        'End Date:',
                        datetime.date(2023,4,7)
                    )

                # with side_col3:
                min_correlation = st.number_input(
                    'Minimun Correlation:',
                    min_value=0.0,
                    max_value=1.0,
                    value=0.83
                )
                
                st.form_submit_button('Update Data', on_click=self.__update_data, args=(timeframe, min_correlation, f'{start_date}' , f'{end_date}'))
        
        st.markdown('', unsafe_allow_html=True)

        up_col1, up_col2 = st.columns([2, 3])
        down_col1, down_col2 = st.columns([5, 2])

        with down_col1:
            st.markdown('<h5>Trades over period</h5>', unsafe_allow_html=True)

            fig = self.backtester.plot_backtest(
                currency1, currency2, ratio, saveonly=True)
            fig.set_figwidth(16)
            st.pyplot(fig,
                      #  use_container_width=True
                      use_container_width=True
                      )

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
                f'<small>Return of Investment: {results["Roi"].values[0]} %</small>', unsafe_allow_html=True)
            st.markdown(
                f'<small>Sharpe Ratio: {results["Sharperatio"].values[0]} </small>', unsafe_allow_html=True)
            st.markdown(
                f'<small>Drawdown: {results["Drawdown"].values[0]} </small>', unsafe_allow_html=True)

        with up_col1:
            st.markdown('<h5>Cointegration between currencies</h5>',
                        unsafe_allow_html=True)

            scatter = alt.Chart(self.cleared_df).mark_point().encode(
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

        with up_col2:

            st.markdown('<h5>Daily Close Price</h5>', unsafe_allow_html=True)

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
