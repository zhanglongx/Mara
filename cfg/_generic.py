import re
import pandas as pd
import matplotlib.pyplot as plt

import mara

class GenericCfg(mara.ConfigProtocol):
    """
    Generic config
    """

    # TODO: compare
    def __init__(self, indicator, fields) -> None:
        if indicator is None or not isinstance(indicator, str):
            raise ValueError('indicator should be one of tushare api')

        self.indicator = indicator

        if fields is None: 
            raise ValueError('fields cannot be None')
        elif isinstance(fields, str):
            fields = [fields]
        elif len(fields) == 0:
            raise ValueError('fields cannot be empty')

        self.fields = fields

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(api, ts_code, start_date, end_date)
        return

    # TODO: ttm
    def get(self, ttm=False) -> pd.DataFrame:
        # FIXME:
        if self.indicator != 'indicator':
            raise ValueError

        api = self.api.fina_indicator

        if isinstance(self.fields, dict):
            fields = self.fields.keys()
            # TODO: _formula()
            raise NotImplementedError()
        else:
            fields = self.fields

        fields.append('end_date')

        result = list()
        for s in self.ts_code:
            df = api(ts_code=s, start_date=self.start_date, end_date=self.end_date, fields=fields)

            df.set_index('end_date', inplace=True)

            # remove duplicated row
            df = df[~df.index.duplicated(keep='first')]

            df.sort_index(inplace=True)

            result.append(df)

        return pd.concat(result, axis=1, keys=self.ts_code)
    
    def _formula(self, report, catalog=None):
        """
        Calculate a report Dataframe based on formulas.
        Hacks: using exec to formula, *DON'T rename parameter 'report'*
        """

        if isinstance(catalog, str):
            # nothing to calculate
            return report[catalog]
        elif isinstance(catalog, dict):
            pass
        else:
            raise TypeError('formula type is not supported')

        # Hacks: 
        for k in catalog.keys():
            left = k
            right = re.sub(r'([^- %+*\/\(\)\d]+)',
                           r'report["\1"]',
                           catalog[k])

            exec('report["%s"] = %s' % (left, right))

        # FIXME:
        return report[list(catalog.keys())[0]]

class Plot:
    """
    Plot the Figure.
    """

    def __init__(self) -> None:
        return

    def draw(self, datas, title, separate=True, **kwargs):
        """
        Draw the plot

        Parameters
        ----------
        datas: a dataframe or list of dataframe
        title: plot title
        separate: if plot side-by-side
        kwargs: passed to df.plot()
        """

        df = pd.concat(datas, axis=1) if isinstance(datas, list) else datas

        if separate == False or len(df.columns) == 1:
            df.plot(title=title, **kwargs)
        else:
            _, axes = plt.subplots(nrows=1, ncols=len(df.columns))

            for i, col in enumerate(df.columns):
                df[col].plot(title=title, ax=axes[i], **kwargs)

        return