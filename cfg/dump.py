from mara import ConfigProtocol

class Dump(ConfigProtocol):

    def init(self, api, ts_code, start_date=None, end_date=None, **kwargs) -> None:
        print(api)
        print(ts_code)

        print(kwargs.keys())
        pass

    def get(self):
        pass

CONFIG=[Dump()]