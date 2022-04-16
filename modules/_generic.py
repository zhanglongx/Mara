import pandas as pd

import mara

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
    def get(self, ttm=False, **kwargs) -> pd.DataFrame:
        pass