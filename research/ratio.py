
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

class Ratio():

    def get_ratio(self, coint_df: pd.DataFrame =
                  pd.read_csv(
                      './data/processing/coint_output.csv', index_col=0),

                  useful_df: pd.DataFrame =
                  pd.read_csv(
                      './data/processing/cleaner_output.csv', index_col=0)
                  
                  ) -> pd.DataFrame:

        rationed_df = self.__apply_ratio_calc(useful_df.median(), coint_df)
        rationed_df.to_csv('./data/analyzed/final_output.csv')
        return rationed_df

    def __apply_ratio_calc(self, median, coint_df) -> pd.DataFrame:
        coint_df['Ratio'] = np.vectorize(
            lambda currency1, currency2: 
                   median[currency1] / median[currency2])(
                   coint_df['Currency1'], coint_df['Currency2'])
                   
        return coint_df.sort_values('Correlation', ascending=False)

