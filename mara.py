import argparse
import sys
import pandas as pd
import tushare as ts
import warnings

from utils.rc import (load_token)

class ConfigProtocol():
    """
    Interface that all source configs need to comply with.
    Inspired by Beancount
    """

    def name(self):
        cls = self.__class__
        return '{}.{}'.format(cls.__module__, cls.__name__)

    __str__ = name

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        """
        Initialize Cfg 
        __init__ is already used by python module run. Here we define another
        init() funcition to do the work.
        normally, you should use super().init() in the inherited only, unless 
        you want to perform some extra additional initialization 

        api: tushare api
        ts_code: {list} tushare ts_code
        start_date: {str} tushare start_date [%Y%m%d]
        end_date: {str} tushare end_date [%Y%m%d]
        """

        self.api = api

        self.ts_code = ts_code

        self.start_date = start_date
        self.end_date   = end_date
        return

    def get(self, ttm=False) -> pd.DataFrame:
        """
        Get the date, all inherited "MUST" implement.
        It should return a dataframe with tow levels of columns.
        The first level of columns being symbols and the second level 
        being indicators, as:

                      |           <symbol1>           |     <symbol 2>
                      | <indicator 1> | <indicator 2> | 
                       -----------------------------------------------
        <time index>  |

        ttm: {boolen} whether output ttm
        """

        raise NotImplementedError()

    def plot(self) -> None:
        """
        Plot, all inherited can choose if to implement.
        If impelmented, ensure it can be called directly, not
        necessarily call get() first.
        """

        warnings.warn('no plot implemented in inherited')
        pass

def main():
    opt = argparse.ArgumentParser(description='Mara main program')

    opt.add_argument('-c', '--column', type=str, default='symbol',
                     help='''
                     Use the specified <COLUMN> to match the <KEYWORD> 
                     (by default 'symbol' column), <COLUMN> are from:
                    'ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date'
                    ''')
    opt.add_argument('--header', action='store_true', default=False,
                    help='add header')
    opt.add_argument('-l', '--list', type=str,
                    help='''
                    list mode, print <LIST> column only, <LIST> are from:
                    'ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date'.
                    NOTE: The '-m' option will be ignored in the list mode
                    ''')
    opt.add_argument('-m', '--module', type=str,
                    help='''
                    Using <MODULE> to get data. <MODULE> is the .py file the module implemented.
                    If this option are specified, the built-in 'BASIC' module will be used.
                    NOTE: This option will only take effect, either at least one keyword is contained,
                    or list mode is not specified
                    ''')
    opt.add_argument('KEYWORD', type=str, nargs='*', 
                     help='''
                     keyword(s) to match. If more than one keyword is specified, then all matches
                     will be output.
                     If no keyword are specified, then only basic information will be outputted. 
                     Which is for performance considerations.
                     Meanwhile, the '-m' option will be ignored in this case
                     ''') 

    arg = opt.parse_args()

    # token
    token = load_token()

    api = ts.pro_api(token=token)

    info = api.stock_basic()

    if arg.match is not None:
        try:
            [col_to_match, match] = arg.match.split(':')
        except ValueError:
            warnings.warn('input {} error'.format(arg.match))
            exit(1)

        info = info[info[col_to_match].str.contains(match) == True]

    if arg.column is None:
        columns = None
    else:
        columns = [arg.column]

    info.to_csv(sys.stdout, index=False, header=arg.header, columns=columns)


if __name__ == '__main__':
    main()