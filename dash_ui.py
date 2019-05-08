import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import report
import config
import plotly.graph_objs as go
import urllib


PAGEMAP = {
    '/test': lambda x: html.P("This is just a test page"),
}

TEMPL_ACCT_HREF = '/accounts/{}'
TEMPL_PORT_HREF = '/portfolios/{}'

if __name__ == "__main__":
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    cfg = config.load_yaml('sample.yaml')

    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                children=[dbc.DropdownMenuItem(name, href=TEMPL_ACCT_HREF.format(name)) for name in report.account_names(cfg)],
                nav=True,
                in_navbar=True,
                label="Accounts",
            ),
            dbc.DropdownMenu(
                children=[dbc.DropdownMenuItem(name, href=TEMPL_PORT_HREF.format(name)) for name in report.portfolio_names(cfg)],
                nav=True,
                in_navbar=True,
                label="Portfolios",
            ),
        ],
        brand="PortfolioAllocation",
        sticky="top",
    )

    for name in report.account_names(cfg):
        PAGEMAP[TEMPL_ACCT_HREF.format(name)] = lambda x: html.P(name)
    for name in report.portfolio_names(cfg):
        PAGEMAP[TEMPL_PORT_HREF.format(name)] = lambda x: html.P(name)

    header = html.Div(
        [
            html.P(
                [
                    "PortfolioAllocation",
                    html.Code(""),
                ]
            )
        ],
        className="mt-4",
    )

    #df = report.account_basic_df(cfg, acct_names[0])

    app.layout = html.Div(
        [
            dcc.Location(id="url"),
            navbar,
            dbc.Container(id="page-content"),
            dbc.Container(
                [
                    dcc.Interval(id="interval", interval=500, n_intervals=0),
                    header,
                    html.Br(),

                    # dash_table.DataTable(
                    #     id='table',
                    #     columns=[{"name": i, "id": i} for i in df.columns],
                    #     data=df.to_dict('records'),
                    # ),

                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                                       2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
                                    y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
                                       350, 430, 474, 526, 488, 537, 500, 439],
                                    name='Rest of world',
                                    marker=go.bar.Marker(
                                        color='rgb(55, 83, 109)'
                                    )
                                ),
                                go.Bar(
                                    x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                                       2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
                                    y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
                                       299, 340, 403, 549, 499],
                                    name='China',
                                    marker=go.bar.Marker(
                                        color='rgb(26, 118, 255)'
                                    )
                                )
                            ],
                            layout=go.Layout(
                                title='US Export of Plastic Scrap',
                                showlegend=True,
                                legend=go.layout.Legend(
                                    x=0,
                                    y=1.0
                                ),
                                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
                            )
                        ),
                        style={'height': 300},
                        id='my-graph'
                    ),
                    html.Div(style={"height": "200px"}),
                ]
            ),
        ]
    )

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        #TODO why is this callback invoked twice, first with None?
        if not pathname:
            return None

        #HACK how do you use input queries in dash?
        def lreplace(str, f, r):
            loc = str.find(f)
            if loc != -1:
                return str[:loc] + r + str[loc+1:]
            return str

        corrected = lreplace(pathname, '@', '?')
        parsed = urllib.parse.urlparse(corrected)

        if parsed.path in PAGEMAP:
            return PAGEMAP[parsed.path](parsed)

        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {parsed.path} was not recognised..."),
            ]
        )

    app.run_server(port=8887, debug=True)