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
            securities = {'securities': statement.positions()}
            if 'holdings' in cfg['accounts'][name]:
                assert 'securities' not in cfg['accounts'][name][
                    'holdings']  # haven't implemented merging securities from user config and from ofx file
                cfg['accounts'][name]['holdings'].update(securities)
            else:
                cfg['accounts'][name]['holdings'] = securities
            # Note: no need to read the cash_balance value from the statement because money market funds show up in statement.positions and should be categorized as cash
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
