import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plot
import formatdf
import report

TEMPL_ACCT_HREF = '/accounts/{}'
TEMPL_PORT_HREF = '/portfolios/{}'

class View:
    def __init__(self):
        self.dfrender = formatdf.DFFormatter(report.df_formatter())

    def navbar(self, accounts, portfolios):
        return dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Home', href='/')),
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

    def home_page(self, securities):
        return dbc.Container(
            [
                self.titled_df('Securities', securities)
            ]
        )

    def titled_df(self, title, df):
        return dbc.Container(
            [
                self.header(title),
                #dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True),
                dash_table.DataTable(
                    data = df.to_dict('records'),
                    columns = self.dfrender.format(df),
                    #filtering=True,
                    sorting=True,
                )
            ]
        )

    def account_page(self, name, basic, securities, categories, hierarchy):
        col0 = [
            self.titled_df(name, basic),
            self.titled_df('Securities', securities),
            self.titled_df('Categories', categories),
        ]

        col1 = [
            dcc.Graph(figure=plot.category_weights(categories)),
            dcc.Graph(figure=plot.category_weights_sunburst(hierarchy)),
        ]
        return graph_layout(col0, col1)

    def portfolio_page(self, name, portfolio, compare, hierarchy):
        col0 = [
            self.titled_df(name, portfolio),
            self.titled_df('Target Portfolio Comparison', compare),
        ]
        col1 = [
            dcc.Graph(figure=plot.category_weights(portfolio)),
            dcc.Graph(figure=plot.category_weights_sunburst(hierarchy)),
        ]
        return graph_layout(col0, col1)


def graph_layout(col0, col1):
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(col0),
                dbc.Col(col1, width=4)
            ])
        ]
    )