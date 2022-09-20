import os
import yaml
import time
import tushare as ts
import pandas as pd

MARARC=os.path.join(os.path.expanduser('~'), '.mararc')

TS_CODE='ts_code'
SYMBOL='symbol'
NAME='name'
AREA='area'
INDUSTRY='industry'
MARKET='market'
END_DATE='end_date'

COLUMNS = [TS_CODE, SYMBOL, NAME, AREA, INDUSTRY, MARKET]

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

        token = rc.pop('token', None)
        if token is None:
            raise SyntaxError('token is missing in {}'.format(filename))

        self.pro = ts.pro_api(token=token)

        self.table_basic    = None
        self.table_old_name = None
    
    def basic(self, **args) -> pd.DataFrame:
        if self.table_basic is None:
            self.table_basic = self.pro.query('stock_basic') 

        return self.table_basic 

    def old_name(self, **args) -> pd.DataFrame:
        if self.table_old_name is None:
            self.table_old_name = self.pro.namechange() 

        return self.table_old_name

    def pro_bar(self, ts_code, start_date, end_date, adj) -> pd.DataFrame:
        # Exception: 抱歉，您每分钟最多访问该接口50次，
        # 权限的具体详情访问：https://tushare.pro/document/1?doc_id=108
        for _ in range(3):
            try:
                # df :
                # ts_code, <date_col>(descending), fields
                df = ts.pro_bar(ts_code=ts_code, 
                                api=self.pro,
                                start_date=start_date, 
                                end_date=end_date,
                                adj=adj)
            except Exception:
                time.sleep(60)
                continue

            break

        return df

    def query_many(self, api, ts_code, start_date, end_date, 
            fields, date_col=END_DATE, latest=False) -> pd.DataFrame:
        '''
        query_many is a simple wrapper around an tushare api. 
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

            break

        df = df.drop_duplicates(subset=date_col, keep='first').\
                pivot(index=TS_CODE, columns=date_col).\
                sort_index(axis=1, level=1)

        if latest == True:
            idx = pd.IndexSlice

            return df.loc[idx[:, idx[:, df.columns.get_level_values(1)[-1]]]]
        else:
            return df

def covert_name(ts, names: list) -> list:
    '''
    convert_name will first lookup basic. if not found, lookup
    the old_name and return the current name
    NOTE: here the partial matching is used
    '''
    if not isinstance(ts, TsWrapper):
        raise TypeError("must have TsWrapper")

    basic = ts.basic()
    old_name = ts.old_name()

    ts_code = []
    for n in names: 
        r = basic[basic[NAME].str.contains(n) == True]

        if r.empty:
            r = old_name[old_name[NAME].str.contains(n) == True]

            if r.empty:
                raise ValueError("{} not exists".format(n))

            r = r.drop_duplicates(subset=TS_CODE)

        ts_code.extend(r[TS_CODE].tolist())

    return basic[basic[TS_CODE].isin(ts_code)][NAME].tolist()

def basic_info(ts, column=NAME, keywords=[]) -> pd.DataFrame:
    info = ts.basic()

    if len(keywords) == 0:
        return info

    if column == NAME:
        keywords = covert_name(ts, keywords)

    return info[info[column].isin(keywords)].sort_values(TS_CODE)