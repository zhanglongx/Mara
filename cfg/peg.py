import mara

import tushare as ts
import pandas as pd

class PEG(mara.ConfigProtocol):
    """
    PEG
    """

    def __init__(self) -> None:
        pass

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(api, ts_code, start_date, end_date, **kwargs)
        return

    def get(self) -> pd.DataFrame:
        # pe = self._pro.daily_basic(ts_code=self.ts_code, fields=['pe'])
        # if pe.empty:
        #     raise ValueError

        # g = self._pro.fina_indicator(ts_code=self.ts_code, fields=['end_date', 'q_profit_yoy'])
        # if g.empty:
        #     raise ValueError

        # print(pe)
        # _ = g['q_profit_yoy'].to_csv('t.csv')
        # print(pe['pe'][0], g['q_profit_yoy'].median())

        # return pe['pe'][0] / g['q_profit_yoy'].median[0]
        pass