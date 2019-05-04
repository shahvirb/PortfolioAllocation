import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

DBC_DOCS = "https://dash-bootstrap-components.opensource.faculty.ai/"
DBC_GITHUB = "https://github.com/facultyai/dash-bootstrap-components"



if __name__ == "__main__":
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Accounts", href=DBC_GITHUB)),
            dbc.NavItem(dbc.NavLink("Portfolios", href=DBC_GITHUB)),
        ],
        brand="PortfolioAllocation",
        brand_href=DBC_DOCS,
        sticky="top",
    )

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

    app.layout = html.Div(
        [
            navbar,
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

    app.run_server(port=8888, debug=True)