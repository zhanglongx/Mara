import datetime
import argparse

import utils.tushare as uts

DEFAULT_DAYS=60

class Recall:

    def __init__(self, ts, ts_code, start_date, days=DEFAULT_DAYS) -> None:
        if not isinstance(ts_code, str):
            raise TypeError

        if start_date is None:
            raise ValueError
        else:
            try:
                _ = datetime.datetime.strptime(start_date, "%Y%m%d")
            except ValueError:
                raise ValueError("start_date {} cannot be parsed"\
                                .format(start_date))

        self.ts = ts
        self.ts_code = ts_code
        self.start_date = start_date 
        self.days = days

    def Run(self) -> dict():
        price = self.ts.pro_bar(ts_code=self.ts_code, 
                                start_date=self.start_date, 
                                adj="hfq")
        if price is None or price.empty:
            raise ValueError("failed to get tushare pro_bar ts_code: {}, date: {}"\
                        .format(self.ts_code, self.start_date))

        price = price.set_index("trade_date")
        price = price["close"]

        # reverse and select only we need
        price = price.iloc[::-1]
        price = price.iloc[0:self.days]

        result = dict()
        result["min_pct"] = price.min() / price.iloc[0]
        result["min_date"] = min_date = price.idxmin()
        result["max_pct"] = price.loc[min_date:].max() / price.iloc[0]
        result["max_date"] = price.loc[min_date:].idxmax()

        result["min_days"] = self._timeDelta(result["min_date"])
        result["max_days"] = self._timeDelta(result["max_date"])

        return result

    def _timeDelta(self, date) -> int:
        try: 
            orig = datetime.datetime.strptime(self.start_date, "%Y%m%d")
        except ValueError:
            raise ValueError("Cannot parse orig: {}".format(self.start_date))
        
        d = datetime.datetime.strptime(date, "%Y%m%d")

        days = d - orig
        return days.days

def basic(ts, symbol) -> str:
    info = ts.basic()

    result=[]
    for col in [uts.TS_CODE, uts.SYMBOL, uts.NAME]:
        r = info[info[col].str.contains(symbol) == True]

        if r.empty: 
            continue

        result.append(r)
        break

    if len(result) == 0:
        raise ValueError("%s not exists".format(symbol))
    elif len(result) > 1:
        raise ValueError("%s has too many match".format(symbol))

    return result[0][uts.TS_CODE].values[0]

def main():
    opt = argparse.ArgumentParser(description="Mara Recall main program")

    opt.add_argument("-s", "--start_date", type=str,
                    help="recall start date in (%%Y%%m%%d)")
    opt.add_argument("-d", "--days", type=int, 
                    default=DEFAULT_DAYS,
                    help="recall days")
    opt.add_argument("SYMBOL", type=str, nargs=1,
                    help="symbol, can be one of ts_code, symbol, name")

    arg = opt.parse_args()

    # token
    ts = uts.TsWrapper()

    # symbol
    ts_code = basic(ts, arg.SYMBOL[0])

    res = Recall(ts, ts_code, arg.start_date, days=arg.days).Run()
    print("{},{},{},{}".format(res["min_days"], res["min_pct"], 
                            res["max_days"], res["max_pct"]))

if __name__ == '__main__':
    main()