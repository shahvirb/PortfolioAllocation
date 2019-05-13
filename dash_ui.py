import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import urllib
import uicontrollers


# TODO surely there's a better way than rolling my own routing mechanism
PAGEMAP = {
    '/test': lambda x: html.P("This is just a test page"),
}

if __name__ == "__main__":
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    uictrl = uicontrollers.UIController('sample.yaml')
    navbar = uictrl.navbar()
    PAGEMAP.update(uictrl.pagemap())

    # def render_account_page(parsed):
    #     name = parsed.path.split('/')[2]
    #     return uictrl.account_page(name)

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

    # df = report.account_basic_df(cfg, acct_names[0])

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

        #HACK how do you use input queries in dash? For now just use '@' to denote
        # the start of the query string
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