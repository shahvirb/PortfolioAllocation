import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
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
                        dbc.Container(id="page-content", fluid=True),
                    ],
                    fluid=True
                ),
            ]
        )

    def securities_table(self, securities):
        titled_df = self.titled_df('Securities', securities)
        table = titled_df.children[1]
        table.style_data_conditional = [
            {
                'if': {
                    'column_id': 'Price',
                    'filter_query': '{Price} <= 0',
                },
                'backgroundColor': 'tomato',
            }
        ]
        return titled_df

    def home_page(self, securities):
        return dbc.Container(
            [
                self.securities_table(securities)
            ]
        )

    def titled_df(self, title, df):
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=self.dfrender.format(df),
            style_as_list_view=True,
            # filtering=True,
            # sorting=True,
        )
        return dbc.Container(
            [
                self.header(title),
                table
            ]
        )

    def account_page(self, name, securities, categories, hierarchy):
        col0 = [
            self.titled_df('Securities', securities),
            self.titled_df('Categories', categories),
        ]
        col1 = [
            dcc.Graph(figure=plot.category_weights_sunburst(hierarchy)),
            dcc.Graph(figure=plot.category_weights(categories)),
        ]

        return graph_layout(col0, col1)

    def portfolio_page(self, name, portfolio, categories, compare, hierarchy, accounts):
        col0 = [
            self.titled_df(name, accounts),
            self.titled_df(name, portfolio),
            self.titled_df('Target Portfolio Comparison', compare),
        ]
        col1 = [
            dcc.Graph(figure=plot.account_weights(accounts)),
            dcc.Graph(figure=plot.category_weights_sunburst(hierarchy)),
            dcc.Graph(figure=plot.category_weights(categories)),
        ]
        return graph_layout(col0, col1)


def graph_layout(col0, col1):
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(col0, width=6),
                dbc.Col(col1, width=6)
            ])
        ],
        fluid=True
    )