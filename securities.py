import pyEX
import functools

MEMO_SIZE = 32

@functools.lru_cache(maxsize=MEMO_SIZE)
def price(symbol):
    return pyEX.price(symbol)

#@functools.lru_cache(maxsize=MEMO_SIZE)
# def category(cfg, symbol):
#     categories = cfg['security_categorization']['categories']
#     for c in categories:
#         if symbol in categories[c]:
#             return c
#     return cfg['security_categorization']['default']


class SecurityCategories():
    def __init__(self, cfg):
        self.symbol_cats = {}
        self.default_category = cfg['security_categorization']['default']
        categories = cfg['security_categorization']['categories']
        for c in categories:
            if categories[c]:
                for s in categories[c]:
                    self.symbol_cats[s] = c

    def category(self, symbol):
        if symbol in self.symbol_cats:
            return self.symbol_cats[symbol]
        else:
            return self.default_category

    def __call__(self, symbol):
        return self.category(symbol)


def categories(cfg):
    symbol_cats = {}
    categories = cfg['security_categorization']['categories']
    for c in categories:
        if categories[c]:
            for s in categories[c]:
                symbol_cats[s] = categories[c]
    return symbol_cats


def category(categories, symbol):
    if symbol not in categories:
        pass