import yaml
import pandas as pd
import securities


def merge_dicts(list):
    d = {}
    for x in list:
        d.update(x)
    return d


def account_securities_df(cfg, account):
    data = {
        'Symbol': [],
        'Qty': [],
        'Price': [],
        'Value': [],
        'Category': [],
    }
    categories = securities.SecurityCategories(cfg)
    #TODO directly make a dataframe instead of a making a dict first
    for symbol,qty in merge_dicts(account).items():
        data['Symbol'].append(symbol)
        data['Qty'].append(qty)
        price = securities.price(symbol)
        data['Price'].append(price)
        data['Value'].append(price * qty)
        data['Category'].append(categories(symbol))
    df = pd.DataFrame.from_dict(data)

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


def print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


def generate_report(input):
    cfg = None
    with open(input, 'r') as doc:
        cfg = yaml.load(doc)

    for account in cfg['accounts']:
        for name, acct in account.items():
            acct_df = account_securities_df(cfg, acct['holdings']['securities'])
            print(name)
            print_df(acct_df)
            print_df(account_categories_df(acct_df))
            print()


if __name__ == "__main__":
    generate_report('sample.yaml')