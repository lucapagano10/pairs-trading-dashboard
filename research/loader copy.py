
from binance.client import Client
from binance.client import AsyncClient
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os
import asyncio


path = os.path.dirname(__file__)


class Loader():

    def __init__(self) -> None:
        self.client = Client()
        # _client = await AsyncClient.create()
        self.symbols = self.__get_symbols()

        self.hist_df = pd.DataFrame
        self.request_weight = 0
        
        # self.hist_df = pd.DataFrame(index=['Time'],  columns=pd.MultiIndex.from_product(
        #     [self.symbols, ['Open', 'High', 'Low', 'Close']]))

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

        :param interval: e.g. '1 year ago', '10days ago', 'datetime'
        :type: str
        """
        self.timeframe = timeframe
        self.interval = interval
        self.end_date = end_date

        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        
        # frames = loop.run_until_complete(self.__get_multi_data())
        
        frames = asyncio.run(self.__get_multi_data())
        
        self.hist_df = self.__set_level_indexing(frames)
        
        self.hist_df.to_csv(os.path.join(
            path, '..', 'data/raw/historical_data.csv'), index=True) if save else None
        return self.hist_df
    
    async def __get_multi_data(self) -> None:
        # return  [ await self.__get_single_data(s) for s in self.symbols]
        return await asyncio.wait([self.__get_single_data(s) for s in self.symbols])


    async def __get_single_data(self, symbol) -> None:
        
        # self.request_weight =  self.request_weight + 1
        # print('weight:', self.request_weight)
        
        # if self.request_weight >= 1150:
        #     asyncio.sleep(60)
        #     self.request_weight =  0
        # await asyncio.sleep(10)
          
        __client = await AsyncClient.create()
        
        try:
            print(symbol)
            frame = pd.DataFrame(await __client.get_historical_klines(
                symbol, self.timeframe, self.interval, self.end_date, limit=5000))
            
            frame = frame.iloc[:, :5]
            frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
            frame = frame.set_index('Time')
            frame.index = pd.to_datetime(frame.index, unit='ms')
            frame = frame.astype(float)
            await __client.session.close()
            
            
        except Exception as e:
            print('error:', e)
            await __client.session.close()
            print(symbol, 'Limit Reached, waiting 60 seconds...')
            await asyncio.sleep(60)
            frame = await self.__get_single_data(symbol)
             
        return frame


    # async def __get_multi_data(self) -> None:
    #     return await asyncio.gather(*[self.__get_single_data(s) for s in self.symbols])


    # async def __get_single_data(self, symbol) -> None:
        
    #     # self.request_weight =  self.request_weight + 1
    #     # print('weight:', self.request_weight)
        
    #     # if self.request_weight >= 1150:
    #     #     asyncio.sleep(60)
    #     #     self.request_weight =  0
            
    #     __client = await AsyncClient.create()
        
    #     try:
    #         print(symbol)
    #         frame = pd.DataFrame(await __client.get_historical_klines(
    #             symbol, self.timeframe, self.interval, self.end_date, limit=5000))
            
    #         frame = frame.iloc[:, :5]
    #         frame.columns = ['Time', 'Open', 'High', 'Low', 'Close']
    #         frame = frame.set_index('Time')
    #         frame.index = pd.to_datetime(frame.index, unit='ms')
    #         frame = frame.astype(float)
    #         await __client.session.close()
    #         # asyncio.sleep(0.5)
            
    #     except Exception as e:
    #         await __client.session.close()
    #         print(symbol, 'Limit Reached, waiting 60 seconds...')
    #         await asyncio.sleep(60)
    #         frame = await self.__get_single_data(symbol)
             
    #     return frame

    def __set_level_indexing(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.concat(dict(zip(self.symbols,df)), axis=1)
