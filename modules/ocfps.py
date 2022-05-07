import mara
import pandas as pd
import numpy as np

class OCFPS(mara.ModuleProtocol):
    '''
    OCFPS

    output close, ocfps, ratio
    '''

    def __init__(self) -> None:
        pass

    def init(self, ts, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(ts, ts_code, start_date, end_date, **kwargs)
        return

    def get(self, latest=True, ttm=True, **kwargs) -> pd.DataFrame:
        result = list()

        for s in self.ts_code:
            close = self.ts.query('daily_basic', ts_code=s,
                                start_date=self.start_date, end_date=self.end_date,
                                fields=['close'], date_col='trade_date', latest=True)

            ocfps = self.ts.query('fina_indicator', ts_code=s,
                                start_date=self.start_date, end_date=self.end_date,
                                fields=['ocfps'], date_col='end_date', latest=False)
            
            if ocfps.empty:
                ocfps = np.nan
            else:
                # type changed
                ocfps = ocfps.groupby(axis=1, level=0).median().values[0]

            close['ocfps'] = ocfps
            close['ratio'] = ocfps / close['close']

            result.append(close)

        return pd.concat(result)

    def plot(self, df: pd.DataFrame) -> None:
        raise NotImplementedError

MODULE=OCFPS()