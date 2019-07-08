import pandas
import click
import logging


@click.command()
@click.argument("path")
def main(path):
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"opening {path}")

    with open(path) as file:
        lines = [(line, count) for count, line in enumerate(top_file(file).readlines())]
        df_summary, skiprows, nrows = read_block(lines, file, ",Cash,")
        df_balances, skiprows, nrows = read_block(
            lines, file, "Cash balances", start=skiprows + nrows + 1
        )
        df_assets, skiprows, nrows = read_block(
            lines, file, "Asset class,PROD Type", start=skiprows + nrows + 1
        )
        pass


def read_block(lines, file, header, start=0):
    for line, n in lines[start:]:
        if line.startswith(header):
            skiprows = n
            for line, n in lines[skiprows:]:
                if line.strip() == "":
                    nrows = n - skiprows - 1
                    return (
                        pandas.read_csv(top_file(file), skiprows=skiprows, nrows=nrows),
                        skiprows,
                        nrows,
                    )
    return None, None, None


def top_file(file):
    file.seek(0)
    return file


if __name__ == "__main__":
    main()
