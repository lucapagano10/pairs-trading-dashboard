
from binance.client import Client
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os
import datetime as dt

path = os.path.dirname(__file__)


class Loader():

    def __init__(self) -> None:
        self.client = Client()
        self.symbols = self.__get_symbols()

        self.hist_df = pd.DataFrame
        self.request_weight = 0


        self.timeframe = str
        self.interval = str
        self.end_date = str

    def __get_symbols(self,) -> list:
        info = self.client.get_exchange_info()
        unused_coins = ['UPUSDT', 'DOWNUSDT', 'BEAR',
                        'BULL', 'USDC', 'PAX', 'TUSD', 'BUSD', 'USDP']
        return [s['symbol'] for s in info['symbols'] if s['symbol'].endswith('USDT') and
                s['status'] == 'TRADING' and
                all(coin not in s['symbol'] for coin in unused_coins)]

    def get_historical_data(self, timeframe: str, interval: str, end_date: str = None, save: bool = True) -> pd.DataFrame:
        """
        :param timeframe: e.g. '15m', '4h', '1d', '3w', '1M'
        :type: str

        :param interval: e.g. '1 year ago', '10days ago', '2022-01-01'
        :type: str
        """
        self.timeframe = timeframe
        self.interval = interval
        self.end_date = end_date

        self.hist_df = self.__get_multi_data()

        self.hist_df.to_csv(os.path.join(
            path, '..', 'data/raw/historical_data.csv'), index=True) if save else None
        
        return self.hist_df

    def __get_multi_data(self) -> None:

        frames = pd.DataFrame()
        with ThreadPoolExecutor(max_workers=13) as executor:
            for frame in executor.map(self.__get_single_data, self.symbols):
                frames = pd.concat([frames, frame], axis=1)
                
        return frames

    def __get_single_data(self, symbol) -> None:

        frame = pd.DataFrame(self.client.get_historical_klines(
            symbol, self.timeframe, self.interval, self.end_date, limit=1000))
        
        frame = frame.iloc[:, :5]
        frame = frame.set_index(frame.columns[0])
        frame.index.name = 'Time'
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame.columns = pd.MultiIndex.from_product([[symbol], ['Open', 'High', 'Low', 'Close']])
        frame = frame.astype(float)
        return frame

    def filter_data(self, timeframe:str, interval: str) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(path, '..', f'data/raw/{timeframe}_3years.csv'), index_col=0, header=[0, 1])
        df.set_index(pd.to_datetime(df.index), inplace=True)
        df = df[(df.index > pd.to_datetime(interval))]
        return df

        # return self.hist_df