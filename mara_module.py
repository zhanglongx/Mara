import sys
import os.path
import runpy
import warnings
import argparse

import yaml
import pandas as pd
import tushare as ts

from dateutil.parser import parse

from utils.tushare import (load_token)
from utils.tushare import (lookup_ts_code)

def main():
    opt = argparse.ArgumentParser(description='Mara Module main program')

    opt.add_argument('-p', '--plot', action='store_true', default=False,
                     help='to plot using')
    opt.add_argument('-s', '--start_date', type=str, 
                     help='tushare start_date')
    opt.add_argument('-e', '--end_date', type=str, 
                     help='tushare end_date')
    opt.add_argument('-t', '--template', type=str, 
                     help='template file in .yaml')
    opt.add_argument('CONFIG', type=str, nargs=1, help='config .py filename') 
    opt.add_argument('SYMBOL', type=str, nargs='+', 
                     help='symbol list, can be one of ts_code, symbol, name') 

    arg = opt.parse_args()

    # token
    token = load_token()

    api = ts.pro_api(token=token)

    # template file
    template = dict()
    if arg.template is not None and os.path.isfile(arg.template):
        with open(arg.template, 'r') as t:
            try:
                template = yaml.safe_load(t)
            except yaml.error.YAMLError:
                warnings.warn('cannot parse {}'.format(arg.template))

    start_date = arg.start_date
    if start_date is not None:
        start_date = parse(start_date).strftime('%Y%m%d') 

    end_date = arg.end_date
    if end_date is not None:
        end_date = parse(end_date).strftime('%Y%m%d')

    # load config modules
    mod = runpy.run_path(arg.CONFIG[0])
    configlist = mod['CONFIG']

    ts_code = lookup_ts_code(api, arg.SYMBOL)
    if len(ts_code) == 0:
        warnings.warn('cannot parse symbol {}'.format(arg.SYMBOL))
        exit(1)

    for c in configlist:
        c.init(api, ts_code, start_date=start_date, end_date=end_date, **template)
        df = c.get()

        df.to_csv(sys.stdout)

        if arg.plot:
            c.plot()

if __name__ == '__main__':
    main()