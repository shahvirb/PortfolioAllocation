import datetime
import pandas as pd
# import pyEX
import functools
import yahoo_finance_api2.share as yfshare
import yahoo_finance_api2.exceptions as yfe

MEMO_SIZE = 128


# class IEXData():
#     def __init__(self, apikey=None):
#         if not apikey:
#             try:
#                 import iexapikey
#                 apikey = iexapikey.IEX_KEY
#             except ModuleNotFoundError as e:
#                 pass
#         self.client = pyEX.Client(apikey)
#
#     @functools.lru_cache(maxsize=MEMO_SIZE)
#     def price(self, symbol, raises=False):
#         try:
#             return self.client.price(symbol)
#         except pyEX.PyEXception as e:
#             if raises:
#                 raise e
#             else:
#                 print(e)
#         return 0


class YahooFinanceData():
    @staticmethod
    def make_datetime(ts):
        return datetime.datetime.fromtimestamp(ts / 1000)

    @staticmethod
    @functools.lru_cache(maxsize=MEMO_SIZE)
    def find_last(symbol):
        def find_last_valid(hd):
            for i, price in reversed(list(enumerate(hd['close']))):
                if price:
                    return i
            return None

        try:
            share = yfshare.Share(symbol)
            if share:
                hd = share.get_historical(yfshare.PERIOD_TYPE_DAY, 5, yfshare.FREQUENCY_TYPE_DAY, 1)
                if hd:
                    return hd, find_last_valid(hd)
        except yfe.YahooFinanceError as e:
            raise e
        return None

    @staticmethod
    def price(symbol, raises=False):
        data, last = YahooFinanceData.find_last(symbol)
        return data['close'][last]

    @staticmethod
    def price_with_time(symbol):
        data, last = YahooFinanceData.find_last(symbol)
        time_str = str(YahooFinanceData.make_datetime(data['timestamp'][last]))
        return data['close'][last], time_str


class SecurityCategories():
    def __init__(self, cfg):
        self.symbol_cats = {}
        self.default_category = cfg['security_categorization']['default']
        categories = cfg['security_categorization']['categories']
        for c in categories:
            if categories[c]:
                for s in categories[c]:
                    self.symbol_cats[s] = c

    def category(self, symbol, default=None):
        if symbol in self.symbol_cats:
            return self.symbol_cats[symbol]
        else:
            return self.default_category if not default else default

    def __call__(self, symbol):
        return self.category(symbol)


def symbol_categories_df(cfg):
    syms = set()
    for act in cfg['accounts']:
        for s in cfg['accounts'][act]['holdings']['securities'].keys():
            syms.add(s)
    cats = SecurityCategories(cfg)
    df = pd.DataFrame()
    datasource = YahooFinanceData()
    for s in syms:
        df.at[s, 'Symbol'] = s
        df.at[s, 'Category'] = cats.category(s, default='{} [Default]'.format(cats.default_category))
        price, time = datasource.price_with_time(s)
        df.at[s, 'Price'] = price
        df.at[s, 'Updated'] = time
    df = df.set_index('Symbol').reset_index().sort_values('Symbol')

    return df


if __name__ == "__main__":
    def config_read_example():
        import config
        cfg = config.load_yaml('sample.yaml')
        cats = symbol_categories_df(cfg)
        datasource = YahooFinanceData()
        cats['Price'] = cats.apply(lambda x: datasource.price(x['Symbol']), axis=1)
        print(cats)


    def one_symbol_example():
        datasource = YahooFinanceData()
        print(datasource.price_with_time('VTI'))


    one_symbol_example()
