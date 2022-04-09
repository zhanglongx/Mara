import argparse
import sys
import tushare as ts
import warnings

from utils.rc import (load_token)

def main():
    opt = argparse.ArgumentParser(description='Mara Symbols main program')

    opt.add_argument('-c', '--column', type=str, 
                    help='''
                    print <column> only, from:
                    'ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date' 
                    ''')
    opt.add_argument('--header', action='store_true', default=False,
                    help='add header')
    opt.add_argument('-m', '--match', type=str,
                     help='''
                     has the format: <column>:<match>,
                     print the match only
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