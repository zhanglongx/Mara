import mara
import pandas as pd
import numpy as np

class PEG(mara.ModuleProtocol):
    '''
    PEG

    output pe, g, peg
    '''

    def __init__(self) -> None:
        pass

    def init(self, ts, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(ts, ts_code, start_date, end_date, **kwargs)
        return

    def get(self, latest=True, ttm=True, **kwargs) -> pd.DataFrame:
        result = list()

        pe_field = 'pe_ttm' if ttm else 'pe'
        for s in self.ts_code:
            pe = self.ts.query('daily_basic', ts_code=s,
                            start_date=self.start_date, end_date=self.end_date,
                            fields=[pe_field], date_col='trade_date', latest=True)

            g = self.ts.query('fina_indicator', ts_code=s,
                           start_date=self.start_date, end_date=self.end_date,
                           fields=['q_profit_yoy'])

            if g.empty:
                g = np.nan
            else:
                # type changed
                g = g.groupby(axis=1, level=0).median().values[0]

            peg = pe
            peg['g'] = g
            peg['peg'] = peg[pe_field] / g

            result.append(peg)

        return pd.concat(result)

MODULE=PEG()