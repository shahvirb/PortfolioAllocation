import yaml


def read_yaml(path):
    with open(path, 'r') as doc:
        return yaml.load(doc)


def includes(yaml):
    return yaml['include'] if 'include' in yaml else ()


def load_yaml(path):
    cfg = read_yaml(path)
    for inc in includes(cfg):
        inc_yaml = read_yaml(inc)
        cfg = {**cfg, **inc_yaml}
    return cfg


class UserConfig:
    def __init__(self, path):
        self.load_yaml(path)

    def load_yaml(self, path):
        self.path = path
        self.cfg = load_yaml(path)

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
