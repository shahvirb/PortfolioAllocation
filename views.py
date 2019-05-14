import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

TEMPL_ACCT_HREF = '/accounts/{}'
TEMPL_PORT_HREF = '/portfolios/{}'

class View:
    def __init__(self):
        # Why is this an object?
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

    def header(self, text):
        return html.Div(
            [
                html.P([text, html.Code("")])
            ],
            className="mt-4",
        )

    def layout(self, navbar):
        return html.Div(
            [
                dcc.Location(id="url"),
                navbar,
                dbc.Container(
                    [
                        dcc.Interval(id="interval", interval=500, n_intervals=0),
                        #self.header('PortfolioAllocation'),
                        dbc.Container(id="page-content"),
                    ]
                ),
            ]
        )

    def home_page(self):
        return self.header('Welcome to PortfolioAllocation')

    def titled_df(self, title, df):
        return dbc.Container(
            [
                self.header(title),
                dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),
            ]
        )

    def account_page(self, name, basic, securities, categories):

        return dbc.Container(
            [
                self.titled_df(name, basic),
                self.titled_df('Securities', securities),
                self.titled_df('Categories', categories),
            ]
        )