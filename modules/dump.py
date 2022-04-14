import mara

class Dump(mara.ModuleProtocol):

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        print(api)
        print(ts_code)

        print(start_date)
        pass

    def get(self):
        pass

MODULE=Dump()