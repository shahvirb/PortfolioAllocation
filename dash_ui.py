import click
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import urllib
import uicontrollers


# TODO surely there's a better way than rolling my own routing mechanism
PAGEMAP = {
    '/test': lambda x: html.P("This is just a test page"),
}

@click.command()
@click.option('--config', default=None)
def start_server(config):
    uictrl = uicontrollers.UIController(config)
    PAGEMAP.update(uictrl.pagemap())

    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.GRID])
    app.layout = uictrl.layout()

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
        # TODO move this to views.py
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {parsed.path} was not recognised..."),
            ]
        )
    app.run_server(port=8887, debug=True)


def main():
    return start_server(obj={})

if __name__ == "__main__":
    main()