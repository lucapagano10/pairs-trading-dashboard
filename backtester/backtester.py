from sklearn.preprocessing import MinMaxScaler
import matplotlib
import pandas as pd
import backtrader as bt 
import os

from research import Researcher

path = os.path.dirname(__file__)

class Backtester(): 
    
    def __init__(self) -> None:
        self.hist_df = pd.DataFrame()
        self.cleared_df = pd.DataFrame()
        self.corr_df = pd.DataFrame()
        self.coint_df = pd.DataFrame()
        self.researched_df = pd.DataFrame()
        self.backtested_df = pd.DataFrame()
        self.backtested_fig = matplotlib

    def plot_backtest(self, currency1:str, currency2:str, ratio:float, saveonly:bool=False) -> matplotlib:
        return self.__single_backtest(currency1, currency2, ratio)
              
    def __single_backtest(self, currency1, currency2, ratio) -> None:
        cerebro = bt.Cerebro()
        
        df = self.__transform_data(currency1, currency2, ratio)
        feed = bt.feeds.PandasData(dataname=df, name=f'{currency1}-{currency2}*{round(ratio,6)}')
        
        cerebro.adddata(feed)
        cerebro.addstrategy(Bbands)
        
        cerebro.broker.setcommission(commission=0.0008)
        cerebro.broker.set_cash(cash=1000)
        
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade')
        
        cerebro.addsizer(bt.sizers.FixedSize,stake=1000)
        
        output = cerebro.run()
        
        self.backtested_df =  self.__get_returns(currency1, currency2, ratio, output)
        # returns_df = self.__get_returns(currency1, currency2, ratio, output)
        # self.backtested_df = pd.concat([self.backtested_df, returns_df]) 
    
        figs = self.__get_figure(cerebro, volume=False)
        return figs[0][0]
    
    def __transform_data(self, currency1, currency2, ratio) -> pd.DataFrame: 
            df = self.hist_df[currency1] - self.hist_df[currency2] * ratio
            
            df[df.columns] = MinMaxScaler().fit_transform(df[df.columns])
            df.index = pd.to_datetime(df.index)
            return df   
        
          
    def __get_returns(self, currency1, currency2, ratio, output) -> pd.DataFrame:
        returns = dict()
        
        returns['Currency1'] = currency1
        returns['Currency2'] = currency2
        returns['Ratio'] = ratio
        
        trade = output[0].analyzers.trade.get_analysis()
        returns['N_trades'] = trade.total.closed
        returns['Won'] = trade.won.total
        returns['Win_rate'] = round(trade.won.total / trade.total.closed * 100, 2)  
              
        returns['Roi']  = round(output[0].analyzers.returns.get_analysis()['rtot'] *100,  2)
        returns['Sharperatio'] = round(output[0].analyzers.sharpe.get_analysis()['sharperatio'], 2)
        returns['Drawdown'] = round(output[0].analyzers.drawdown.get_analysis().max.drawdown, 2) 
        
        return pd.DataFrame(returns,index=[0])
    
      
    def __get_figure(self, cerebro,plotter=None, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=300, tight=True, use=None,
             **kwargs) -> matplotlib:
 
        if cerebro._exactbars > 0:
            return

        if not plotter:
            from backtrader import plot
            if cerebro.p.oldsync:
                plotter = plot.Plot_OldSync(**kwargs)
            else:
                plotter = plot.Plot(**kwargs)

        figs = []
        for stratlist in cerebro.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)

                figs.append(rfig)
                
        return figs


class Bbands(bt.Strategy):

    def __init__(self) -> None:
        self.pos = 0
        self.bbands = bt.indicators.BollingerBands(period=20, devfactor=2)


    def next(self) -> None:
        values = (self.data.high, self.data.low,
                self.data.close, self.data.open)
        
        max_value = max(*values)
        min_value = min(*values)

        if not self.pos and min_value < self.bbands.bot:
            self.pos = 1
            self.buy() 

        elif self.pos == 1 and max_value > self.bbands.mid:
            self.pos = 0
            self.close() 

        if not self.pos and max_value > self.bbands.top:
            self.pos = -1
            self.sell() 

        elif self.pos == -1 and min_value < self.bbands.mid:
            self.pos = 0
            self.close() 
