
from binance.client import Client
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os

path = os.path.dirname(__file__)

class Loader():

    def __init__(self) -> None:
        
        self.timeframe = str
        self.interval = str
        self.end_date = str
        
        
    def load_data(self, timeframe:str, interval: str) -> pd.DataFrame:
        
        df = pd.read_csv(os.path.join(path, '..', f'data/raw/{timeframe}_3years.csv'), index_col=0, header=[0, 1])
        df.set_index(pd.to_datetime(df.index), inplace=True)
        
        return self.__filter_data(df, interval)
        
        
    def __filter_data(self, df:pd.DataFrame, interval: str) -> pd.DataFrame:
         
        return df[(df.index > pd.to_datetime(interval))]