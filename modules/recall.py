import datetime
import pandas as pd

import mara
import utils.tushare as uts

class Recall(mara.ModuleProtocol):
    '''
    Recall

    output min_pct, max_pct, min_days, max_days, now_pct
    '''

    def __init__(self) -> None:
        pass

    def init(self, ts, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(ts, ts_code, start_date, end_date, **kwargs)
        return

    def get(self, latest=True, ttm=True, **kwargs) -> pd.DataFrame:
        array = list()        
        for s in self.ts_code:
            price = self.ts.pro_bar(ts_code=s, 
                                    start_date=self.start_date, 
                                    end_date=self.end_date,
                                    adj='hfq')
            if price is None or price.empty:
                raise ValueError('failed to get tushare pro_bar ts_code: {}, date: {}'\
                            .format(self.ts_code, self.start_date))

            price = price.set_index('trade_date')
            price = price['close']

            # reverse and select only we need
            price = price.iloc[::-1]

            result = dict()
            result[uts.TS_CODE] = s

            result['min_pct'] = price.min() / price.iloc[0]
            min_date = price.idxmin()

            result['max_pct'] = price.loc[min_date:].max() / price.iloc[0]
            max_date = price.loc[min_date:].idxmax()

            result['min_days'] = self._timeDelta(min_date)
            result['max_days'] = self._timeDelta(max_date)

            result['now_pct'] = price.iloc[-1] / price[0]

            array.append(pd.DataFrame(result, index=[0]))

        return pd.concat(array, ignore_index=True)

    def _timeDelta(self, date) -> int:
        try: 
            orig = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        except ValueError:
            raise ValueError('Cannot parse orig: {}'.format(self.start_date))
        
        d = datetime.datetime.strptime(date, '%Y%m%d')

        days = d - orig
        return days.days

    def plot(self, df: pd.DataFrame) -> None:
        raise NotImplementedError

MODULE=Recall()