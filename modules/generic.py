from signal import raise_signal
import pandas as pd

import mara

LIST={
    'daily_basic': {
        'close': '当日收盘价',
        'turnover_rate': '换手率（%）',
        'turnover_rate_f': '换手率（自由流通股）',
        'volume_ratio': '量比',
        'pe': '市盈率（总市值/净利润，亏损的PE为空）',
        'pe_ttm': '市盈率（TTM，亏损的PE为空）',
        'pb': '市净率（总市值/净资产）',
        'ps': '市销率',
        'ps_ttm': '市销率（TTM）',
        'dv_ratio': '股息率（%）',
        'dv_ttm': '股息率（TTM）（%）',
        'total_share': '总股本（万股）',
        'float_share': '流通股本（万股）',
        'free_share': '自由流通股本（万）',
        'total_mv': '总市值（万元）',
        'circ_mv': '流通市值（万元）',
    },

    'fina_indicator': {
        'q_op_yoy': '营业利润同比增长率(%)(单季度)',
        'q_profit_yoy': '净利润同比增长率(%)(单季度)',
    },
}

DATE_COL={
    'daily_basic': 'trade_date',
    'fina_indicator': 'end_date',
}

class GenericMod(mara.ModuleProtocol):
    '''
    generic module
    '''

    def __init__(self, **kwargs) -> None:
        pass

    def init(self, ts, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        super().init(ts, ts_code, start_date, end_date)
        return

    # FIXME: ttm
    def get(self, latest=True, ttm=True, **kwargs) -> pd.DataFrame:
        name = None
        api_name = None

        if not kwargs is None:
            name = kwargs.pop('param', None)

        if name is None:
            raise ValueError('no name specified')

        for k in LIST.keys():
            for f in LIST[k].keys():
                if f == name:
                    api_name = k

        if api_name is None:
            raise ValueError('api with field: {} not found'.format(name))

        result = list()
        for s in self.ts_code:
            df = self.ts.query(api_name, ts_code=s,
                            start_date=self.start_date,
                            end_date=self.end_date,
                            fields=[name],
                            date_col=DATE_COL[api_name],
                            latest=latest)

            result.append(df)

        return pd.concat(result)

MODULE=GenericMod()