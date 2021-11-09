import json
import requests
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

from config import *


app = dash.Dash()
server = app.server

def get_show_scatter():
    sctx = []
    scty = []
    r_get = requests.get(rest_api_url+"11")
    data_dict = json.loads(r_get.text)
    for key, value in data_dict.items():
        sctx.append(key)
        scty.append(value)
    trace = go.Scatter(
        x=sctx,
        y=scty,
        name='energy'
    )
    layout=go.Layout(
        title='Energy Information of September 2021',
        yaxis={
            'hoverformat': '.6f'
        }
    )
    return go.Figure(
        data = [trace],
        layout = layout
    )

app.layout = html.Div([
    dcc.Graph(
        id='show_scatter',
        figure=get_show_scatter()
    ),
], style={'margin': 100})

if __name__ == '__main__':
    app.run_server(debug=True)