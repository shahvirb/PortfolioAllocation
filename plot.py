import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import cufflinks as cf


def category_weights(df):
    return df.iplot(
        asFigure=True,
        kind='pie',
        labels='Category',
        values='Weight',
        title='Category Weights',
    )


def category_weights_sunburst(df):
    trace = go.Sunburst(
        #ids = list(df['labels'].values),
        labels = list(df['labels'].values),
        parents = list(df['parents'].values),
        values = list(df['Weight'].values),
    )
    layout = go.Layout(
        title = 'Category Weights',
        #margin=go.layout.Margin(t=0, l=0, r=0, b=0),
    )
    return go.Figure([trace], layout)


if __name__ == '__main__':
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    trace = go.Sunburst(
        labels=["Eve", "Cain", "Seth", "Enos", "Noam", "Abel", "Awan", "Enoch", "Azura"],
        parents=["", "Eve", "Eve", "Seth", "Seth", "Eve", "Eve", "Awan", "Eve"],
        values=[10, 14, 12, 10, 2, 6, 6, 4, 4],
    )

    layout = go.Layout()

    app.layout = html.Div(children=[
        dcc.Graph(
            id='example-graph',
            figure=go.Figure([trace], layout),
            ),
        ])

    app.run_server(debug=True)