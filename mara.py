import argparse
import sys
import warnings

from matplotlib.pyplot import axis

# XXX:
warnings.simplefilter(action='ignore', category=FutureWarning)

import runpy
import pandas as pd

import utils.tushare as uts

class ModuleProtocol():
    '''
    interface that all source modules need to comply with.
    inspired by Beancount
    '''

    def name(self):
        cls = self.__class__
        return '{}.{}'.format(cls.__module__, cls.__name__)

    __str__ = name

    def init(self, ts, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        '''
        initialize module
        __init__ is already used by python module run. Here we define another
        init() funcition to do the work.
        normally, you should use super().init() in the inherited only, unless 
        you want to perform some extra additional initialization 

        ts: utils.tushare.tsWrapper
        ts_code: {list} tushare ts_code
        start_date: {str} tushare start_date [%Y%m%d]
        end_date: {str} tushare end_date [%Y%m%d]
        '''

        self.ts = ts

        self.ts_code = ts_code

        self.start_date = start_date
        self.end_date   = end_date
        return

    def get(self, ttm=False) -> pd.DataFrame:
        '''
        get the date, all inherited "MUST" implement.
        it may return a dataframe with one or two levels of columns.
        the first level of columns is indicator and the second level
        (if have) is date, as:

                                 |    <indicator1>    | <indicator2>
                  (if presented) | <date 1> | <date2> | 
                   -----------------------------------------------
        <ts_code>  |

        ttm: {boolen} whether use ttm
        '''

        # only derived class
        raise NotImplementedError()

    def plot(self) -> None:
        '''
        plot, all inherited can choose if to implement.
        if impelmented, ensure it can be called directly, not
        necessarily call get() first.
        '''

        warnings.warn('no plot implemented in inherited')
        pass

# TODO: may make basic a module
def basic(ts, column=uts.NAME, keywords=[]) -> pd.DataFrame:
    info = ts.basic()

    if len(keywords) == 0:
        return info

    result=[]
    for k in keywords:
        r = info[info[column].str.contains(k) == True]

        if r.empty: 
            raise ValueError('no keyword matched: {}'.format(k))

        result.append(r)

    return pd.concat(result).drop_duplicates().reset_index(drop=True)

def main():
    opt = argparse.ArgumentParser(description='Mara main program')

    # FIXME: from uts enumerate
    opt.add_argument('-c', '--column', type=str, default=uts.NAME,
                     help='''
                     use the specified <COLUMN> to match the <KEYWORD> 
                     (by default 'name' column), <COLUMN> are from:
                    'ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date'
                    ''')
    opt.add_argument('--header', action='store_true', default=False,
                    help='add header')
    opt.add_argument('--list', type=str,
                    help='''
                    list mode, print <LIST> column only, <LIST> are from:
                    'ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date'.
                    NOTE: The '-m' option will be ignored in the list mode
                    ''')
    opt.add_argument('-l', '--lastest', type=str,
                    help='print on the latest date only. Not all modules accept it')
    opt.add_argument('-m', '--module', type=str,
                    help='''
                    use <MODULE> to get data. <MODULE> is the .py file the module implemented in.
                    If this option are not specified, the built-in 'BASIC' module will be used.
                    NOTE: This option will only take effect, if at least one keyword is contained,
                    and list mode is not specified
                    ''')
    opt.add_argument('--sort', type=int, default=0,
                    help='''
                    ascending sort of output by #<SORT> column. if module is specified, the sort 
                    column start with the first column of module output, else start with the first
                    column of basic
                    ''')
    opt.add_argument('-s', '--start_date', type=str, default='20170101',
                    help='''
                    start date [%%Y%%m%%d] for module. Not all modules accept it
                    ''')
    opt.add_argument('-e', '--end_date', type=str,
                    help='''
                    end date [%%Y%%m%%d] for module. Not all modules accept it
                    ''')
    opt.add_argument('KEYWORD', type=str, nargs='*', 
                     help='''
                     keyword(s) to match. If more than one keywords are specified, then all matches
                     will be output.
                     If no keyword are specified, then only basic information will be outputted. 
                     Which is for performance considerations.
                     Meanwhile, the '-m' option will be ignored in this case
                     ''') 

    arg = opt.parse_args()

    # initialize the api
    ts = uts.TsWrapper()

    output = basic(ts, arg.column, keywords=arg.KEYWORD)

    if not arg.list is None:
        output = output[arg.list]
    # NOTE: keyword is suppressed for performance consideration, 
    #       may removed further
    elif not arg.module is None and len(arg.KEYWORD) != 0:
        ts_codes = output[uts.TS_CODE].to_list()

        if not arg.lastest is None:
            raise NotImplemented('\'-l\' is not implemented')

        try:
            # FIXME: 
            m = runpy.run_path(arg.module)['MODULE']
        except :
            warnings.warn('load module {} failed'.format(arg.module))
            exit(1)

        m.init(ts, ts_codes, \
            start_date=arg.start_date, \
            end_date=arg.end_date)

        df = m.get(ttm=True)

        arg.sort = len(output.columns) + arg.sort

        output = pd.merge(output, df, on=uts.TS_CODE)

    # sort
    if arg.list is None:
        if (arg.sort >= len(output.columns) or arg.sort < 0):
            raise ValueError('sort on {} is out of range'.format(arg.sort))

        output = output.sort_values(output.columns[arg.sort])

    output.to_csv(sys.stdout, index=False, header=arg.header)

if __name__ == '__main__':
    main()