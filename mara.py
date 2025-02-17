import argparse
import os
import pathlib
import sys
import warnings

# XXX:
warnings.simplefilter(action='ignore', category=FutureWarning)

import runpy
import datetime
import pandas as pd
import matplotlib.pyplot as plt

import utils.tushare as uts
import version

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

    def get(self, latest=True, ttm=False, **kwargs) -> pd.DataFrame:
        '''
        get the date, all inherited 'MUST' implement.
        it may return a dataframe with one or two levels of columns.
        the first level of columns is indicator and the second level
        (if have) is date, as:

                                 |    <indicator1>    | <indicator2>
                  (if presented) | <date 1> | <date2> | 
                   -----------------------------------------------
        <ts_code>  |

        latest: {boolen} series or latest only
        ttm: {boolen} whether use ttm
        '''

        # only derived class
        raise NotImplementedError()

    def plot(self, df: pd.DataFrame) -> None:
        '''
        plot, all inherited can choose if to implement.
        if not implemented, the super provides a basic implement.
        '''

        for c in df.columns.get_level_values(0):
            df[c].transpose().plot(subplots=True, title=c)

def check_date(s) -> None:
    if not s is None:
        try:
            _ = datetime.datetime.strptime(s, '%Y%m%d')
        except:
            warnings.warn('{} is in wrong format'.format(s))
            exit(1)

def export_filebase(arg) -> str:
    schema = []
    if arg.module is not None:
        # Basename without <.ext>, see:
        # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
        schema.append(pathlib.Path(arg.module).stem)
    if arg.arg is not None:
        schema.append(arg.arg)
    if len(arg.KEYWORD) != 0:
        # FIXME: only [0]?
        schema.append(arg.KEYWORD[0])
    
    base = '_'.join(schema)
    for i in range(1, 10):
        f = base + '_{}.xlsx'.format(i)
        if not os.path.exists(f):
            return f

    raise RuntimeError('cannot compose a suitable filename')

def main():
    opt = argparse.ArgumentParser(description='Mara main program')

    opt.add_argument('-c', '--column', type=str, default=uts.NAME,
                     help='''
                     use the specified <COLUMN> to match the <KEYWORD> 
                     (by default 'name' column), <COLUMN> are from: {}
                    '''.format(', '.join(uts.COLUMNS)))
    opt.add_argument('--header', action='store_true', default=False,
                    help='add header')
    opt.add_argument('--list', action='store_true', default=False,
                    help='''
                    list mode, print <COLUMN> only, <COLUMN> is specified by '-c'.
                    NOTE: The '-m' option will be ignored in the list mode
                    ''')
    opt.add_argument('-m', '--module', type=str,
                    help='''
                    use <MODULE> to get data. <MODULE> is the .py file the module implemented in.
                    If this option are not specified, the built-in 'BASIC' module will be used.
                    NOTE: This option will only take effect, if at least one keyword is contained,
                    and list mode is not specified
                    ''')
    opt.add_argument('-a', '--arg', type=str,
                    help='''
                    some modules require input arguments, use this option to pass it to the module
                    ''')
    opt.add_argument('-p', '--plot', action='store_true', default=False,
                    help='''
                    use pd.plot.line() to plot. 
                    It will automatically turn off '--no-latest'.
                    NOTE: This option will only take effect, when '-m' option specified and take effect. 
                    ''')
    opt.add_argument('--sort', type=int, default=0,
                    help='''
                    ascending sort of output by #<SORT> column. If module is specified, the sort 
                    column start with the first column of module output, else start with the first
                    column of basic
                    ''')
    opt.add_argument('-s', '--start-date', type=str, default='20170101',
                    help='''
                    start date [%%Y%%m%%d] for module. All modules accept it
                    ''')
    opt.add_argument('-e', '--end-date', type=str,
                    help='''
                    end date [%%Y%%m%%d] for module. All modules accept it
                    ''')
    opt.add_argument('--no-ttm', action='store_true', default=False,
                    help='''
                    output ttm by default. It can be changed to no ttm. Not all modules accept it
                    ''')
    opt.add_argument('--no-latest', action='store_true', default=False,
                    help='print all, not only the latest date. Not all modules accept it')
    opt.add_argument('-v', '--version', action='version',
                    version='%(prog)s {}'.format(version.__version__))
    opt.add_argument('-x', '--excel', action='store_true', default=False,
                    help='''
                    export to excel, instead of stdout. 
                    The file name has the schema as: <module>_<arg>_<KEYWORD0>_<int>
                    <int> is an auto-increment integer number
                    ''')
    opt.add_argument('KEYWORD', type=str, nargs='*', 
                     help='''
                     keyword(s) to match. If more than one keywords are specified, then all matches
                     will be output.
                     If no keyword are specified, then only basic information will be outputted. 
                     This is for performance considerations.
                     Meanwhile, the '-m' option will be ignored in this case
                     ''') 

    arg = opt.parse_args()

    # date valid
    # FIXME: date order
    check_date(arg.start_date)
    check_date(arg.end_date)

    # initialize the api
    ts = uts.TsWrapper()

    if not arg.column in uts.COLUMNS:
        raise ValueError('{} not in {}'.format(arg.column, ','.join(uts.COLUMNS)))

    output = uts.basic_info(ts, arg.column, keywords=arg.KEYWORD)

    if arg.list == True:
        output = output[arg.column]
    # NOTE: keyword is suppressed for performance consideration, 
    #       may removed further
    elif not arg.module is None and len(arg.KEYWORD) != 0:
        ts_codes = output[uts.TS_CODE].to_list()

        try:
            # FIXME: 
            m = runpy.run_path(arg.module)['MODULE']
        except :
           warnings.warn('load module {} failed'.format(arg.module))
           exit(1)

        m.init(ts, ts_codes, \
            start_date=arg.start_date, \
            end_date=arg.end_date)

        if arg.plot and not arg.no_latest:
            warnings.warn('\'-p\' specified, using \'--no-latest\'')
            arg.no_latest = True

        # FIXME: hard-coded
        df = m.get(latest=(not arg.no_latest), 
                ttm=(not arg.no_ttm), 
                **{'arg': arg.arg})

        arg.sort = len(output.columns) + arg.sort

        # Ensure both DataFrames have the same level of column indices
        if isinstance(df.columns, pd.MultiIndex):
            output.columns = pd.MultiIndex.from_product([output.columns, ['']])
        output = pd.merge(output, df, on=uts.TS_CODE)

        if arg.plot:
            m.plot(df)

            plt.show()
    else:
        # XXX: 'basic' module
        pass

    # sort
    # FIXME: remove restrictions on list?
    if arg.list != True:
        if (arg.sort >= len(output.columns) or arg.sort < 0):
            raise ValueError('sort on {} is out of range'.format(arg.sort))

        output = output.sort_values(output.columns[arg.sort])

    if arg.excel:
        base = export_filebase(arg)
        output.to_excel(base, index=False, header=arg.header)
    else:
        output.to_csv(sys.stdout, index=False, header=arg.header)

if __name__ == '__main__':
    main()