import pandas
import click
import logging
from pathlib import Path

@click.command()
@click.argument("path")
def main(path):
    logging.basicConfig(level=logging.DEBUG)
    path = Path(path)
    logging.info(f"opening {path}")

    summary, balances, assets = read_bmo_file(path)

    gen_accounts_yaml(path.name, assets)

    pass

def gen_accounts_yaml(name, assets):
    assets = assets[assets.Symbol != ' ']


def read_bmo_file(path):
    # TODO the assets csv section has 2 extra commas that need to be dealt with
    with open(path) as file:
        lines = [(line, count) for count, line in enumerate(top_file(file).readlines())]
        df_summary, skiprows, nrows = read_block(lines, file, ",Cash,", None)
        df_balances, skiprows, nrows = read_block(
            lines, file, "Asset class,PROD Type", start=skiprows + nrows + 1
        )
        df_assets, skiprows, nrows = read_block(
            lines, file, "Asset class,PROD Type", start=skiprows + nrows + 1
        )
    return df_summary, df_balances, df_assets


def read_block(lines, file, header, index_col=None, start=0):
    for line, n in lines[start:]:
        if line.startswith(header):
            skiprows = n
            for line, n in lines[skiprows:]:
                if line.strip() == "":
                    nrows = n - skiprows - 1
                    return (
                        pandas.read_csv(top_file(file), skiprows=skiprows, nrows=nrows, index_col=index_col),
                        skiprows,
                        nrows,
                    )
    return None, None, None


def top_file(file):
    file.seek(0)
    return file


if __name__ == "__main__":
    main()
