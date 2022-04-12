import re
import pandas as pd
import matplotlib.pyplot as plt
import warnings

import mara

def apiWrapper(api, ts_code, start_date, end_date, 
            fields, date_col='end_date', latest=False) -> pd.DataFrame:
    '''
    apiWrapper is a simple wrapper around an tushare api. 
    and it will pivot to:

                   |    <indicator1>    | <indicator2>
                   | <date 1> | <date2> | 
                    -----------------------------------------------
        <ts_code>  |
    '''
    if date_col not in fields:
        fields.append(date_col)

    if 'ts_code' not in fields:
        fields.append('ts_code')
    
    df = api(ts_code=ts_code, start_date=start_date, end_date=end_date, 
            fields=fields)
    if df.empty:
        raise ValueError

    df = df.drop_duplicates().\
            pivot(index='ts_code', columns=date_col).\
            sort_index(axis=1, level=1)

    if latest == True:
        idx = pd.IndexSlice

        return df.loc[idx[:, idx[:, df.columns.get_level_values(1)[-1]]]]
    else:
        return df

class GenericMod(mara.ModuleProtocol):
    """
    Generic config
    """

    def __init__(self, indicator, fields, **kwargs) -> None:
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
        self.plot_params = kwargs

        # get will output here
        self.df = None

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(api, ts_code, start_date, end_date)
        return

    # TODO: ttm
    def get(self, ttm=False) -> pd.DataFrame:
        # FIXME:
        if self.indicator == 'fina_indicator':
            api = self.api.fina_indicator
        elif self.indicator == 'balancesheet':
            api = self.api.balancesheet
        else:
            raise NotImplementedError()

        if isinstance(self.fields, dict):
            fields = self.fields.keys()
            # TODO: _formula(), note fields is list now!
            raise NotImplementedError()
        else:
            fields = self.fields

        result = list()
        for s in self.ts_code:
            df = apiWrapper(api, ts_code=s, index='end_date',
                            start_date=self.start_date, end_date=self.end_date, 
                            fields=fields)

            result.append(df)

        self.df = pd.concat(result, axis=1, keys=self.ts_code) 
        return self.df
    
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

    def plot(self) -> None:
        if self.plot_params is None:
            plot_params = self.plot_params
        else:
            plot_params = dict()

        if self.df is None:
            warnings.warn('no dataframe, automatilly get...' )
            self.get()

        df = self.df
        for f in df.columns.levels[1]:
            kind = plot_params[f] if f in plot_params else 'line'

            select = df.xs(f, axis=1, level=1)
            select.plot(title=f, kind=kind)

        plt.show()