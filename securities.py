import pandas as pd
import pyEX
import functools

MEMO_SIZE = 128

class SecurityData():
    def __init__(self, apikey=None):
        if not apikey:
            try:
                import iexapikey
                apikey = iexapikey.IEX_KEY
            except ModuleNotFoundError as e:
                pass
        self.client = pyEX.Client(apikey)

    @functools.lru_cache(maxsize=MEMO_SIZE)
    def price(self, symbol, raises=False):
        try:
            return self.client.price(symbol)
        except pyEX.PyEXception as e:
            if raises:
                raise e
        return 0


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
    datasource = SecurityData()
    for s in syms:
        df.at[s, 'Symbol'] = s
        df.at[s, 'Category'] = cats.category(s, default='{} [Default]'.format(cats.default_category))
        pr = None
        try:
            pr = datasource.price(s, raises=True)
        except pyEX.PyEXception as e:
            pass
        df.at[s, 'Price'] = pr
    df = df.set_index('Symbol').reset_index().sort_values('Symbol')

    return df


if __name__ == "__main__":
    import config
    cfg = config.load_yaml('sample.yaml')
    cats = symbol_categories_df(cfg)
    cats['Price'] = cats.apply(lambda x: price(x.name), axis=1)
