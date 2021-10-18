import re
import pandas as pd
import matplotlib.pyplot as plt

from pandas import date_range
from numpy.random import randn

class Data:
    """
    Fetch the Data.
    """

    def __init__(self, symbol: str, compare=False) -> None:
        self.symbols = [symbol]

        # test only, tempz
        if compare == True:
            self.symbols.append('002')

        self._reports = [pd.concat([genTest('CataA'), genTest('CataB')], axis=1) 
                            for i in range(len(self.symbols))]

        pass

    def get(self, catalog, ttm=False) -> pd.DataFrame:
        """
        Return data (pd.Dataframe). axis[0] is time series, axis[1] is symbols.
        """

        pd.DataFrame()

        if isinstance(catalog, dict) and len(catalog.keys()) > 1:
            raise ValueError('catalog length must be 1')

        return pd.concat([self._formula(r, catalog=catalog) for r in self._reports], 
                            keys=self.symbols, axis=1)

    def _formula(self, report, catalog=None):
        """
        Calculate a report Dataframe based on formulas.
        Hacks: using exec to formula, *DON't rename parameter 'report'*
        """

        if isinstance(catalog, str):
            # nothing to calculate
            return report[catalog]
        elif isinstance(catalog, dict):
            pass
        else:
            raise TypeError('formulas type is not supported')

        # Hacks: 
        for k in catalog.keys():
            left = k
            right = re.sub(r'([^- %+*\/\(\)\d]+)',
                           r'report["\1"]',
                           catalog[k])

            exec('report["%s"] = %s' % (left, right))

        # tempz
        return report[list(catalog.keys())[0]]

class Plot:
    """
    Plot the Figure.
    """

    def __init__(self) -> None:
        pass

    def draw(self, datas, title, separate=True, kind='line'):

        df = pd.concat(datas, axis=1) if isinstance(datas, list) else datas

        if separate == False or len(df.columns) == 1:
            df.plot(title=title, kind=kind)

        else:
            _, axes = plt.subplots(nrows=1, ncols=len(df.columns))

            for i, col in enumerate(df.columns):
                df[col].plot(title=title, kind=kind, ax=axes[i])

        return

def genTest(catalog, date_start='1/1/2000'):
    ts = pd.Series(randn(5), index=date_range(date_start, periods=5))
    ts = ts.cumsum()

    df = pd.DataFrame(randn(5), index=ts.index, columns=[catalog])
    return df.cumsum()