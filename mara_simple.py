import sys
import warnings
import argparse

import tushare as ts

import cfg._generic as generic

from dateutil.parser import parse

from utils.rc import (load_token)
from utils.tushare import (lookup_ts_code)

def main():
    opt = argparse.ArgumentParser(description='Mara Simple main program')

    opt.add_argument('-s', '--start_date', type=str, 
                     help='tushare start_date')
    opt.add_argument('-e', '--end_date', type=str, 
                     help='tushare end_date')
    opt.add_argument('APINAME', type=str, nargs=1, help='tushare api name') 
    opt.add_argument('FIELDS', type=str, nargs=1, help='tushare api fields') 
    opt.add_argument('SYMBOL', type=str, nargs='+', 
                     help='symbol list, can be one of ts_code, symbol, name') 

    arg = opt.parse_args()

    # token
    token = load_token()

    api = ts.pro_api(token=token)

    # start/end date
    start_date = arg.start_date
    if start_date is not None:
        start_date = parse(start_date).strftime('%Y%m%d') 

    end_date = arg.end_date
    if end_date is not None:
        end_date = parse(end_date).strftime('%Y%m%d')

    # api_name
    api_name = arg.APINAME[0]

    # fields
    fields = arg.FIELDS[0]

    # symbol
    ts_code = lookup_ts_code(api, arg.SYMBOL)
    if len(ts_code) == 0:
        warnings.warn('cannot parse symbol {}'.format(arg.SYMBOL))
        exit(1)

    g = generic.GenericCfg(api_name, fields)
    g.init(api, ts_code, start_date=start_date, end_date=end_date)

    df = g.get()

    df.to_csv(sys.stdout)

if __name__ == '__main__':
    main()