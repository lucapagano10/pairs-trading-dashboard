import pandas as pd
import research
import os
path = os.path.dirname(__file__)

class Researcher():
    
    def __init__(self) -> None:
        self.hist_df = pd.DataFrame()
        self.cleared_df = pd.DataFrame()
        self.corr_df = pd.DataFrame()
        self.coint_df = pd.DataFrame()
        self.researched_df = pd.DataFrame()
    
    
    def load_researched_data(self) -> None:
        self.hist_df = pd.read_csv(os.path.join(path,"..", "data/raw/historical_data.csv"), header=[0, 1], index_col=0)
        self.cleared_df = pd.read_csv(os.path.join(path,"..", "data/processing/cleaner_output.csv"), index_col=0)
        self.corr_df = pd.read_csv(os.path.join(path,"..", "data/processing/corr_output.csv"))
        self.coint_df = pd.read_csv(os.path.join(path,"..", "data/processing/coint_output.csv"))
        self.researched_df = pd.read_csv(os.path.join(path,"..", "data/researched/research_output.csv"))

        
    def filter_research_data(self,timeframe:str, min_correlation:float, interval:str) -> None:
        """
        :param timeframe: e.g. '15m', '4h', '1d', '3w', '1M'
        :type: str
        
        :param min_correlation: e.g. '0.83' is 83%
        :type: float
                
        :param interval: datetime
        :type: str
        """
        self.hist_df = research.Loader().load_data(timeframe, interval)
        self.__read_research_data(min_correlation)
        
    def __read_research_data(self, min_correlation: float) -> None:
        self.cleared_df = research.Cleaner().get_cleared_data(self.hist_df, save=False)
        self.corr_df = research.Correlation().get_log_correlation(self.cleared_df, min_correlation=min_correlation, save=False)
        self.coint_df = research.Cointegration().get_cointegration(self.corr_df, self.cleared_df, save=False)
        self.researched_df = research.Ratio().get_ratio(self.coint_df, self.cleared_df, save=False)