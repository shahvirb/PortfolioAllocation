import yaml
import pandas as pd
import securities


def merge_dicts(list):
    d = {}
    for x in list:
        d.update(x)
    return d


def account_basic_df(cfg, account):
    categories = securities.SecurityCategories(cfg)
    df = pd.DataFrame()
    for symbol,qty in merge_dicts(account).items():
        df.at[symbol, 'Symbol'] = symbol
        df.at[symbol, 'Qty'] = qty
        price = securities.price(symbol)
        df.at[symbol, 'Price'] = price
        df.at[symbol, 'Value'] = price * qty
        df.at[symbol, 'Category'] = categories(symbol)
    df = df.set_index('Symbol')
    return df


def account_securities_df(cfg, account):
    df = account_basic_df(cfg, account)
    df.at['Total','Value'] = df['Value'].sum()
    df['Weight'] = df['Value'] / df.at['Total','Value']
    return df


def account_categories_df(df):
    cats = df.groupby('Category')['Value'].sum().to_frame()
    cats['Weight'] = cats['Value'] / cats['Value'].sum()
    cats = cats.sort_values(by=['Weight'], ascending=False)
    cats.at['Total', 'Value'] = cats['Value'].sum()
    cats.at['Total', 'Weight'] = cats['Weight'].sum()
    return cats


def portfolio_df(cfg, portfolio):
    portfolios = []
    for name in cfg['accounts']:
        acct = cfg['accounts'][name]
        acct_df = account_basic_df(cfg, acct['holdings']['securities'])
        acct_df['Account'] = name
        portfolios.append(acct_df)
    port_df = pd.concat(portfolios)
    port_df['Weight'] = port_df['Value'] / port_df['Value'].sum()
    port_df = port_df.reset_index().set_index('Account')
    return port_df


def run_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


def print_df(df):
    if run_from_ipython():
        display(df)
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)


def read_yaml(path):
    with open(path, 'r') as doc:
        return yaml.load(doc)


def load_yaml(path):
    cfg = read_yaml(path)
    if 'include' in cfg and cfg['include']:
        for inc in cfg['include']:
            inc_yaml = read_yaml(inc)
            cfg = {**cfg, **inc_yaml}
    return cfg


def accounts_report(cfg):
    for name in cfg['accounts']:
        acct = cfg['accounts'][name]
        acct_df = account_securities_df(cfg, acct['holdings']['securities'])
        print(name)
        print_df(acct_df)
        print_df(account_categories_df(acct_df))
        print()


def portfolios_report(cfg):
    for name in cfg['portfolios']:
        port = cfg['portfolios'][name]
        print(name)
        port_df = portfolio_df(cfg, port)
        print_df(port_df)
        print()


def generate_report(input):
    cfg = load_yaml(input)
    accounts_report(cfg)
    portfolios_report(cfg)

if __name__ == "__main__":
    generate_report('sample.yaml')