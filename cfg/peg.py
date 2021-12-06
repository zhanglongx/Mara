import mara

import pandas as pd

from cfg._generic import (apiWrapper)

class PEG(mara.ConfigProtocol):
    """
    PEG
    """

    def __init__(self) -> None:
        pass

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(api, ts_code, start_date, end_date, **kwargs)
        return

    def get(self, ttm=False) -> pd.DataFrame:
        result = list()
        for s in self.ts_code:
            pe = apiWrapper(self.api.daily_basic, ts_code=s, index='trade_date',
                            start_date=self.start_date, end_date=self.end_date,
                            fields=['pe'])
            # TODO: more
            pe = pe.iloc[-1:]
            
            g = apiWrapper(self.api.fina_indicator, ts_code=s, index='end_date',
                           start_date=self.start_date, end_date=self.end_date,
                           fields=['q_profit_yoy'])

            g = g.median(0)[0]
            peg = pe / g

            result.append(peg)

            # g = self._pro.fina_indicator(ts_code=self.ts_code, fields=['end_date', 'q_profit_yoy'])
            # if g.empty:
            #     raise ValueError

            # print(pe)
            # _ = g['q_profit_yoy'].to_csv('t.csv')
            # print(pe['pe'][0], g['q_profit_yoy'].median())

            # return pe['pe'][0] / g['q_profit_yoy'].median[0]
        return pd.concat(result, axis=1, keys=self.ts_code)

CONFIG=[PEG()]