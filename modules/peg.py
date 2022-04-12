import mara

import pandas as pd

from modules._generic import (apiWrapper)

class PEG(mara.ModuleProtocol):
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
            pe = apiWrapper(self.api.daily_basic, ts_code=s, index='ts_code',
                            start_date=self.start_date, end_date=self.end_date,
                            fields=['pe'])
            # TODO: more
            pe = pe.iloc[-1:]
            
            g = apiWrapper(self.api.fina_indicator, ts_code=s, index='ts_code',
                           start_date=self.start_date, end_date=self.end_date,
                           fields=['q_profit_yoy'])

            g = g.median(0)[0]

            peg = pe
            peg['g'] = g
            peg['peg'] = peg['pe'] / peg['g']

            result.append(peg)

        return pd.concat(result)

MODULE=[PEG()]