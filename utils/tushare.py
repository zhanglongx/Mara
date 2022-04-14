import os
import yaml
import time
import tushare as ts
import pandas as pd

MARARC=os.path.join(os.path.expanduser("~"), ".mararc")

TS_CODE='ts_code'
SYMBOL='symbol'
NAME='name'
AREA='area'
INDUSTRY='industry'
MARKET='market'

class TsWrapper:
    def __init__(self, filename=MARARC) -> None:
        '''
        filename: {str} mara rc file in yaml format:
            token: <tushare token>
        '''
        if not os.path.isfile(filename):
            raise FileNotFoundError('{} not exists'.format(filename))

        with open(filename, 'r') as r:
            rc = yaml.safe_load(r)

        token = rc.pop("token", None)
        if token is None:
            raise SyntaxError('token is missing in {}'.format(filename))

        self.pro = ts.pro_api(token=token)
    
    def basic(self, **args):
        return self.pro.query('stock_basic', **args)

    def query(self, api, ts_code, start_date, end_date, 
            fields, date_col='end_date', latest=False) -> pd.DataFrame:
        '''
        one is a simple wrapper around an tushare api. 
        and will pivot to:

                       |    <indicator1>    | <indicator2>
                       | <date 1> | <date2> | 
                        -----------------------------------------------
            <ts_code>  |

        sometimes, tushare will have access restrictions to the api request,
        apiWrapper will retry incase of exceptions returned
        '''

        if date_col not in fields:
            fields.append(date_col)

        if TS_CODE not in fields:
            fields.append(TS_CODE)
        
        # Exception: 抱歉，您每分钟最多访问该接口50次，
        # 权限的具体详情访问：https://tushare.pro/document/1?doc_id=108
        for _ in range(3):
            try:
                # df :
                # ts_code, <date_col>(descending), fields
                df = self.pro.query(api, ts_code=ts_code, 
                                    start_date=start_date, end_date=end_date, 
                                    fields=fields)
            except Exception:
                time.sleep(60)
                continue

            if df.empty:
                raise ValueError

            break

        df = df.drop_duplicates(subset=date_col, keep='first').\
                pivot(index=TS_CODE, columns=date_col).\
                sort_index(axis=1, level=1)

        if latest == True:
            idx = pd.IndexSlice

            return df.loc[idx[:, idx[:, df.columns.get_level_values(1)[-1]]]]
        else:
            return df
