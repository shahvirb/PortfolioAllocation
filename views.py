import dash_bootstrap_components as dbc

TEMPL_ACCT_HREF = '/accounts/{}'
TEMPL_PORT_HREF = '/portfolios/{}'

class View:
    def __init__(self):
        pass

    def navbar(self, accounts, portfolios):
        return dbc.NavbarSimple(
            children=[
                dbc.DropdownMenu(
                    children=[dbc.DropdownMenuItem(name, href=TEMPL_ACCT_HREF.format(name)) for name in
                              accounts],
                    nav=True,
                    in_navbar=True,
                    label="Accounts",
                ),
                dbc.DropdownMenu(
                    children=[dbc.DropdownMenuItem(name, href=TEMPL_PORT_HREF.format(name)) for name in
                              portfolios],
                    nav=True,
                    in_navbar=True,
                    label="Portfolios",
                ),
            ],
            brand="PortfolioAllocation",
            sticky="top",
        )

    def account_page(self, name, basic):
        # TODO do something with the name
        return dbc.Table.from_dataframe(basic, striped=True, bordered=True, hover=True)