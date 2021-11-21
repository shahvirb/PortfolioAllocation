import numpy as np
import pandas as pd
from dash_table import FormatTemplate as FormatTemplate
from dash_table.Format import Format

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
        # display(df)
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
    def write_row(df, symbol, qty, price, value, category):
        df.at[symbol, 'Symbol'] = symbol
        df.at[symbol, 'Qty'] = qty
        df.at[symbol, 'Price'] = price
        df.at[symbol, 'Value'] = value
        df.at[symbol, 'Category'] = category

    categories = securities.SecurityCategories(cfg)
    df = pd.DataFrame()
    datasource = securities.YahooFinanceData()
    holdings = account['holdings']
    if 'securities' in holdings:
        for symbol, qty in holdings['securities'].items():
            price = datasource.price(symbol)
            write_row(df, symbol, qty, price, price*qty, categories(symbol))
    if 'cash' in holdings:
        write_row(df, 'Cash', np.nan, np.nan, holdings['cash'], 'Cash')
    if 'fixed value' in holdings:
        for name, item in holdings['fixed value'].items():
            write_row(df, name, np.nan, np.nan, item['value'], item['category'])
    df = df.reset_index()
    return df[['Symbol', 'Category', 'Price', 'Qty', 'Value']]


def account_securities_df(cfg, account):
    df = account_basic_df(cfg, account)
    # df.at['Total','Value'] = df['Value'].sum()
    df['Weight'] = df['Value'] / df['Value'].sum()
    return df


def group_df_by(df, label):
    cats = df.groupby(label)['Value'].sum().to_frame()
    cats['Weight'] = cats['Value'] / cats['Value'].sum()
    cats = cats.sort_values(by=['Weight'], ascending=False)
    return cats.reset_index()


def account_categories_df(df):
    return group_df_by(df, 'Category')


def account_hierarchy(securities_df):
    categories = securities_df.groupby(['Category']).sum().reset_index().rename(index=str,
                                                                                columns={'Category': 'labels'})
    root_label = 'Weights'
    categories['parents'] = root_label
    categories['Weight'] = 0  # because of branchvalues == remainder
    symbols = securities_df.groupby(['Symbol', 'Category']).sum()
    try:
        symbols = symbols.drop('Cash')  # This causes a circular reference because the symbol name == category name
    except KeyError:
        # If we're here then 'Cash' doesn't exist and we can no-op
        pass

    symbols = symbols.reset_index().rename(index=str, columns={'Symbol': 'labels', 'Category': 'parents'})
    merged = categories.merge(symbols, how='outer')
    # merged.set_index('labels')
    root = pd.DataFrame({
        'labels': root_label,
        'parents': '',
        'Weight': 0,
    }, index=[0])
    merged = pd.concat([root, merged])
    # Ensure no circular references
    assert True not in set(merged['labels'] == merged['parents'])
    return merged


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
    port_df = port_df[['Account', 'Symbol', 'Category', 'Price', 'Qty', 'Value', 'Weight']]
    port_df.reset_index(drop=True, inplace=True)
    return port_df


def portfolio_comparison(target, pdf):
    assert 1.0 - sum(
        target['holdings']['category_weighted'].values()) < 1e-4  # Ensure that target portfolio weights sum to 1
    dedupe = pdf.groupby(['Symbol', 'Category']).sum().reset_index()
    # report.print_df(dedupe.reset_index())
    compare = dedupe.pivot(index='Category', columns='Symbol', values=['Value', 'Weight'])

    # Create new rows for categories which exist in target but not in pdf
    missing_categories = set(target['holdings']['category_weighted'].keys()) - set(compare.index.values)
    for c in missing_categories:
        compare.loc[c, :] = np.nan

    compare['Value', 'Total'] = compare['Value'].sum(axis=1)
    compare['Weight', 'Total'] = compare['Weight'].sum(axis=1)
    compare['Weight', 'Error'] = compare['Weight', 'Total'] - [target['holdings']['category_weighted'].get(name, 0) for
                                                               name in compare.index]
    compare['Value', 'Error'] = compare['Weight', 'Error'] * compare['Value', 'Total'].sum()
    assert compare['Value', 'Error'].sum() <= 0.01

    compare = flatten_multiindex_columns(compare).reset_index()
    compare = compare[['Category', 'Value Total', 'Value Error', 'Weight Total', 'Weight Error']]
    return compare


def portfolio_target_comparison(cfg, port):
    return portfolio_comparison(cfg['target_portfolios'][port['target']], portfolio_df(cfg, port))


def portfolio_hierarchy(pdf):
    hierarchy = account_hierarchy(pdf)
    hierarchy['Weight'] = 0  # because branch_values == 'remainder
    accounts = pdf.rename(index=str, columns={'Account': 'labels', 'Symbol': 'parents'})
    merged = hierarchy.merge(accounts, how='outer')
    return merged


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


def df_formatter():
    return {
        'Price': {'type': 'numeric', 'format': FormatTemplate.money(2)},
        # Format(precision=0, scheme=Scheme.fixed, symbol=Symbol.yes, symbol_prefix='$'),
        'Value': {'type': 'numeric', 'format': FormatTemplate.money(0)},
        'Weight': {'type': 'numeric', 'format': FormatTemplate.percentage(1)},
        # 'Qty': {'type': 'numeric', 'format': Format(precision=.3)},
    }


if __name__ == "__main__":
    generate_report('sample.yaml')
