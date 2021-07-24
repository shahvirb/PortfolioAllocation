import decimal

import yaml


def read_yaml(path):
    with open(path, 'r') as doc:
        return yaml.load(doc, Loader=yaml.FullLoader)


def includes(yaml):
    return yaml['include'] if 'include' in yaml else ()


def load_yaml(path):
    cfg = read_yaml(path)
    for inc in includes(cfg):
        inc_yaml = read_yaml(inc)
        cfg = {**cfg, **inc_yaml}
    return cfg


def load_ofx(cfg):
    for name, acct in cfg['accounts'].items():
        if 'ofx' in acct:
            import ofxparser
            ofx = ofxparser.readfile(acct['ofx'])
            statement = ofxparser.Statement(ofx, acct['ofx_accountid'])
            cfg['accounts'][name]['holdings'] = {
                'securities': statement.positions(),
                'cash': float(decimal.Decimal(
                    cfg['accounts'][name].get('cash', 0)) + statement.cash_balance())
            }
            # cast the resulting cash value to a float because the user yaml file cash value is a float
    return cfg


class UserConfig:
    def __init__(self, path):
        self.load_yaml(path)

    def load_yaml(self, path):
        self.path = path
        self.cfg = load_yaml(path)
        self.cfg = load_ofx(self.cfg)

    def __getitem__(self, item):
        return self.cfg[item]

    def __setitem__(self, key, value):
        self.cfg[key] = value

    def account_names(self):
        return [name for name in self.cfg['accounts']]

    def portfolio_names(self):
        return [name for name in self.cfg['portfolios']]

    def get_account(self, name):
        return self.cfg['accounts'][name]

    def get_portfolio(self, name):
        return self.cfg['portfolios'][name]


if __name__ == "__main__":
    pass
