import re
import warnings
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

class Data:
    """
    Fetch the Data from tushare

    Parameters
    ---------
    symbols: a string or list. same as ts_code
    token: tushare token
    compare: NOT supported now
    fields: tushare fields
    start_date: tushare api start_date
    """

    # TODO: compare
    def __init__(self, symbols, token, compare=False, fields='', start_date='20160101') -> None:
        if isinstance(symbols, str):
            self.symbols = [symbols]
        elif isinstance(symbols, list):
            if len(symbols) > 2:
                raise ValueError('symbols should be less than 2')
            elif len(symbols) > 1 and compare == True: 
                warnings.warn('symbols > 2, no compare')
                compare = False

            self.symbols = symbols
        else:
            raise TypeError('symbols type error')

        if not isinstance(fields, list):
            raise TypeError('fields type error')

        self.token = token
        self.fields = fields
        self.start_date = start_date

        self._fetch()

        return

    # TODO: ttm
    def get(self, catalog, ttm=False) -> pd.DataFrame:
        """
        Return data (pd.Dataframe). axis[0] is time series, axis[1] is symbols.

        Parameters
        ----------
        catalog: a string or dict. 
        ttm: NOT supported now.
        """

        if isinstance(catalog, dict) and len(catalog.keys()) > 1:
            raise ValueError('catalog length must be 1')

        return pd.concat([self._formula(r, catalog=catalog) for r in self._reports], 
                            keys=self.symbols, axis=1)
    
    def _fetch(self) -> pd.DataFrame:
        fields = self.fields
        for t in ['ts_code', 'end_date']:
            fields.append(t)

        pro = ts.pro_api(token=self.token)

        # TODO: check symbols

        self._reports = []
        for s in self.symbols:
            df = pro.fina_indicator(ts_code=s, fields=fields, start_date=self.start_date)
            df.set_index('end_date', inplace=True)

            # remove duplicated row
            df = df[~df.index.duplicated(keep='first')]

            df.sort_index(inplace=True)

            self._reports.append(df)

        return

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