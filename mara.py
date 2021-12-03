import os.path
import runpy
import warnings
import argparse

import yaml
import pandas as pd
import tushare as ts

from dateutil.parser import parse

MARARC='/home/zhlx/.mararc'

class ConfigProtocol():
    """
    Interface that all source configs need to comply with.
    Inspired by Beancount
    """

    def name(self):
        cls = self.__class__
        return '{}.{}'.format(cls.__module__, cls.__name__)

    __str__ = name

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs):
        pass

    def get(self) -> pd.DataFrame:
        pass

def main():
    opt = argparse.ArgumentParser(description='Mara main program')

    opt.add_argument('-s', '--start_date', type=str, 
                     help='tushare start_date')
    opt.add_argument('-e', '--end_date', type=str, 
                     help='tushare end_date')
    opt.add_argument('-t', '--template', type=str, 
                     help='template file in .yaml')
    opt.add_argument('CONFIG', type=str, nargs=1, help='config filename') 
    opt.add_argument('SYMBOL', type=str, nargs='+', help='symbol list') 

    arg = opt.parse_args()

    # MARARC file
    if not os.path.isfile(MARARC):
        raise ValueError('{} not exists'.format(MARARC))

    with open(MARARC, 'r') as r:
        try:
            rc = yaml.safe_load(r)
        except yaml.error.YAMLError:
            warnings.warn('cannot parse {}'.format(MARARC))
            exit(1)

    token = rc.pop('token', None)
    if token is None:
        warnings.warn('token is missing in {}'.format(MARARC))
        exit(1)

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
        start_date = parse(start_date).strftime('%Y-%m-%d') 

    end_date = arg.end_date
    if end_date is not None:
        end_date = parse(end_date).strftime('%Y-%m-%d')

    # load config modules
    mod = runpy.run_path(arg.CONFIG[0])
    configlist = mod['CONFIG']

    for c in configlist:
        c.init(api, arg.SYMBOL, start_date=start_date, end_date=end_date, **template)

if __name__ == '__main__':
    main()