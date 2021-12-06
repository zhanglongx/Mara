import warnings

def lookup_ts_code(api, symbols):
    """
    Lookup keyword, and return ts_code
    symbols may be in one of ts_code, symbol, name

    api: tushare api
    symbols: {str, list} symbols to lookup
    """

    if isinstance(symbols, str):
        symbols = [symbols]
    elif isinstance(symbols, list):
        pass
    else:
        raise TypeError()

    info = api.stock_basic()
    ts_code = []
    for s in symbols:
        code = None
        for k in ['ts_code', 'symbol', 'name']:
            if s in list(info[k]):
                code = info.loc[info[info[k] == s].index, 'ts_code']
                break

        if code is None:
            warnings.warn('{} is not found'.format(s))
            continue

        ts_code.append(code.to_string(index=False))

    return ts_code