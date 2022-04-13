import mara
import pandas as pd

from modules._generic import (apiWrapper)

class PEG(mara.ModuleProtocol):
    """
    PEG

    output pe, g, peg
    """

    def __init__(self) -> None:
        pass

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(api, ts_code, start_date, end_date, **kwargs)
        return

    def get(self, ttm=False) -> pd.DataFrame:
        result = list()

        pe_field = 'pe_ttm' if ttm else 'pe'
        for s in self.ts_code:
            pe = apiWrapper(self.api.daily_basic, ts_code=s,
                            start_date=self.start_date, end_date=self.end_date,
                            fields=[pe_field], date_col='trade_date', latest=True)

            g = apiWrapper(self.api.fina_indicator, ts_code=s,
                           start_date=self.start_date, end_date=self.end_date,
                           fields=['q_profit_yoy'])

            # type changed
            g = g.groupby(axis=1, level=0).median().values[0]

            peg = pe
            peg['g'] = g
            peg['peg'] = peg[pe_field] / g

            result.append(peg)

        return pd.concat(result)

MODULE=[PEG()]