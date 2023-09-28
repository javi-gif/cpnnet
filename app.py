

import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import time
import datetime
import requests
import json
from datetime import date


url = 'https://portal.cpnnetsecurity.com/api/estimates/search'
headers = {'authtoken':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiQXBpRmluYW5jaWVyYSIsIm5hbWUiOiJBcGlfRmluYW5jaWVyYSIsImV4cGlyYXRpb25fZGF0ZSI6IjIwMjQtMDgtMzAgMTU6MzY6MDAiLCJleHAiOjE3MjUwNDY1NjB9.7L0UZzDlbDXkra-5GXTtjzUD4LYWr0ajwaVrhvAauR0'}
r = requests.get(url,headers=headers)
posts = r.json()
data = []
for x in r.json():
   # print(x['number'])
   # status=x['status']
   # assigned_staff=x['assigned_staff']
    data.append(x) 
    df=pd.json_normalize(data)

df=df.astype({'total':'float','sent':'float'})

mgr_options = df["assigned_staff"].astype(str).unique()

app = dash.Dash()

app.layout = html.Div([
    html.H2("Sales Funnel Report"),
    html.Div(
        [
            dcc.Dropdown(
                id="assigned_staff",
                options=[{
                    'label': i,
                    'value': i
                } for i in mgr_options],
                value='All Managers'),
        ],
        style={'width': '25%',
               'display': 'inline-block'}),
    dcc.Graph(id='funnel-graph'),
])


@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'),
    dash.dependencies.Input('assigned_staff', 'value')
    )
def update_graph(assigned_staff):
    if assigned_staff == "All Managers":
        df_plot = df.copy()
    else:
        df_plot = df[df['assigned_staff'] == assigned_staff]

    pv = pd.pivot_table(
        df_plot,
        index=['company'],
        columns=["status"],
        values=['total'],
        aggfunc=sum,
        fill_value=0
        )

    trace1 = go.Bar(x=pv.index, y=pv[('total', 'Draft')], name='Draft')
    trace2 = go.Bar(x=pv.index, y=pv[('total', 'Accepted')], name='Accepted')
    trace3 = go.Bar(x=pv.index, y=pv[('total', 'Sent')], name='Sent')
    trace4 = go.Bar(x=pv.index, y=pv[('total', 'Expired')], name='Expired')

    return {
        'data': [trace1, trace2, trace3, trace4],
        'layout':
        go.Layout(
            title='Customer Order Status for {}'.format(assigned_staff),
            barmode='stack')
    }


if __name__ == '__main__':
    app.run_server(debug=True)