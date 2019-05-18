import pandas as pd
import securities
import qgrid
import config

# def merge_dicts(list):
#     d = {}
#     for x in list:
#         d.update(x)
#     return d


def run_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


def init_display():
    import qgrid
    from IPython.display import display, HTML
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.ast_node_interactivity = "all"


def print_df(df):
    if run_from_ipython():
        #display(df)
        flat = flatten_multiindex_columns(df)
        qgrid_widget = qgrid.show_grid(flat, show_toolbar=True)
        display(qgrid_widget)
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)


def flatten_multiindex_columns(df):
    if df.ndim > 1 and isinstance(df.columns, pd.MultiIndex):
        flat = df
        flat.columns = [' '.join(col).strip() for col in df.columns.values]
        return flat
    return df


def account_basic_df(cfg, account):
    categories = securities.SecurityCategories(cfg)
    df = pd.DataFrame()
    for symbol,qty in account['holdings']['securities'].items():
        df.at[symbol, 'Symbol'] = symbol
        df.at[symbol, 'Qty'] = qty
        price = securities.price(symbol)
        df.at[symbol, 'Price'] = price
        df.at[symbol, 'Value'] = price * qty
        df.at[symbol, 'Category'] = categories(symbol)
    cash = pd.DataFrame({
        'Symbol':['Cash'],
        'Value': [account['holdings']['cash']],
        'Category': 'Cash'
    })
    df = df.append(cash, ignore_index=True)
    #df = df.set_index('Symbol', drop=False)
    df = df.reset_index()
    return df[['Symbol', 'Category', 'Price', 'Qty', 'Value']]


def account_securities_df(cfg, account):
    df = account_basic_df(cfg, account)
    # df.at['Total','Value'] = df['Value'].sum()
    df['Weight'] = df['Value'] / df['Value'].sum()
    return df


def account_categories_df(df):
    cats = df.groupby('Category')['Value'].sum().to_frame()
    cats['Weight'] = cats['Value'] / cats['Value'].sum()
    cats = cats.sort_values(by=['Weight'], ascending=False)
    # cats.at['Total', 'Value'] = cats['Value'].sum()
    # cats.at['Total', 'Weight'] = cats['Weight'].sum()
    return cats.reset_index()


def portfolio_df(cfg, portfolio):
    portfolios = []

    accounts = set()
    if 'accounts' in portfolio:
        accounts.update(portfolio['accounts'])
    if 'portfolios' in portfolio:
        accounts.update([act for pname in portfolio['portfolios'] for act in cfg['portfolios'][pname]['accounts']])

    for name in accounts:
        acct = cfg.get_account(name)
        acct_df = account_basic_df(cfg, acct)
        acct_df['Account'] = name
        portfolios.append(acct_df)
    port_df = pd.concat(portfolios)
    port_df['Weight'] = port_df['Value'] / port_df['Value'].sum()
    return port_df[['Account', 'Symbol', 'Category', 'Price', 'Qty', 'Value', 'Weight']]


def portfolio_comparison(target, pdf):
    dedupe = pdf.groupby(['Symbol', 'Category']).sum().reset_index()
    #report.print_df(dedupe.reset_index())
    compare = dedupe.pivot(index='Category', columns='Symbol', values=['Value', 'Weight'])
    compare['Value', 'Total'] = compare['Value'].sum(axis=1)
    compare['Weight', 'Total'] = compare['Weight'].sum(axis=1)
    compare['Weight', 'Error'] = compare['Weight','Total'] - [target['holdings']['category_weighted'][name] for name in compare.index]
    compare['Value', 'Error'] = compare['Weight', 'Error'] * compare['Value', 'Total'].sum()
    assert compare['Value', 'Error'].sum() <= 0.01
    compare = flatten_multiindex_columns(compare).reset_index()
    return compare[['Category', 'Value Total', 'Value Error', 'Weight Total', 'Weight Error']]


def portfolio_target_comparison(cfg, port):
    return portfolio_comparison(cfg['target_portfolios'][port['target']], portfolio_df(cfg, port))


def accounts_report(cfg):
    for name in cfg.account_names():
        acct = cfg.get_account(name)
        acct_df = account_securities_df(cfg, acct)
        print(name)
        print_df(acct_df)
        cats = account_categories_df(acct_df)
        print_df(cats)
        print()


def portfolios_report(cfg):
    for name in cfg.portfolio_names():
        port = cfg['portfolios'][name]
        print(name)
        port_df = portfolio_df(cfg, port)
        print_df(port_df)
        compare = portfolio_comparison(cfg['target_portfolios'][port['target']], port_df)
        print_df(compare)
        print()


def generate_report(input):
    cfg = config.UserConfig(input)
    accounts_report(cfg)
    portfolios_report(cfg)


if __name__ == "__main__":
    generate_report('sample.yaml')